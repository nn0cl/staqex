"""Legacy AST binding for control mixtures, using the live evaluator context."""

from __future__ import annotations

import cmath
from typing import Any

from ...ast_nodes import Coin, Expr, KetLit, LitBool, LitFloat, LitInt, Var, WhenExpr
from ..joint import EPS, Joint, World, _coalesce
from ..quantum_ops import ket_support
from .context import EvaluatorContext
from .errors import KernelError
from .values import evaluate_value


def bind_when(
    context: EvaluatorContext, joint: Joint, name: str, expr: WhenExpr
) -> Joint:
    """Bind a legacy ``WhenExpr`` without taking ownership of evaluator state."""

    if joint.is_vacuum():
        return Joint.empty()

    out_worlds: list[World] = []
    for world in joint.worlds:
        controls = _ctrl_masses(context, expr.ctrl, world.assign)
        for control_value, control_probability in controls.items():
            if control_probability <= EPS:
                continue

            arm_body = _matching_arm_body(context, expr, control_value)
            if arm_body is None:
                continue

            amplitude = world.amp * cmath.sqrt(control_probability)
            if isinstance(arm_body, Coin):
                _append_coin_worlds(out_worlds, world, name, amplitude)
            elif isinstance(arm_body, KetLit):
                _append_ket_worlds(out_worlds, world, name, amplitude, arm_body)
            else:
                value = evaluate_value(context, arm_body, world.assign)
                out_worlds.append(
                    World(
                        assign={**world.assign, name: value},
                        amp=amplitude,
                        coord_phase=dict(world.coord_phase),
                    )
                )

    if not out_worlds:
        return Joint.empty()
    return Joint(worlds=_coalesce(out_worlds))


def _matching_arm_body(
    context: EvaluatorContext, expr: WhenExpr, control_value: Any
) -> Any | None:
    # A matching arm takes precedence over ``else`` regardless of source order.
    for arm in expr.arms:
        if not arm.is_else and _pat_match(
            arm.pat, control_value, context._enum_value_type
        ):
            return arm.body

    for arm in expr.arms:
        if arm.is_else:
            return arm.body
    return None


def _append_coin_worlds(
    out_worlds: list[World], world: World, name: str, amplitude: complex
) -> None:
    for value in (0, 1):
        out_worlds.append(
            World(
                assign={**world.assign, name: value},
                amp=amplitude * cmath.sqrt(0.5),
                coord_phase=dict(world.coord_phase),
            )
        )


def _append_ket_worlds(
    out_worlds: list[World],
    world: World,
    name: str,
    amplitude: complex,
    arm_body: KetLit,
) -> None:
    try:
        pairs = ket_support(arm_body.label)
    except ValueError as error:
        raise KernelError(str(error)) from error

    for value, ket_amplitude in pairs:
        output_amplitude = amplitude * ket_amplitude
        if abs(output_amplitude) ** 2 > EPS:
            out_worlds.append(
                World(
                    assign={**world.assign, name: value},
                    amp=output_amplitude,
                    coord_phase=dict(world.coord_phase),
                )
            )


def _ctrl_masses(
    context: EvaluatorContext, control: Expr, assignment: dict[str, Any]
) -> dict[Any, float]:
    if isinstance(control, Coin):
        return {0: 0.5, 1: 0.5}
    if isinstance(control, Var):
        if control.name in assignment:
            return {assignment[control.name]: 1.0}
        # Classical enum/object values and scalars remain Evaluator-owned.
        if control.name in context.objects:
            return {context.objects[control.name]: 1.0}
        if control.name in context.scalars:
            return {context.scalars[control.name]: 1.0}
        raise KernelError(
            f"when control `{control.name}` is not bound in this world"
        )
    if isinstance(control, (LitInt, LitFloat, LitBool)):
        return {context._lit(control): 1.0}
    value = evaluate_value(context, control, assignment)
    return {value: 1.0}


def _pat_match(pat: Any, control: Any, enum_value_type: type[Any]) -> bool:
    if pat == control:
        return True
    if isinstance(pat, (int, float)) and isinstance(control, (int, float)):
        return float(pat) == float(control)
    # LISS-0225: bare variant identifiers match EnumValue controls.
    if isinstance(control, enum_value_type):
        if isinstance(pat, str) and pat == control.variant:
            return True
        if isinstance(pat, Var) and pat.name == control.variant:
            return True
    return False
