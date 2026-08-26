"""Physical-axiom static checks beyond core typecheck.

- INTERFER_INDEPENDENT_STATE_ERROR: interfer of disjoint coin/ket lineages
- COIN_IN_EVOLVE_ERROR: fresh entropy inside evolve bodies
- NESTED_WHEN_ERROR: when in ctrl (arms already checked in nested_when.py)
"""

from __future__ import annotations

from typing import Any, Iterator

from .ast_nodes import (
    Attr,
    BinOp,
    Call,
    Coin,
    CompilationUnit,
    Dirac,
    EvolveExpr,
    Expr,
    Inspect,
    KetLit,
    Lambda,
    Measure,
    Pipe,
    Snapshot,
    StateBind,
    TupleExpr,
    UnaryNot,
    Var,
    WhenExpr,
)


def check_physical_axioms(unit: CompilationUnit) -> list[dict[str, Any]]:
    diags: list[dict[str, Any]] = []
    if unit.main is None:
        return diags
    lineage: dict[str, frozenset[int]] = {}
    next_id = [0]

    def fresh() -> frozenset[int]:
        next_id[0] += 1
        return frozenset({next_id[0]})

    def lin_of(expr: Expr) -> frozenset[int]:
        if isinstance(expr, Coin) or isinstance(expr, KetLit):
            return fresh()
        if isinstance(expr, Var):
            return lineage.get(expr.name, frozenset())
        if isinstance(expr, Dirac):
            return lin_of(expr.arg)
        if isinstance(expr, BinOp):
            return lin_of(expr.lhs) | lin_of(expr.rhs)
        if isinstance(expr, WhenExpr):
            s = lin_of(expr.ctrl)
            for arm in expr.arms:
                s |= lin_of(arm.body)
            return s
        if isinstance(expr, Call):
            op = _op_name(expr)
            if op == "interfer":
                arg_lins = [lin_of(a) for a in expr.args]
                for i in range(len(arg_lins)):
                    for j in range(i + 1, len(arg_lins)):
                        a, b = arg_lins[i], arg_lins[j]
                        if a and b and a.isdisjoint(b):
                            diags.append(
                                {
                                    "code": "INTERFER_INDEPENDENT_STATE_ERROR",
                                    "line": expr.span.line,
                                    "col": expr.span.col,
                                    "message": (
                                        "`interfer` requires a shared coherent history "
                                        "(common coin/ket lineage). Independent states "
                                        "yield classical mixture, not quantum interference."
                                    ),
                                }
                            )
                s: frozenset[int] = frozenset()
                for L in arg_lins:
                    s |= L
                return s
            if op in {
                "phase",
                "diffuse",
                "grover_diffuse",
                "map",
                "project",
                "cnot",
                "apply",
                "capply",
                "ocapply",
                "toffoli",
                "hadamard",
                "shift",
                "walk_shift",
            } and expr.args:
                s = frozenset()
                for a in expr.args:
                    s |= lin_of(a)
                return s
            if op == "expect":
                return frozenset()  # classical scalar — no quantum lineage
            s = frozenset()
            for a in expr.args:
                s |= lin_of(a)
            return s
        if isinstance(expr, Inspect):
            return lin_of(expr.expr)
        if isinstance(expr, Attr):
            return lin_of(expr.obj)
        if isinstance(expr, Pipe):
            return lin_of(expr.rhs)
        if isinstance(expr, TupleExpr):
            s = frozenset()
            for it in expr.items:
                s |= lin_of(it)
            return s
        if isinstance(expr, EvolveExpr):
            _scan_evolve_coin(expr, diags)
            s = frozenset()
            for seed in expr.seeds:
                s |= lin_of(seed)
            return s
        if isinstance(expr, Lambda):
            return lin_of(expr.body)
        return frozenset()

    for stmt in unit.main.body.stmts:
        if isinstance(stmt, StateBind):
            L = lin_of(stmt.expr)
            for n in stmt.names:
                lineage[n] = L
        elif isinstance(stmt, (Measure, Snapshot)):
            lin_of(stmt.expr)

    # Nested when in ctrl (arms handled by nested_when.py)
    for stmt in unit.main.body.stmts:
        for expr in _stmt_exprs(stmt):
            for when in _all_when(expr):
                if _contains_when(when.ctrl):
                    diags.append(
                        {
                            "code": "NESTED_WHEN_ERROR",
                            "line": when.span.line,
                            "col": when.span.col,
                            "message": (
                                "Cannot nest `mix` inside the control expression. "
                                "Bind the control first, or use a joint pushforward."
                            ),
                        }
                    )
    return diags


