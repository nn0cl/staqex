"""AT-TDD Phase 1 Red: WP-0094 Tensor parity and grouping boundary."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.ast_nodes import BinOp, Call, TensorExpr, Var  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402


def _compile(rhs: str):
    return compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            State left = |0>
            State right = |1>
            State third = |0>
            State result = {rhs}
            measure result
        }}
        """
    )


def _result_expr(compiled):
    assert compiled.unit is not None, compiled.diagnostics
    assert compiled.unit.main is not None, compiled.diagnostics
    return next(
        stmt.expr
        for stmt in compiled.unit.main.body.stmts
        if getattr(stmt, "name", None) == "result"
    )


def test_tensor_alias_lowers_to_the_same_tensor_ast_as_infix() -> None:
    infix = _result_expr(_compile("left *|* right"))
    alias = _result_expr(_compile("tensor(left, right)"))

    assert isinstance(infix, TensorExpr)
    assert isinstance(alias, TensorExpr)
    assert isinstance(infix.left, Var) and isinstance(alias.left, Var)
    assert isinstance(infix.right, Var) and isinstance(alias.right, Var)
    assert alias.left.name == infix.left.name == "left"
    assert alias.right.name == infix.right.name == "right"


def test_tensor_alias_rejects_more_than_two_arguments_at_compile_time() -> None:
    compiled = _compile("tensor(left, right, third)")

    assert "TENSOR_ARITY_ERROR" in {
        diagnostic.get("code", "") for diagnostic in compiled.diagnostics
    }


def test_tensor_infix_is_left_associative_and_preserves_factor_order() -> None:
    expr = _result_expr(_compile("left *|* right *|* third"))

    assert isinstance(expr, TensorExpr)
    assert isinstance(expr.left, TensorExpr)
    assert isinstance(expr.left.left, Var)
    assert isinstance(expr.left.right, Var)
    assert isinstance(expr.right, Var)
    assert [
        expr.left.left.name,
        expr.left.right.name,
        expr.right.name,
    ] == ["left", "right", "third"]


def test_tensor_and_arithmetic_mixture_requires_explicit_grouping() -> None:
    ungrouped = _compile("left *|* right * third")
    grouped = _compile("(left *|* right) * third")

    ungrouped_codes = {
        diagnostic.get("code", "") for diagnostic in ungrouped.diagnostics
    }
    grouped_codes = {
        diagnostic.get("code", "") for diagnostic in grouped.diagnostics
    }
    assert "TENSOR_GROUPING_ERROR" in ungrouped_codes
    assert "TENSOR_GROUPING_ERROR" not in grouped_codes


def test_tensor_alias_is_not_a_classical_collection_constructor() -> None:
    expr = _result_expr(_compile("tensor(left, right)"))

    assert not isinstance(expr, (Call, BinOp))
    assert isinstance(expr, TensorExpr)
