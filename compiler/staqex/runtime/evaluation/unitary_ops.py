"""Unitary ops for evaluator evolution."""

from __future__ import annotations

from ...ast_nodes import Call, Expr, Var
from .context import EvaluatorContext
from .errors import KernelError
from ..joint import Joint
from .values import evaluate_value


def bind_apply_multi(
    context: EvaluatorContext, joint: Joint, names: list[str], expr: Call
) -> Joint:
    """apply(U, w…) rebound as ``state (n…) = apply(U, w…)`` (LISS-0228)."""
    from ..unitaries import apply_unitary_on_wires

    u_expr = expr.args[0]
    wires = [a.name for a in expr.args[1:]]  # type: ignore[union-attr]
    # LISS-0112 Slice B / LISS-0239: bare Identity is a no-op on any
    # computational level (incl. Qutrit |2⟩); must run before qubit-bit gate.
    if (
        isinstance(u_expr, Var)
        and u_expr.name.upper() in {"I", "ID", "IDENTITY"}
        and len(wires) == 1
    ):
        if list(names) == wires:
            return joint
        w0 = wires[0]
        new = names[0]
        return joint.bind_pushforward(new, lambda a, w=w0: a[w])
    u_mat = context._resolve_unitary_matrix(u_expr, len(wires))
    try:
        updated = apply_unitary_on_wires(joint, wires, u_mat)
    except ValueError as e:
        raise KernelError(str(e)) from e
    if list(names) == wires:
        return updated
    # Relabel wire coordinates to bind names when they differ.
    from ..joint import World, _coalesce

    out: list[World] = []
    for w in updated.worlds:
        assign = dict(w.assign)
        cp = dict(w.coord_phase)
        for old, new in zip(wires, names):
            if old == new:
                continue
            if old in assign:
                assign[new] = assign.pop(old)
            if old in cp:
                cp[new] = cp.pop(old)
        out.append(World(assign=assign, amp=w.amp, coord_phase=cp))
    return Joint(worlds=_coalesce(out))

def bind_cnot_multi(
    context: EvaluatorContext, joint: Joint, names: list[str], expr: Call
) -> Joint:
    """``state (c, t) = cnot(c, t)`` — keep both wires after CNOT (linear)."""
    from ..joint import World, _coalesce
    from ..quantum_ops import cnot_bit

    ctrl_old = expr.args[0].name  # type: ignore[union-attr]
    tgt_old = expr.args[1].name  # type: ignore[union-attr]
    ctrl_new, tgt_new = names
    out: list[World] = []
    for w in joint.worlds:
        if ctrl_old not in w.assign or tgt_old not in w.assign:
            raise KernelError(
                f"cnot needs coordinates `{ctrl_old}` and `{tgt_old}` on the joint"
            )
        assign = {
            k: v
            for k, v in w.assign.items()
            if k not in {ctrl_old, tgt_old}
        }
        cp = {
            k: v
            for k, v in w.coord_phase.items()
            if k not in {ctrl_old, tgt_old}
        }
        ctrl_v = w.assign[ctrl_old]
        tgt_v = cnot_bit(ctrl_v, w.assign[tgt_old])
        assign[ctrl_new] = ctrl_v
        assign[tgt_new] = tgt_v
        if ctrl_old in w.coord_phase:
            cp[ctrl_new] = w.coord_phase[ctrl_old]
        if tgt_old in w.coord_phase:
            cp[tgt_new] = w.coord_phase[tgt_old]
        out.append(World(assign=assign, amp=w.amp, coord_phase=cp))
    return Joint(worlds=_coalesce(out))


