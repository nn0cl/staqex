"""DAG / AST → logical Circuit (Phase 4.1)."""

from __future__ import annotations

from dataclasses import dataclass
import re

from ...ast_nodes import (
    Attr,
    BinOp,
    Call,
    Coin,
    CompilationUnit,
    Dirac,
    EvolveExpr,
    Expr,
    ExprStmt,
    ForEachStmt,
    FunDecl,
    KetLit,
    LitFloat,
    LitInt,
    Measure,
    OpExpr,
    StateBind,
    Span,
    SuzukiPolicy,
    TupleExpr,
    TypeRef,
    UnitConvert,
    Var,
    WhenExpr,
)
from ...ast_nodes import OpBin, OpBinder
from ...ir.dag import Dag, lower_source_ast
from ...second_quantization import SecondQuantizationMappingError, resolve_mapping_expr
from ...finite_binder import lower_finite_binder_operators
from .circuit import Circuit, Gate
from .trotter import (
    TrotterError,
    compile_hamiltonian,
    eval_time_expr,
    suzuki_gates,
    resolve_suzuki_order,
    resolve_suzuki_steps,
)
from ...static_hilbert import MVP_MAX_LOGICAL_QUBITS
from ...kernel_literals import SECOND_QUANTIZED_FAMILIES as _SECOND_QUANTIZED_FAMILIES
from ...scientific_semantic_ir import (
    MIXTURE_PROJECTION_REJECTION_CODE,
    MIXTURE_PROJECTION_REJECTION_REASON,
)

# LISS-0050 (Architecture Path, 2026-07-25, ADR 0094): a plain
# `evolve ... under H for t` with no `using Suzuki(...)` policy has no
# non-arbitrary way to pick a Trotter step count. Reject rather than
# silently derive-and-clamp one.
QASM_TROTTER_STEPS_REQUIRED = "QASM_TROTTER_STEPS_REQUIRED"

# LISS-0049 (Architecture Path Option B, 2026-07-25): a call to a
# user-defined `fn` inside `main` has no QASM lowering yet. Reject with an
# actionable diagnostic instead of silently falling back to the
# empty-program sketch below.
QASM_FUNCTION_CALL_UNSUPPORTED = "QASM_FUNCTION_CALL_UNSUPPORTED"
_QASM_FUNCTION_CALL_UNSUPPORTED_MESSAGE = (
    "Emitting QASM for function calls is currently unsupported. Please "
    "inline the function logic manually."
)

# LISS-0372: an `apply(rx|ry|rz(theta), q)` whose angle does not resolve
# to a closed classical scalar must not silently drop the gate from the
# circuit -- reject explicitly instead.
QASM_ROTATION_ANGLE_UNRESOLVED = "QASM_ROTATION_ANGLE_UNRESOLVED"

QASM_EVOLVE_UNTIL_UNSUPPORTED = "E_QPU_UNSUPPORTED_CAPABILITY"
_QASM_EVOLVE_UNTIL_UNSUPPORTED_MESSAGE = (
    "QASM emission does not support runtime evolve-until repetition"
)

EVOLUTION_TARGET_UNSUPPORTED = "EVOLUTION_TARGET_UNSUPPORTED"
EVOLUTION_MAPPING_MISSING = "binder_register_mapping_missing"
EVOLUTION_BUDGET_EXCEEDED = "resource_budget_exceeded"
EVOLUTION_LIMIT_REALIZATION_PENDING = "formal_limit_realization_pending"
_EVOLUTION_TARGET_UNSUPPORTED_MESSAGE = (
    "the QPU backend does not yet lower the explicit `Operator * State` "
    "evolution surface; no circuit was emitted"
)


@dataclass(frozen=True)
class EvolutionTargetProfile:
    """Target-owned realization policy; never inferred from source physics."""

    suzuki_order: int = 2
    suzuki_steps: int = 1
    realization_mode: str = "approximate"
    resource_budget_qubits: int | None = None
    capability_limitations: tuple[str, ...] = ()
    # Explicit logical-register witness for finite binder realization. The
    # mapping is target input; it is never inferred from source binder names.
    register_mapping: dict[str, str] | None = None
    limit_realization_method: str | None = None
    limit_order: int | None = None
    limit_steps: int | None = None
    limit_error_budget: float | None = None

# LISS-0074 Slice E: never silently embed qudit carriers as qubit OPENQASM.
UNSUPPORTED_LOCAL_DIMENSION = "UNSUPPORTED_LOCAL_DIMENSION"
_UNSUPPORTED_LOCAL_DIMENSION_MESSAGE = (
    "qudit / qutrit carriers are not supported by OpenQASM emission "
    "(deferred; no silent qubit embedding)"
)
_QUDIT_TYPE_NAMES = frozenset({"Qutrit", "Qudit", "QutritRegister", "QuditRegister"})


def _type_ref_mentions_qudit(ref: TypeRef | None) -> bool:
    if ref is None:
        return False
    if ref.name in _QUDIT_TYPE_NAMES:
        return True
    return any(_type_ref_mentions_qudit(arg) for arg in ref.args)


def qudit_capability_reject(unit: CompilationUnit) -> Circuit | None:
    """Reject units that declare qudit carriers before qubit QASM lowering."""
    if unit.main is None:
        return None
    for stmt in unit.main.body.stmts:
        if isinstance(stmt, StateBind) and _type_ref_mentions_qudit(stmt.ty):
            return Circuit(
                n_qubits=0,
                n_bits=0,
                gates=[],
                notes=[_UNSUPPORTED_LOCAL_DIMENSION_MESSAGE],
                reject_code=UNSUPPORTED_LOCAL_DIMENSION,
                provenance={
                    "reason": "unsupported_local_dimension",
                    "source_node_id": f"ast:{stmt.span.line}:{stmt.span.col}",
                    "target_plan": None,
                },
                allocation_started=False,
                allocated_qubits=(),
                partial_program=None,
            )
    return None


