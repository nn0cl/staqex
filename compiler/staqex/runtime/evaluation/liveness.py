"""Pure coordinate liveness and automatic Trace-Out algorithms.

The Evaluator remains the sole owner of mutable runtime state. This module
only analyzes existing AST values and transforms the supplied ``Joint``.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ...ast_nodes import (
    Attr,
    BinOp,
    BlockExpr,
    Call,
    Coin,
    Dirac,
    EvolveExpr,
    Expr,
    ExprStmt,
    Hole,
    Inspect,
    KetLit,
    KetSumBinder,
    Lambda,
    LitBool,
    LitFloat,
    LitInt,
    LitString,
    ListExpr,
    Measure,
    NormExpr,
    OpAttr,
    OpBin,
    OpBinder,
    OpCall,
    OpGridQuad,
    OpHop,
    OpIdentity,
    OpIndexed,
    OpLit,
    OpNumber,
    OpPauli,
    OpPow,
    OpQuadrature,
    OpVar,
    Pipe,
    SetComprehension,
    Snapshot,
    StateBind,
    SuperposeExpr,
    TensorExpr,
    TupleExpr,
    UnaryNot,
    UnitConvert,
    Vacuum,
    Var,
    WhenExpr,
)
from ..joint import Joint


def joint_coord_names(joint: Joint) -> set[str]:
    """Return the coordinate names appearing in a joint support."""
    names: set[str] = set()
    for world in joint.worlds:
        names.update(world.assign)
    return names


def trace_out_dead_fn_locals(
    joint: Joint, pre_live: set[str], result_names: list[str]
) -> Joint:
    """Drop function-local coordinates except incoming names and results."""
    keep = pre_live | set(result_names)
    for coord in sorted(joint_coord_names(joint) - keep):
        joint = joint.trace_out(coord)
    return joint


def main_interproc_trace_eligible(stmts: list[Any]) -> bool:
    """ADR 0158: skip mains with Inspect or Snapshot observations."""
    for stmt in stmts:
        if isinstance(stmt, Snapshot):
            return False
        if isinstance(stmt, StateBind) and expr_has_inspect(stmt.expr):
            return False
        if isinstance(stmt, Measure) and expr_has_inspect(stmt.expr):
            return False
        if isinstance(stmt, ExprStmt) and expr_has_inspect(stmt.expr):
            return False
    return True


def stmts_live_vars(stmts: list[Any]) -> set[str]:
    """Return the free-variable union of the supplied subsequent statements."""
    live: set[str] = set()
    for stmt in stmts:
        if isinstance(stmt, StateBind):
            live |= expr_free_vars(stmt.expr)
        elif isinstance(stmt, Measure):
            live |= expr_free_vars(stmt.expr)
            live |= set(stmt.tracing_out)
        elif isinstance(stmt, Snapshot):
            live |= expr_free_vars(stmt.expr)
        elif isinstance(stmt, ExprStmt):
            live |= expr_free_vars(stmt.expr)
    return live


def trace_out_dead_caller_coords(
    joint: Joint,
    live_out: set[str],
    result_names: list[str],
) -> Joint:
    """Drop caller coordinates absent from live-out and result names."""
    keep = live_out | set(result_names)
    for coord in sorted(joint_coord_names(joint) - keep):
        joint = joint.trace_out(coord)
    return joint


def expr_has_inspect(expr: Expr) -> bool:
    """Return whether an expression tree contains an Inspect operation."""
    if isinstance(expr, Inspect):
        return True
    if isinstance(expr, BinOp):
        return expr_has_inspect(expr.lhs) or expr_has_inspect(expr.rhs)
    if isinstance(expr, Call):
        return expr_has_inspect(expr.callee) or any(
            expr_has_inspect(arg) for arg in expr.args
        )
    if isinstance(expr, (WhenExpr, SuperposeExpr)):
        if expr_has_inspect(expr.ctrl):
            return True
        return any(expr_has_inspect(arm.body) for arm in expr.arms)
    if isinstance(expr, Pipe):
        return expr_has_inspect(expr.lhs) or expr_has_inspect(expr.rhs)
    if isinstance(expr, Attr):
        return expr_has_inspect(expr.obj)
    if isinstance(expr, (TupleExpr, ListExpr)):
        return any(expr_has_inspect(item) for item in expr.items)
    if isinstance(expr, BlockExpr):
        return any(expr_has_inspect(let.expr) for let in expr.lets) or expr_has_inspect(
            expr.result
        )
    if isinstance(expr, Dirac):
        return expr_has_inspect(expr.arg)
    if isinstance(expr, UnitConvert):
        return expr_has_inspect(expr.expr)
    if isinstance(expr, Lambda):
        return expr_has_inspect(expr.body)
    return False


def _walk_binder_free_vars(
    node: Any,
    names: set[str],
    walk: Callable[[Any], None],
) -> bool:
    """Visit binder inputs and remove the bound name after its body."""
    if isinstance(node, SetComprehension):
        domain = node.domain
        walk(getattr(domain, "start", None))
        walk(getattr(domain, "end", None))
        walk(getattr(domain, "width", None))
        for condition in node.conditions:
            walk(condition)
        names.discard(node.variable)
        return True

    if isinstance(node, OpBinder):
        domain = node.domain
        walk(domain)
        walk(getattr(domain, "start", None))
        walk(getattr(domain, "end", None))
        walk(getattr(domain, "width", None))
        walk(node.guard)
        walk(node.body)
        names.discard(node.variable)
        return True

    return False


def _walk_operator_free_vars(
    node: Any,
    names: set[str],
    walk: Callable[[Any], None],
) -> bool:
    """Visit operator AST nodes; return whether the node was handled."""
    if isinstance(node, OpVar):
        names.add(node.name)
        return True
    if isinstance(node, OpIndexed):
        walk(node.base)
        walk(node.index)
        return True
    if isinstance(node, (OpBin, OpPow, OpCall)):
        if isinstance(node, OpBin):
            walk(node.lhs)
            walk(node.rhs)
        elif isinstance(node, OpPow):
            walk(node.base)
        else:
            for arg in node.args:
                walk(arg)
        return True
    if isinstance(node, OpAttr):
        walk(node.obj)
        return True
    if isinstance(
        node,
        (OpLit, OpPauli, OpHop, OpNumber, OpQuadrature, OpGridQuad, OpIdentity),
    ):
        return True
    return False


def _walk_expression_free_vars(
    node: Any,
    names: set[str],
    walk: Callable[[Any], None],
) -> None:
    """Visit child expressions for the non-binder expression AST variants."""
    if isinstance(node, BinOp):
        walk(node.lhs)
        walk(node.rhs)
    elif isinstance(node, UnaryNot):
        walk(node.expr)
    elif isinstance(node, Call):
        walk(node.callee)
        for arg in node.args:
            walk(arg)
    elif isinstance(node, (WhenExpr, SuperposeExpr)):
        walk(node.ctrl)
        for arm in node.arms:
            walk(arm.body)
    elif isinstance(node, Pipe):
        walk(node.lhs)
        walk(node.rhs)
    elif isinstance(node, Lambda):
        walk(node.body)
        names.discard(node.param)
    elif isinstance(node, Attr):
        walk(node.obj)
    elif isinstance(node, Inspect):
        walk(node.expr)
    elif isinstance(node, UnitConvert):
        walk(node.expr)
    elif isinstance(node, (TupleExpr, ListExpr)):
        for item in node.items:
            walk(item)
    elif isinstance(node, BlockExpr):
        for let in node.lets:
            walk(let.expr)
        walk(node.result)
    elif isinstance(node, Dirac):
        walk(node.arg)
    elif isinstance(node, EvolveExpr):
        for term in node.seeds:
            walk(term)
        if node.body is not None:
            for let in node.body.lets:
                walk(let.expr)
            walk(node.body.result)
        if isinstance(node.times, Expr):
            walk(node.times)
        if node.duration is not None:
            walk(node.duration)
        if node.hamiltonian is not None:
            walk(node.hamiltonian)
    elif isinstance(node, TensorExpr):
        walk(node.left)
        walk(node.right)


def expr_free_vars(expr: Expr) -> set[str]:
    """Collect free variable names from the existing expression AST."""
    names: set[str] = set()

    def walk(node: Any) -> None:
        if node is None:
            return
        if isinstance(node, Var):
            names.add(node.name)
            return
        if isinstance(node, (LitInt, LitFloat, LitBool, LitString, Coin, Vacuum, Hole)):
            return
        if isinstance(
            node,
            (
                KetLit,
                OpLit,
                OpPauli,
                OpHop,
                OpNumber,
                OpQuadrature,
                OpGridQuad,
                OpIdentity,
            ),
        ):
            return
        if isinstance(node, KetSumBinder):
            walk(getattr(node.domain, "width", None))
            return
        if isinstance(node, NormExpr):
            walk(node.state)
            return
        if _walk_binder_free_vars(node, names, walk):
            return
        if _walk_operator_free_vars(node, names, walk):
            return
        _walk_expression_free_vars(node, names, walk)

    walk(expr)
    return names
