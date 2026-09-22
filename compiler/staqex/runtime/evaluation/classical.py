"""Classical/value evaluation services for the evaluator runtime.

The service owns recursive value dispatch and unit/attribute lookup. Runtime
state and DTO identity remain owned by the ``Evaluator`` context callbacks.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Any

from ...ast_nodes import (
    Attr,
    BinOp,
    Call,
    Coin,
    Dirac,
    Expr,
    LitBool,
    LitFloat,
    LitInt,
    LitString,
    OpBinder,
    UnitConvert,
    Vacuum,
    Var,
    WhenExpr,
)
from ...dimensions import (
    UNIT_AFFINE_TO_CANONICAL,
    UNIT_SCALE_TO_CANONICAL,
    UNIT_TABLE,
    from_canonical_magnitude,
    to_canonical_magnitude,
    unit_canonical,
)
from ...scientific_vocabulary import resolve_scientific_binding
from .context import EvaluatorContext
from .errors import KernelError


def apply_value_op(op: str, left: Any, right: Any) -> Any:
    """Apply the evaluator's classical value operator semantics."""
    if op == "+":
        return left + right
    if op == "-":
        return left - right
    if op == "*":
        return left * right
    if op == "/":
        if right == 0 or right == 0.0:
            return ("Err", "DivByZero")
        if isinstance(left, bool) or isinstance(right, bool):
            return left / right
        if isinstance(left, Fraction) or isinstance(right, Fraction):
            return Fraction(left) / Fraction(right)
        if isinstance(left, int) and isinstance(right, int):
            return Fraction(left, right)
        return left / right
    if op == "^":
        return left**right
    if op == "==":
        return left == right
    if op == "!=":
        return left != right
    if op == "<":
        return left < right
    if op == "<=":
        return left <= right
    if op == ">":
        return left > right
    if op == ">=":
        return left >= right
    if op == "&&":
        return bool(left) and bool(right)
    if op == "||":
        return bool(left) or bool(right)
    if op == "Implies":
        return (not bool(left)) or bool(right)
    raise KernelError(f"unknown op {op}")


def _is_runtime_type(value: Any, type_name: str) -> bool:
    return type(value).__name__ == type_name


def _is_object_value(value: Any) -> bool:
    return _is_runtime_type(value, "ClassInstance") or _is_runtime_type(
        value, "StructValue"
    )


def _is_enum_value(value: Any) -> bool:
    return _is_runtime_type(value, "EnumValue")


def _lit(expr: Any) -> Any:
    if isinstance(expr, LitInt):
        return expr.value
    if isinstance(expr, LitFloat):
        return expr.value
    if isinstance(expr, LitBool):
        return expr.value
    if isinstance(expr, LitString):
        return expr.value
    raise KernelError("not a literal")


def evaluate_value(
    context: EvaluatorContext, expr: Any, assign: dict[str, Any]
) -> Any:
    """Evaluate one classical value without owning evaluator state."""
    if isinstance(expr, (LitInt, LitFloat, LitBool, LitString)):
        return _lit(expr)
    if isinstance(expr, Var):
        return _evaluate_var(context, expr, assign)
    if isinstance(expr, Coin):
        raise KernelError(
            "coin() cannot be evaluated as a classical value; bind via state"
        )
    if isinstance(expr, Vacuum):
        raise KernelError("vacuum() is not a classical value")
    if isinstance(expr, Dirac):
        return evaluate_value(context, expr.arg, assign)
    if isinstance(expr, BinOp):
        return _evaluate_binary(context, expr, assign)
    if isinstance(expr, UnitConvert):
        return evaluate_unit_convert(context, expr, assign)
    if isinstance(expr, Attr):
        return _evaluate_attribute(context, expr, assign)
    if isinstance(expr, WhenExpr):
        return _evaluate_when(context, expr, assign)
    if isinstance(expr, Call):
        return _evaluate_call(context, expr, assign)
    if isinstance(expr, OpBinder):
        return context._evaluate_classical_op_binder(expr, assign)
    raise KernelError(f"cannot evaluate {type(expr).__name__} as value")


def _evaluate_var(
    context: EvaluatorContext, expr: Var, assign: dict[str, Any]
) -> Any:
    name = resolve_scientific_binding(expr.name, assign)
    if name in assign:
        return assign[name]
    scalars = context._scalar_environment()
    if expr.name in scalars:
        return scalars[expr.name]
    raise KernelError(f"unbound variable `{expr.name}`")


def _evaluate_binary(
    context: EvaluatorContext, expr: BinOp, assign: dict[str, Any]
) -> Any:
    if expr.op in {"+", "-"}:
        value, _unit = evaluate_value_with_unit(context, expr, assign)
        return value
    return apply_value_op(
        expr.op,
        evaluate_value(context, expr.lhs, assign),
        evaluate_value(context, expr.rhs, assign),
    )