def explicit_evolution_capability_reject(
    unit: CompilationUnit,
    target_profile: EvolutionTargetProfile | None,
) -> Circuit | None:
    """Reject before allocation so unsupported evolution cannot leak a
    partially lowered circuit."""
    if unit.main is None:
        return None
    binds_by_name = {
        stmt.names[0]: stmt.expr
        for stmt in unit.main.body.stmts
        if isinstance(stmt, StateBind) and len(stmt.names) == 1
    }
    def has_binder(expr: object) -> bool:
        if isinstance(expr, OpBinder):
            return True
        if isinstance(expr, OpBin):
            return has_binder(expr.lhs) or has_binder(expr.rhs)
        return False

    def exponential_hamiltonian_has_binder(expr: Call) -> bool:
        """Inspect only operator bindings referenced by this exponential."""
        if not expr.args:
            return False

        def walk(value: object) -> bool:
            if isinstance(value, Var):
                bound = binds_by_name.get(value.name)
                return has_binder(bound)
            if isinstance(value, (list, tuple)):
                return any(walk(item) for item in value)
            if isinstance(value, (BinOp, Call)):
                fields = (value.lhs, value.rhs) if isinstance(value, BinOp) else (
                    value.args,
                    value.kwargs or (),
                )
                return any(walk(item) for item in fields)
            return False

        return walk(expr.args[0])
    for stmt in unit.main.body.stmts:
        if not (
            isinstance(stmt, StateBind)
            and isinstance(stmt.expr, EvolveExpr)
            and stmt.expr.explicit_transform
        ):
            continue
        if stmt.expr.until_predicate is not None:
            return _rejected_target_circuit(
                QASM_EVOLVE_UNTIL_UNSUPPORTED,
                _generic_explicit_provenance(stmt, "until_requires_dynamic_target"),
            )
        result = stmt.expr.body.result if stmt.expr.body is not None else None
        source_name = result.lhs.name if isinstance(result, BinOp) and isinstance(result.lhs, Var) else None
        source_expr = binds_by_name.get(source_name or "")
        state_name = result.rhs.name if isinstance(result, BinOp) and isinstance(result.rhs, Var) else None
        state_expr = binds_by_name.get(state_name or "")
        if (
            isinstance(source_expr, Call)
            and isinstance(source_expr.callee, Var)
            and source_expr.callee.name == "exp"
            and not exponential_hamiltonian_has_binder(source_expr)
        ):
            return _rejected_target_circuit(
                "E_QPU_CANONICAL_FINITE_EVOLUTION_UNSUPPORTED",
                _explicit_provenance(
                    stmt,
                    "finite_projection_unavailable",
                    "exp(-i * H * duration / hbar)",
                ),
            )
        if isinstance(state_expr, WhenExpr):
            return _rejected_target_circuit(
                MIXTURE_PROJECTION_REJECTION_CODE,
                _explicit_provenance(
                    stmt,
                    MIXTURE_PROJECTION_REJECTION_REASON,
                    "Coin/Mix/when mixture",
                ),
            )
        if isinstance(source_expr, OpExpr) and getattr(source_expr, "op", None) == "*":
            left_value = getattr(getattr(source_expr, "lhs", None), "value", None)
            if isinstance(left_value, (int, float)) and left_value not in {1, -1}:
                return _rejected_target_circuit(
                    "E_QPU_UNSUPPORTED_CAPABILITY",
                    _explicit_provenance(stmt, "non_unitary_target", "mathematical operator product"),
                )
        if target_profile is None:
            return _rejected_target_circuit(
                EVOLUTION_TARGET_UNSUPPORTED,
                _generic_explicit_provenance(stmt, "target_profile_required"),
            )
        if target_profile.realization_mode != "approximate":
            return _rejected_target_circuit(
                EVOLUTION_TARGET_UNSUPPORTED,
                _generic_explicit_provenance(stmt, "unsupported_realization_mode"),
            )
    return None


def lower_unit_to_circuit(
    unit: CompilationUnit,
    *,
    target_profile: EvolutionTargetProfile | None = None,
) -> Circuit:
    """Prefer structural AST patterns; else DAG-driven heuristic."""
    rejected = qudit_capability_reject(unit)
    if rejected is not None:
        return rejected
    rejected = formal_limit_capability_reject(unit, target_profile)
    if rejected is not None:
        return rejected
    rejected = explicit_evolution_capability_reject(unit, target_profile)
    if rejected is not None:
        return rejected
    rejected = register_resource_budget_reject(unit, target_profile)
    if rejected is not None:
        return rejected
    circ = _from_ast_patterns(unit, target_profile=target_profile)
    if circ is not None:
        return circ
    dag = lower_source_ast(unit)
    return _from_dag(dag)


def formal_limit_capability_reject(
    unit: CompilationUnit,
    target_profile: EvolutionTargetProfile | None = None,
) -> Circuit | None:
    """Preserve a written formal Limit and reject it before target allocation."""
    explicit_source_names = {
        source.name
        for statement in (unit.main.body.stmts if unit.main is not None else ())
        if isinstance(statement, StateBind)
        and isinstance(statement.expr, Call)
        and isinstance(statement.expr.callee, Var)
        and statement.expr.callee.name == "Realize"
        for key, source in (statement.expr.kwargs or ())
        if key == "source" and isinstance(source, Var)
    }
    explicit_limit_spans = {
        (statement.expr.span.line, statement.expr.span.col)
        for statement in (unit.main.body.stmts if unit.main is not None else ())
        if isinstance(statement, StateBind)
        and statement.names
        and statement.names[0] in explicit_source_names
        and isinstance(statement.expr, Call)
        and isinstance(statement.expr.callee, Var)
        and statement.expr.callee.name == "Limit"
    }

    def walk(value):
        if isinstance(value, Call) and isinstance(value.callee, Var):
            if value.callee.name == "Limit":
                if (value.span.line, value.span.col) in explicit_limit_spans:
                    return None
                method = target_profile.limit_realization_method if target_profile else None
                order = target_profile.limit_order if target_profile else None
                steps = target_profile.limit_steps if target_profile else None
                error_budget = target_profile.limit_error_budget if target_profile else None
                provenance = {
                    "source_span": value.span,
                    "source_transform": "Limit product of infinitesimal steps",
                    "state_shape": "Operator",
                    "realization_kind": "rejected",
                    "realization_policy": "finite_policy_required",
                    "approximation_order_or_null": None,
                    "approximation_steps_or_null": None,
                    "error_budget_or_null": None,
                    "resource_estimate_or_null": None,
                    "capability_rejection_or_null": "EVOLUTION_REALIZATION_REQUIRED",
                    "reason": "missing_finite_realization",
                    "source_node_id": f"ast:{value.span.line}:{value.span.col}",
                }
                if method is not None or order is not None or steps is not None:
                    provenance.update(
                        {
                            "limit_method": method,
                            "limit_order": order,
                            "limit_steps": steps,
                            "limit_error_budget": error_budget,
                        }
                    )
                return _rejected_target_circuit(
                    "EVOLUTION_REALIZATION_REQUIRED", provenance
                )
        if isinstance(value, (list, tuple)):
            for item in value:
                result = walk(item)
                if result is not None:
                    return result
        elif hasattr(value, "__dict__"):
            for child in vars(value).values():
                result = walk(child)
                if result is not None:
                    return result
        return None

    return walk(unit.main.body if unit.main is not None else None)


def _limit_source_for_bind(
    bind: StateBind,
    binds: list[StateBind],
    source_operator_env: dict[str, OpExpr],
) -> Call | None:
    ev = bind.expr
    if not (isinstance(ev, EvolveExpr) and ev.body is not None):
        return None
    result = ev.body.result
    if not (isinstance(result, BinOp) and isinstance(result.lhs, Var)):
        return None
    source = source_operator_env.get(result.lhs.name)
    if isinstance(source, Call) and isinstance(source.callee, Var) and source.callee.name == "Limit":
        return source
    if isinstance(source, Call) and isinstance(source.callee, Var) and source.callee.name == "Realize":
        for key, value in source.kwargs or ():
            if key == "source" and isinstance(value, Var):
                formal = source_operator_env.get(value.name)
                if isinstance(formal, Call) and isinstance(formal.callee, Var) and formal.callee.name == "Limit":
                    return formal
    return None


