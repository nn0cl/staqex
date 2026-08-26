"""Reject nested `mix` on unmeasured State (physical coherence rule).

Nested pattern matching on State coordinates mimics sequential mid-circuit
measurement / classical if-cascade and drops a clear unitary vs reduction
distinction (cf. OpenQASM / QIR: branch only on classical bits after measure).

Single-level `mix` remains the Discrete mixture / pushforward form (ADR 0024).
Nested `mix` → `NESTED_WHEN_ERROR`.
"""

from __future__ import annotations

from typing import Any, Iterator

from .ast_nodes import (
    Attr,
    BinOp,
    Call,
    CompilationUnit,
    Dirac,
    EvolveBody,
    EvolveExpr,
    Expr,
    Inspect,
    Lambda,
    Measure,
    Pipe,
    Snapshot,
    StateBind,
    TensorExpr,
    TupleExpr,
    WhenExpr,
)


MSG = (
    "Cannot apply nested `mix` on unmeasured State. "
    "Nested pattern matching violates unitarity and implies implicit decoherence. "
    "Use an operator (`cnot`, `evolve`, `expect`) for coherent transforms, "
    "`project` for explicit reduction, or a joint pushforward "
    "(e.g. `s0 == s1`, `b0 * 2 + b1`) instead of nesting."
)


def check_nested_when(unit: CompilationUnit) -> list[dict[str, Any]]:
    diags: list[dict[str, Any]] = []
    if unit.main is None:
        return diags
    for stmt in unit.main.body.stmts:
        for expr in _stmt_exprs(stmt):
            for when in _find_when(expr):
                if _arms_contain_when(when):
                    diags.append(
                        {
                            "code": "NESTED_WHEN_ERROR",
                            "line": when.span.line,
                            "col": when.span.col,
                            "message": MSG,
                        }
                    )
    return diags


def _stmt_exprs(stmt: Any) -> Iterator[Expr]:
    if isinstance(stmt, StateBind):
        yield stmt.expr
    elif isinstance(stmt, Measure):
        yield stmt.expr
    elif isinstance(stmt, Snapshot):
        yield stmt.expr
    elif hasattr(stmt, "expr"):
        yield stmt.expr


def _find_when(expr: Expr) -> Iterator[WhenExpr]:
    if isinstance(expr, WhenExpr):
        yield expr
        for arm in expr.arms:
            yield from _find_when(arm.body)
        yield from _find_when(expr.ctrl)
        return
    yield from _walk(expr)


def _arms_contain_when(when: WhenExpr) -> bool:
    return any(_contains_when(arm.body) for arm in when.arms)


def _contains_when(expr: Expr) -> bool:
    if isinstance(expr, WhenExpr):
        return True
    return any(True for _ in _find_when(expr))


def _walk(expr: Expr) -> Iterator[WhenExpr]:
    if isinstance(expr, BinOp):
        yield from _find_when(expr.lhs)
        yield from _find_when(expr.rhs)
    elif isinstance(expr, Call):
        yield from _find_when(expr.callee)
        for a in expr.args:
            yield from _find_when(a)
    elif isinstance(expr, Attr):
        yield from _find_when(expr.obj)
    elif isinstance(expr, Dirac):
        yield from _find_when(expr.arg)
    elif isinstance(expr, Inspect):
        yield from _find_when(expr.expr)
    elif isinstance(expr, Pipe):
        yield from _find_when(expr.lhs)
        yield from _find_when(expr.rhs)
    elif isinstance(expr, TensorExpr):
        # LISS-0375: a nested `mix` wrapped in a `*|*` tensor product
        # (e.g. `a *|* mix (c) { ... }`) must be found the same way one
        # wrapped in a BinOp/Pipe already is.
        yield from _find_when(expr.left)
        yield from _find_when(expr.right)
    elif isinstance(expr, Lambda):
        yield from _find_when(expr.body)
    elif isinstance(expr, TupleExpr):
        for e in expr.items:
            yield from _find_when(e)
    elif isinstance(expr, EvolveExpr):
        for s in expr.seeds:
            yield from _find_when(s)
        if expr.duration is not None:
            yield from _find_when(expr.duration)
        if expr.hamiltonian is not None:
            yield from _find_when(expr.hamiltonian)
        if expr.body is not None:
            yield from _walk_evolve_body(expr.body)
    elif isinstance(expr, WhenExpr):
        yield from _find_when(expr)


def _walk_evolve_body(body: EvolveBody) -> Iterator[WhenExpr]:
    for lb in body.lets:
        yield from _find_when(lb.expr)
    yield from _find_when(body.result)
