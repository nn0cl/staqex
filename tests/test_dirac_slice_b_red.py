"""AT-TDD Phase 1 Red: LISS-0073 Slice B — bra–ket inner juxtaposition."""

from __future__ import annotations

import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.ast_nodes import BraLit, Call, KetLit, StateBind, Var
from compiler.staqex.lexer import Lexer
from compiler.staqex.pipeline import compile_source
from compiler.staqex.tokens import TokenKind

BRA_OPEN = "<"
KET_CLOSE = ">"
EBNF_PATH = _REPO / "docs" / "specs" / "grammar" / "staqex.ebnf"


def _codes(compiled) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compiled.diagnostics}


def _main_binds(compiled) -> list[StateBind]:
    assert compiled.unit is not None, compiled.diagnostics
    assert compiled.unit.main is not None, "expected MainDecl"
    return [stmt for stmt in compiled.unit.main.body.stmts if isinstance(stmt, StateBind)]


def _inner_overlap_source() -> str:
    # ASCII spelling <phi|psi> (single bar), not <phi||psi>.
    return f"""
        package t
        pub fn main() -> Unit {{
            State overlap = inner({BRA_OPEN}0|, |1{KET_CLOSE})
            State observed = Coin()
            Measure observed
        }}
        """


def test_bra_ket_juxtaposition_parses_as_inner_call() -> None:
    compiled = compile_source(_inner_overlap_source())

    assert "LEX_ERROR" not in _codes(compiled), compiled.diagnostics
    assert "PARSE_ERROR" not in _codes(compiled), compiled.diagnostics
    binds = [bind for bind in _main_binds(compiled) if bind.name == "overlap"]
    assert len(binds) == 1
    expr = binds[0].expr
    assert isinstance(expr, Call)
    assert isinstance(expr.callee, Var) and expr.callee.name == "inner"
    assert len(expr.args) == 2
    assert isinstance(expr.args[0], BraLit) and expr.args[0].label == "0"
    assert isinstance(expr.args[1], KetLit) and expr.args[1].label == "1"


def test_bra_ket_inner_typechecks_like_function_inner() -> None:
    compiled = compile_source(_inner_overlap_source())

    assert compiled.ok, compiled.diagnostics
    assert "OPERATOR_ALGEBRA_TYPE_ERROR" not in _codes(compiled)


def test_alone_bra_still_parses_without_following_ket() -> None:
    compiled = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            State bra = {BRA_OPEN}0|
            State observed = Coin()
            Measure observed
        }}
        """
    )

    assert "PARSE_ERROR" not in _codes(compiled), compiled.diagnostics
    binds = [bind for bind in _main_binds(compiled) if bind.name == "bra"]
    assert len(binds) == 1
    assert isinstance(binds[0].expr, BraLit)
    assert binds[0].expr.label == "0"


def test_pipeline_remains_distinct_from_ket_close() -> None:
    tokens, diagnostics = Lexer(f"x |> |+{KET_CLOSE}").tokenize()

    assert not diagnostics
    kinds = [token.kind for token in tokens if token.kind is not TokenKind.EOF]
    assert TokenKind.PIPE_OP in kinds
    assert TokenKind.KET in kinds
    assert kinds.count(TokenKind.PIPE_OP) == 1


def test_ebnf_documents_bra_ket_inner_juxtaposition() -> None:
    text = EBNF_PATH.read_text(encoding="utf-8")
    # Slice B documents the north-star inner surface somewhere in the grammar.
    assert "bra_lit" in text and "ket_lit" in text, (
        "EBNF must document the ASCII bra/ket primary forms"
    )


def main() -> None:
    test_bra_ket_juxtaposition_parses_as_inner_call()
    print("PASS test_bra_ket_juxtaposition_parses_as_inner_call")
    test_bra_ket_inner_typechecks_like_function_inner()
    print("PASS test_bra_ket_inner_typechecks_like_function_inner")
    test_alone_bra_still_parses_without_following_ket()
    print("PASS test_alone_bra_still_parses_without_following_ket")
    test_pipeline_remains_distinct_from_ket_close()
    print("PASS test_pipeline_remains_distinct_from_ket_close")
    test_ebnf_documents_bra_ket_inner_juxtaposition()
    print("PASS test_ebnf_documents_bra_ket_inner_juxtaposition")
    print("OK - LISS-0073 Slice B Phase 1 Red")


if __name__ == "__main__":
    main()