def _realize_call_for_bind(
    bind: StateBind, source_operator_env: dict[str, OpExpr]
) -> Call | None:
    ev = bind.expr
    if not (isinstance(ev, EvolveExpr) and ev.body is not None):
        return None
    result = ev.body.result
    if not (isinstance(result, BinOp) and isinstance(result.lhs, Var)):
        return None
    source = source_operator_env.get(result.lhs.name)
    if isinstance(source, Call) and isinstance(source.callee, Var):
        if source.callee.name == "Realize":
            return source
    return None


def _profile_from_realize(
    realize: Call, target: EvolutionTargetProfile
) -> EvolutionTargetProfile:
    values = dict(realize.kwargs or ())

    def literal(name: str):
        return getattr(values.get(name), "value", None)

    return EvolutionTargetProfile(
        suzuki_order=target.suzuki_order,
        suzuki_steps=target.suzuki_steps,
        realization_mode=target.realization_mode,
        resource_budget_qubits=target.resource_budget_qubits,
        capability_limitations=target.capability_limitations,
        register_mapping=target.register_mapping,
        limit_realization_method=literal("method"),
        limit_order=literal("order"),
        limit_steps=literal("steps"),
        limit_error_budget=literal("error_budget"),
    )


def _limit_formula_parts(limit: Call) -> tuple[Expr, Expr] | None:
    if len(limit.args) != 1:
        return None
    formula = limit.args[0]
    if not (isinstance(formula, BinOp) and formula.op == "^"):
        return None
    value = formula.lhs
    if isinstance(value, BinOp) and value.op == "-":
        value = value.rhs
    if not (isinstance(value, BinOp) and value.op == "/"):
        return None
    numerator = value.lhs
    if not (isinstance(numerator, BinOp) and numerator.op == "*"):
        return None
    left = numerator.lhs
    if not (isinstance(left, BinOp) and left.op == "*"):
        return None
    h_term = left.rhs
    duration = numerator.rhs
    if not isinstance(h_term, Var):
        return None
    return h_term, duration


def _lower_formal_limit(
    bind: StateBind,
    limit: Call,
    qubit_of: dict[str, int],
    alloc,
    op_env: dict[str, OpExpr],
    scalars: dict[str, float],
    profile: EvolutionTargetProfile,
) -> tuple[list[Gate], dict[str, object]]:
    parts = _limit_formula_parts(limit)
    if parts is None:
        raise TrotterError(
            EVOLUTION_TARGET_UNSUPPORTED,
            "formal Limit has no supported finite product shape",
        )
    h_term, duration = parts
    result = bind.expr.body.result  # type: ignore[union-attr]
    assert isinstance(result, BinOp) and isinstance(result.rhs, Var)
    order = 1 if profile.limit_realization_method == "product" else profile.limit_order
    assert profile.limit_steps is not None
    policy_span = limit.span
    synthetic = EvolveExpr(
        seeds=[result.rhs],
        times=1,
        body=None,
        span=limit.span,
        duration=duration,
        hamiltonian=h_term,
        suzuki=SuzukiPolicy(
            order=LitInt(value=order or 1, span=policy_span),
            steps=LitInt(value=profile.limit_steps, span=policy_span),
            tolerance=None,
            error_mode=None,
            span=policy_span,
        ),
    )
    synthetic_bind = StateBind(
        names=bind.names,
        expr=synthetic,
        span=bind.span,
        ty=bind.ty,
    )
    gates = _lower_evolve_under(
        synthetic_bind, qubit_of, alloc, op_env, scalars
    )
    provenance = {
        "source_span": limit.span,
        "source_transform": "Limit product of infinitesimal steps",
        "state_shape": "State",
        "realization_kind": "approximate",
        "realization_policy": "finite_limit",
        "limit_method": profile.limit_realization_method,
        "limit_order": order,
        "limit_steps": profile.limit_steps,
        "limit_error_budget": profile.limit_error_budget,
        "approximation_order_or_null": order,
        "approximation_steps_or_null": profile.limit_steps,
        "error_budget_or_null": profile.limit_error_budget,
        "resource_estimate_or_null": {
            "qubits": max(qubit_of.values(), default=-1) + 1,
            "gates": len(gates),
        },
        "capability_rejection_or_null": None,
    }
    return gates, provenance


