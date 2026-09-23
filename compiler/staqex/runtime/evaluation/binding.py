"""Binder dispatch successor for the evaluator runtime.

This module owns only the dispatcher control flow.  Runtime state and family
implementations remain on the ``EvaluatorContext`` supplied by the facade.
"""

from __future__ import annotations

from typing import Any

from ...ast_nodes import (
    BinOp,
    BlockExpr,
    Call,
    Coin,
    Dirac,
    EvolveExpr,
    Expr,
    Hole,
    Inspect,
    KetLit,
    KetSumBinder,
    LitBool,
    LitFloat,
    LitInt,
    LitString,
    NormExpr,
    OpBinder,
    Pipe,
    SetComprehension,
    SuperposeExpr,
    TensorExpr,
    TupleExpr,
    UnitConvert,
    Vacuum,
    Var,
    WhenExpr,
    Attr,
)
from ...measure_sink_port import MeasureSinkPort
from ...stdlib.io_ops import format_marginal_table
from ...scientific_vocabulary import resolve_scientific_binding
from ..joint import Joint
from .calls import bind_call
from .context import EvaluatorContext
from .errors import KernelDiagnosticError, KernelError


def bind_names(
    context: EvaluatorContext,
    joint: Joint,
    names: list[str],
    expr: Expr,
    *,
    logs: list[str] | None = None,
    inspect_out: MeasureSinkPort | None = None,
) -> Joint:
    """Dispatch a multi-name binder while preserving legacy ordering."""
    if isinstance(expr, EvolveExpr):
        return context._bind_evolve(joint, names, expr)
    if isinstance(expr, TensorExpr):
        return context._bind_tensor(joint, names, expr)
    if isinstance(expr, Call) and isinstance(expr.callee, Var):
        if expr.callee.name == "tensor":
            if len(expr.args) != 2:
                raise KernelError("tensor requires exactly two arguments")
            return context._bind_tensor(
                joint,
                names,
                TensorExpr(left=expr.args[0], right=expr.args[1], span=expr.span),
            )
        if any(isinstance(a, Hole) for a in expr.args):
            if len(names) != 1:
                raise KernelError("Partial bind expects a single name")
            return bind_call(context, joint, names[0], expr)
        objects = context._object_environment()
        if expr.callee.name in objects and type(objects[expr.callee.name]).__name__ == "PartialValue":
            if len(names) != 1:
                raise KernelError("Partial completion expects a single name")
            return bind_call(context, joint, names[0], expr)
        fun = context._function_environment().get(expr.callee.name)
        if fun is not None:
            classical_heads = {
                "Float", "Int", "Bool", "Mass", "Time", "Length",
                "Current", "Temperature", "Energy", "Frequency",
                "Stiffness", "Momentum",
            }
            if (
                len(names) == 1
                and fun.return_type is not None
                and fun.return_type.name in classical_heads
            ):
                value, unit = context._evaluate_value_with_unit(expr, {})
                context._put_unit(context._scalar_environment(), names[0], unit)
                context._scalar_environment()[names[0]] = value
                return joint.bind_const(names[0], value)
            return context._bind_user_fun(
                joint, names, expr, fun, logs=logs, inspect_out=inspect_out
            )
    if isinstance(expr, TupleExpr):
        if len(expr.items) != len(names):
            raise KernelError(
                f"tuple arity {len(expr.items)} != bind arity {len(names)}"
            )
        for name, item in zip(names, expr.items):
            joint = bind(context, joint, name, item, logs=logs, inspect_out=inspect_out)
        return joint
    if (
        isinstance(expr, Call)
        and isinstance(expr.callee, Var)
        and expr.callee.name == "apply"
        and len(expr.args) >= 2
        and len(names) == len(expr.args) - 1
        and all(isinstance(a, Var) for a in expr.args[1:])
    ):
        return context._bind_apply_multi(joint, names, expr)
    if (
        isinstance(expr, Call)
        and isinstance(expr.callee, Var)
        and expr.callee.name == "cnot"
        and len(expr.args) == 2
        and len(names) == 2
        and all(isinstance(a, Var) for a in expr.args)
    ):
        return context._bind_cnot_multi(joint, names, expr)
    if len(names) != 1:
        raise KernelError(f"cannot bind {len(names)} names to {type(expr).__name__}")
    out = bind(context, joint, names[0], expr, logs=logs, inspect_out=inspect_out)
    context._verify_static_uncompute_bind(out, names[0], expr)
    return out


