"""Invocation frame services for the evaluator runtime."""

from __future__ import annotations

from fractions import Fraction
from typing import Any

from ...ast_nodes import AssignStmt, Call, Measure, OpVar, ReturnStmt, Snapshot, StateBind, Var
from ..joint import Joint
from .context import EvaluatorContext
from .errors import KernelError


def _joint_coord_names(context: EvaluatorContext, joint: Joint) -> set[str]:
    names: set[str] = set()
    for world in joint.worlds:
        names.update(world.assign)
    return names


def _trace_out_dead_fn_locals(
    context: EvaluatorContext,
    joint: Joint,
    pre_live: set[str],
    result_names: list[str],
) -> Joint:
    keep = pre_live | set(result_names)
    for coord in sorted(_joint_coord_names(context, joint) - keep):
        joint = joint.trace_out(coord)
    return joint


def _restore_operators(context: EvaluatorContext, saved: dict[str, Any]) -> None:
    operators = context._operator_environment()
    operators.clear()
    operators.update(saved)


def restore_frame(
    context: EvaluatorContext,
    receiver: Any,
    frame_units: dict[str, str],
) -> None:
    """Restore the receiver frame through the evaluator context boundary."""
    context._restore_frame(receiver, frame_units)


def bind_method(
        context,
        joint: Joint,
        name: str,
        receiver: Any,
        method: Any,
        args: list[Any],
        *,
        logs: list[str] | None = None,
        inspect_out: Any | None = None,
    ) -> Joint:
        """Run a measure-free method and bind its explicit result."""
        if method.name == "init":
            raise KernelError("`init` is a constructor; call `ClassName(…)` instead")
        if len(args) != len(method.params):
            raise KernelError(
                f"`{method.name}` expects {len(method.params)} args, got {len(args)}"
            )
        prev_this = context._current_receiver()
        prev_frame = context._frame_environment()["units"]
        context._set_current_receiver(receiver)
        context._set_frame_units({})
        # Local classical env for params + this fields
        local: dict[str, Any] = dict(receiver.fields)
        for param, arg in zip(method.params, args):
            if isinstance(arg, Var) and arg.name in context._object_environment():
                obj = context._object_environment()[arg.name]
                # struct: copy-on-pass; class: reference
                if type(obj).__name__ == "StructValue":
                    local[param.name] = context._copy_runtime_value(obj)
                else:
                    local[param.name] = obj
            else:
                v, unit = context._evaluate_value_with_unit(arg, {})
                if type(v).__name__ == "StructValue":
                    local[param.name] = context._copy_runtime_value(v)
                else:
                    local[param.name] = v
                if unit is not None:
                    context._frame_environment()["units"][param.name] = unit

        last_val: Any = None
        last_unit: str | None = None
        result_joint: Joint | None = None
        try:
            for stmt in method.body.stmts:
                if isinstance(stmt, Measure):
                    raise KernelError(
                        f"`measure` forbidden inside method `{method.name}`"
                    )
                if isinstance(stmt, Snapshot):
                    raise KernelError(
                        f"`snapshot` forbidden inside method `{method.name}`"
                    )
                if isinstance(stmt, ReturnStmt):
                    continue
                if isinstance(stmt, AssignStmt):
                    context._execute_assignment(stmt, local)
                    # Reflect this.fields into local for subsequent reads of bare names
                    local.update(receiver.fields)
                    continue
                if isinstance(stmt, StateBind):
                    if stmt.ty is not None and stmt.ty.name == "Operator":
                        if len(stmt.names) != 1:
                            raise KernelError("Operator bind expects a single name")
                        # LISS-0413: resolve the same way the top-level
                        # Operator StateBind dispatch does -- unlike this
                        # method's own Operator-typed *parameters|struct
                        # fields the runtime evaluator already resolves,
                        # a *local* Operator bind here previously stored
                        # its raw AST, so a struct-field coefficient
                        # (`weights.a * X`) failed with `cannot compile
                        # operator node OpAttr`.
                        context._operator_environment()[stmt.names[0]] = context._resolve_operator(
                            stmt.expr
                        )
                        continue
                    # Evaluate RHS with this/local; bind into local (classical methods)
                    if len(stmt.names) != 1:
                        raise KernelError(
                            f"method `{method.name}` binds must be single-name"
                        )
                    # Prefer classical eval of method bodies (physics helpers)
                    try:
                        val, unit = context._evaluate_value_with_unit(stmt.expr, local)
                        local[stmt.names[0]] = val
                        last_val = val
                        last_unit = unit
                        context._put_unit(
                            context._frame_environment()["units"], stmt.names[0], unit
                        )
                        if (
                            stmt.ty is not None
                            and stmt.ty.name not in {"State", "Operator", "Delta"}
                        ):
                            try:
                                if isinstance(val, Fraction):
                                    context._scalar_environment()[stmt.names[0]] = val
                                else:
                                    context._scalar_environment()[stmt.names[0]] = float(val)
                                context._put_unit(
                                    context._scalar_units_environment(), stmt.names[0], unit
                                )
                            except (TypeError, ValueError):
                                pass
                    except KernelError:
                        # Quantum bind path (rare in methods)
                        joint = context._bind_names(
                            joint,
                            stmt.names,
                            stmt.expr,
                            logs=logs,
                            inspect_out=inspect_out,
                        )
                        last_val = None
                        last_unit = None
                else:
                    raise KernelError(
                        f"unsupported stmt in method `{method.name}`: "
                        f"{type(stmt).__name__}"
                    )
            if method.body.result is not None:
                try:
                    # Methods such as `advance()` return a classical field
                    # projection after updating the receiver.  Resolve that
                    # expression in the method-local environment first;
                    # quantum expressions still use the Joint binder.
                    value, unit = context._evaluate_value_with_unit(
                        method.body.result, local
                    )
                    last_unit = unit
                    result_joint = joint.bind_const(name, value)
                    try:
                        if isinstance(value, Fraction):
                            context._scalar_environment()[name] = value
                        else:
                            context._scalar_environment()[name] = float(value)
                        context._put_unit(context._scalar_units_environment(), name, unit)
                    except (TypeError, ValueError):
                        pass
                except KernelError:
                    result_joint = context._bind(
                        joint,
                        name,
                        method.body.result,
                        logs=logs,
                        inspect_out=inspect_out,
                    )
        finally:
            context._set_current_receiver(prev_this)
            context._set_frame_units(prev_frame)

        if result_joint is not None:
            return result_joint

        if method.body.result is None:
            raise KernelError(
                f"method `{method.name}` has no explicit return"
            )
        if last_val is None:
            return context._bind(
                joint,
                name,
                method.body.result,
                logs=logs,
                inspect_out=inspect_out,
            )
        if last_unit is not None:
            context._scalar_units_environment()[name] = last_unit
        return joint.bind_const(name, last_val)