def _from_ast_patterns(
    unit: CompilationUnit,
    *,
    target_profile: EvolutionTargetProfile | None = None,
) -> Circuit | None:
    if unit.main is None:
        return None
    stmts = unit.main.body.stmts
    binds = [s for s in stmts if isinstance(s, StateBind)]
    measures = [s for s in stmts if isinstance(s, Measure)]
    if not measures:
        return None

    # Classical / Operator env for Trotter (LISS-0008)
    op_env: dict[str, OpExpr] = {}
    source_operator_env: dict[str, OpExpr] = {}
    scalars: dict[str, float] = {}
    from ...stdlib.prelude import PRELUDE_CONSTANTS

    scalars.update({k: float(v) for k, v in PRELUDE_CONSTANTS.items()})
    # Typed second-quantized locals, kept symbolic until a JordanWigner
    # mapping resolves them into an ordinary Pauli OpExpr in op_env
    # (LISS-0032, ADR 0093).
    second_quantized_env: dict[str, object] = {}
    lowered_binders, _ = lower_finite_binder_operators(unit)
    # LISS-0411/0412 (ADR 0206 completion for this static-only backend):
    # struct-of-literals objects, needed both for the JordanWigner
    # mapping below (struct-field fermionic coefficients) and for the
    # op_env resolution pass after the loop.
    from ...static_operator_resolution import collect_static_operator_context

    _, _, static_objects = collect_static_operator_context(unit)
    for b in binds:
        if b.ty is not None and b.ty.name == "Operator" and len(b.names) == 1:
            source_operator_env[b.names[0]] = b.expr  # type: ignore[assignment]
            op_env[b.names[0]] = lowered_binders.get(b.names[0], b.expr)  # type: ignore[assignment]
        elif b.ty is not None and b.ty.name in {"Float", "Int"} and len(b.names) == 1:
            if isinstance(b.expr, LitFloat):
                scalars[b.names[0]] = float(b.expr.value)
            elif isinstance(b.expr, LitInt):
                scalars[b.names[0]] = float(b.expr.value)
        # ADR 0195: Type-First dimensioned locals (Energy/Time/...) --
        # canonicalize to the SI value so `for dur` / dimensioned
        # coefficients are visible to Trotter QASM lowering the same way
        # the real-hbar runtime evolve path already sees them.
        elif b.ty is not None and len(b.names) == 1 and isinstance(b.expr, (Attr, UnitConvert)):
            from ...dimensions import to_canonical_magnitude

            canon = None
            if isinstance(b.expr, UnitConvert) and isinstance(b.expr.expr, Attr):
                inner = b.expr.expr
                if isinstance(inner.obj, (LitFloat, LitInt)):
                    try:
                        raw, _unit = to_canonical_magnitude(float(inner.obj.value), inner.name)
                        canon = raw
                    except KeyError:
                        canon = None
            elif isinstance(b.expr, Attr) and isinstance(b.expr.obj, (LitFloat, LitInt)):
                try:
                    raw, _unit = to_canonical_magnitude(float(b.expr.obj.value), b.expr.name)
                    canon = raw
                except KeyError:
                    canon = None
            if canon is not None:
                scalars[b.names[0]] = canon
        # ADR 0184 / LISS-0305: classical multi-bind `J, h = 1.0, 0.5` → QASM coeffs.
        elif (
            len(b.names) >= 2
            and isinstance(b.expr, TupleExpr)
            and len(b.expr.items) == len(b.names)
        ):
            for name, item in zip(b.names, b.expr.items):
                if isinstance(item, LitFloat):
                    scalars[name] = float(item.value)
                elif isinstance(item, LitInt):
                    scalars[name] = float(item.value)
        elif (
            b.ty is not None
            and b.ty.name in _SECOND_QUANTIZED_FAMILIES
            and len(b.names) == 1
        ):
            name = b.names[0]
            mapped_expr = None
            if b.ty.name == "QubitOperator":
                try:
                    mapped_expr = resolve_mapping_expr(
                        b.expr, second_quantized_env, scalars, static_objects
                    )
                except SecondQuantizationMappingError:
                    mapped_expr = None
            if mapped_expr is not None:
                op_env[name] = mapped_expr  # type: ignore[assignment]
            else:
                second_quantized_env[name] = b.expr

    # LISS-0411 (ADR 0206 completion for this static-only backend): resolve
    # struct-field coefficients and nested Operator-returning calls in
    # op_env, the same way the live Evaluator does at runtime
    # (LISS-0407/0410) -- e.g. `Operator H = scale * f(weights)` already
    # runs fine via `evolve`; QASM emission previously still hit the
    # pre-ADR-0206 vague `cannot compile sparse Pauli for OpCall`.
    from ...static_operator_resolution import resolve_static_operator

    for op_name, op_ast in list(op_env.items()):
        try:
            op_env[op_name] = resolve_static_operator(
                op_ast, unit=unit, operators=op_env, objects=static_objects
            )
        except (ValueError, TypeError, KeyError):
            pass

    # Target realization must be completely preflighted before the static
    # forEach elaboration below can allocate logical qubits.
    if target_profile is not None:
        for bind in binds:
            if isinstance(bind.expr, EvolveExpr) and bind.expr.explicit_transform:
                target_rejection = _explicit_target_rejection(
                    bind, binds, source_operator_env, target_profile
                )
                if target_rejection is not None:
                    return target_rejection

    # Map state names → logical qubit ids as we allocate
    qubit_of: dict[str, int] = {}
    gates: list[Gate] = []
    next_q = 0
    notes: list[str] = []
    evolution_provenance: dict[str, object] | None = None
    reject_code: str | None = None

    def alloc(name: str) -> int:
        nonlocal next_q
        if name not in qubit_of:
            qubit_of[name] = next_q
            next_q += 1
        return qubit_of[name]

    def reject(code: str, message: str) -> Circuit:
        notes.append(f"{code}: {message}")
        return Circuit(
            n_qubits=1,
            n_bits=1,
            gates=[],
            notes=notes,
            reject_code=code,
        )

    register_sizes: dict[str, int] = {}
    for b in binds:
        if (
            b.ty is not None
            and b.ty.name == "QubitRegister"
            and len(b.ty.args) == 1
            and len(b.names) == 1
        ):
            try:
                register_sizes[b.names[0]] = int(b.ty.args[0].name)
            except ValueError:
                pass

    # ADR 0069: statically elaborate `forEach q in reg { apply(...) }`.
    # before ordinary source binds are lowered.  The generated element names
    # are compiler-internal and never become Staqex classical values.
    for stmt in stmts:
        if not isinstance(stmt, ForEachStmt):
            continue
        count = _static_register_size(stmt.collection, register_sizes)
        if count is None:
            notes.append("FOR_EACH_DYNAMIC_BOUND_ERROR: static register required")
            continue
        if count > MVP_MAX_LOGICAL_QUBITS:
            reject_code = "STATIC_HILBERT_RESOURCE_ERROR"
            notes.append(
                "STATIC_HILBERT_RESOURCE_ERROR: static Hilbert expansion exceeds "
                f"the MVP budget ({MVP_MAX_LOGICAL_QUBITS})"
            )
            continue
        for index in range(count):
            element_name = f"__foreach_{stmt.element}_{index}"
            q = alloc(element_name)
            for body_stmt in stmt.body.stmts:
                call = _foreach_apply_call(body_stmt, stmt.element)
                if call is None:
                    continue
                gate_nm = _unitary_gate_name(call.args[0])
                if gate_nm in {"x", "y", "z", "h", "s", "t"}:
                    gates.append(
                        Gate(
                            gate_nm,  # type: ignore[arg-type]
                            (q,),
                            comment=f"forEach {stmt.element}[{index}]",
                        )
                    )

    user_fn_names = {d.name for d in unit.decls if isinstance(d, FunDecl)}

    for b in binds:
        if b.ty is not None and b.ty.name in {"Operator", "Float", "Int"}:
            continue
        if (
            isinstance(b.expr, Call)
            and isinstance(b.expr.callee, Var)
            and b.expr.callee.name in user_fn_names
        ):
            return reject(
                QASM_FUNCTION_CALL_UNSUPPORTED,
                _QASM_FUNCTION_CALL_UNSUPPORTED_MESSAGE,
            )
        if isinstance(b.expr, EvolveExpr) and b.expr.explicit_transform:
            if b.expr.until_predicate is not None:
                return reject(
                    QASM_EVOLVE_UNTIL_UNSUPPORTED,
                    _QASM_EVOLVE_UNTIL_UNSUPPORTED_MESSAGE,
                )
            if target_profile is None:
                return reject(
                    EVOLUTION_TARGET_UNSUPPORTED,
                    _EVOLUTION_TARGET_UNSUPPORTED_MESSAGE,
                )
            try:
                realization_order = target_profile.suzuki_order
                realization_steps = target_profile.suzuki_steps
                limit_source = _limit_source_for_bind(b, binds, source_operator_env)
                if limit_source is not None:
                    realize_call = _realize_call_for_bind(b, source_operator_env)
                    realize_profile = (
                        _profile_from_realize(realize_call, target_profile)
                        if realize_call is not None
                        else target_profile
                    )
                    if realize_profile.limit_realization_method == "product":
                        return _rejected_target_circuit(
                            EVOLUTION_TARGET_UNSUPPORTED,
                            {
                                "source_span": limit_source.span,
                                "source_transform": "Limit product of infinitesimal steps",
                                "state_shape": "State",
                                "realization_kind": "rejected",
                                "realization_policy": "explicit_realize",
                                "limit_method": "product",
                                "approximation_order_or_null": None,
                                "approximation_steps_or_null": realize_profile.limit_steps,
                                "error_budget_or_null": realize_profile.limit_error_budget,
                                "limit_steps": realize_profile.limit_steps,
                                "limit_error_budget": realize_profile.limit_error_budget,
                                    "capability_rejection_or_null": "EVOLUTION_PRODUCT_NOT_UNITARY_QPU",
                                "resource_estimate_or_null": None,
                            },
                        )
                    t_gates, evolution_provenance = _lower_formal_limit(
                        b, limit_source, qubit_of, alloc, op_env, scalars, realize_profile
                    )
                    realization_order = evolution_provenance["limit_order"]
                    realization_steps = evolution_provenance["limit_steps"]
                else:
                    t_gates = _lower_explicit_evolve(
                        b, qubit_of, alloc, op_env, scalars, target_profile
                    )
                gates.extend(t_gates)
                notes.append(
                    "explicit evolution realization: approximate "
                    f"Suzuki S{realization_order} "
                    f"steps={realization_steps}; "
                    f"resource_estimate=gates~{len(t_gates)}, "
                    f"qubits~{max(next_q, 1)}"
                )
                if target_profile.capability_limitations:
                    notes.append(
                        "target capability limitations: "
                        + ", ".join(target_profile.capability_limitations)
                    )
                if (
                    target_profile.resource_budget_qubits is not None
                    and next_q > target_profile.resource_budget_qubits
                ):
                    return reject(
                        EVOLUTION_TARGET_UNSUPPORTED,
                        "explicit evolution exceeds the target profile qubit budget",
                    )
            except TrotterError as e:
                return reject(e.code, e.message)
            continue
        if isinstance(b.expr, EvolveExpr) and b.expr.hamiltonian is not None:
            if b.expr.until_predicate is not None:
                return reject(
                    QASM_EVOLVE_UNTIL_UNSUPPORTED,
                    _QASM_EVOLVE_UNTIL_UNSUPPORTED_MESSAGE,
                )
            try:
                t_gates = _lower_evolve_under(
                    b, qubit_of, alloc, op_env, scalars
                )
                gates.extend(t_gates)
            except TrotterError as e:
                return reject(e.code, e.message)
            continue
        if isinstance(b.expr, EvolveExpr) and b.expr.explicit_transform:
            if b.expr.until_predicate is not None:
                return reject(
                    QASM_EVOLVE_UNTIL_UNSUPPORTED,
                    _QASM_EVOLVE_UNTIL_UNSUPPORTED_MESSAGE,
                )
            return reject(
                EVOLUTION_TARGET_UNSUPPORTED,
                _EVOLUTION_TARGET_UNSUPPORTED_MESSAGE,
            )
        if isinstance(b.expr, Coin):
            return _reject_mixture_projection(
                source_span=b.span,
                source_transform="Coin() mixture",
                source_node_id=f"ast:{b.span.line}:{b.span.col}",
            )
        if isinstance(b.expr, KetLit):
            q = alloc(b.name)
            lab = b.expr.label
            if lab == "+":
                gates.append(Gate("h", (q,), comment=f"|+⟩ on {b.name}"))
            elif lab == "1":
                gates.append(Gate("x", (q,), comment=f"|1⟩ on {b.name}"))
            elif lab == "-":
                gates.append(Gate("x", (q,), comment=f"|-⟩ prep X"))
                gates.append(Gate("h", (q,), comment=f"|-⟩ prep H"))
            else:
                notes.append(f"|{lab}⟩ on {b.name} ≈ |0⟩ idle / multi-qubit later")
            continue
        if isinstance(b.expr, Call) and isinstance(b.expr.callee, Var) and b.expr.callee.name == "cnot":
            if len(b.expr.args) == 2 and all(isinstance(a, Var) for a in b.expr.args):
                ctrl_n = b.expr.args[0].name
                tgt_n = b.expr.args[1].name
                if ctrl_n not in qubit_of:
                    notes.append(f"cnot ctrl `{ctrl_n}` unbound")
                    continue
                ctrl = qubit_of[ctrl_n]
                if tgt_n in qubit_of:
                    tgt = qubit_of[tgt_n]
                else:
                    tgt = alloc(tgt_n)
                qubit_of[b.name] = tgt
                gates.append(Gate("cx", (ctrl, tgt), comment=f"cnot {ctrl_n}→{tgt_n}"))
                continue
        if isinstance(b.expr, Call) and isinstance(b.expr.callee, Var) and b.expr.callee.name == "apply":
            gate_nm = _unitary_gate_name(b.expr.args[0]) if b.expr.args else None
            if (
                gate_nm in {"x", "y", "z", "h", "s", "t", "rx", "ry", "rz"}
                and len(b.expr.args) == 2
                and isinstance(b.expr.args[1], Var)
            ):
                src = b.expr.args[1].name
                if src not in qubit_of:
                    notes.append(f"apply target `{src}` unbound")
                    continue
                q = qubit_of[src]
                qubit_of[b.name] = q
                ang = (
                    _rotation_angle(b.expr.args[0], scalars)
                    if gate_nm in {"rx", "ry", "rz"}
                    else None
                )
                if gate_nm in {"rx", "ry", "rz"} and ang is None:
                    reject_code = QASM_ROTATION_ANGLE_UNRESOLVED
                    notes.append(
                        f"{QASM_ROTATION_ANGLE_UNRESOLVED}: apply({gate_nm}(…)) "
                        "angle is not a closed classical scalar"
                    )
                    continue
                gates.append(
                    Gate(
                        gate_nm,  # type: ignore[arg-type]
                        (q,),
                        angle=ang,
                        comment=f"apply({gate_nm}, {src})",
                    )
                )
                continue
        if isinstance(b.expr, Call) and isinstance(b.expr.callee, Var) and b.expr.callee.name == "capply":
            # capply(ctrl, U, tgt) with single control
            if len(b.expr.args) == 3 and isinstance(b.expr.args[0], Var) and isinstance(
                b.expr.args[2], Var
            ):
                u = _unitary_gate_name(b.expr.args[1])
                ctrl_n = b.expr.args[0].name
                tgt_n = b.expr.args[2].name
                if ctrl_n not in qubit_of or tgt_n not in qubit_of:
                    notes.append(f"capply unbound wires `{ctrl_n}`/`{tgt_n}`")
                    continue
                ctrl, tgt = qubit_of[ctrl_n], qubit_of[tgt_n]
                qubit_of[b.name] = tgt
                if u == "x":
                    gates.append(Gate("cx", (ctrl, tgt), comment=f"capply X {ctrl_n}→{tgt_n}"))
                elif u == "z":
                    gates.append(Gate("cz", (ctrl, tgt), comment=f"capply Z {ctrl_n}→{tgt_n}"))
                else:
                    notes.append(f"capply({u}) not mapped to QASM yet")
                continue
        if isinstance(b.expr, Call) and isinstance(b.expr.callee, Var) and b.expr.callee.name == "expect":
            notes.append(f"expect(...) on `{b.name}` is classical — skipped in QASM")
            continue
        if isinstance(b.expr, WhenExpr) and isinstance(b.expr.ctrl, Var):
            ctrl_name = b.expr.ctrl.name
            if ctrl_name not in qubit_of:
                notes.append(f"when ctrl `{ctrl_name}` unbound; reject mixture")
            return _reject_mixture_projection(
                source_span=b.span,
                source_transform="when mixture",
                source_node_id=f"ast:{b.span.line}:{b.span.col}",
            )
        if isinstance(b.expr, Dirac) or isinstance(b.expr, LitInt):
            q = alloc(b.name)
            val = _dirac_bit(b.expr)
            if val == 1:
                gates.append(Gate("x", (q,), comment=f"dirac(1) {b.name}"))
            else:
                notes.append(f"dirac(0) on {b.name} = |0⟩ (idle)")
            continue

    # interfer nodes: RZ on involved qubits (phase kick heuristic)
    # handled via DAG path primarily

    m = measures[0]
    if isinstance(m.expr, Var) and m.expr.name in qubit_of:
        q = qubit_of[m.expr.name]
    elif qubit_of:
        q = next(reversed(list(qubit_of.values())))
        notes.append("measure fallback: last allocated qubit")
    else:
        q = alloc("_m")
        gates.append(Gate("h", (q,), comment="empty program fallback"))

    gates.append(Gate("measure", (q,), bits=(0,), comment="terminal measure"))
    n_q = max(next_q, 1)
    return Circuit(
        n_qubits=n_q,
        n_bits=1,
        gates=gates,
        notes=notes,
        reject_code=reject_code,
        provenance=evolution_provenance,
    )


