"""Classical function and method call evaluation services."""

from __future__ import annotations

from typing import Any, Mapping, MutableMapping, Protocol

from ...ast_nodes import (
    AssignStmt,
    Attr,
    Call,
    FunDecl,
    Measure,
    ReturnStmt,
    Snapshot,
    StateBind,
    Var,
)
from ...stdlib import math_ops
from .classical import evaluate_value
from .errors import KernelError


class ClassicalCallContext(Protocol):
    """Live evaluator-owned environments and callbacks needed by call evaluation."""

    funs: Mapping[str, Any]
    classes: Mapping[str, Any]
    structs: Mapping[str, Any]
    objects: MutableMapping[str, Any]
    scalars: MutableMapping[str, Any]
    scalar_units: MutableMapping[str, str]

    def _resolve_receiver_instance(self, expr: Any) -> Any: ...

    def _current_receiver(self) -> Any: ...

    def _set_current_receiver(self, value: Any) -> None: ...

    def _frame_environment(self) -> Mapping[str, Any]: ...

    def _set_frame_units(self, value: dict[str, str]) -> None: ...

    def _call_local_units_environment(self) -> MutableMapping[str, str] | None: ...

    def _set_call_local_units_environment(
        self, value: MutableMapping[str, str] | None
    ) -> None: ...

    def _eval_value_with_unit(
        self, expr: Any, assign: dict[str, Any]
    ) -> tuple[Any, str | None]: ...

    def _execute_assignment(
        self, stmt: Any, local: dict[str, Any] | None = None
    ) -> None: ...


