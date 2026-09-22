"""Object-field assignment services for the evaluator runtime."""

from __future__ import annotations

from typing import Any

from ...ast_nodes import Attr, Var
from .context import EvaluatorContext
from .errors import KernelError


def execute_assignment(
    context: EvaluatorContext,
    statement: Any,
    local: dict[str, Any] | None = None,
) -> None:
    target = statement.target
    if not isinstance(target, Attr):
        raise KernelError("assignment target must be `obj.field` or `this.field`")
    environment = local if local is not None else {}
    value, unit = context._evaluate_value_with_unit(statement.value, environment)

    if isinstance(target.obj, Var) and target.obj.name == "this":
        receiver = context._current_receiver()
        if receiver is None:
            raise KernelError("`this` is only valid inside a class method")
        if target.name not in receiver.mutable and not context._is_initializing():
            raise KernelError(
                f"IMMUTABLE_ASSIGNMENT_ERROR: field `{target.name}` is not "
                "`var` (cannot assign through `this`)"
            )
        receiver.fields[target.name] = value
        context._put_unit(receiver.field_units, target.name, unit)
        return

    objects = context._object_environment()
    if isinstance(target.obj, Var) and target.obj.name in objects:
        obj = objects[target.obj.name]
        if type(obj).__name__ == "StructValue":
            raise KernelError(
                f"IMMUTABLE_ASSIGNMENT_ERROR: struct `{obj.struct_name}` "
                "fields are immutable"
            )
        if type(obj).__name__ == "ClassInstance":
            if target.name not in obj.mutable:
                raise KernelError(
                    f"IMMUTABLE_ASSIGNMENT_ERROR: field `{target.name}` is not `var`"
                )
            obj.fields[target.name] = value
            context._put_unit(obj.field_units, target.name, unit)
            return
    raise KernelError("assignment target is not a mutable object field")