def bind_user_function(
        context,
        joint: Joint,
        names: list[str],
        expr: Call,
        fun: Any,
        *,
        logs: list[str] | None = None,
        inspect_out: Any | None = None,
    ) -> Joint:
        """Compatibility body for the extracted user-function frame."""
        if len(expr.args) != len(fun.params):
            raise KernelError(
                f"`{fun.name}` expects {len(fun.params)} args, got {len(expr.args)}"
            )
        pre_live = _joint_coord_names(context, joint)
        saved_operators = dict(context._operator_environment())
        # Bind arguments onto parameter coordinates
        for param, arg in zip(fun.params, expr.args):
            if param.ty is not None and param.ty.name == "Operator":
                context._operator_environment()[param.name] = context._resolve_operator( arg)
                continue
            if isinstance(arg, Var) and arg.name == param.name:
                continue
            if isinstance(arg, Var):
                src = arg.name
                try:
                    joint = joint.bind_pushforward(
                        param.name, lambda a, s=src: a[s]
                    )
                except KeyError as exc:
                    raise KernelError(
                        f"RUNTIME_ERROR: unbound coordinate `{src}` while "
                        f"binding parameter `{param.name}` of `{fun.name}`"
                    ) from exc
            else:
                # ADR 0130: KetLit / Dirac / nested State-forming exprs.
                joint = context._bind(
                    joint,
                    param.name,
                    arg,
                    logs=logs,
                    inspect_out=inspect_out,
                )

        for stmt in fun.body.stmts:
            if isinstance(stmt, Measure):
                raise KernelError(
                f"`measure` is forbidden inside library fn `{fun.name}` "
                    "(measure-free module boundary)"
                )
            if isinstance(stmt, Snapshot):
                raise KernelError(
                    f"`snapshot` is forbidden inside library fn `{fun.name}`"
                )
            if isinstance(stmt, ReturnStmt):
                continue
            if isinstance(stmt, StateBind):
                if stmt.ty is not None and stmt.ty.name == "Operator":
                    if len(stmt.names) != 1:
                        raise KernelError("Operator bind expects a single name")
                    # LISS-0413: same fix as _bind_method -- a local
                    # Operator bind inside a library fn previously stored
                    # its raw AST unresolved (unlike this same function's
                    # own Operator-typed *parameter* binding a few lines
                    # above, which already resolves).
                    context._operator_environment()[stmt.names[0]] = context._resolve_operator(
                        stmt.expr
                    )
                    continue
                joint = context._bind_names(
                    joint,
                    stmt.names,
                    stmt.expr,
                    logs=logs,
                    inspect_out=inspect_out,
                )
            else:
                raise KernelError(
                    f"unsupported stmt in fn `{fun.name}`: {type(stmt).__name__}"
                )

        if fun.body.result is not None:
            if len(names) == 0:
                # A result with no destination is still evaluated for its
                # state-preserving transform, but has no visible coordinate.
                result_joint = _trace_out_dead_fn_locals(context, joint, pre_live, names)
                _restore_operators(context, saved_operators)
                return result_joint
            # Operator-returning functions bind their result in the operator
            # environment, not as a Joint coordinate.  A library function
            # commonly ends with `return local_operator`; routing that
            # OpVar through the ordinary value binder loses the callee-local
            # operator and raises `cannot bind expr OpVar` at the caller.
            if (
                len(names) == 1
                and fun.return_type is not None
                and fun.return_type.name == "Operator"
                and isinstance(fun.body.result, (Var, OpVar))
                and fun.body.result.name in context._operator_environment()
            ):
                context._operator_environment()[names[0]] = context._operator_environment()[fun.body.result.name]
                returned_operator = context._operator_environment()[names[0]]
                _restore_operators(context, saved_operators)
                context._operator_environment()[names[0]] = returned_operator
                return joint
            result_joint = context._bind_names(
                joint,
                names,
                fun.body.result,
                logs=logs,
                inspect_out=inspect_out,
            )
            if "Uncompute" in fun.effects:
                for n in names:
                    context._require_uncompute_zero(result_joint, n)
            result_joint = _trace_out_dead_fn_locals(context, result_joint, pre_live, names)
            _restore_operators(context, saved_operators)
            return result_joint

        # Legacy state-transformer path: project parameter coordinates into
        # the caller's bind names when no explicit result expression exists.
        if len(names) == 0:
            result_joint = _trace_out_dead_fn_locals(context, joint, pre_live, names)
            _restore_operators(context, saved_operators)
            return result_joint
        if len(names) == len(fun.params):
            updates = {
                n: (lambda a, p=p.name: a[p])
                for n, p in zip(names, fun.params)
            }
            result_joint = joint.bind_multi(updates)
            result_joint = _trace_out_dead_fn_locals(context, result_joint, pre_live, names)
            _restore_operators(context, saved_operators)
            return result_joint
        if len(names) == 1 and len(fun.params) == 1:
            p = fun.params[0].name
            result_joint = joint.bind_pushforward(names[0], lambda a, pn=p: a[pn])
            result_joint = _trace_out_dead_fn_locals(context, result_joint, pre_live, names)
            _restore_operators(context, saved_operators)
            return result_joint
        raise KernelError(
            f"`{fun.name}` result arity {len(fun.params)} != bind arity {len(names)}"
        )