def _evaluate_attribute(
    context: EvaluatorContext, expr: Attr, assign: dict[str, Any]
) -> Any:
    if isinstance(expr.obj, (LitInt, LitFloat)) and expr.name in UNIT_TABLE:
        return float(expr.obj.value)
    if _is_math_constant(expr):
        from ...stdlib.prelude import PRELUDE_CONSTANTS

        return PRELUDE_CONSTANTS[expr.name]

    qualified = context._expr_qualname(expr.obj)
    enums = context._enum_environment()
    if qualified is not None and qualified in enums:
        return _evaluate_enum_variant(context, enums[qualified], expr.name)
    if isinstance(expr.obj, Var) and expr.obj.name == "this":
        return _evaluate_receiver_field(context, expr.name)
    if isinstance(expr.obj, Var) and expr.obj.name in assign:
        return _evaluate_bound_field(assign[expr.obj.name], expr.name)

    objects = context._object_environment()
    if isinstance(expr.obj, Var) and expr.obj.name in objects:
        return _evaluate_bound_field(objects[expr.obj.name], expr.name)
    instance = evaluate_value(context, expr.obj, assign)
    return _evaluate_bound_field(instance, expr.name)


def _is_math_constant(expr: Attr) -> bool:
    return (
        isinstance(expr.obj, Var)
        and expr.obj.name == "Math"
        and expr.name in {"pi", "sqrt2", "inv_sqrt2"}
    )


def _evaluate_enum_variant(context: EvaluatorContext, enum: Any, name: str) -> Any:
    if name not in enum.variants:
        raise KernelError(f"enum `{enum.qualified_name}` has no variant `{name}`")
    return context._make_enum_value(enum.qualified_name, name)


def _evaluate_receiver_field(context: EvaluatorContext, name: str) -> Any:
    receiver = context._current_receiver()
    if receiver is None:
        raise KernelError("`this` is only valid inside a class method")
    if name not in receiver.fields:
        raise KernelError(f"class `{receiver.class_name}` has no field `{name}`")
    return receiver.fields[name]


def _evaluate_bound_field(instance: Any, name: str) -> Any:
    if _is_object_value(instance):
        return _field_value(instance, name)
    if _is_enum_value(instance):
        raise KernelError("enum values have no fields")
    raise KernelError(f"cannot evaluate attribute `.{name}` on {instance!r}")


def _evaluate_when(
    context: EvaluatorContext, expr: WhenExpr, assign: dict[str, Any]
) -> Any:
    control = evaluate_value(context, expr.ctrl, assign)
    for arm in expr.arms:
        if not arm.is_else and arm.pat == control:
            return evaluate_value(context, arm.body, assign)
    for arm in expr.arms:
        if arm.is_else:
            return evaluate_value(context, arm.body, assign)
    raise KernelError("mix: no matching arm")


def _evaluate_call(
    context: EvaluatorContext, expr: Call, assign: dict[str, Any]
) -> Any:
    qualified = context._expr_qualname(expr.callee)
    if qualified is not None and qualified in context._struct_environment():
        return context._construct_struct(qualified, expr, assign)
    if qualified is not None and qualified in context._class_environment():
        return context._construct_instance(qualified, expr)
    return context._evaluate_classical_call(expr, assign)


def evaluate_classical_value(
    context: EvaluatorContext, expr: Any, assign: dict[str, Any]
) -> Any:
    """Compatibility name for the classical value successor."""
    return evaluate_value(context, expr, assign)


def evaluate_unit_convert(
    context: EvaluatorContext, expr: UnitConvert, assign: dict[str, Any]
) -> float:
    raw, source = evaluate_value_with_unit(context, expr.expr, assign)
    raw = float(raw)
    if source is None:
        if isinstance(expr.expr, Attr) and expr.expr.name in (
            set(UNIT_SCALE_TO_CANONICAL) | set(UNIT_AFFINE_TO_CANONICAL)
        ):
            source = expr.expr.name
        else:
            raise KernelError("unit conversion requires a known source unit suffix")
    target = expr.target_unit
    if source in UNIT_SCALE_TO_CANONICAL and target in UNIT_SCALE_TO_CANONICAL:
        return _convert_scaled_unit(raw, source, target)
    if source in UNIT_AFFINE_TO_CANONICAL and target in UNIT_AFFINE_TO_CANONICAL:
        return _convert_affine_unit(raw, source, target)
    raise KernelError(f"unit `{source}` → `{target}` is not in the scale or affine set")


def _convert_scaled_unit(raw: float, source: str, target: str) -> float:
    src_canon, src_factor = UNIT_SCALE_TO_CANONICAL[source]
    tgt_canon, tgt_factor = UNIT_SCALE_TO_CANONICAL[target]
    if src_canon != tgt_canon:
        raise KernelError(
            f"cannot convert `{source}` to `{target}` "
            f"(canonical {src_canon} vs {tgt_canon})"
        )
    return raw * (src_factor / tgt_factor)


def _convert_affine_unit(raw: float, source: str, target: str) -> float:
    src_canon, src_scale, src_offset = UNIT_AFFINE_TO_CANONICAL[source]
    tgt_canon, tgt_scale, tgt_offset = UNIT_AFFINE_TO_CANONICAL[target]
    if src_canon != tgt_canon:
        raise KernelError(
            f"cannot convert `{source}` to `{target}` "
            f"(affine canonical {src_canon} vs {tgt_canon})"
        )
    canonical = raw * src_scale + src_offset
    return (canonical - tgt_offset) / tgt_scale


