"""Class, struct, and initializer construction services."""

from __future__ import annotations

from typing import Any

from ...ast_nodes import AssignStmt, Call, Measure, ReturnStmt, Snapshot, StateBind, Var
from .context import EvaluatorContext
from .errors import KernelError


def construct_instance(
    context: EvaluatorContext, class_name: str, expr: Any
) -> Any:
    classes = context._class_environment()
    cls = classes.get(class_name)
    if cls is None:
        raise KernelError(f"unknown class `{class_name}`")
    if not isinstance(expr, Call):
        raise KernelError(
            f"class `{class_name}` instance requires `{cls.qualified_name}(…)`"
        )
    qualified = context._expr_qualname(expr.callee)
    if qualified is not None and qualified not in classes:
        raise KernelError(f"unknown constructor `{qualified}()`")

    init = next((method for method in cls.methods if method.name == "init"), None)
    if expr.args and init is None:
        raise KernelError(
            f"`{cls.qualified_name}(…)` has no `fn init`; "
            "use defaults or declare `fn init(...)`"
        )
    if init is not None and len(expr.args) != len(init.params):
        raise KernelError(
            f"`{cls.qualified_name}(…)` / `init` expects {len(init.params)} args, "
            f"got {len(expr.args)}"
        )

    fields: dict[str, Any] = {}
    mutable: set[str] = set()
    for field_bind in cls.fields:
        if len(field_bind.names) != 1:
            raise KernelError("class field must be a single name")
        fields[field_bind.names[0]] = context._evaluate_nested_value(field_bind.expr, {})
    for member in cls.members:
        if member.default is not None:
            fields[member.name] = context._evaluate_nested_value(member.default, {})
        if member.mutable:
            mutable.add(member.name)

    instance = context._make_class_instance(cls.qualified_name, fields, mutable)
    if init is not None:
        run_init(context, instance, init, list(expr.args))
    else:
        for member in cls.members:
            if member.name not in instance.fields:
                raise KernelError(
                    f"class `{cls.qualified_name}` member `{member.name}` needs a "
                    "default or `fn init(...)`"
                )
    for member in cls.members:
        if member.name not in instance.fields:
            raise KernelError(
                f"class `{cls.qualified_name}` field `{member.name}` was not "
                "initialized by `fn init`"
            )
    return instance


def run_init(
    context: EvaluatorContext, receiver: Any, init: Any, args: list[Any]
) -> None:
    previous_receiver = context._current_receiver()
    previous_initializing = context._is_initializing()
    previous_units = context._frame_environment()["units"]
    context._set_current_receiver(receiver)
    context._set_initializing(True)
    context._set_frame_units({})
    local: dict[str, Any] = dict(receiver.fields)
    try:
        for parameter, argument in zip(init.params, args):
            objects = context._object_environment()
            if isinstance(argument, Var) and argument.name in objects:
                local[parameter.name] = context._copy_runtime_value(objects[argument.name])
            else:
                value, unit = context._evaluate_value_with_unit(argument, {})
                local[parameter.name] = context._copy_runtime_value(value)
                if unit is not None:
                    context._frame_environment()["units"][parameter.name] = unit
        for statement in init.body.stmts:
            if isinstance(statement, (Measure, Snapshot)):
                raise KernelError("`measure`/`snapshot` forbidden inside `init`")
            if isinstance(statement, ReturnStmt):
                raise KernelError("`init` cannot return a value")
            if isinstance(statement, AssignStmt):
                context._execute_assignment(statement, local)
                local.update(receiver.fields)
                continue
            if isinstance(statement, StateBind):
                if len(statement.names) != 1:
                    raise KernelError("`init` binds must be single-name")
                local[statement.names[0]] = context._evaluate_nested_value(
                    statement.expr, local
                )
                continue
            raise KernelError(
                f"unsupported stmt in `init`: {type(statement).__name__}"
            )
    finally:
        context._set_current_receiver(previous_receiver)
        context._set_initializing(previous_initializing)
        context._set_frame_units(previous_units)


def construct_struct(
    context: EvaluatorContext,
    struct_name: str,
    expr: Any,
    assign: dict[str, Any] | None = None,
) -> Any:
    structs = context._struct_environment()
    struct = structs.get(struct_name)
    if struct is None:
        raise KernelError(f"unknown struct `{struct_name}`")
    if not isinstance(expr, Call):
        raise KernelError(f"struct `{struct_name}` requires `{struct.qualified_name}(…)`")
    qualified = context._expr_qualname(expr.callee)
    if qualified is not None and qualified not in structs:
        raise KernelError(f"unknown struct constructor `{qualified}()`")

    fields: dict[str, Any] = {}
    field_units: dict[str, str] = {}
    kwargs = getattr(expr, "kwargs", None) or []
    if kwargs and expr.args:
        raise KernelError(
            f"`{struct.qualified_name}`: cannot mix positional and named fields"
        )
    if kwargs:
        by_name = {key: value for key, value in kwargs}
        for member in struct.fields:
            if member.name not in by_name:
                if member.default is None:
                    raise KernelError(
                        f"struct `{struct.qualified_name}` missing field `{member.name}`"
                    )
                value, unit = context._evaluate_value_with_unit(member.default, {})
            else:
                value, unit = eval_struct_arg(context, by_name[member.name], assign)
            fields[member.name] = value
            context._put_unit(field_units, member.name, unit)
        extra = set(by_name) - {member.name for member in struct.fields}
        if extra:
            raise KernelError(
                f"struct `{struct.qualified_name}` unknown fields: "
                f"{', '.join(sorted(extra))}"
            )
    elif not expr.args:
        for member in struct.fields:
            if member.default is None:
                raise KernelError(
                    f"struct `{struct.qualified_name}` field `{member.name}` "
                    "requires a constructor argument"
                )
            value, unit = context._evaluate_value_with_unit(member.default, {})
            fields[member.name] = value
            context._put_unit(field_units, member.name, unit)
    else:
        if len(expr.args) != len(struct.fields):
            raise KernelError(
                f"`{struct.qualified_name}(…)` expects {len(struct.fields)} args, "
                f"got {len(expr.args)}"
            )
        for member, argument in zip(struct.fields, expr.args):
            value, unit = eval_struct_arg(context, argument, assign)
            fields[member.name] = value
            context._put_unit(field_units, member.name, unit)
    return context._make_struct_value(struct.qualified_name, fields, field_units)


def eval_struct_arg(
    context: EvaluatorContext, argument: Any, assign: dict[str, Any] | None = None
) -> tuple[Any, str | None]:
    if isinstance(argument, Var) and assign is not None and argument.name in assign:
        return context._copy_runtime_value(assign[argument.name]), None
    objects = context._object_environment()
    if isinstance(argument, Var) and argument.name in objects:
        return context._copy_runtime_value(objects[argument.name]), None
    return context._evaluate_value_with_unit(argument, assign or {})