def resolve_unitary_matrix(
    context: EvaluatorContext, u_expr: Expr, n_wires: int
) -> list[list[complex]]:
    """Resolve Operator / Hadamard / Pauli / S|T / rx|ry|rz → dense unitary."""
    from ..hamiltonian import compile_hamiltonian, op_n_qubits
    from ..unitaries import named_gate_matrix, rotation_gate_matrix
    from ...ast_nodes import Call, Var

    if isinstance(u_expr, Call) and isinstance(u_expr.callee, Var):
        op = u_expr.callee.name.lower()
        if op in {"rx", "ry", "rz"}:
            if len(u_expr.args) != 1:
                raise KernelError(f"{op} requires (theta)")
            if n_wires != 1:
                raise KernelError(f"{op} is 1-qubit; pass one target wire")
            theta = float(evaluate_value(context, u_expr.args[0], {}))
            return rotation_gate_matrix(op[1], theta)
        qft_mat = qft_family_matrix(context, u_expr, n_wires)
        if qft_mat is not None:
            return qft_mat

    if not isinstance(u_expr, Var):
        raise KernelError(
            "unitary must be an Operator / gate name / rx|ry|rz(theta)"
        )
    uname = u_expr.name
    op_ast = context._unitary_operator_definition(uname)
    operator_environment = context._unitary_operator_environment()
    if op_ast is not None:
        from ..qft_dense import DenseMatrixOp

        if isinstance(op_ast, DenseMatrixOp):
            if op_ast.n_qubits != n_wires:
                raise KernelError(
                    f"Operator `{uname}` needs {op_ast.n_qubits} wires, "
                    f"got {n_wires}"
                )
            return op_ast.matrix
        if isinstance(op_ast, Call):
            qft_mat = qft_family_matrix(context, op_ast, n_wires)
            if qft_mat is not None:
                return qft_mat
        try:
            nq = op_n_qubits(
                op_ast, operator_environment, context._scalar_environment()
            )
            if nq == 0:
                raise KernelError("unitary apply does not support Fock N operators")
            if nq != n_wires:
                raise KernelError(
                    f"Operator `{uname}` needs {nq} wires, got {n_wires}"
                )
            return compile_hamiltonian(
                op_ast,
                env=operator_environment,
                scalars=context._scalar_environment(),
                n_qubits=n_wires,
            )
        except ValueError as e:
            raise KernelError(str(e)) from e
    u_mat = named_gate_matrix(uname)
    if u_mat is None:
        raise KernelError(
            f"unknown unitary `{uname}` "
            "(Operator name, H/S/T, Pauli X|Y|Z|I, or rx|ry|rz(theta))"
        )
    if n_wires != 1:
        raise KernelError(f"gate `{uname}` is 1-qubit; pass one target wire")
    return u_mat


def qft_family_matrix(
    context: EvaluatorContext, call: Call, n_wires: int
) -> list[list[complex]] | None:
    """Dense exact QFT family for Joint apply (LISS-0228)."""
    from ..qft_dense import cqft_matrix, iqft_matrix, qft_matrix
    from ...ast_nodes import Var

    if not isinstance(call.callee, Var):
        return None
    name = call.callee.name
    if name not in {"qft", "iqft", "cqft", "ciqft"}:
        return None
    if name in {"qft", "iqft"}:
        if len(call.args) != 1 or not isinstance(call.args[0], Var):
            raise KernelError("qft/iqft requires a QubitRegister argument")
        n = context._static_register_size(call.args[0].name)
        if n is None:
            raise KernelError(
                f"qft/iqft register `{call.args[0].name}` has no static size"
            )
        if n_wires != n:
            raise KernelError(
                f"Operator `{name}` needs {n} wires, got {n_wires}"
            )
        return iqft_matrix(n) if name == "iqft" else qft_matrix(n)
    # cqft / ciqft
    if len(call.args) != 2 or not all(isinstance(a, Var) for a in call.args):
        raise KernelError(
            "cqft/ciqft requires QubitRegister control and target"
        )
    ctrl_n = context._static_register_size(
        call.args[0].name  # type: ignore[union-attr]
    )
    tgt_n = context._static_register_size(
        call.args[1].name  # type: ignore[union-attr]
    )
    if ctrl_n != 1 or tgt_n is None:
        raise KernelError(
            "cqft/ciqft requires QubitRegister<1> control and QubitRegister<N> target"
        )
    need = 1 + tgt_n
    if n_wires != need:
        raise KernelError(
            f"Operator `{name}` needs {need} wires, got {n_wires}"
        )
    return cqft_matrix(tgt_n, inverse=(name == "ciqft"))