_CLASSICAL_HEADS = {
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


def _is_class_instance(value: Any) -> bool:
    """Recognize the evaluator-owned class DTO without importing its owner."""
    return type(value).__name__ == "ClassInstance"


def _class_method(
    context: ClassicalCallContext, class_name: str, method_name: str
) -> Any:
    """Resolve a declared method while preserving evaluator diagnostics."""
    class_decl = context.classes.get(class_name) or context.classes.get(
        class_name.split(".")[-1]
    )
    if class_decl is None:
        raise KernelError(f"unknown class `{class_name}`")

    method = next(
        (
            candidate
            for candidate in class_decl.methods
            if candidate.name == method_name
        ),
        None,
    )
    if method is None:
        raise KernelError(f"class `{class_name}` has no method `{method_name}`")
    return method


def _return_expression(body: Any) -> Any | None:
    """Select an explicit return, falling back to the body's result value."""
    return next(
        (
            statement.expr
            for statement in body.stmts
            if isinstance(statement, ReturnStmt)
        ),
        body.result,
    )


def eval_classical_call(
    context: ClassicalCallContext,
    expr: Call,
    assign: dict[str, Any] | None = None,
) -> Any:
    """Evaluate a pure classical Call as a classical value (ADR 0179)."""
    if isinstance(expr.callee, Var):
        if math_ops.known_math_op(expr.callee.name):
            if len(expr.args) != 1:
                raise KernelError(
                    f"`{expr.callee.name}` expects exactly 1 argument, "
                    f"got {len(expr.args)}"
                )
            arg_value = evaluate_value(context, expr.args[0], assign or {})
            return math_ops.apply_math(expr.callee.name, arg_value)

        function = context.funs.get(expr.callee.name)
        if function is None:
            raise KernelError(
                "call cannot be classical value in Phase 2.2 value context"
            )
        if function.return_type is None or (
            function.return_type.name not in _CLASSICAL_HEADS
            and function.return_type.name not in context.structs
        ):
            raise KernelError(
                "call cannot be classical value in Phase 2.2 value context: "
                f"`{function.name}` is not a pure classical-returning fn"
            )
        return eval_classical_user_fun(context, function, expr, assign)

    if isinstance(expr.callee, Attr):
        return eval_classical_method_call(context, expr, _CLASSICAL_HEADS)
    raise KernelError("call cannot be classical value in Phase 2.2 value context")


def eval_classical_method_call(
    context: ClassicalCallContext,
    expr: Call,
    classical_heads: set[str],
) -> Any:
    """Evaluate ``recv.method(…)`` returning a classical head (ADR 0179)."""
    callee = expr.callee
    if not isinstance(callee, Attr):
        raise KernelError("call cannot be classical value in Phase 2.2 value context")
    method_name = callee.name
    receiver_expr = callee.obj
    instance = context._resolve_receiver_instance(receiver_expr)
    if instance is None:
        raise KernelError(
            "classical method call requires a bound receiver "
            f"(got `{type(receiver_expr).__name__}`)"
        )
    if not _is_class_instance(instance):
        raise KernelError(
            f"classical method `{method_name}` requires a class instance"
        )

    method = _class_method(context, instance.class_name, method_name)
    if method.return_type is None or method.return_type.name not in classical_heads:
        raise KernelError(
            "call cannot be classical value in Phase 2.2 value context: "
            f"`{method_name}` is not a pure classical-returning method"
        )
    if len(expr.args) != len(method.params):
        raise KernelError(
            f"`{method_name}` expects {len(method.params)} args, "
            f"got {len(expr.args)}"
        )

    previous_receiver = context._current_receiver()
    context._set_current_receiver(instance)
    try:
        local: dict[str, Any] = dict(instance.fields)
        for parameter, argument in zip(method.params, expr.args):
            if isinstance(argument, Var) and argument.name in context.objects:
                local[parameter.name] = context.objects[argument.name]
            elif isinstance(argument, Var) and argument.name in context.scalars:
                local[parameter.name] = context.scalars[argument.name]
            else:
                local[parameter.name] = evaluate_value(context, argument, {})
        for statement in method.body.stmts:
            if isinstance(statement, AssignStmt):
                context._execute_assignment(statement, local)
                local.update(instance.fields)
        result = _return_expression(method.body)
        if result is None:
            raise KernelError(f"method `{method_name}` has no return")
        return evaluate_value(context, result, local)
    finally:
        context._set_current_receiver(previous_receiver)


def eval_classical_user_fun(
    context: ClassicalCallContext,
    function: FunDecl,
    expr: Call,
    assign: dict[str, Any] | None = None,
) -> Any:
    """Evaluate a classical-returning library function as a value."""
    value, _unit = eval_classical_user_fun_value(context, function, expr, assign)
    return value


def eval_classical_user_fun_value(
    context: ClassicalCallContext,
    function: FunDecl,
    expr: Call,
    assign: dict[str, Any] | None = None,
) -> tuple[Any, str | None]:
    """Evaluate a classical function with object/scalar args and local units."""
    if len(expr.args) != len(function.params):
        raise KernelError(
            f"`{function.name}` expects {len(function.params)} args, "
            f"got {len(expr.args)}"
        )

    parent = assign if assign is not None else {}
    local: dict[str, Any] = {}
    local_units: dict[str, str] = {}
    previous_receiver = context._current_receiver()
    previous_frame_units = context._frame_environment()["units"]
    previous_call_units = context._call_local_units_environment()
    context._set_frame_units({})
    context._set_call_local_units_environment(local_units)
    try:
        for parameter, argument in zip(function.params, expr.args):
            if isinstance(argument, Var) and argument.name in parent:
                local[parameter.name] = parent[argument.name]
                if (
                    previous_call_units is not None
                    and argument.name in previous_call_units
                ):
                    local_units[parameter.name] = previous_call_units[argument.name]
                elif argument.name in context.scalar_units:
                    local_units[parameter.name] = context.scalar_units[argument.name]
            elif isinstance(argument, Var) and argument.name in context.objects:
                local[parameter.name] = context.objects[argument.name]
            elif isinstance(argument, Var) and argument.name in context.scalars:
                local[parameter.name] = context.scalars[argument.name]
                if argument.name in context.scalar_units:
                    local_units[parameter.name] = context.scalar_units[argument.name]
            else:
                value, unit = context._eval_value_with_unit(argument, parent)
                local[parameter.name] = value
                if unit is not None:
                    local_units[parameter.name] = unit

        for value in local.values():
            if _is_class_instance(value):
                context._set_current_receiver(value)
                break

        frame_units = context._frame_environment()["units"]
        for statement in function.body.stmts:
            if isinstance(statement, ReturnStmt):
                continue
            if isinstance(statement, AssignStmt):
                context._execute_assignment(statement, local)
                continue
            if isinstance(statement, StateBind) and len(statement.names) == 1:
                value, unit = context._eval_value_with_unit(statement.expr, local)
                local[statement.names[0]] = value
                if unit is not None:
                    local_units[statement.names[0]] = unit
                    frame_units[statement.names[0]] = unit
                continue
            if isinstance(statement, (Measure, Snapshot)):
                raise KernelError(
                    f"`measure`/`snapshot` forbidden inside classical fn "
                    f"`{function.name}`"
                )

        result = _return_expression(function.body)
        if result is None:
            raise KernelError(f"`{function.name}` has no return")
        if isinstance(result, Call) and isinstance(result.callee, Attr):
            receiver_expr = result.callee.obj
            if isinstance(receiver_expr, Var) and receiver_expr.name in local:
                receiver = local[receiver_expr.name]
                context._set_current_receiver(receiver)
                if not _is_class_instance(receiver):
                    raise KernelError(
                        f"`{function.name}` receiver is not a class instance"
                    )
                method = _class_method(
                    context, receiver.class_name, result.callee.name
                )
                method_result = _return_expression(method.body)
                if method_result is None:
                    raise KernelError(
                        f"method `{result.callee.name}` has no return"
                    )
                return (
                    evaluate_value(context, method_result, dict(receiver.fields)),
                    None,
                )
        return context._eval_value_with_unit(result, local)
    finally:
        context._set_current_receiver(previous_receiver)
        context._set_frame_units(previous_frame_units)
        context._set_call_local_units_environment(previous_call_units)


__all__ = [
    "ClassicalCallContext",
    "eval_classical_call",
    "eval_classical_method_call",
    "eval_classical_user_fun",
    "eval_classical_user_fun_value",
]
