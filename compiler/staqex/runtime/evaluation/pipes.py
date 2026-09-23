"""Pipe, block-expression, and polynomial fusion services."""

from __future__ import annotations

import math
from typing import Any

from ...ast_nodes import (
    BinOp,
    BlockExpr,
    Call,
    Expr,
    ExprStmt,
    ForEachStmt,
    FunDecl,
    Hole,
    LitFloat,
    LitInt,
    Measure,
    Pipe,
    ReturnStmt,
    Snapshot,
    StateBind,
    TupleExpr,
    Var,
)
from ..joint import Joint
from .context import EvaluatorContext
from .errors import KernelError


def bind_block_expr(
    context: EvaluatorContext, joint: Joint, name: str, expr: BlockExpr
) -> Joint:
    """Evaluate a bare block and trace out temporary coordinates."""
    pre_live = context._joint_coord_names(joint)
    for let in expr.lets:
        if isinstance(let.expr, Call):
            joint = context._bind(joint, let.name, let.expr)
        else:
            joint = joint.bind_pushforward(
                let.name,
                lambda assignment, value=let.expr: context._evaluate_value(
                    value, assignment
                ),
            )
    if isinstance(expr.result, Call):
        joint = context._bind(joint, name, expr.result)
    else:
        joint = joint.bind_pushforward(
            name,
            lambda assignment, value=expr.result: context._evaluate_value(
                value, assignment
            ),
        )
    return context._trace_out_dead_fn_locals(joint, pre_live, [name])


def try_bind_fused_unary_pipe(
    context: EvaluatorContext,
    joint: Joint,
    name: str,
    expr: Pipe,
    *,
    logs: list[str] | None = None,
    inspect_out: Any | None = None,
) -> Joint | None:
    """Fuse an eligible pure unary pipe chain into one Joint pass."""
    base, stages = flatten_pipe(expr)
    if stages and isinstance(base, TupleExpr) and isinstance(stages[0], Call):
        base = piped_call(Pipe(lhs=base, rhs=stages[0], span=expr.span))
        stages = stages[1:]
    if len(stages) < 2:
        return None
    resolved: list[tuple[FunDecl, list[Expr | None]]] = []
    for stage in stages:
        item = resolve_fuse_stage(context, stage)
        if item is None:
            return None
        resolved.append(item)

    joint = context._bind(joint, name, base, logs=logs, inspect_out=inspect_out)
    if all(len(slots) == 1 and slots[0] is None for _fun, slots in resolved):
        funs = [fun for fun, _slots in resolved]
        returns = [fuse_simple_return(fun) for fun in funs]
        if all(result is not None for result in returns):
            composed = compose_poly_pipe(
                funs, [result for result in returns if result is not None]
            )
            if composed is not None:
                if len(composed) <= 2:
                    scale = composed[1] if len(composed) > 1 else 0.0
                    bias = composed[0] if composed else 0.0
                    context._set_fusion_evidence((scale, bias), None)
                else:
                    context._set_fusion_evidence(None, tuple(composed))
                return joint.bind_pushforward(
                    name,
                    lambda assignment, coeffs=composed, source=name: eval_poly(
                        coeffs, assignment[source]
                    ),
                )

    context._set_fusion_evidence(None, None)
    for fun, slots in resolved:
        result = fuse_simple_return(fun)
        assert result is not None
        joint = joint.bind_pushforward(
            name,
            lambda assignment, function=fun, bound=slots, expression=result,
            source=name: eval_fused_stage(
                context, assignment, function, bound, expression, source
            ),
        )
    return joint


def resolve_fuse_stage(
    context: EvaluatorContext, stage: Expr
) -> tuple[FunDecl, list[Expr | None]] | None:
    """Resolve a bare unary function, one-hole call, or one-hole partial."""
    functions = context._function_environment()
    objects = context._object_environment()
    if isinstance(stage, Var):
        fun = functions.get(stage.name)
        if (
            fun is not None
            and len(fun.params) == 1
            and not fun.effects
            and fuse_simple_return(fun) is not None
        ):
            return fun, [None]
        partial = objects.get(stage.name)
        if type(partial).__name__ != "PartialValue":
            return None
        fun = functions.get(partial.fun_name)
        if (
            fun is None
            or fun.effects
            or len(fun.params) != len(partial.slots)
            or fuse_simple_return(fun) is None
            or sum(slot is None for slot in partial.slots) != 1
        ):
            return None
        return fun, list(partial.slots)
    if isinstance(stage, Call) and isinstance(stage.callee, Var):
        if sum(isinstance(argument, Hole) for argument in stage.args) != 1:
            return None
        fun = functions.get(stage.callee.name)
        if (
            fun is None
            or fun.effects
            or len(fun.params) != len(stage.args)
            or fuse_simple_return(fun) is None
        ):
            return None
        return fun, [None if isinstance(arg, Hole) else arg for arg in stage.args]
    return None


def eval_fused_stage(
    context: EvaluatorContext,
    assignment: dict[str, Any],
    fun: FunDecl,
    slots: list[Expr | None],
    result: Expr,
    source: str,
) -> Any:
    environment = dict(assignment)
    for parameter, slot in zip(fun.params, slots):
        environment[parameter.name] = (
            assignment[source]
            if slot is None
            else context._evaluate_value(slot, assignment)
        )
    return context._evaluate_value(result, environment)


