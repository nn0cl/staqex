"""Observation execution mechanics extracted from the Evaluator facade."""

from __future__ import annotations

from typing import Any, TextIO

from ...ast_nodes import *  # noqa: F403
from ...finite_binder import operator_declared_space
from ...measure_sink_port import (
    MeasureSinkPort, TextIOMeasureSinkAdapter, resolve_measure_sink
)
from ..joint import EPS, Joint, sample_from_marginal
from ..lindblad import evolve_lindblad
from ..matrix import Matrix
from ..mixed_state import DensityStateValue, density_from_call, matrix_from_list


def execute_deferred_state_measure_plan(
    context, unit: CompilationUnit, *, stdout: TextIO | None = None
) -> Any:
    """Run approved deferred State/Measure mechanics without dispatch.

    The statement list is used only as the syntax payload associated with
    the already-validated plan family.  Meaning, family eligibility, and
    authority come from ``RuntimeExecutionPlan`` and its semantic IR.
    """
    context._prepare_first_family_context(unit)
    inspect_stream = context.inspect_sink if context.inspect_sink is not None else stdout
    inspect_out: MeasureSinkPort | None = (
        TextIOMeasureSinkAdapter(inspect_stream)
        if inspect_stream is not None
        else None
    )
    stmts = unit.main.body.stmts
    logs: list[str] = []
    joint, measure_result, measurement_kind, deferred_binds_applied = (
        context._run_deferred_state_binds(
            Joint.unit(),
            stmts,
            logs=logs,
            inspect_out=inspect_out,
            stdout=stdout,
            interproc_trace=context._main_interproc_trace_eligible(stmts),
        )
    )
    return context._eval_result_type(
        joint=joint,
        measure=measure_result,
        rng_calls_before_measure=context._rng_calls_before_measure,
        logs=logs,
        mixed_state_measured=context.mixed_state_measured,
        execution_lane=context.execution_lane,
        measurement_kind=measurement_kind,
        deferred_pushforward=True,
        deferred_binds_applied=deferred_binds_applied,
        last_algebraic_fusion=context.last_algebraic_fusion,
        last_poly_fusion=context.last_poly_fusion,
        data_parallel_workers=context.data_parallel_workers,
        dynamic_outcomes_confirmed=context._dynamic_outcomes_confirmed,
        evolution_provenance=context.evolution_provenance,
    )

def _prepare_first_family_context(context, unit: CompilationUnit) -> None:
    """Initialize only the evaluator context needed by State/Measure."""
    from ...stdlib.prelude import PRELUDE_CONSTANTS

    context.funs = {}
    context.classes = {}
    context.enums = {}
    context.structs = {}
    context.objects = {}
    context.mixed_states = {}
    context.ket_labels = {}
    context.povms = {}
    context.static_register_sizes = {}
    context.operator_spaces = {}
    context.mixed_state_measured = False
    context.execution_lane = None
    context._dynamic_outcomes_confirmed = True
    context.evolution_provenance = None
    context._this = None
    context._unit = unit
    context.operators = {}
    context._compiled_operator_cache = {}
    context.scalars = dict(PRELUDE_CONSTANTS)
    context.scalar_units = {}
    context._frame_units = {}
    context._resolved_host_arrays = {}
    for statement in unit.main.body.stmts if unit.main is not None else ():
        if (
            isinstance(statement, StateBind)
            and statement.ty is not None
            and statement.ty.name == "Operator"
            and len(statement.names) == 1
        ):
            if isinstance(statement.expr, OpPauli):
                context.operators[statement.names[0]] = statement.expr
            else:
                propagator = context._explicit_propagator(statement.expr)
                if propagator is not None:
                    context.operators[statement.names[0]] = propagator
    for declaration in unit.decls:
        if isinstance(declaration, FunDecl) and declaration.name != "main":
            context.funs[declaration.qualified_name] = declaration
            context.funs[declaration.name] = declaration
        elif isinstance(declaration, ClassDecl):
            context.classes[declaration.qualified_name] = declaration
            context.classes[declaration.name] = declaration
        elif isinstance(declaration, EnumDecl):
            context.enums[declaration.qualified_name] = declaration
            context.enums[declaration.name] = declaration
        elif isinstance(declaration, StructDecl):
            context.structs[declaration.qualified_name] = declaration
            context.structs[declaration.name] = declaration