def bind_apply(
    context: EvaluatorContext, joint: Joint, name: str, expr: Call
) -> Joint:
    """apply(U, w0[, w1, …]) — apply unitary matrix (not e^{-iHt})."""
    from ..unitaries import apply_unitary_on_wires

    if len(expr.args) < 2:
        raise KernelError("apply requires (U, wire[, wire…])")
    u_expr = expr.args[0]
    wire_args = expr.args[1:]
    if not all(isinstance(a, Var) for a in wire_args):
        raise KernelError("apply wires must be state variables")
    wires = [a.name for a in wire_args]  # type: ignore[union-attr]
    # LISS-0112 Slice B: bare Identity is a no-op (preserves D=3 levels).
    if (
        isinstance(u_expr, Var)
        and u_expr.name.upper() in {"I", "ID", "IDENTITY"}
        and len(wires) == 1
    ):
        if name in wires:
            return joint
        w0 = wires[0]
        return joint.bind_pushforward(name, lambda a, w=w0: a[w])
    u_mat = resolve_unitary_matrix(context, u_expr, len(wires))
    try:
        updated = apply_unitary_on_wires(joint, wires, u_mat)
    except ValueError as e:
        raise KernelError(str(e)) from e

    if name in wires:
        return updated
    w0 = wires[0]
    return updated.bind_pushforward(name, lambda a, w=w0: a[w])


def is_unitary_name(context: EvaluatorContext, name: str) -> bool:
    """Return whether a value can be selected as a controlled-gate unitary."""

    from ..unitaries import named_gate_matrix

    return (
        context._unitary_operator_definition(name) is not None
        or named_gate_matrix(name) is not None
    )


def split_capply_args(
    context: EvaluatorContext, args: list[Expr]
) -> tuple[list[str], list[int], Expr, list[str]]:
    """Parse capply(c0[, !c1…], U, t0[, …]) — polarity 1=filled, 0=open (`!`)."""
    from ...ast_nodes import UnaryNot

    u_idx = None
    for i, a in enumerate(args):
        if isinstance(a, Var) and is_unitary_name(context, a.name):
            u_idx = i
            break
    if u_idx is None:
        raise KernelError(
            "capply requires a unitary name (Operator / Hadamard / Pauli) "
            "between controls and targets"
        )
    if u_idx < 1:
        raise KernelError("capply requires at least one control before U")
    if u_idx >= len(args) - 1:
        raise KernelError("capply requires at least one target after U")
    ctrl_args = args[:u_idx]
    u_expr = args[u_idx]
    tgt_args = args[u_idx + 1 :]

    ctrls: list[str] = []
    poles: list[int] = []
    for a in ctrl_args:
        if isinstance(a, Var):
            ctrls.append(a.name)
            poles.append(1)
        elif isinstance(a, UnaryNot) and isinstance(a.expr, Var):
            ctrls.append(a.expr.name)
            poles.append(0)
        else:
            raise KernelError(
                "capply controls must be state vars or open-polarity `!var`"
            )
    if not all(isinstance(a, Var) for a in tgt_args):
        raise KernelError("capply targets must be state variables")
    tgts = [a.name for a in tgt_args]  # type: ignore[union-attr]
    if len(set(ctrls + tgts)) != len(ctrls) + len(tgts):
        raise KernelError("capply wires must be distinct")
    return ctrls, poles, u_expr, tgts


def bind_capply(
    context: EvaluatorContext,
    joint: Joint,
    name: str,
    expr: Call,
    *,
    force_all_open: bool = False,
    op_label: str = "capply",
) -> Joint:
    """capply / ocapply — filled, open, or mixed polarities (ADR 0048)."""
    from ..unitaries import apply_unitary_on_wires, multi_controlled_unitary

    if len(expr.args) < 3:
        raise KernelError(f"{op_label} requires (ctrl[, …], U, tgt[, …])")
    ctrls, poles, u_expr, tgts = split_capply_args(context, list(expr.args))
    if force_all_open:
        poles = [0] * len(ctrls)
    u_mat = resolve_unitary_matrix(context, u_expr, len(tgts))
    mask = 0
    for p in poles:
        mask = (mask << 1) | p
    cu = multi_controlled_unitary(
        u_mat, n_controls=len(ctrls), active_mask=mask
    )
    wires = [*ctrls, *tgts]
    try:
        updated = apply_unitary_on_wires(joint, wires, cu)
    except ValueError as e:
        raise KernelError(str(e)) from e
    if name in wires:
        return updated
    t0 = tgts[0]
    return updated.bind_pushforward(name, lambda a, w=t0: a[w])
