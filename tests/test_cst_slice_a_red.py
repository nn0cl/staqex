"""AT-TDD Phase 1 Red: LISS-0072 Slice A — lossless trivia/CST skeleton."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.lexer import Lexer
from compiler.staqex.tokens import TokenKind

KET_CLOSE = ">"


def _load_cst_api():
    from compiler.staqex.cst import build_lossless_cst, lossless_lex

    return lossless_lex, build_lossless_cst


def _non_eof(tokens):
    return [token for token in tokens if token.kind is not TokenKind.EOF]


def test_lossless_lex_retains_comment_and_whitespace_trivia() -> None:
    lossless_lex, _ = _load_cst_api()
    source = "package demo  // package note\n\npub fn main() -> Unit {\n    measure |0>\n}\n"

    tokens = lossless_lex(source)

    plain_tokens, plain_diags = Lexer(source).tokenize()
    assert not plain_diags
    assert [entry.token.kind for entry in tokens if entry.token.kind is not TokenKind.EOF] == [
        token.kind for token in _non_eof(plain_tokens)
    ]
    assert any(
        trivia.kind == "comment" and "package note" in trivia.text
        for entry in tokens
        for trivia in (*entry.leading_trivia, *entry.trailing_trivia)
    )
    assert any(
        trivia.kind == "whitespace" and "\n\n" in trivia.text
        for entry in tokens
        for trivia in (*entry.leading_trivia, *entry.trailing_trivia)
    )


def test_lossless_lex_preserves_ascii_math_token_kinds() -> None:
    lossless_lex, _ = _load_cst_api()
    source = f"State psi = |0{KET_CLOSE} // ascii ket\nmeasure psi\n"

    tokens = lossless_lex(source)

    kinds = [entry.token.kind for entry in tokens if entry.token.kind is not TokenKind.EOF]
    assert TokenKind.KET in kinds
    assert any(
        trivia.kind == "comment" and "ascii ket" in trivia.text
        for entry in tokens
        for trivia in (*entry.leading_trivia, *entry.trailing_trivia)
    )


def test_build_lossless_cst_exposes_root_and_original_source() -> None:
    _, build_lossless_cst = _load_cst_api()
    source = "package demo\npub fn main() -> Unit {\n    measure |0>\n}\n"

    cst = build_lossless_cst(source)

    assert cst.kind == "CompilationUnit"
    assert cst.source == source
    assert cst.children, "lossless CST root should expose child nodes/tokens"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")
    print("OK - LISS-0072 Slice A Phase 1 Red")