def compose_affine_pipe(
    funs: list[FunDecl], returns: list[Expr]
) -> tuple[float, float] | None:
    poly = compose_poly_pipe(funs, returns)
    if poly is None or len(poly) > 2:
        return None
    if len(poly) == 1:
        return (0.0, poly[0])
    return (poly[1], poly[0])


def compose_poly_pipe(
    funs: list[FunDecl], returns: list[Expr]
) -> list[float] | None:
    coeffs = [0.0, 1.0]
    for fun, result in zip(funs, returns):
        parsed = parse_poly(result, fun.params[0].name)
        if parsed is None:
            return None
        coeffs = compose_poly(parsed, coeffs)
        if coeffs is None or len(coeffs) > 8:
            return None
    return coeffs


def eval_poly(coeffs: list[float], value: Any) -> Any:
    accumulator: Any = 0.0
    for coefficient in reversed(coeffs):
        accumulator = accumulator * value + coefficient
    return accumulator


def compose_poly(outer: list[float], inner: list[float]) -> list[float] | None:
    if not is_finite_poly(outer) or not is_finite_poly(inner):
        return None
    result = [0.0]
    power = [1.0]
    for coefficient in outer:
        for index, value in enumerate(power):
            if index >= len(result):
                result.extend([0.0] * (index + 1 - len(result)))
            result[index] += coefficient * value
            if not math.isfinite(result[index]):
                return None
        power = mul_poly(power, inner)
        if power is None:
            return None
    return trim_exact_zero_tail(result)


def mul_poly(a: list[float], b: list[float]) -> list[float] | None:
    if not is_finite_poly(a) or not is_finite_poly(b):
        return None
    result = [0.0] * (len(a) + len(b) - 1)
    for i, left in enumerate(a):
        for j, right in enumerate(b):
            result[i + j] += left * right
            if not math.isfinite(result[i + j]):
                return None
    return result


def add_poly(
    a: list[float], b: list[float], sign: float = 1.0
) -> list[float] | None:
    if not is_finite_poly(a) or not is_finite_poly(b) or not math.isfinite(sign):
        return None
    result = [0.0] * max(len(a), len(b))
    for i in range(len(result)):
        result[i] = (a[i] if i < len(a) else 0.0) + sign * (
            b[i] if i < len(b) else 0.0
        )
        if not math.isfinite(result[i]):
            return None
    return trim_exact_zero_tail(result)


def is_finite_poly(coeffs: list[float]) -> bool:
    return all(math.isfinite(coefficient) for coefficient in coeffs)


def trim_exact_zero_tail(coeffs: list[float]) -> list[float]:
    while len(coeffs) > 1 and coeffs[-1] == 0.0:
        coeffs.pop()
    return coeffs


def parse_poly(expr: Expr, param: str) -> list[float] | None:
    if isinstance(expr, Var):
        return [0.0, 1.0] if expr.name == param else None
    if isinstance(expr, LitInt):
        return [float(expr.value)]
    if isinstance(expr, LitFloat):
        value = float(expr.value)
        return [value] if math.isfinite(value) else None
    if isinstance(expr, BinOp):
        left = parse_poly(expr.lhs, param)
        right = parse_poly(expr.rhs, param)
        if left is None or right is None:
            return None
        if expr.op == "+":
            return add_poly(left, right)
        if expr.op == "-":
            return add_poly(left, right, -1.0)
        if expr.op == "*":
            return mul_poly(left, right)
    return None


def parse_affine(expr: Expr, param: str) -> tuple[float, float] | None:
    poly = parse_poly(expr, param)
    if poly is None or len(poly) > 2:
        return None
    if len(poly) == 1:
        return (0.0, poly[0])
    return (poly[1], poly[0])


def flatten_pipe(expr: Pipe) -> tuple[Expr, list[Expr]]:
    stages: list[Expr] = []
    current: Expr = expr
    while isinstance(current, Pipe):
        stages.append(current.rhs)
        current = current.lhs
    stages.reverse()
    return current, stages


def fuse_simple_return(fun: FunDecl) -> Expr | None:
    for statement in fun.body.stmts:
        if isinstance(statement, ReturnStmt):
            return statement.expr
        if isinstance(statement, (Measure, Snapshot, StateBind, ForEachStmt, ExprStmt)):
            return None
    return fun.body.result


def piped_call(expr: Pipe) -> Call:
    if not isinstance(expr.rhs, Call):
        raise KernelError(
            "PIPE_CALLABLE_ERROR: pipeline right-hand side must be a function call"
        )
    rhs = expr.rhs
    hole_indexes = [
        index for index, argument in enumerate(rhs.args) if isinstance(argument, Hole)
    ]
    if (
        hole_indexes
        and isinstance(expr.lhs, TupleExpr)
        and len(expr.lhs.items) == len(hole_indexes)
    ):
        items = iter(expr.lhs.items)
        return Call(
            callee=rhs.callee,
            args=[next(items) if isinstance(argument, Hole) else argument for argument in rhs.args],
            span=rhs.span,
        )
    if hole_indexes:
        filled = False
        args: list[Expr] = []
        for argument in rhs.args:
            if not filled and isinstance(argument, Hole):
                args.append(expr.lhs)
                filled = True
            else:
                args.append(argument)
        return Call(callee=rhs.callee, args=args, span=rhs.span)
    return Call(callee=rhs.callee, args=[expr.lhs, *rhs.args], span=rhs.span)
