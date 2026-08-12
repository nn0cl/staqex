"""AT-TDD Phase 1 Red: LISS-0073 Slice F — commutator / anticommutator brackets."""

from __future__ import annotations

import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.ast_nodes import Call, ListExpr, StateBind, Var
from compiler.staqex.pipeline import compile_source

EBNF_PATH = _REPO / "docs" / "specs" / "grammar" / "staqex.ebnf"


def _codes(compiled) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compiled.diagnostics}


def _main_binds(compiled) -> list[StateBind]:
    assert compiled.unit is not None, compiled.diagnostics
    assert compiled.unit.main is not None, "expected MainDecl"
    return [stmt for stmt in compiled.unit.main.body.stmts if isinstance(stmt, StateBind)]


def test_operator_brackets_parse_as_commutator() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Operator C = [X, Y]
            State observed = coin()
            measure observed
        }
        """
    )

    assert "PARSE_ERROR" not in _codes(compiled), compiled.diagnostics
    binds = [bind for bind in _main_binds(compiled) if bind.name == "C"]
    assert len(binds) == 1
    expr = binds[0].expr
    assert isinstance(expr, Call)
    assert isinstance(expr.callee, Var) and expr.callee.name == "commutator"
    assert len(expr.args) == 2
    assert isinstance(expr.args[0], Var) and expr.args[0].name == "X"
    assert isinstance(expr.args[1], Var) and expr.args[1].name == "Y"


def test_operator_braces_parse_as_anticommutator() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Operator C = {X, Y}
            State observed = coin()
            measure observed
        }
        """
    )

    assert "PARSE_ERROR" not in _codes(compiled), compiled.diagnostics
    binds = [bind for bind in _main_binds(compiled) if bind.name == "C"]
    expr = binds[0].expr
    assert isinstance(expr, Call)
    assert isinstance(expr.callee, Var) and expr.callee.name == "anticommutator"
    assert len(expr.args) == 2
    assert isinstance(expr.args[0], Var) and expr.args[0].name == "X"
    assert isinstance(expr.args[1], Var) and expr.args[1].name == "Y"


def test_expr_two_element_list_remains_list_expr() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State xs = [X, Y]
            State observed = coin()
            measure observed
        }
        """
    )

    assert "PARSE_ERROR" not in _codes(compiled), compiled.diagnostics
    binds = [bind for bind in _main_binds(compiled) if bind.name == "xs"]
    assert isinstance(binds[0].expr, ListExpr)
    assert len(binds[0].expr.items) == 2


def test_expr_braces_parse_as_anticommutator() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State a = {X, Y}
            State observed = coin()
            measure observed
        }
        """
    )

    assert "PARSE_ERROR" not in _codes(compiled), compiled.diagnostics
    binds = [bind for bind in _main_binds(compiled) if bind.name == "a"]
    expr = binds[0].expr
    assert isinstance(expr, Call)
    assert isinstance(expr.callee, Var) and expr.callee.name == "anticommutator"
    assert len(expr.args) == 2


def test_bracket_punctuation_typechecks_like_function_forms() -> None:
    fn_ok = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Operator C = commutator(X, Y)
            Operator A = anticommutator(X, Y)
            State observed = coin()
            measure observed
        }
        """
    )
    punct_ok = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Operator C = [X, Y]
            Operator A = {X, Y}
            State observed = coin()
            measure observed
        }
        """
    )

    assert fn_ok.ok, fn_ok.diagnostics
    assert punct_ok.ok, punct_ok.diagnostics
    assert "OPERATOR_ALGEBRA_TYPE_ERROR" not in _codes(punct_ok)


def test_ebnf_documents_commutator_anticommutator_brackets() -> None:
    text = EBNF_PATH.read_text(encoding="utf-8")
    assert re.search(
        r"commutator|anticommutator|bracket_commutator|brace_anticommutator",
        text,
        re.IGNORECASE,
    ), "EBNF must document [A,B] / {A,B} algebra brackets"
    assert "Slice F" in text or "commutator" in text.lower()


def main() -> None:
    test_operator_brackets_parse_as_commutator()
    print("PASS test_operator_brackets_parse_as_commutator")
    test_operator_braces_parse_as_anticommutator()
    print("PASS test_operator_braces_parse_as_anticommutator")
    test_expr_two_element_list_remains_list_expr()
    print("PASS test_expr_two_element_list_remains_list_expr")
    test_expr_braces_parse_as_anticommutator()
    print("PASS test_expr_braces_parse_as_anticommutator")
    test_bracket_punctuation_typechecks_like_function_forms()
    print("PASS test_bracket_punctuation_typechecks_like_function_forms")
    test_ebnf_documents_commutator_anticommutator_brackets()
    print("PASS test_ebnf_documents_commutator_anticommutator_brackets")
    print("OK - LISS-0073 Slice F")


if __name__ == "__main__":
    main()
