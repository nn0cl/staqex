"""Compile-time-only Operator AST resolution for static-analysis passes
that have no live `Evaluator` state (LISS-0411, completing ADR 0206 for
`unitarity_check.py` and the QASM/Trotter backend).

Both consumers already do their own narrow walk of `unit.main.body.stmts`
collecting `Operator` binds and numeric scalar literals; neither tracks
struct construction at all, so a struct-field `Operator` coefficient
(`weights.a * X`) was invisible to both -- unlike the live `Evaluator`,
which resolves it via `runtime.op_attr_elaboration.materialize_op_attrs`.

This module adds the one missing piece -- struct-of-literals constant
folding -- as pure, safe compile-time evaluation: a struct is only
folded when every field value is itself a numeric literal or a
previously-folded scalar. Genuinely dynamic values (a function call, a
Host array) are simply not added, matching the scalars-only behavior
these callers already had for non-struct cases.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from .ast_nodes import (
    Call,
    CompilationUnit,
    FunDecl,
    LitFloat,
    LitInt,
    OpAttr,
    OpBin,
    OpCall,
    OpExpr,
    OpLit,
    OpPow,
    OpVar,
    ReturnStmt,
    StateBind,
    StructDecl,
    Var,
)
from .runtime.op_attr_elaboration import OpAttrElaborationError, _op_attr_float


def _struct_field_names(unit: CompilationUnit) -> dict[str, list[str]]:
    names: dict[str, list[str]] = {}
    for decl in unit.decls:
        if isinstance(decl, StructDecl):
            names[decl.name] = [f.name for f in decl.fields]
    return names


def _numeric_lit(expr: Any, scalars: dict[str, float]) -> float | None:
    if isinstance(expr, (LitInt, LitFloat)):
        return float(expr.value)
    if isinstance(expr, Var) and expr.name in scalars:
        return scalars[expr.name]
    return None


def collect_static_operator_context(
    unit: CompilationUnit,
) -> tuple[dict[str, Any], dict[str, float], dict[str, Any]]:
    """Walk `unit.main` (and library `FunDecl` bodies) collecting
    `Operator` binds, numeric scalar literals, and struct-of-literals
    constructions. Returns `(operators, scalars, objects)`; `objects`
    values are `SimpleNamespace(fields={...})`, matching the `.fields`
    shape `materialize_op_attrs` already expects from a runtime
    `StructValue`/`ClassInstance`.
    """
    from .stdlib.prelude import PRELUDE_CONSTANTS

    operators: dict[str, Any] = {}
    scalars: dict[str, float] = dict(PRELUDE_CONSTANTS)
    objects: dict[str, Any] = {}
    field_names = _struct_field_names(unit)

    def _walk(stmts: list[Any]) -> None:
        for stmt in stmts:
            if not isinstance(stmt, StateBind) or len(stmt.names) != 1:
                continue
            if stmt.ty is not None and stmt.ty.name == "Operator":
                operators[stmt.names[0]] = stmt.expr
                continue
            if (
                stmt.ty is not None
                and stmt.ty.name in field_names
                and isinstance(stmt.expr, Call)
            ):
                fields: dict[str, float] = {}
                ok = True
                if stmt.expr.kwargs:
                    for fname, fexpr in stmt.expr.kwargs:
                        val = _numeric_lit(fexpr, scalars)
                        if val is None:
                            ok = False
                            break
                        fields[fname] = val
                else:
                    decl_names = field_names[stmt.ty.name]
                    if len(stmt.expr.args) != len(decl_names):
                        ok = False
                    else:
                        for fname, fexpr in zip(decl_names, stmt.expr.args):
                            val = _numeric_lit(fexpr, scalars)
                            if val is None:
                                ok = False
                                break
                            fields[fname] = val
                if ok:
                    objects[stmt.names[0]] = SimpleNamespace(fields=fields)
                continue
            if stmt.ty is not None and stmt.ty.name not in {"State", "Operator", "Delta"}:
                val = _numeric_lit(stmt.expr, scalars)
                if val is not None:
                    scalars[stmt.names[0]] = val

    if unit.main is not None:
        _walk(unit.main.body.stmts)
    for decl in unit.decls:
        if isinstance(decl, FunDecl):
            _walk(decl.body.stmts)

    return operators, scalars, objects


def _find_operator_fun(unit: CompilationUnit, name: str) -> FunDecl | None:
    for decl in unit.decls:
        if (
            isinstance(decl, FunDecl)
            and decl.name == name
            and decl.return_type is not None
            and decl.return_type.name == "Operator"
        ):
            return decl
    return None


def _resolve_static_call(
    call: OpCall,
    *,
    unit: CompilationUnit,
    operators: dict[str, Any],
    objects: dict[str, Any],
    _seen: frozenset[str],
) -> Any:
    """Statically inline a call to a known Operator-returning function
    (mirrors `Evaluator._resolve_op_call`, purely as AST substitution --
    no runtime execution). Only handles the common single-return-
    expression shape with object-typed params rekeyed by parameter name
    (LISS-0297's own pattern); anything else is left unresolved and
    falls through to the caller's existing best-effort `except`.

    Uses a fresh `local_operators` scope for the callee's own local
    `Operator` binds (proper lexical scoping, matching the runtime
    `_resolve_operator_factory_call`'s own `local_ops` -- functions
    don't implicitly see the caller's Operator names). Found necessary
    after a real infinite-recursion bug: a callee's own local `Operator
    H = ...` and the *caller's* outer `Operator H = f(...)` sharing the
    name `H` caused unbounded self-reference when both were resolved
    against the same `operators` dict."""
    if call.name in _seen:
        return call
    fun = _find_operator_fun(unit, call.name)
    if fun is None or len(fun.params) != len(call.args):
        return call
    local_objects = dict(objects)
    for param, arg in zip(fun.params, call.args):
        if isinstance(arg, OpVar) and arg.name in objects:
            local_objects[param.name] = objects[arg.name]
    local_operators: dict[str, Any] = {}
    for stmt in fun.body.stmts:
        if (
            isinstance(stmt, StateBind)
            and stmt.ty is not None
            and stmt.ty.name == "Operator"
            and len(stmt.names) == 1
        ):
            local_operators[stmt.names[0]] = stmt.expr
    result = next(
        (s.expr for s in fun.body.stmts if isinstance(s, ReturnStmt)),
        fun.body.result,
    )
    if result is None:
        return call
    return _resolve_static_tree(
        result,
        unit=unit,
        operators=local_operators,
        objects=local_objects,
        _seen=_seen | {call.name},
    )


def _resolve_static_tree(
    expr: Any,
    *,
    unit: CompilationUnit,
    operators: dict[str, Any],
    objects: dict[str, Any],
    _seen: frozenset[str],
) -> Any:
    if isinstance(expr, OpAttr):
        value = _op_attr_float(expr, objects)
        return OpLit(value=float(value), span=expr.span)
    if isinstance(expr, OpCall):
        resolved = _resolve_static_call(
            expr, unit=unit, operators=operators, objects=objects, _seen=_seen
        )
        if resolved is expr:
            return expr
        return _resolve_static_tree(
            resolved, unit=unit, operators=operators, objects=objects, _seen=_seen
        )
    if isinstance(expr, OpBin):
        new_lhs = _resolve_static_tree(
            expr.lhs, unit=unit, operators=operators, objects=objects, _seen=_seen
        )
        new_rhs = _resolve_static_tree(
            expr.rhs, unit=unit, operators=operators, objects=objects, _seen=_seen
        )
        if new_lhs is expr.lhs and new_rhs is expr.rhs:
            return expr
        return OpBin(op=expr.op, lhs=new_lhs, rhs=new_rhs, span=expr.span)
    if isinstance(expr, OpPow):
        new_base = _resolve_static_tree(
            expr.base, unit=unit, operators=operators, objects=objects, _seen=_seen
        )
        if new_base is expr.base:
            return expr
        return OpPow(base=new_base, exp=expr.exp, span=expr.span)
    if isinstance(expr, OpVar) and expr.name in operators and expr.name not in _seen:
        # Indirection through a bound Operator name (LISS-0410's own
        # "Operator H = G" case, statically) -- resolve G's tree too.
        return _resolve_static_tree(
            operators[expr.name],
            unit=unit,
            operators=operators,
            objects=objects,
            _seen=_seen | {expr.name},
        )
    return expr


def resolve_static_operator(
    op_ast: Any,
    *,
    unit: CompilationUnit,
    operators: dict[str, Any],
    objects: dict[str, Any],
) -> Any:
    """Resolve `OpAttr` struct-field coefficients and nested Operator-
    returning calls against a statically collected context, reusing the
    same struct-field elaboration logic the live `Evaluator` uses
    (`op_attr_elaboration._op_attr_float`), purely as compile-time AST
    substitution. May raise `OpAttrElaborationError` for a genuinely
    malformed reference (unknown field, etc.) -- callers should treat
    that the same as any other can't-statically-determine case they
    already handle (both existing callers already wrap their resolution
    attempt in a broad `except` for exactly this reason)."""
    return _resolve_static_tree(
        op_ast, unit=unit, operators=operators, objects=objects, _seen=frozenset()
    )