def _main_deferred_eligible(stmts: list[Any]) -> bool:
    """ADR 0140: StateBind* + terminal Measure only (no inspect/snapshot/ops)."""
    if not stmts:
        return False
    measure_i: int | None = None
    for i, stmt in enumerate(stmts):
        if isinstance(stmt, Measure):
            if measure_i is not None:
                return False
            measure_i = i
            continue
        if not isinstance(stmt, StateBind):
            return False
        if not _is_deferred_state_bind(stmt):
            return False
    return measure_i is not None and measure_i == len(stmts) - 1

def _is_deferred_state_bind(stmt: StateBind) -> bool:
    if stmt.ty is not None and stmt.ty.name != "State":
        return False
    # ADR 0180: untyped classical/Operator/object binds are not State binds.
    if stmt.ty is None and not stmt.via_state_keyword:
        return False
    # inspect / snapshot force a read boundary (ADR 0030 / 0029).
    if _expr_has_inspect(stmt.expr):
        return False
    return True

def _expr_has_inspect(expr: Expr) -> bool:
    if isinstance(expr, Inspect):
        return True
    if isinstance(expr, BinOp):
        return _expr_has_inspect(expr.lhs) or _expr_has_inspect(
            expr.rhs
        )
    if isinstance(expr, Call):
        return _expr_has_inspect(expr.callee) or any(
            _expr_has_inspect(a) for a in expr.args
        )
    if isinstance(expr, (WhenExpr, SuperposeExpr)):
        if _expr_has_inspect(expr.ctrl):
            return True
        return any(_expr_has_inspect(arm.body) for arm in expr.arms)
    if isinstance(expr, Pipe):
        return _expr_has_inspect(expr.lhs) or _expr_has_inspect(
            expr.rhs
        )
    if isinstance(expr, Attr):
        return _expr_has_inspect(expr.obj)
    if isinstance(expr, (TupleExpr, ListExpr)):
        return any(_expr_has_inspect(i) for i in expr.items)
    if isinstance(expr, BlockExpr):
        return any(
            _expr_has_inspect(let.expr) for let in expr.lets
        ) or _expr_has_inspect(expr.result)
    if isinstance(expr, Dirac):
        return _expr_has_inspect(expr.arg)
    if isinstance(expr, UnitConvert):
        return _expr_has_inspect(expr.expr)
    if isinstance(expr, Lambda):
        return _expr_has_inspect(expr.body)
    return False

def _expr_free_vars(expr: Expr) -> set[str]:
    names: set[str] = set()

    def walk(node: Any) -> None:
        if node is None:
            return
        if isinstance(node, Var):
            names.add(node.name)
            return
        if isinstance(node, (LitInt, LitFloat, LitBool, LitString, Coin, Vacuum, Hole)):
            return
        if isinstance(node, KetLit):
            return
        if isinstance(node, KetSumBinder):
            domain = node.domain
            walk(getattr(domain, "width", None))
            return
        if isinstance(node, NormExpr):
            walk(node.state)
            return
        if isinstance(node, SetComprehension):
            domain = node.domain
            walk(getattr(domain, "start", None))
            walk(getattr(domain, "end", None))
            walk(getattr(domain, "width", None))
            for condition in node.conditions:
                walk(condition)
            names.discard(node.variable)
            return
        if isinstance(node, OpBinder):
            domain = node.domain
            walk(domain)
            walk(getattr(domain, "start", None))
            walk(getattr(domain, "end", None))
            walk(getattr(domain, "width", None))
            walk(node.guard)
            walk(node.body)
            names.discard(node.variable)
            return
        if isinstance(node, OpVar):
            names.add(node.name)
            return
        if isinstance(node, OpIndexed):
            walk(node.base)
            walk(node.index)
            return
        if isinstance(node, (OpBin, OpPow, OpCall)):
            if isinstance(node, OpBin):
                walk(node.lhs)
                walk(node.rhs)
            elif isinstance(node, OpPow):
                walk(node.base)
            else:
                for arg in node.args:
                    walk(arg)
            return
        if isinstance(node, OpAttr):
            walk(node.obj)
            return
        if isinstance(node, (OpLit, OpPauli, OpHop, OpNumber, OpQuadrature, OpGridQuad, OpIdentity)):
            return
        if isinstance(node, BinOp):
            walk(node.lhs)
            walk(node.rhs)
            return
        if isinstance(node, UnaryNot):
            walk(node.expr)
            return
        if isinstance(node, Call):
            walk(node.callee)
            for a in node.args:
                walk(a)
            return
        if isinstance(node, (WhenExpr, SuperposeExpr)):
            walk(node.ctrl)
            for arm in node.arms:
                walk(arm.body)
            return
        if isinstance(node, Pipe):
            walk(node.lhs)
            walk(node.rhs)
            return
        if isinstance(node, Lambda):
            walk(node.body)
            names.discard(node.param)
            return
        if isinstance(node, Attr):
            walk(node.obj)
            return
        if isinstance(node, Inspect):
            walk(node.expr)
            return
        if isinstance(node, UnitConvert):
            walk(node.expr)
            return
        if isinstance(node, (TupleExpr, ListExpr)):
            for item in node.items:
                walk(item)
            return
        if isinstance(node, BlockExpr):
            for let in node.lets:
                walk(let.expr)
            walk(node.result)
            return
        if isinstance(node, Dirac):
            walk(node.arg)
            return
        if isinstance(node, EvolveExpr):
            for t in node.seeds:
                walk(t)
            if node.body is not None:
                for lb in node.body.lets:
                    walk(lb.expr)
                walk(node.body.result)
            if isinstance(node.times, Expr):
                walk(node.times)
            if node.duration is not None:
                walk(node.duration)
            if node.hamiltonian is not None:
                walk(node.hamiltonian)
            return
        if isinstance(node, TensorExpr):
            walk(node.left)
            walk(node.right)
            return

    walk(expr)
    return names