def _lower_explicit_evolve(
    bind: StateBind,
    qubit_of: dict[str, int],
    alloc,
    op_env: dict[str, OpExpr],
    scalars: dict[str, float],
    profile: EvolutionTargetProfile,
) -> list[Gate]:
    ev = bind.expr
    assert isinstance(ev, EvolveExpr) and ev.body is not None
    result = ev.body.result
    if not (isinstance(result, BinOp) and result.op == "*"):
        raise TrotterError(
            EVOLUTION_TARGET_UNSUPPORTED,
            "explicit QPU lowering requires `propagator * state`",
        )
    propagator = result.lhs
    if isinstance(propagator, Var):
        propagator = op_env.get(propagator.name)
    if not (
        isinstance(propagator, Call)
        and isinstance(propagator.callee, Var)
        and propagator.callee.name == "exp"
        and len(propagator.args) == 1
    ):
        raise TrotterError(
            EVOLUTION_TARGET_UNSUPPORTED,
            "QPU lowering requires a canonical explicit exponential propagator",
        )
    exponent = propagator.args[0]
    if not (
        isinstance(exponent, BinOp)
        and exponent.op == "/"
        and isinstance(exponent.lhs, BinOp)
        and exponent.lhs.op == "*"
        and isinstance(exponent.lhs.lhs, BinOp)
            and exponent.lhs.lhs.op == "*"
    ):
        raise TrotterError(
            EVOLUTION_TARGET_UNSUPPORTED,
            "QPU lowering requires `exp(-i * H * duration / hbar)`",
        )
    signed_i = exponent.lhs.lhs.lhs
    if not (
        isinstance(signed_i, BinOp)
        and signed_i.op == "-"
        and isinstance(signed_i.rhs, Var)
        and signed_i.rhs.name == "i"
        and isinstance(signed_i.lhs, LitFloat)
        and signed_i.lhs.value == 0.0
    ):
        raise TrotterError(
            EVOLUTION_TARGET_UNSUPPORTED,
            "QPU lowering refuses an exponential whose written phase is not `-i`",
        )
    if not (isinstance(exponent.rhs, Var) and exponent.rhs.name == "hbar"):
        raise TrotterError(
            EVOLUTION_TARGET_UNSUPPORTED,
            "QPU lowering requires the written denominator `hbar`",
        )
    hamiltonian = exponent.lhs.lhs.rhs
    duration = exponent.lhs.rhs
    policy_span = Span(line=ev.span.line, col=ev.span.col)
    policy = SuzukiPolicy(
        order=LitInt(value=profile.suzuki_order, span=policy_span),
        steps=LitInt(value=profile.suzuki_steps, span=policy_span),
        tolerance=None,
        error_mode=None,
        span=policy_span,
    )
    lowered = EvolveExpr(
        seeds=[result.rhs],
        times=1,
        body=None,
        span=ev.span,
        duration=duration,
        hamiltonian=hamiltonian,
        suzuki=policy,
    )
    lowered_bind = StateBind(
        names=bind.names,
        expr=lowered,
        span=bind.span,
        ty=bind.ty,
    )
    return _lower_evolve_under(lowered_bind, qubit_of, alloc, op_env, scalars)