def evaluate_value_with_unit(
    context: EvaluatorContext, expr: Any, assign: dict[str, Any]
) -> tuple[Any, str | None]:
    if isinstance(expr, Attr):
        if isinstance(expr.obj, (LitInt, LitFloat)) and expr.name in UNIT_TABLE:
            return float(expr.obj.value), expr.name
        field_unit = attr_field_unit(context, expr, assign)
        if field_unit is not None or attr_is_object_field(context, expr, assign):
            return evaluate_value(context, expr, assign), field_unit
    if isinstance(expr, UnitConvert):
        return evaluate_unit_convert(context, expr, assign), expr.target_unit
    if isinstance(expr, Var):
        name = resolve_scientific_binding(expr.name, assign)
        if name in assign:
            return assign[name], context._unit_for(name)
        scalars = context._scalar_environment()
        if expr.name in scalars:
            return scalars[expr.name], context._scalar_unit(expr.name)
    if isinstance(expr, BinOp) and expr.op in {"+", "-"}:
        return _evaluate_unit_binary(context, expr, assign)
    return evaluate_value(context, expr, assign), None


def _evaluate_unit_binary(
    context: EvaluatorContext, expr: BinOp, assign: dict[str, Any]
) -> tuple[Any, str | None]:
    left, left_unit = evaluate_value_with_unit(context, expr.lhs, assign)
    right, right_unit = evaluate_value_with_unit(context, expr.rhs, assign)
    if left_unit is not None and right_unit is not None and left_unit != right_unit:
        left_canon, right_canon = unit_canonical(left_unit), unit_canonical(right_unit)
        if left_canon is not None and left_canon == right_canon:
            return _promote_and_restore(expr, left, right, left_unit, right_unit)
    output_unit = left_unit if left_unit == right_unit else (left_unit or right_unit)
    if left_unit and right_unit and left_unit != right_unit:
        output_unit = None
    return apply_value_op(expr.op, left, right), output_unit


def _promote_and_restore(
    expr: BinOp,
    left: Any,
    right: Any,
    left_unit: str,
    right_unit: str,
) -> tuple[Any, str]:
    left_value, _ = to_canonical_magnitude(float(left), left_unit)
    right_value, _ = to_canonical_magnitude(float(right), right_unit)
    result = apply_value_op(expr.op, left_value, right_value)
    try:
        restored = from_canonical_magnitude(float(result), left_unit)
    except KeyError as error:
        raise KernelError(
            f"cannot restore display unit `{left_unit}` after promote"
        ) from error
    return restored, left_unit


def attr_host(
    context: EvaluatorContext, expr: Attr, assign: dict[str, Any] | None = None
) -> Any:
    if isinstance(expr.obj, Var) and expr.obj.name == "this":
        return context._current_receiver()
    if isinstance(expr.obj, Var) and assign and expr.obj.name in assign:
        instance = assign[expr.obj.name]
        if _is_object_value(instance):
            return instance
    objects = context._object_environment()
    if isinstance(expr.obj, Var) and expr.obj.name in objects:
        instance = objects[expr.obj.name]
        if _is_object_value(instance):
            return instance
    return None


def resolve_receiver_instance(
    context: EvaluatorContext,
    receiver_expr: Expr,
    assign: dict[str, Any] | None = None,
) -> Any:
    objects = context._object_environment()
    if isinstance(receiver_expr, Var) and receiver_expr.name in objects:
        return objects[receiver_expr.name]
    if isinstance(receiver_expr, Var):
        return None
    try:
        candidate = evaluate_value(context, receiver_expr, assign or {})
    except KernelError:
        return None
    return candidate if _is_object_value(candidate) else None


def attr_is_object_field(
    context: EvaluatorContext, expr: Attr, assign: dict[str, Any] | None = None
) -> bool:
    host = attr_host(context, expr, assign)
    return host is not None and expr.name in host.fields


def attr_field_unit(
    context: EvaluatorContext, expr: Attr, assign: dict[str, Any] | None = None
) -> str | None:
    host = attr_host(context, expr, assign)
    return None if host is None else host.field_units.get(expr.name)


def _field_value(instance: Any, name: str) -> Any:
    fields = instance.fields
    type_name = getattr(instance, "class_name", getattr(instance, "struct_name", "value"))
    if name not in fields:
        raise KernelError(f"`{type_name}` has no field `{name}`")
    return fields[name]


def resolve_attribute(
    context: EvaluatorContext, expr: Any, assign: dict[str, Any] | None = None
) -> Any:
    return evaluate_value(context, expr, assign or {})


def construct_instance(context: EvaluatorContext, class_name: str, expr: Any) -> Any:
    from .constructors import construct_instance as successor

    return successor(context, class_name, expr)


def construct_struct(
    context: EvaluatorContext,
    struct_name: str,
    expr: Any,
    assign: dict[str, Any] | None = None,
) -> Any:
    from .constructors import construct_struct as successor

    return successor(context, struct_name, expr, assign)