def _deferred_bind_cone(
    
    pending: list[StateBind],
    measure_expr: Expr,
    *,
    extra_needed: set[str] | None = None,
) -> set[str]:
    needed = _expr_free_vars(measure_expr)
    if extra_needed:
        needed |= set(extra_needed)
    changed = True
    while changed:
        changed = False
        for bind in pending:
            if needed.intersection(bind.names):
                fv = _expr_free_vars(bind.expr)
                if not fv <= needed:
                    needed |= fv
                    changed = True
    return needed

def _apply_measure_tracing_out(context, joint: Joint, stmt: Measure) -> Joint:
    """ADR 0173: Born partial-trace leftovers before terminal measure."""
    for name in stmt.tracing_out:
        joint = joint.trace_out(name)
    return joint

def _run_deferred_state_binds(
    context,
    joint: Joint,
    stmts: list[Any],
    *,
    logs: list[str],
    inspect_out: MeasureSinkPort | None,
    stdout: TextIO | None,
    interproc_trace: bool = False,
) -> tuple[Joint, Any | None, str | None, int]:
    pending = [s for s in stmts if isinstance(s, StateBind)]
    measure_stmt = stmts[-1]
    assert isinstance(measure_stmt, Measure)
    needed = context._deferred_bind_cone(
        pending,
        measure_stmt.expr,
        extra_needed=(
            set(measure_stmt.tracing_out)
            | {
                name
                for stmt in pending
                if stmt.ty is not None and stmt.ty.name == "Operator"
                for name in context._expr_free_vars(stmt.expr)
            }
        ),
    )
    applied = 0
    for i, stmt in enumerate(pending):
        if stmt.ty is not None and stmt.ty.name == "Operator":
            if len(stmt.names) != 1:
                raise context._kernel_error("Operator bind expects a single name")
            name = stmt.names[0]
            declared_space = operator_declared_space(stmt.ty)
            if declared_space is not None:
                context.operator_spaces[name] = declared_space
            explicit_propagator = context._explicit_propagator(stmt.expr)
            op_val = (
                explicit_propagator
                if explicit_propagator is not None
                else context._resolve_operator_expr(stmt.expr)
            )
            if (
                isinstance(op_val, Call)
                and isinstance(op_val.callee, Var)
                and op_val.callee.name == "outer"
            ):
                op_val = context._materialize_outer(joint, op_val)
            context.operators[name] = op_val
            applied += 1
            continue
        if (
            stmt.ty is not None
            and stmt.ty.name in {"Float", "Bool"}
            and len(stmt.ty.args) >= 1
        ):
            # Coefficient arrays are compile-time inputs for Operator
            # lowering and do not become Joint coordinates.
            continue
        # POVM and DensityState declarations are execution metadata for
        # the terminal measurement, not Joint coordinates.  The deferred
        # callable path must register them before resolving the measure
        # effect, including when the measured density state is returned
        # by a zero-argument function rather than named in `mixed_states`.
        if stmt.ty is not None and stmt.ty.name == "POVM":
            context._bind_povm(stmt)
            applied += 1
            continue
        if stmt.ty is not None and stmt.ty.name == "DensityState":
            context._bind_mixed_state(stmt)
            applied += 1
            continue
        if not needed.intersection(stmt.names):
            continue
        joint = context._bind_names(
            joint, stmt.names, stmt.expr, logs=logs, inspect_out=inspect_out
        )
        applied += 1
        # Keep the deferred path's classical environment in sync with
        # the legacy executor.  Binder domains and classical functions
        # resolve named Int/Float values through `context.scalars`, while
        # `_bind_names` stores the value in the Joint coordinate.
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
            and len(stmt.names) == 1
        ):
            context._maybe_capture_classical_scalar(joint, stmt.names[0])
        if interproc_trace and context._is_library_user_call(stmt.expr):
            later: list[Any] = [
                s for s in pending[i + 1 :] if needed.intersection(s.names)
            ]
            later.append(measure_stmt)
            live = context._stmts_live_vars(later)
            joint = context._trace_out_dead_caller_coords(
                joint, live, stmt.names
            )
    context._rng_calls_before_measure = context.rng_calls
    measurement_kind = context._resolve_measurement_kind(measure_stmt.povm)
    joint = context._apply_measure_tracing_out(joint, measure_stmt)
    mixed = context._mixed_state_for_measure(measure_stmt.expr)
    if mixed is not None:
        measure_result = context._measure_mixed(
            mixed,
            sink=measure_stmt.sink,
            stdout=stdout,
        )
        context.mixed_state_measured = True
    else:
        measure_result = context._measure(
            joint, measure_stmt.expr, sink=measure_stmt.sink, stdout=stdout
        )
    return joint, measure_result, measurement_kind, applied

