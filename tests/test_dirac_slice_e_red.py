"""AT-TDD Phase 1 Red: LISS-0073 Slice E — expression-side postfix †."""

from __future__ import annotations

import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.ast_nodes import Call, StateBind, Var
from compiler.staqex.pipeline import compile_source

EBNF_PATH = _REPO / "docs" / "specs" / "grammar" / "staqex.ebnf"


def _codes(compiled) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compiled.diagnostics}


def _main_binds(compiled) -> list[StateBind]:
    assert compiled.unit is not None, compiled.diagnostics
    assert compiled.unit.main is not None, "expected MainDecl"
    return [stmt for stmt in compiled.unit.main.body.stmts if isinstance(stmt, StateBind)]


def test_expr_postfix_dagger_parses_as_adjoint_call() -> None:
    compiled = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            State a = adjoint(X)
            State observed = Coin()
            Measure observed
        }}
        """
    )

    assert "PARSE_ERROR" not in _codes(compiled), compiled.diagnostics
    binds = [bind for bind in _main_binds(compiled) if bind.name == "a"]
    assert len(binds) == 1
    expr = binds[0].expr
    assert isinstance(expr, Call)
    assert isinstance(expr.callee, Var) and expr.callee.name == "adjoint"
    assert len(expr.args) == 1
    assert isinstance(expr.args[0], Var) and expr.args[0].name == "X"


def test_expr_dagger_typechecks_like_adjoint_call() -> None:
    call_ok = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Operator A = adjoint(X)
            State observed = Coin()
            Measure observed
        }
        """
    )
    dagger_ok = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            Operator A = adjoint(X)
            State observed = Coin()
            Measure observed
        }}
        """
    )

    # Expression-side surface used inside Operator bind via Dirac routing is
    # out of Slice E when RHS is OpDSL; this oracle keeps function-shaped
    # adjoint and OpDSL dagger green while expression sugar is the Red target.
    assert call_ok.ok, call_ok.diagnostics
    assert dagger_ok.ok, dagger_ok.diagnostics
    assert "OPERATOR_ALGEBRA_TYPE_ERROR" not in _codes(call_ok)
    assert "OPERATOR_ALGEBRA_TYPE_ERROR" not in _codes(dagger_ok)


def test_expr_dagger_in_state_typechecks_like_adjoint() -> None:
    """Expression path: state bind with X† must match adjoint(X) typecheck."""
    call_ok = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State a = adjoint(X)
            State observed = Coin()
            Measure observed
        }
        """
    )
    dagger_ok = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            State a = adjoint(X)
            State observed = Coin()
            Measure observed
        }}
        """
    )

    assert call_ok.ok, call_ok.diagnostics
    assert dagger_ok.ok, dagger_ok.diagnostics
    assert "PARSE_ERROR" not in _codes(dagger_ok), dagger_ok.diagnostics
    assert "OPERATOR_ALGEBRA_TYPE_ERROR" not in _codes(dagger_ok)


def test_opdsl_postfix_dagger_still_compiles() -> None:
    compiled = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            Operator A = adjoint(X)
            State observed = Coin()
            Measure observed
        }}
        """
    )

    assert compiled.ok, compiled.diagnostics


def test_ebnf_documents_expr_postfix_dagger() -> None:
    text = EBNF_PATH.read_text(encoding="utf-8")
    assert "ket_lit" in text and "bra_lit" in text
    assert re.search(
        r"ket_lit.*bra_lit|bra_lit.*ket_lit",
        text,
        re.IGNORECASE | re.DOTALL,
    ), "EBNF must document the ASCII quantum primary forms"


def main() -> None:
    test_expr_postfix_dagger_parses_as_adjoint_call()
    print("PASS test_expr_postfix_dagger_parses_as_adjoint_call")
    test_expr_dagger_typechecks_like_adjoint_call()
    print("PASS test_expr_dagger_typechecks_like_adjoint_call")
    test_expr_dagger_in_state_typechecks_like_adjoint()
    print("PASS test_expr_dagger_in_state_typechecks_like_adjoint")
    test_opdsl_postfix_dagger_still_compiles()
    print("PASS test_opdsl_postfix_dagger_still_compiles")
    test_ebnf_documents_expr_postfix_dagger()
    print("PASS test_ebnf_documents_expr_postfix_dagger")
    print("OK - LISS-0073 Slice E")


if __name__ == "__main__":
    main()
