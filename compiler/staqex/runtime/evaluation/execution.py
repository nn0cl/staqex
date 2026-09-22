"""Execution-shell successor for the evaluator runtime.

This module owns statement execution order while the live mutable state remains
owned by the ``Evaluator`` context passed into its callbacks.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any, TextIO

from ...ast_nodes import (
    AssignStmt, Call, ClassDecl, CompilationUnit, DynamicQpuStmt, EnumDecl,
    ExprStmt, ForEachStmt, FunDecl, KetLit, Measure, ReturnStmt, Snapshot,
    StateBind, StructDecl, TupleExpr, Var,
)
from ...continuous_lowering import GridHamiltonianRef
from ...finite_binder import lower_finite_binder_operators, operator_declared_space
from ...kernel_literals import SECOND_QUANTIZED_FAMILIES as _SECOND_QUANTIZED_FAMILIES
from ...stdlib.io_ops import format_snapshot_csv
from ...stdlib.prelude import PRELUDE_CONSTANTS
from ...measure_sink_port import MeasureSinkPort, TextIOMeasureSinkAdapter
from .calls import bind_call
from .context import EvaluatorContext
from .errors import KernelError
from ..joint import Joint
from .operators import resolve_operator
from .values import evaluate_value


def _prepare_execution_context(
    context: EvaluatorContext, unit: CompilationUnit
) -> dict[str, Any]:
    context.funs = {}
    context.classes = {}
    context.enums = {}
    context.structs = {}
    context.objects = {}
    context.mixed_states = {}
    context.ket_labels = {}
    context.povms = {}
    context.static_register_sizes = {}
    context.operator_spaces: dict[str, int] = {}
    context.mixed_state_measured = False
    context.execution_lane = None
    # LISS-0389: True until a dynamic-lane mid-circuit collapse finds a
    # recorded controller binding physically unreachable (vacuumed).
    context._dynamic_outcomes_confirmed = True
    context.evolution_provenance = None
    context._this = None
    context._unit = unit
    context.operators = {
        alias: GridHamiltonianRef(alias) for alias in context.grid_hamiltonians
    }
    # LISS-0432: `context.operators[name]` never rebinds mid-run, so a
    # `project ... onto P` target compiled once via `compile_hamiltonian`
    # (e.g. LISS-0430's P_F) is safe to reuse for every later `project`
    # against the same name/width within this Evaluator instance --
    # avoids literally recompiling the identical matrix a second time
    # for the confirmed design's own `X / ||X||` literal repetition.
    context._compiled_operator_cache: dict[tuple[str, int], Any] = {}
    host_arrays = context._resolve_host_coefficient_arrays(unit)
    context._resolved_host_arrays = host_arrays
    lowered_binders, _ = lower_finite_binder_operators(unit, host_arrays=host_arrays)
    for stmt in unit.main.body.stmts:
        if (
            isinstance(stmt, StateBind)
            and stmt.ty is not None
            and stmt.ty.name == "QubitRegister"
            and len(stmt.names) == 1
            and len(stmt.ty.args) == 1
        ):
            try:
                context.static_register_sizes[stmt.names[0]] = int(stmt.ty.args[0].name)
            except ValueError:
                pass
    context.scalars = dict(PRELUDE_CONSTANTS)
    context.scalar_units = {}
    context._frame_units = {}
    for d in unit.decls:
        if isinstance(d, FunDecl) and d.name != "main":
            context.funs[d.qualified_name] = d
            context.funs[d.name] = d
        elif isinstance(d, ClassDecl):
            context.classes[d.qualified_name] = d
            context.classes[d.name] = d
        elif isinstance(d, EnumDecl):
            context.enums[d.qualified_name] = d
            context.enums[d.name] = d
        elif isinstance(d, StructDecl):
            context.structs[d.qualified_name] = d
            context.structs[d.name] = d


    return lowered_binders


def _build_terminal_result(
    context: EvaluatorContext,
    joint: Joint,
    measure_result: Any | None,
    measurement_kind: str | None,
    logs: list[str],
) -> Any:
    return context._eval_result_type(
        joint=joint,
        measure=measure_result,
        rng_calls_before_measure=context._rng_calls_before_measure,
        logs=logs,
        mixed_state_measured=context.mixed_state_measured,
        execution_lane=context.execution_lane,
        measurement_kind=measurement_kind,
        deferred_pushforward=False,
        deferred_binds_applied=0,
        last_algebraic_fusion=context.last_algebraic_fusion,
        last_poly_fusion=context.last_poly_fusion,
        data_parallel_workers=context.data_parallel_workers,
        dynamic_outcomes_confirmed=context._dynamic_outcomes_confirmed,
        evolution_provenance=context.evolution_provenance,
    )


def execute_legacy_ast_body(
    context: EvaluatorContext,
    unit: CompilationUnit,
    *,
    stdout: TextIO | None = None,
) -> Any:
    joint = Joint.unit()
    if unit.main is None:
        return context._eval_result_type(
            joint=Joint.empty(),
            data_parallel_workers=context.data_parallel_workers,
        )

    lowered_binders = _prepare_execution_context(context, unit)
    measure_result: Any | None = None
    measurement_kind: str | None = None
    logs: list[str] = []
    inspect_stream = context.inspect_sink if context.inspect_sink is not None else stdout
    inspect_out: MeasureSinkPort | None = (
        TextIOMeasureSinkAdapter(inspect_stream)
        if inspect_stream is not None
        else None
    )
    deferred_pushforward = False
    deferred_binds_applied = 0

    stmts = unit.main.body.stmts
    interproc_trace = context._main_interproc_trace_eligible(stmts)
    if context._main_deferred_eligible(stmts):
        joint, measure_result, measurement_kind, deferred_binds_applied = (
            context._run_deferred_state_binds(
                joint,
                stmts,
                logs=logs,
                inspect_out=inspect_out,
                stdout=stdout,
                interproc_trace=interproc_trace,
            )
        )
        deferred_pushforward = True
        return context._eval_result_type(
            joint=joint,
            measure=measure_result,
            rng_calls_before_measure=context._rng_calls_before_measure,
            logs=logs,
            mixed_state_measured=context.mixed_state_measured,
            execution_lane=context.execution_lane,
            measurement_kind=measurement_kind,
            deferred_pushforward=deferred_pushforward,
            deferred_binds_applied=deferred_binds_applied,
            last_algebraic_fusion=context.last_algebraic_fusion,
            last_poly_fusion=context.last_poly_fusion,
            data_parallel_workers=context.data_parallel_workers,
        )

    for stmt_i, stmt in enumerate(stmts):
        if isinstance(stmt, ReturnStmt):
            raise KernelError("`main` cannot return; use terminal `measure`")
        if isinstance(stmt, DynamicQpuStmt):
            # LISS-0387 (ADR 0200): Host has already Fake-gated this run
            # by the time the evaluator is reached (unchanged from
            # LISS-0383) — real execution proceeds unconditionally here.
            joint = context._run_dynamic_qpu_block(
                joint, stmt, logs=logs, inspect_out=inspect_out
            )
            continue
        if isinstance(stmt, ForEachStmt):
            joint = context._run_foreach(joint, stmt)
            continue
        if isinstance(stmt, ExprStmt):
            if isinstance(stmt.expr, Call):
                joint = bind_call(context, joint, "__expr_stmt", stmt.expr)
                continue
            raise KernelError("unsupported expression statement")
        if isinstance(stmt, StateBind):
            if stmt.ty is not None and stmt.ty.name == "POVM":
                context._bind_povm(stmt)
                continue
            if stmt.ty is not None and stmt.ty.name == "DensityState":
                context._bind_mixed_state(stmt)
                continue
            if (
                len(stmt.names) == 1
                and isinstance(stmt.expr, KetLit)
                and stmt.expr.label in {"0", "1"}
                and (stmt.ty is None or stmt.ty.name == "State")
            ):
                # LISS-0380: Ensemble may reference a named ket Var.
                context.ket_labels[stmt.names[0]] = stmt.expr.label
            if stmt.ty is not None and stmt.ty.name == "QubitRegister":
                # Static Hilbert shape is compile-time metadata; it has no
                # runtime allocation or state coordinate in the Kernel.
                continue
            if (
                stmt.ty is not None
                and stmt.ty.name in ("Float", "Bool")
                and len(stmt.ty.args) >= 1
            ):
                # LISS-0406/LISS-0432: `Float[N]…`/`Bool[N]…`
                # coefficient-tensor declarations (ADR 0119, literal or
                # `host("key")`-sourced) are compile-time coefficient
                # data consumed only via the
                # Operator sum-binder lowering above (host_arrays) --
                # they have no live Joint/scalar role.
                continue
            if stmt.ty is not None and stmt.ty.name == "Operator":
                if len(stmt.names) != 1:
                    raise KernelError("Operator bind expects a single name")
                declared_space = operator_declared_space(stmt.ty)
                if declared_space is not None:
                    context.operator_spaces[stmt.names[0]] = declared_space
                explicit_propagator = context._explicit_propagator(stmt.expr)
                op_val = (
                    lowered_binders[stmt.names[0]]
                    if stmt.names[0] in lowered_binders
                    else explicit_propagator
                    if explicit_propagator is not None
                    else resolve_operator(context, stmt.expr)
                )
                # LISS-0229: materialize outer(psi, phi) against the live Joint.
                if (
                    isinstance(op_val, Call)
                    and isinstance(op_val.callee, Var)
                    and op_val.callee.name == "outer"
                ):
                    op_val = context._materialize_outer(joint, op_val)
                context.operators[stmt.names[0]] = op_val
                continue
            # ADR 0180: inferred Operator bind `H = Z + …` (no type head).
            if (
                stmt.ty is None
                and len(stmt.names) == 1
                and context._looks_like_operator_rhs(stmt.expr)
            ):
                op_val = resolve_operator(context, stmt.expr)
                context.operators[stmt.names[0]] = op_val
                continue
            if stmt.ty is not None and stmt.ty.name in _SECOND_QUANTIZED_FAMILIES:
                if len(stmt.names) != 1:
                    raise KernelError("second-quantized bind expects a single name")
                context._bind_second_quantized(stmt.names[0], stmt.ty.name, stmt.expr)
                continue
            # Class / struct construction (typed or ADR 0180 inferred Call)
            if len(stmt.names) == 1 and isinstance(stmt.expr, Call):
                tname = stmt.ty.name if stmt.ty is not None else None
                if tname is None:
                    tname = context._expr_qualname(stmt.expr.callee)
                if tname is not None and tname in context.classes:
                    context.objects[stmt.names[0]] = context._construct_instance(
                        tname, stmt.expr
                    )
                    continue
                if tname is not None and tname in context.structs:
                    callee_name = context._expr_qualname(stmt.expr.callee)
                    if (
                        callee_name is not None
                        and callee_name != tname
                        and callee_name in context.funs
                    ):
                        # Struct-typed binding via a free function that
                        # returns the struct (not a direct `Point(...)`
                        # constructor call) -- LISS-0338's deferred gap.
                        val, _unit = context._eval_value_with_unit(stmt.expr, {})
                        context.objects[stmt.names[0]] = val
                        continue
                    context.objects[stmt.names[0]] = context._construct_struct(
                        tname, stmt.expr
                    )
                    continue
            if stmt.ty is not None and len(stmt.names) == 1:
                tname = stmt.ty.name
                if tname in context.enums:
                    val = evaluate_value(context, stmt.expr, {})
                    if not isinstance(val, context._enum_value_type) or (
                        val.enum_name not in {tname, context.enums[tname].qualified_name}
                        and val.enum_name.split(".")[-1] != tname.split(".")[-1]
                    ):
                        raise KernelError(
                            f"ENUM_TYPE_MISMATCH: expected `{tname}`, got {val!r}"
                        )
                    context.objects[stmt.names[0]] = val
                    continue
            # Capture Type-First / ADR 0180 classical scalars for H coefficients
            # ADR 0184 / LISS-0305: classical multi-bind `J, h = 1.0, 0.5`.
            if (
                stmt.ty is None
                and len(stmt.names) >= 2
                and isinstance(stmt.expr, TupleExpr)
                and len(stmt.expr.items) == len(stmt.names)
                and not stmt.via_state_keyword
                and all(context._is_closed(it) for it in stmt.expr.items)
            ):
                try:
                    for name, item in zip(stmt.names, stmt.expr.items):
                        val, unit = context._eval_value_with_unit(item, {})
                        if isinstance(val, Fraction):
                            context.scalars[name] = val
                        elif isinstance(val, int) and not isinstance(val, bool):
                            context.scalars[name] = val
                        else:
                            context.scalars[name] = float(val)
                        if unit is not None:
                            context.scalar_units[name] = unit
                        else:
                            context.scalar_units.pop(name, None)
                    continue
                except (KernelError, TypeError, ValueError):
                    pass
            if (
                (
                    stmt.ty is None
                    or (
                        stmt.ty.name not in {"State", "Operator", "Delta"}
                        and stmt.ty.name not in context.classes
                        and stmt.ty.name not in context.structs
                        and stmt.ty.name not in context.enums
                    )
                )
                and len(stmt.names) == 1
                and context._is_closed(stmt.expr)
                and not stmt.via_state_keyword
            ):
                try:
                    val, unit = context._eval_value_with_unit(stmt.expr, {})
                    # ADR 0160: classical Type-First keeps Fraction; float only at State.
                    if isinstance(val, Fraction):
                        context.scalars[stmt.names[0]] = val
                    elif isinstance(val, int) and not isinstance(val, bool):
                        context.scalars[stmt.names[0]] = val
                    else:
                        context.scalars[stmt.names[0]] = float(val)
                    if unit is not None:
                        context.scalar_units[stmt.names[0]] = unit
                    else:
                        context.scalar_units.pop(stmt.names[0], None)
                    # Pure classical inferred bind: do not force Joint axis.
                    if stmt.ty is None:
                        continue
                except (KernelError, TypeError, ValueError):
                    pass
            # LISS-0231 / LISS-0292: classical Type-First-returning free fn
            # with object args (e.g. road_m(qty)) — do not Joint-bind params.
            _classical_ret = {
                "Float",
                "Int",
                "Bool",
                "Mass",
                "Time",
                "Length",
                "Current",
                "Temperature",
                "Energy",
                "Frequency",
                "Stiffness",
                "Momentum",
            }
            if (
                stmt.ty is not None
                and stmt.ty.name in _classical_ret
                and len(stmt.names) == 1
                and isinstance(stmt.expr, Call)
                and isinstance(stmt.expr.callee, Var)
                and stmt.expr.callee.name in context.funs
                and stmt.names[0] not in context.scalars
            ):
                fun = context.funs[stmt.expr.callee.name]
                if (
                    fun.return_type is not None
                    and fun.return_type.name in _classical_ret
                ):
                    val, unit = context._eval_classical_user_fun_value(
                        fun, stmt.expr
                    )
                    if isinstance(val, Fraction):
                        context.scalars[stmt.names[0]] = val
                    elif isinstance(val, int) and not isinstance(val, bool):
                        context.scalars[stmt.names[0]] = val
                    else:
                        context.scalars[stmt.names[0]] = float(val)
                    if unit is not None:
                        context.scalar_units[stmt.names[0]] = unit
                    else:
                        context.scalar_units.pop(stmt.names[0], None)
                    joint = joint.bind_const(
                        stmt.names[0], context.scalars[stmt.names[0]]
                    )
                    continue
            joint = context._bind_names(
                joint, stmt.names, stmt.expr, logs=logs, inspect_out=inspect_out
            )
            if interproc_trace and context._is_library_user_call(stmt.expr):
                live = context._stmts_live_vars(stmts[stmt_i + 1 :])
                joint = context._trace_out_dead_caller_coords(
                    joint, live, stmt.names
                )
            # LISS-0137: method / joint-bound classical Float → scalars for
            # Operator coeffs and `evolve … for t` (empty-env _eval_value).
            if (
                stmt.ty is not None
                and stmt.ty.name
                not in {
                    "State",
                    "Operator",
                    "Delta",
                    "POVM",
                    "DensityState",
                    "QubitRegister",
                }
                and stmt.ty.name not in context.classes
                and stmt.ty.name not in context.structs
                and stmt.ty.name not in context.enums
                and len(stmt.names) == 1
                and stmt.names[0] not in context.scalars
            ):
                context._maybe_capture_classical_scalar(joint, stmt.names[0])
        elif isinstance(stmt, AssignStmt):
                    context._execute_assignment(stmt)
        elif isinstance(stmt, Snapshot):
            marg = context._expr_marginal(joint, stmt.expr)
            text = format_snapshot_csv(marg)
            context._emit_sink(stmt.sink, text, stdout=stdout)
            logs.append(f"snapshot:{stmt.sink}:{marg}")
        elif isinstance(stmt, Measure):
            context._rng_calls_before_measure = context.rng_calls
            measurement_kind = context._resolve_measurement_kind(stmt.povm)
            joint = context._apply_measure_tracing_out(joint, stmt)
            mixed = context._mixed_state_for_measure(stmt.expr)
            if mixed is not None:
                measure_result = context._measure_mixed(
                    mixed, sink=stmt.sink, stdout=stdout
                )
                context.mixed_state_measured = True
            else:
                measure_result = context._measure(joint, stmt.expr, sink=stmt.sink, stdout=stdout)
            break
        else:
            raise KernelError(f"unsupported stmt {type(stmt)}")

    return _build_terminal_result(
        context, joint, measure_result, measurement_kind, logs
    )
