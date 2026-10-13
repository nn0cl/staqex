"""Closed-expression eligibility using the Evaluator's live read context."""

from __future__ import annotations

from typing import Any, Mapping, Protocol

from ...ast_nodes import (
    Expr,
    LitInt,
    LitFloat,
    LitBool,
    LitString,
    Var,
    Attr,
    UnitConvert,
    BinOp,
)


class ClosedExpressionContext(Protocol):
    scalars: Mapping[str, Any]
    objects: Mapping[str, Any]

    def _is_closed(self, expr: Expr) -> bool: ...


def is_closed(context: ClosedExpressionContext, expr: Expr) -> bool:
    if isinstance(expr, (LitInt, LitFloat, LitBool, LitString)):
        return True
    if isinstance(expr, Var):
        # Prelude / already-bound classical scalars (ADR 0062)
        return expr.name in context.scalars
    if isinstance(expr, Attr):
        if (
            isinstance(expr.obj, Var)
            and expr.obj.name == "Math"
            and expr.name in {"pi", "sqrt2", "inv_sqrt2"}
        ):
            return True
        # Struct / class field projections are classical once the object exists
        # (LISS-0137: Float J = c.J → Operator coeffs).
        if isinstance(expr.obj, Var) and expr.obj.name in context.objects:
            return True
        # Unit-suffixed literals are closed classical magnitudes.
        if isinstance(expr.obj, (LitInt, LitFloat)):
            from ...dimensions import UNIT_TABLE

            return expr.name in UNIT_TABLE
        return False
    if isinstance(expr, UnitConvert):
        return context._is_closed(expr.expr)
    if isinstance(expr, BinOp):
        return context._is_closed(expr.lhs) and context._is_closed(expr.rhs)
    return False