def _explicit_target_rejection(
    bind: StateBind,
    binds: list[StateBind],
    source_operator_env: dict[str, OpExpr],
    profile: EvolutionTargetProfile,
) -> Circuit | None:
    """Preflight typed mapping and budget before any QPU allocation."""
    ev = bind.expr
    assert isinstance(ev, EvolveExpr) and ev.body is not None
    result = ev.body.result
    propagator_name = result.lhs.name if isinstance(result, BinOp) and isinstance(result.lhs, Var) else None
    propagator = next(
        (b.expr for b in binds if propagator_name and b.names == [propagator_name]),
        None,
    )
    h_name = None
    if (
        isinstance(propagator, Call)
        and isinstance(propagator.callee, Var)
        and propagator.callee.name == "Realize"
    ):
        source_name = next(
            (value.name for key, value in propagator.kwargs or ()
             if key == "source" and isinstance(value, Var)),
            None,
        )
        formal = source_operator_env.get(source_name or "")
        if isinstance(formal, Call) and isinstance(formal.callee, Var) and formal.callee.name == "Limit":
            parts = _limit_formula_parts(formal)
            h_name = parts[0].name if parts and isinstance(parts[0], Var) else None
    elif isinstance(propagator, Call) and propagator.args:
        exponent = propagator.args[0]
        if isinstance(exponent, BinOp) and isinstance(exponent.lhs, BinOp):
            h_term = exponent.lhs.lhs.rhs if isinstance(exponent.lhs.lhs, BinOp) else None
            h_name = h_term.name if isinstance(h_term, Var) else None
    source_h = source_operator_env.get(h_name or "")
    binder = _find_operator_binder(source_h)
    if binder is None:
        return None
    domain = binder.domain
    start = getattr(getattr(domain, "start", None), "value", None)
    end = getattr(getattr(domain, "end", None), "value", None)
    qubits = int(end - start + 1) if isinstance(start, (int, float)) and isinstance(end, (int, float)) else 0
    domain_text = f"{int(start)}..{int(end)}" if qubits else "unknown"
    mapping = profile.register_mapping or {}
    acting_register = mapping.get(binder.kind)
    estimate = {"qubits": qubits, "gates": max(qubits, 1)}
    provenance = {
        "source_span": bind.span,
        "source_transform": "exp(-i * H * duration / hbar) * State",
        "state_shape": "State",
        "realization_kind": "rejected",
        "realization_policy": "approximate_suzuki",
        "binder_kind": binder.kind,
        "binder_domain": domain_text,
        "bound_symbols": [binder.variable],
        "acting_register": acting_register or "missing",
        "operator_family": "PauliSum",
        "register_mapping": acting_register or "missing",
        "approximation_order_or_null": profile.suzuki_order,
        "approximation_steps_or_null": profile.suzuki_steps,
        "error_budget_or_null": None,
        "resource_estimate_or_null": estimate,
        "resource_budget": {"qubits": profile.resource_budget_qubits},
        "capability_rejection_or_null": None,
    }
    mapping_match = (
        re.fullmatch(r"q\[(\d+)\.\.(\d+)\]", acting_register)
        if acting_register
        else None
    )
    mapping_covers_domain = bool(
        mapping_match
        and qubits
        and int(mapping_match.group(1)) == int(start)
        and int(mapping_match.group(2)) == int(end)
    )
    if not mapping_covers_domain:
        provenance["capability_rejection_or_null"] = EVOLUTION_MAPPING_MISSING
        return _rejected_target_circuit(EVOLUTION_TARGET_UNSUPPORTED, provenance)
    if profile.resource_budget_qubits is not None and qubits > profile.resource_budget_qubits:
        return _rejected_resource_budget_circuit(
            EVOLUTION_TARGET_UNSUPPORTED,
            f"required {qubits} qubits exceeds target budget {profile.resource_budget_qubits}",
            provenance={
                "reason": "resource_budget_exceeded_before_allocation",
                "source_evidence": {
                    "source_node_id": f"ast:{bind.span.line}:{bind.span.col}",
                    "required_qubits": qubits,
                    "resource_budget_qubits": profile.resource_budget_qubits,
                },
                "target_plan": None,
            },
        )
    return None