def _mixed_state_for_measure(context, expr: Expr) -> DensityStateValue | None:
    """Resolve a measure target to a DensityStateValue when applicable.

    LISS-0377: previously only bare ``Var`` names already present in
    ``mixed_states`` took the mixed path, so ``measure make()`` fell
    through to Joint vacuum measurement with an empty marginal.
    """
    if isinstance(expr, Var):
        return context.mixed_states.get(expr.name)
    if (
        not isinstance(expr, Call)
        or not isinstance(expr.callee, Var)
        or expr.args
    ):
        return None
    fun = context.funs.get(expr.callee.name)
    if (
        fun is None
        or fun.return_type is None
        or fun.return_type.name != "DensityState"
    ):
        return None
    domain = (
        fun.return_type.args[0].name if fun.return_type.args else "Unknown"
    )
    result_expr: Expr | None = fun.body.result
    if result_expr is None:
        for stmt in fun.body.stmts:
            if isinstance(stmt, ReturnStmt):
                result_expr = stmt.expr
                break
    if not isinstance(result_expr, Call):
        raise context._kernel_error("unsupported DensityState construction")
    try:
        return density_from_call(
            result_expr,
            domain=domain,
            scalars=context._float_scalars(context.scalars),
            ket_labels=context.ket_labels,
        )
    except ValueError as exc:
        raise context._kernel_error(str(exc)) from exc

def _resolve_measurement_kind(context, povm: Expr | None) -> str:
    if povm is None:
        return "ComputationalBasis"
    if isinstance(povm, Var) and povm.name in context.povms:
        return context.povms[povm.name][1]
    raise context._kernel_error("INVALID_POVM_EFFECT")

def _bind_povm(context, stmt: StateBind) -> None:
    if (
        isinstance(stmt.expr, Call)
        and context._call_name(stmt.expr) == "ComputationalBasis"
    ):
        domain = stmt.ty.args[0].name if stmt.ty and stmt.ty.args else "Unknown"
        context.povms[stmt.names[0]] = (domain, "ComputationalBasis")
        return
    raise context._kernel_error("INVALID_POVM_EFFECT")