def bind(
    context: EvaluatorContext,
    joint: Joint,
    name: str,
    expr: Expr,
    *,
    logs: list[str] | None = None,
    inspect_out: MeasureSinkPort | None = None,
) -> Joint:
    """Dispatch one binder without importing or constructing ``Evaluator``."""
    if isinstance(expr, Inspect):
        marg = context._expr_marginal(joint, expr.expr)
        text = format_marginal_table(marg, label=expr.label)
        if inspect_out is not None:
            inspect_out.write(text)
        if logs is not None:
            logs.append(f"inspect:{expr.label or ''}:{marg}")
        return bind(context, joint, name, expr.expr, logs=logs, inspect_out=inspect_out)
    if isinstance(expr, Coin):
        return joint.bind_split(name, {0: 0.5, 1: 0.5})
    if isinstance(expr, Vacuum):
        return Joint.empty()
    if isinstance(expr, KetLit):
        return context._bind_ket(joint, name, expr)
    if isinstance(expr, KetSumBinder):
        return context._bind_ket_sum_binder(joint, name, expr)
    if isinstance(expr, NormExpr):
        return joint.bind_const(name, context._compute_norm(joint, expr.state))
    if isinstance(expr, SetComprehension):
        return joint.bind_const(name, context._evaluate_set_comprehension(expr, {}))
    if isinstance(expr, OpBinder):
        return joint.bind_pushforward(
            name, lambda a: context._evaluate_classical_op_binder(expr, a)
        )
    if isinstance(expr, Dirac):
        if context._is_closed(expr.arg):
            return joint.bind_const(name, context._evaluate_nested_value(expr.arg, {}))
        return joint.bind_pushforward(
            name, lambda a: context._evaluate_nested_value(expr.arg, a)
        )
    if isinstance(expr, (LitInt, LitFloat, LitBool, LitString)):
        return joint.bind_const(name, context._lit(expr))
    if isinstance(expr, Var):
        return joint.bind_pushforward(
            name, lambda a: a[resolve_scientific_binding(expr.name, a)]
        )
    if isinstance(expr, BinOp) and expr.op == "*":
        lhs_state = context._is_state_producing_bind_expr(expr.lhs)
        rhs_state = context._is_state_producing_bind_expr(expr.rhs)
        if lhs_state != rhs_state:
            state_expr = expr.lhs if lhs_state else expr.rhs
            scalar_expr = expr.rhs if lhs_state else expr.lhs
            return context._bind_scaled_state(joint, name, state_expr, scalar_expr)
    if isinstance(expr, BinOp) and isinstance(expr.rhs, NormExpr) and expr.op == "/":
        return context._bind_state_divided_by_norm(joint, name, expr.lhs, expr.rhs)
    if isinstance(expr, BinOp):
        return joint.bind_pushforward(
            name, lambda a: context._evaluate_nested_value(expr, a)
        )
    if isinstance(expr, Attr):
        return joint.bind_pushforward(
            name, lambda a: context._evaluate_nested_value(expr, a)
        )
    if isinstance(expr, UnitConvert):
        return joint.bind_pushforward(
            name, lambda a: context._evaluate_nested_value(expr, a)
        )
    if isinstance(expr, WhenExpr):
        return context._bind_when(joint, name, expr)
    if isinstance(expr, SuperposeExpr):
        raise KernelDiagnosticError(
            "COHERENT_EXECUTION_UNSUPPORTED",
            "`superpose` type-checks but coherent amplitude/phase execution "
            "is not yet implemented in the Static Kernel",
            line=expr.span.line,
            col=expr.span.col,
        )
    if isinstance(expr, Call):
        return bind_call(context, joint, name, expr)
    if isinstance(expr, Pipe):
        fused = context._try_bind_fused_unary_pipe(
            joint, name, expr, logs=logs, inspect_out=inspect_out
        )
        if fused is not None:
            return fused
        if isinstance(expr.rhs, Call):
            return bind_call(context, joint, name, context._piped_call(expr))
        if isinstance(expr.rhs, Var):
            if isinstance(expr.lhs, TupleExpr):
                partial = context._object_environment().get(expr.rhs.name)
                if type(partial).__name__ == "PartialValue":
                    need = sum(1 for slot in partial.slots if slot is None)
                    if need == len(expr.lhs.items):
                        synthetic = Call(
                            callee=expr.rhs,
                            args=list(expr.lhs.items),
                            span=expr.span,
                        )
                        return bind_call(context, joint, name, synthetic)
            synthetic = Call(callee=expr.rhs, args=[expr.lhs], span=expr.span)
            return bind_call(context, joint, name, synthetic)
        raise KernelError(
            "PIPE_CALLABLE_ERROR: pipeline right-hand side must be a function call "
            "or unary fn name"
        )
    if isinstance(expr, EvolveExpr):
        return context._bind_evolve(joint, [name], expr)
    if isinstance(expr, BlockExpr):
        return context._bind_block_expr(joint, name, expr)
    if isinstance(expr, TensorExpr):
        raise KernelError("tensor product requires tuple bind `(a, b) = left *|* right`")
    raise KernelError(f"cannot bind expr {type(expr).__name__}")