def _find_operator_binder(expr: OpExpr | None) -> OpBinder | None:
    if isinstance(expr, OpBinder):
        return expr
    if isinstance(expr, OpBin):
        return _find_operator_binder(expr.lhs) or _find_operator_binder(expr.rhs)
    return None


def _generic_explicit_provenance(
    bind: StateBind, rejection: str
) -> dict[str, object]:
    return {
        "source_span": bind.span,
        "source_transform": "explicit operator * state",
        "state_shape": "State",
        "realization_kind": "rejected",
        "realization_policy": "target_capability_required",
        "approximation_order_or_null": None,
        "approximation_steps_or_null": None,
        "error_budget_or_null": None,
        "resource_estimate_or_null": None,
        "capability_rejection_or_null": rejection,
        "reason": rejection,
        "source_node_id": f"ast:{bind.span.line}:{bind.span.col}",
    }


def _explicit_provenance(
    bind: StateBind, reason: str, source_transform: str
) -> dict[str, object]:
    provenance = _generic_explicit_provenance(bind, reason)
    provenance["source_transform"] = source_transform
    provenance["reason"] = reason
    return provenance


def register_resource_budget_reject(
    unit: CompilationUnit,
    target_profile: EvolutionTargetProfile | None,
) -> Circuit | None:
    """Reject statically allocatable qubits before lowering allocates wires."""
    if target_profile is None or target_profile.resource_budget_qubits is None:
        return None
    if unit.main is None:
        return None
    binds_by_name = {
        stmt.names[0]: stmt.expr
        for stmt in unit.main.body.stmts
        if isinstance(stmt, StateBind) and len(stmt.names) == 1
    }

    def references_binder(value: object) -> bool:
        if isinstance(value, Var):
            bound = binds_by_name.get(value.name)
            return isinstance(bound, OpBinder) or (
                isinstance(bound, OpBin)
                and (references_binder(bound.lhs) or references_binder(bound.rhs))
            )
        if isinstance(value, OpBinder):
            return True
        if isinstance(value, OpBin):
            return references_binder(value.lhs) or references_binder(value.rhs)
        if isinstance(value, (BinOp, Call)):
            fields = (value.lhs, value.rhs) if isinstance(value, BinOp) else (
                value.args,
                value.kwargs or (),
            )
            return any(references_binder(item) for item in fields)
        if isinstance(value, (list, tuple)):
            return any(references_binder(item) for item in value)
        return False

    # The finite binder path owns its own domain/mapping/budget estimate.  Do
    # not let the generic state preflight replace that more precise evidence.
    for stmt in unit.main.body.stmts:
        if not (
            isinstance(stmt, StateBind)
            and isinstance(stmt.expr, EvolveExpr)
            and stmt.expr.explicit_transform
            and stmt.expr.body is not None
            and isinstance(stmt.expr.body.result, BinOp)
        ):
            continue
        result = stmt.expr.body.result
        source = binds_by_name.get(result.lhs.name) if isinstance(result.lhs, Var) else None
        if isinstance(source, Call) and isinstance(source.callee, Var) and source.callee.name == "exp":
            if references_binder(source.args[0]) if source.args else False:
                return None
    register_sizes: dict[str, int] = {}
    required = 0
    evidence: dict[str, object] | None = None
    for stmt in unit.main.body.stmts:
        if not (
            isinstance(stmt, StateBind)
            and stmt.ty is not None
            and stmt.ty.name == "QubitRegister"
            and len(stmt.ty.args) == 1
            and len(stmt.names) == 1
        ):
            continue
        size = getattr(stmt.ty.args[0], "name", "")
        if not str(size).isdigit():
            continue
        register_sizes[stmt.names[0]] = int(size)
        required += int(size)
        evidence = {
            "source_node_id": f"ast:{stmt.span.line}:{stmt.span.col}",
            "required_qubits": required,
        }
    for stmt in unit.main.body.stmts:
        if isinstance(stmt, ForEachStmt):
            size = _static_register_size(stmt.collection, register_sizes)
            if size is not None and not (
                isinstance(stmt.collection, Var)
                and stmt.collection.name in register_sizes
            ):
                required += size
                evidence = {
                    "source_node_id": f"ast:{stmt.span.line}:{stmt.span.col}",
                    "required_qubits": required,
                }
        if not isinstance(stmt, StateBind) or len(stmt.names) != 1:
            continue
        if stmt.ty is not None and stmt.ty.name == "QubitRegister":
            continue
        if isinstance(stmt.expr, (KetLit, Coin, Dirac, WhenExpr)):
            required += 1
            evidence = {
                "source_node_id": f"ast:{stmt.span.line}:{stmt.span.col}",
                "required_qubits": required,
            }
    if required <= target_profile.resource_budget_qubits:
        return None
    return _rejected_resource_budget_circuit(
        EVOLUTION_TARGET_UNSUPPORTED,
        f"required {required} qubits exceeds target budget {target_profile.resource_budget_qubits}",
        provenance={
            "reason": "resource_budget_exceeded_before_allocation",
            "source_evidence": evidence,
            "target_plan": None,
        },
    )


def _rejected_target_circuit(code: str, provenance: dict[str, object]) -> Circuit:
    provenance = dict(provenance)
    return Circuit(
        n_qubits=0,
        n_bits=0,
        gates=[],
        notes=[f"{code}: target realization rejected before allocation"],
        reject_code=code,
        provenance=provenance,
    )


def _rejected_resource_budget_circuit(
    code: str,
    message: str,
    *,
    provenance: dict[str, object] | None = None,
) -> Circuit:
    """Reject before allocation without leaking partial target evidence."""
    return Circuit(
        n_qubits=0,
        n_bits=0,
        gates=[],
        notes=[f"{code}: {message}"],
        reject_code=code,
        provenance=provenance,
        allocation_started=False,
        allocated_qubits=(),
        partial_program=None,
    )


def _static_register_size(
    collection: Expr, register_sizes: dict[str, int] | None = None
) -> int | None:
    """Return a finite register size, or None for a dynamic/unsupported bound."""
    if isinstance(collection, Var) and register_sizes is not None:
        size = register_sizes.get(collection.name)
        return size if size is not None and size > 0 else None
    if not (
        isinstance(collection, Call)
        and isinstance(collection.callee, Var)
        and collection.callee.name == "register"
        and len(collection.args) == 1
        and isinstance(collection.args[0], LitInt)
    ):
        return None
    size = collection.args[0].value
    return size if size > 0 else None