def _bind_mixed_state(context, stmt: StateBind) -> None:
    if len(stmt.names) != 1 or stmt.ty is None:
        raise context._kernel_error("DensityState bind expects one name")
    domain = stmt.ty.args[0].name if stmt.ty.args else "Unknown"
    expr = stmt.expr
    if isinstance(expr, Call) and context._call_name(expr) == "DensityState":
        try:
            context.mixed_states[stmt.names[0]] = density_from_call(
                expr,
                domain=domain,
                scalars=context._float_scalars(context.scalars),
                ket_labels=context.ket_labels,
            )
        except ValueError as exc:
            raise context._kernel_error(str(exc)) from exc
        return
    if isinstance(expr, Call) and context._call_name(expr) == "lindblad":
        if len(expr.args) != 4 or not isinstance(expr.args[0], Var):
            raise context._kernel_error("lindblad requires a DensityState source")
        source = context.mixed_states.get(expr.args[0].name)
        if source is None:
            raise context._kernel_error("lindblad source must be a DensityState")
        # A declaration-only source contract may still carry unresolved
        # placeholders. Keep that path opaque; numerical lowering starts
        # only when all MVP inputs are explicit.
        if (
            isinstance(expr.args[1], Var)
            and expr.args[1].name not in context.operators
        ) or (
            isinstance(expr.args[2], Var)
        ) or (
            isinstance(expr.args[3], Var)
            and expr.args[3].name not in context.scalars
        ):
            context.mixed_states[stmt.names[0]] = DensityStateValue(
                matrix=[row[:] for row in source.matrix],
                domain=domain,
                operation="lindblad",
            )
            context.execution_lane = "cpu/simulator"
            return
        n_qubits = context._density_matrix_n_qubits(source.matrix)
        hamiltonian = context._resolve_lindblad_hamiltonian(expr.args[1], n_qubits)
        jumps = context._resolve_lindblad_jumps(expr.args[2], n_qubits)
        try:
            total_time = float(context._evaluate_value(expr.args[3], {}))
            evolved = evolve_lindblad(
                source.matrix,
                hamiltonian,
                jumps,
                total_time=total_time,
                dt=context.SOURCE_LINDBLAD_DT,
            )
        except (context._kernel_error, TypeError, ValueError, RuntimeError) as exc:
            raise context._kernel_error(str(exc)) from exc
        context.mixed_states[stmt.names[0]] = DensityStateValue(
            matrix=evolved,
            domain=domain,
            operation="lindblad",
        )
        context.execution_lane = "cpu/simulator"
        return
    if isinstance(expr, Call) and context._call_name(expr) == "apply":
        if len(expr.args) < 2 or not isinstance(expr.args[1], Var):
            raise context._kernel_error("mixed apply requires a DensityState source")
        source = context.mixed_states.get(expr.args[1].name)
        if source is None:
            raise context._kernel_error("mixed apply source must be a DensityState")
        context.mixed_states[stmt.names[0]] = source
        return
    raise context._kernel_error("unsupported DensityState construction")

def _resolve_lindblad_jumps(context, expr: Expr, n_qubits: int) -> list[Matrix]:
    if isinstance(expr, ListExpr):
        if expr.items:
            raise context._kernel_error(
                "non-empty Lindblad jumps must use JumpSet([RawMatrix(...)])"
            )
        return []
    if not isinstance(expr, Call) or context._call_name(expr) != "JumpSet":
        raise context._kernel_error("Lindblad jump input must be JumpSet or an empty list")
    if len(expr.args) != 1 or not isinstance(expr.args[0], ListExpr):
        raise context._kernel_error("JumpSet requires a finite list")
    jumps: list[Matrix] = []
    for item in expr.args[0].items:
        if isinstance(item, Var):
            if item.name not in context.operators:
                raise context._kernel_error(
                    f"SYMBOLIC_JUMP_LOWERING_REQUIRED: jump `{item.name}` "
                    "must resolve to an Operator"
                )
            try:
                jumps.append(context._compile_lindblad_operator(item.name, n_qubits))
            except ValueError as exc:
                raise context._kernel_error(str(exc)) from exc
            continue
        if not isinstance(item, Call) or context._call_name(item) != "RawMatrix":
            raise context._kernel_error("JumpSet entries must be explicit RawMatrix values")
        if len(item.args) != 1:
            raise context._kernel_error("RawMatrix requires a finite square numeric matrix")
        try:
            matrix = matrix_from_list(item.args[0])
        except ValueError as exc:
            raise context._kernel_error(str(exc)) from exc
        jumps.append(matrix)
    return jumps

