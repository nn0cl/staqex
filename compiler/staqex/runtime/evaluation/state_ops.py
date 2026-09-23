"""State construction and State/Operator algebra successors."""

from __future__ import annotations

import itertools
from typing import Any

from ...ast_nodes import Call, Expr, KetLit, KetSumBinder, NormExpr, Var
from ..joint import EPS, Joint, World, _coalesce
from ..qft_dense import DenseMatrixOp
from ..quantum_ops import ket_support
from .context import EvaluatorContext
from .errors import KernelError


def bind_ket(context: EvaluatorContext, joint: Joint, name: str, expr: KetLit) -> Joint:
    try:
        pairs = ket_support(expr.label)
    except ValueError as error:
        raise KernelError(str(error)) from error
    if joint.is_vacuum():
        return Joint.empty()
    out: list[World] = []
    for world in joint.worlds:
        for value, amplitude in pairs:
            next_amplitude = world.amp * amplitude
            if abs(next_amplitude) ** 2 > EPS:
                out.append(
                    World(
                        assign={**world.assign, name: value},
                        amp=next_amplitude,
                        coord_phase=dict(world.coord_phase),
                    )
                )
    return Joint(worlds=_coalesce(out))


def bind_ket_sum_binder(
    context: EvaluatorContext, joint: Joint, name: str, expr: KetSumBinder
) -> Joint:
    """Bind the literal, unnormalized Sigma ket-sum."""
    width_raw = context._evaluate_value(expr.domain.width, {})
    try:
        width = int(width_raw)
    except (TypeError, ValueError) as error:
        raise KernelError("Sigma ket-sum domain width must be Int") from error
    if width < 1:
        raise KernelError("Sigma ket-sum domain width must be >= 1")
    labels = tuple(expr.domain.labels)
    patterns = itertools.product(labels, repeat=width)
    return joint.bind_split(name, {pattern: 1.0 for pattern in patterns})


def is_state_producing_bind_expr(expr: Expr) -> bool:
    return isinstance(expr, (KetLit, KetSumBinder))


def bind_scaled_state(
    context: EvaluatorContext,
    joint: Joint,
    name: str,
    state_expr: Expr,
    scalar_expr: Expr,
) -> Joint:
    scale = context._evaluate_value(scalar_expr, {})
    temporary = f"__scale_tmp_{id(state_expr)}"
    sub = context._bind(joint, temporary, state_expr)
    out: list[World] = []
    for world in sub.worlds:
        assign = {key: value for key, value in world.assign.items() if key != temporary}
        assign[name] = world.assign[temporary]
        out.append(
            World(
                assign=assign,
                amp=world.amp * scale,
                coord_phase=dict(world.coord_phase),
            )
        )
    return Joint(worlds=_coalesce(out))


def bind_state_divided_by_norm(
    context: EvaluatorContext,
    joint: Joint,
    name: str,
    state_expr: Expr,
    norm_expr: NormExpr,
) -> Joint:
    temporary = f"__div_tmp_{id(state_expr)}"
    sub = context._bind(joint, temporary, state_expr)
    norm = compute_norm(context, joint, norm_expr.state)
    out: list[World] = []
    for world in sub.worlds:
        assign = {key: value for key, value in world.assign.items() if key != temporary}
        assign[name] = world.assign[temporary]
        out.append(
            World(
                assign=assign,
                amp=world.amp / norm,
                coord_phase=dict(world.coord_phase),
            )
        )
    return Joint(worlds=_coalesce(out))


def compute_norm(context: EvaluatorContext, joint: Joint, state_expr: Expr) -> float:
    temporary = f"__norm_tmp_{id(state_expr)}"
    sub = context._bind(joint, temporary, state_expr)
    total = sum(abs(world.amp) ** 2 for world in sub.worlds)
    if total <= EPS:
        raise KernelError("||...|| of a zero-norm (vacuum) state")
    return total**0.5


def bind_prepare_selection(
    context: EvaluatorContext, joint: Joint, name: str, expr: Call
) -> Joint:
    if len(expr.args) != 1:
        raise KernelError("prepare_selection requires (n)")
    n_raw = context._evaluate_value(expr.args[0], {})
    if type(n_raw) is not int:
        raise KernelError("prepare_selection n must be Int")
    if n_raw < 1:
        raise KernelError("prepare_selection requires n >= 1")
    patterns = itertools.product((0, 1), repeat=n_raw)
    return joint.bind_split(name, {pattern: 1.0 / (2**n_raw) for pattern in patterns})


def bind_inner(
    context: EvaluatorContext, joint: Joint, name: str, expr: Call
) -> Joint:
    if len(expr.args) != 2 or not all(isinstance(arg, Var) for arg in expr.args):
        raise KernelError("inner requires two state variables")
    available = joint.worlds[0].assign if joint.worlds else {}
    left = context._resolve_scientific_binding(expr.args[0].name, available)
    right = context._resolve_scientific_binding(expr.args[1].name, available)
    left_amplitudes = joint.amplitude_marginal(left)
    right_amplitudes = joint.amplitude_marginal(right)
    keys = set(left_amplitudes) | set(right_amplitudes)
    overlap = sum(
        left_amplitudes.get(key, 0j).conjugate() * right_amplitudes.get(key, 0j)
        for key in keys
    )
    value = float(overlap.real) if abs(overlap.imag) < 1e-10 else float(abs(overlap))
    return Joint(worlds=_coalesce([World(assign={name: value}, amp=1 + 0j)]))


def materialize_outer(
    context: EvaluatorContext, joint: Joint, expr: Call
) -> DenseMatrixOp:
    if len(expr.args) != 2 or not all(isinstance(arg, Var) for arg in expr.args):
        raise KernelError("outer requires two state variables")
    psi = expr.args[0].name
    phi = expr.args[1].name
    psi_amplitudes = joint.amplitude_marginal(psi)
    phi_amplitudes = joint.amplitude_marginal(phi)
    labels = sorted(set(psi_amplitudes) | set(phi_amplitudes) | {0, 1})
    if any(label not in (0, 1) for label in labels):
        raise KernelError("outer MVP requires qubit computational labels {0,1}")
    matrix = [
        [
            psi_amplitudes.get(row, 0j) * phi_amplitudes.get(column, 0j).conjugate()
            for column in (0, 1)
        ]
        for row in (0, 1)
    ]
    return DenseMatrixOp(matrix=matrix, n_qubits=1)