def _foreach_apply_call(stmt, element: str) -> Call | None:
    """Extract `apply(U, element)` from a static loop body."""
    if not isinstance(stmt, ExprStmt) or not isinstance(stmt.expr, Call):
        return None
    call = stmt.expr
    if not (
        isinstance(call.callee, Var)
        and call.callee.name == "apply"
        and len(call.args) == 2
        and isinstance(call.args[1], Var)
        and call.args[1].name == element
    ):
        return None
    return call


def _lower_evolve_under(
    bind: StateBind,
    qubit_of: dict[str, int],
    alloc,
    op_env: dict[str, OpExpr],
    scalars: dict[str, float],
) -> list[Gate]:
    """Lower `state (…)= evolve (…) under H for t` via first-order Pauli Trotter."""
    ev = bind.expr
    assert isinstance(ev, EvolveExpr) and ev.hamiltonian is not None
    names = bind.names
    # Ensure seed wires exist (allocate |0⟩ idle if missing).
    site_qubits: list[int] = []
    for i, name in enumerate(names):
        if name in qubit_of:
            site_qubits.append(qubit_of[name])
        elif i < len(ev.seeds) and isinstance(ev.seeds[i], Var):
            src = ev.seeds[i].name
            if src in qubit_of:
                q = qubit_of[src]
            else:
                q = alloc(src)
            qubit_of[name] = q
            site_qubits.append(q)
        else:
            site_qubits.append(alloc(name))
    n_qubits = len(site_qubits)
    if ev.duration is None:
        raise TrotterError(
            "QASM_TROTTER_BAD_TIME",
            "hamiltonian evolve requires `under H for t`",
        )
    t = eval_time_expr(ev.duration, scalars)
    terms = compile_hamiltonian(
        ev.hamiltonian,  # type: ignore[arg-type]
        env=op_env,
        scalars=scalars,
        n_qubits=n_qubits,
    )
    if ev.suzuki is None:
        raise TrotterError(
            QASM_TROTTER_STEPS_REQUIRED,
            "emitting QASM for `evolve ... under H for t` requires an "
            "explicit step-count policy. Add `using Suzuki(order = 2, "
            "steps = N)` for an exact step count, or `using Suzuki(order = "
            "2, tolerance = X, error = Bound | EmpiricalEstimate)` for an "
            "error-bound-derived count.",
        )
    resolved_steps = resolve_suzuki_steps(ev.suzuki, terms, t, scalars)
    order = resolve_suzuki_order(ev.suzuki.order, scalars)
    return suzuki_gates(
        terms, t, site_qubits, steps=resolved_steps, order=order
    )


def _from_dag(dag: Dag) -> Circuit:
    gates: list[Gate] = []
    notes = ["DAG heuristic lowering (no AST coin/when pattern)"]
    qmap: dict[int, int] = {}
    next_q = 0

    def q_for(nid: int) -> int:
        nonlocal next_q
        if nid not in qmap:
            qmap[nid] = next_q
            next_q += 1
        return qmap[nid]

    for n in dag.nodes:
        if n.kind == "coin":
            q = q_for(n.id)
            gates.append(Gate("h", (q,), comment=f"dag coin n{n.id}"))
        elif n.kind == "when":
            # CX if has ≥2 inputs (ctrl + body)
            if len(n.inputs) >= 2:
                c, t = q_for(n.inputs[0]), q_for(n.id)
                if c == t:
                    t = q_for(n.id + 10_000)  # force distinct
                gates.append(Gate("cx", (c, t), comment=f"dag when n{n.id}"))
            else:
                q = q_for(n.id)
                gates.append(Gate("rz", (q,), angle=0.0, comment=f"dag when rz n{n.id}"))
        elif n.kind == "interfer":
            for inp in n.inputs:
                q = q_for(inp)
                gates.append(Gate("rz", (q,), angle=0.0, comment=f"dag interfer phase n{n.id}"))
            q = q_for(n.id)
            gates.append(Gate("h", (q,), comment=f"dag interfer mix n{n.id}"))
        elif n.kind == "measure":
            src = n.inputs[0] if n.inputs else n.id
            q = q_for(src)
            gates.append(Gate("measure", (q,), bits=(0,), comment=f"dag measure n{n.id}"))

    if not any(g.name == "measure" for g in gates):
        q = 0 if next_q == 0 else next_q - 1
        if next_q == 0:
            next_q = 1
            gates.append(Gate("h", (0,), comment="dag empty"))
        gates.append(Gate("measure", (q,), bits=(0,)))

    return Circuit(n_qubits=max(next_q, 1), n_bits=1, gates=gates, notes=notes)


def _reject_mixture_projection(
    *,
    source_span: Span,
    source_transform: str,
    source_node_id: str,
) -> Circuit:
    """Reject a Coin/Mix realization without allocating target artifacts."""
    return _rejected_target_circuit(
        MIXTURE_PROJECTION_REJECTION_CODE,
        {
            "source_span": source_span,
            "source_transform": source_transform,
            "state_shape": "State",
            "realization_kind": "rejected",
            "realization_policy": "finite_projection_required",
            "capability_rejection_or_null": MIXTURE_PROJECTION_REJECTION_REASON,
            "reason": MIXTURE_PROJECTION_REJECTION_REASON,
            "source_node_id": source_node_id,
        },
    )


def _dirac_bit(expr) -> int:
    if isinstance(expr, LitInt):
        return int(expr.value)
    if isinstance(expr, Dirac):
        return _dirac_bit(expr.arg)
    return 0


def _unitary_gate_name(expr) -> str | None:
    """Map Staqex unitary token (Var `X`/`H`/`S`/… or `rx(θ)`) to QASM id."""
    if isinstance(expr, Var):
        n = expr.name
        if n in {"X", "Y", "Z", "H", "S", "T"}:
            return n.lower()
        if n in {"x", "y", "z", "h", "s", "t"}:
            return n
    if isinstance(expr, Call) and isinstance(expr.callee, Var):
        op = expr.callee.name.lower()
        if op in {"rx", "ry", "rz"}:
            return op
    return None


def _rotation_angle(expr, scalars: dict[str, float]) -> float | None:
    """Extract θ from rx|ry|rz(θ) Call; literals / named classical scalars."""
    if not (isinstance(expr, Call) and isinstance(expr.callee, Var)):
        return None
    if expr.callee.name.lower() not in {"rx", "ry", "rz"} or len(expr.args) != 1:
        return None
    arg = expr.args[0]
    if isinstance(arg, LitFloat):
        return float(arg.value)
    if isinstance(arg, LitInt):
        return float(arg.value)
    if isinstance(arg, Var):
        if arg.name in scalars:
            return float(scalars[arg.name])
    if isinstance(arg, BinOp) and arg.op == "/" and isinstance(arg.lhs, Var):
        # pi / 2.0
        if arg.lhs.name in scalars and isinstance(arg.rhs, (LitFloat, LitInt)):
            return float(scalars[arg.lhs.name]) / float(arg.rhs.value)
    return None