def _resolve_lindblad_hamiltonian(context, expr: Expr, n_qubits: int) -> Matrix:
    from ..unitaries import named_gate_matrix

    if isinstance(expr, Var) and expr.name in context.operators:
        try:
            return context._compile_lindblad_operator(expr.name, n_qubits)
        except ValueError as exc:
            raise context._kernel_error(str(exc)) from exc
    if isinstance(expr, Var):
        matrix = named_gate_matrix(expr.name)
        if matrix is not None:
            return matrix
    raise context._kernel_error("source Lindblad MVP requires a resolvable Hamiltonian")

def _compile_lindblad_operator(context, name: str, n_qubits: int) -> Matrix:
    from ..hamiltonian import compile_hamiltonian

    return compile_hamiltonian(
        context.operators[name],
        env=context.operators,
        scalars=context.scalars,
        n_qubits=n_qubits,
    )

def _emit_measure_text(
    context,
    sink: str | None,
    text: str,
    *,
    stdout: TextIO | None,
) -> None:
    """Emit measure/snapshot text via MeasureSinkPort (ADR 0171)."""
    if context.measure_sink is not None:
        context.measure_sink.write(text)
        return
    port = resolve_measure_sink(sink, stdout=stdout)
    if port is None:
        return
    port.write(text)

def _emit_sink(
    context,
    sink: str | None,
    text: str,
    *,
    stdout: TextIO | None,
) -> None:
    """Emit snapshot/diagnostic text; preserve write_sink newline policy."""
    if context.measure_sink is not None:
        context.measure_sink.write(text)
        return
    from ...measure_sink_port import _STDOUT_ALIASES

    if (sink is None or sink in _STDOUT_ALIASES) and text and not text.endswith("\n"):
        text = text + "\n"
    port = resolve_measure_sink(sink, stdout=stdout)
    if port is None:
        return
    port.write(text)

def _measure_mixed(
    context,
    state: DensityStateValue,
    *,
    sink: str | None,
    stdout: TextIO | None,
) -> Any:
    marginal = {
        index: max(0.0, float(state.matrix[index][index].real))
        for index in range(len(state.matrix))
    }
    marginal = {key: value for key, value in marginal.items() if value > EPS}
    if not marginal:
        return context._measure_result_type(
            value=None, vacuum=True, marginal={}, rng_calls=context.rng_calls, sink=sink
        )
    context.rng_calls += 1
    value = sample_from_marginal(marginal, context.rng)
    text = context._format_value(value)
    context._emit_measure_text(sink, text + "\n", stdout=stdout)
    return context._measure_result_type(
        value=value,
        vacuum=False,
        marginal=marginal,
        rng_calls=context.rng_calls,
        sink=sink,
        output=text,
    )

def _expr_marginal(context, joint: Joint, expr: Expr) -> dict[Any, float]:
    if isinstance(expr, Var):
        return joint.marginal(expr.name)
    # general: pushforward values across worlds
    from collections import defaultdict

    acc: dict[Any, float] = defaultdict(float)
    if joint.is_vacuum():
        return {}
    for w in joint.worlds:
        try:
            v = context._evaluate_value(expr, w.assign)
        except context._kernel_error:
            continue
        acc[v] += abs(w.amp) ** 2
    return {k: v for k, v in acc.items() if v > EPS}

def _measure(
    context,
    joint: Joint,
    expr: Expr,
    *,
    sink: str | None,
    stdout: TextIO | None,
) -> Any:
    marginal = context._expr_marginal(joint, expr)
    if not marginal:
        text = ""  # vacuum: no sample
        # Preserve prior behavior: attempt an empty write on the stdout path.
        if sink is None or sink in {"stdout", "Stdout", "STDOUT"}:
            context._emit_measure_text(sink, text, stdout=stdout)
        return context._measure_result_type(
            value=None,
            vacuum=True,
            marginal={},
            rng_calls=context.rng_calls,
            sink=sink,
            output=text,
        )

    context.rng_calls += 1  # terminal measure draws once
    value = sample_from_marginal(marginal, context.rng)
    text = "" if value is None else context._format_value(value)
    payload = (text + "\n") if text else ""
    if sink is None or sink in {"stdout", "Stdout", "STDOUT"}:
        if text:
            context._emit_measure_text(sink, payload, stdout=stdout)
    else:
        context._emit_measure_text(sink, payload, stdout=None)
    return context._measure_result_type(
        value=value,
        vacuum=False,
        marginal=marginal,
        rng_calls=context.rng_calls,
        sink=sink,
        output=text,
    )