def _scan_evolve_coin(expr: EvolveExpr, diags: list[dict[str, Any]]) -> None:
    if expr.body is None:
        return
    for node in _walk_all(expr.body.result):
        if isinstance(node, Coin):
            diags.append(
                {
                    "code": "COIN_IN_EVOLVE_ERROR",
                    "line": node.span.line,
                    "col": node.span.col,
                    "message": (
                        "`coin()` inside `evolve` injects fresh entropy mid-evolution. "
                        "Bind randomness outside; keep evolve as deterministic pushforward."
                    ),
                }
            )
    for lb in expr.body.lets:
        for node in _walk_all(lb.expr):
            if isinstance(node, Coin):
                diags.append(
                    {
                        "code": "COIN_IN_EVOLVE_ERROR",
                        "line": node.span.line,
                        "col": node.span.col,
                        "message": (
                            "`coin()` inside `evolve` injects fresh entropy mid-evolution. "
                            "Bind randomness outside; keep evolve as deterministic pushforward."
                        ),
                    }
                )


def _op_name(expr: Call) -> str:
    cal = expr.callee
    if isinstance(cal, Var):
        return cal.name
    if isinstance(cal, Attr):
        return cal.name
    return ""


def _stmt_exprs(stmt: Any) -> Iterator[Expr]:
    if isinstance(stmt, StateBind):
        yield stmt.expr
    elif isinstance(stmt, (Measure, Snapshot)):
        yield stmt.expr


def _all_when(expr: Expr) -> Iterator[WhenExpr]:
    if isinstance(expr, WhenExpr):
        yield expr
        yield from _all_when(expr.ctrl)
        for arm in expr.arms:
            yield from _all_when(arm.body)
        return
    for node in _walk_all(expr):
        if isinstance(node, WhenExpr):
            yield node


def _contains_when(expr: Expr) -> bool:
    return any(isinstance(n, WhenExpr) for n in _walk_all(expr)) or isinstance(
        expr, WhenExpr
    )


def _walk_all(expr: Expr) -> Iterator[Expr]:
    yield expr
    if isinstance(expr, BinOp):
        yield from _walk_all(expr.lhs)
        yield from _walk_all(expr.rhs)
    elif isinstance(expr, Call):
        yield from _walk_all(expr.callee)
        for a in expr.args:
            yield from _walk_all(a)
    elif isinstance(expr, Attr):
        yield from _walk_all(expr.obj)
    elif isinstance(expr, Dirac):
        yield from _walk_all(expr.arg)
    elif isinstance(expr, Inspect):
        yield from _walk_all(expr.expr)
    elif isinstance(expr, UnaryNot):
        yield from _walk_all(expr.expr)
    elif isinstance(expr, Pipe):
        yield from _walk_all(expr.lhs)
        yield from _walk_all(expr.rhs)
    elif isinstance(expr, Lambda):
        yield from _walk_all(expr.body)
    elif isinstance(expr, TupleExpr):
        for it in expr.items:
            yield from _walk_all(it)
    elif isinstance(expr, WhenExpr):
        yield from _walk_all(expr.ctrl)
        for arm in expr.arms:
            yield from _walk_all(arm.body)
    elif isinstance(expr, EvolveExpr):
        for s in expr.seeds:
            yield from _walk_all(s)
        if expr.duration is not None:
            yield from _walk_all(expr.duration)
        if expr.hamiltonian is not None:
            yield from _walk_all(expr.hamiltonian)
        if expr.body is not None:
            for lb in expr.body.lets:
                yield from _walk_all(lb.expr)
            yield from _walk_all(expr.body.result)
