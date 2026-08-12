"""DAG / AST → logical Circuit (Phase 4.1)."""

from __future__ import annotations

from ...ast_nodes import (
    Attr,
    BinOp,
    Call,
    Coin,
    CompilationUnit,
    Dirac,
    EvolveExpr,
    ExprStmt,
    ForEachStmt,
    FunDecl,
    KetLit,
    LitFloat,
    LitInt,
    Measure,
    OpExpr,
    StateBind,
    TupleExpr,
    TypeRef,
    UnitConvert,
    Var,
    WhenExpr,
)
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
                n_qubits=1,
                n_bits=1,
                gates=[],
                notes=[_UNSUPPORTED_LOCAL_DIMENSION_MESSAGE],
                reject_code=UNSUPPORTED_LOCAL_DIMENSION,
            )
    return None


def lower_unit_to_circuit(unit: CompilationUnit) -> Circuit:
    """Prefer structural AST patterns; else DAG-driven heuristic."""
    rejected = qudit_capability_reject(unit)
    if rejected is not None:
        return rejected
    circ = _from_ast_patterns(unit)
    if circ is not None:
        return circ
    dag = lower_source_ast(unit)
    return _from_dag(dag)


def _from_ast_patterns(unit: CompilationUnit) -> Circuit | None:
    if unit.main is None:
        return None
    stmts = unit.main.body.stmts
    binds = [s for s in stmts if isinstance(s, StateBind)]
    measures = [s for s in stmts if isinstance(s, Measure)]
    if not measures:
        return None

    # Classical / Operator env for Trotter (LISS-0008)
    op_env: dict[str, OpExpr] = {}
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

    # Map state names → logical qubit ids as we allocate
    qubit_of: dict[str, int] = {}
    gates: list[Gate] = []
    next_q = 0
    notes: list[str] = []
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
            n_qubits=max(next_q, 1),
            n_bits=1,
            gates=gates,
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
        if isinstance(b.expr, Coin):
            q = alloc(b.name)
            gates.append(Gate("h", (q,), comment=f"coin() → |+⟩ on {b.name}"))
            continue
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
                notes.append(f"when ctrl `{ctrl_name}` unbound; skip CX pattern")
                continue
            if _is_copy_when(b.expr):
                tgt = alloc(b.name)
                ctrl = qubit_of[ctrl_name]
                gates.append(Gate("cx", (ctrl, tgt), comment=f"when-copy {ctrl_name}→{b.name}"))
                continue
            # generic when: RZ annotation + note (amplitude IR later)
            tgt = alloc(b.name)
            gates.append(Gate("h", (tgt,), comment=f"when-mixture prep {b.name}"))
            gates.append(Gate("rz", (tgt,), angle=0.0, comment="when phase placeholder"))
            notes.append(f"generic when on `{b.name}` lowered to H+RZ(0) placeholder")
            continue
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
        n_qubits=n_q, n_bits=1, gates=gates, notes=notes, reject_code=reject_code
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


def _is_copy_when(w: WhenExpr) -> bool:
    zero_arm = else_arm = None
    for arm in w.arms:
        if arm.is_else:
            else_arm = arm.body
        elif arm.pat == 0:
            zero_arm = arm.body
    if zero_arm is None or else_arm is None:
        return False
    return _is_dirac_or_lit(zero_arm, 0) and _is_dirac_or_lit(else_arm, 1)


def _is_dirac_or_lit(expr, value: int) -> bool:
    if isinstance(expr, LitInt) and expr.value == value:
        return True
    if isinstance(expr, Dirac):
        return _is_dirac_or_lit(expr.arg, value)
    return False


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
