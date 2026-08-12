"""ASCII-source boundary tests for historical Unicode quantum spellings."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.lexer import Lexer
from compiler.staqex.pipeline import compile_source
from compiler.staqex.tokens import TokenKind

KET_CLOSE = "\u27e9"  # ⟩
BRA_OPEN = "\u27e8"  # ⟨
TENSOR = "\u2297"  # ⊗
DAGGER = "\u2020"  # †


def _non_eof(tokens):
    return [token for token in tokens if token.kind is not TokenKind.EOF]


def test_unicode_ket_is_rejected_while_ascii_ket_is_accepted() -> None:
    ascii_tokens, ascii_diags = Lexer("|0>").tokenize()
    unicode_tokens, unicode_diags = Lexer(f"|0{KET_CLOSE}").tokenize()

    assert not ascii_diags
    assert unicode_diags
    assert _non_eof(ascii_tokens)[0].kind is TokenKind.KET
    assert _non_eof(ascii_tokens)[0].literal == "0"
    assert all(token.kind is not TokenKind.KET for token in _non_eof(unicode_tokens))


def test_pipeline_remains_distinct_from_rejected_unicode_ket_close() -> None:
    tokens, diagnostics = Lexer(f"x |> |+{KET_CLOSE}").tokenize()

    assert diagnostics
    kinds = [token.kind for token in _non_eof(tokens)]
    assert TokenKind.IDENT in kinds
    assert TokenKind.PIPE_OP in kinds
    assert TokenKind.KET not in kinds


def test_unicode_tensor_is_rejected_while_ascii_tensor_is_accepted() -> None:
    ascii_tokens, ascii_diags = Lexer("*|*").tokenize()
    unicode_tokens, unicode_diags = Lexer(TENSOR).tokenize()

    assert not ascii_diags
    assert unicode_diags
    assert _non_eof(ascii_tokens)[0].kind is TokenKind.TENSOR_OP
    assert all(token.kind is not TokenKind.TENSOR_OP for token in _non_eof(unicode_tokens))


def test_unicode_bra_is_rejected() -> None:
    tokens, diagnostics = Lexer(f"{BRA_OPEN}0|").tokenize()

    assert diagnostics
    assert all(token.kind is not TokenKind.BRA for token in _non_eof(tokens))


def test_postfix_dagger_is_rejected() -> None:
    tokens, diagnostics = Lexer(f"X{DAGGER}").tokenize()

    assert diagnostics
    assert TokenKind.DAGGER not in [token.kind for token in _non_eof(tokens)]


def test_unicode_ket_program_is_rejected() -> None:
    ascii_ok = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State psi = |0>
            measure psi
        }
        """
    )
    unicode_ok = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            State psi = |0{KET_CLOSE}
            measure psi
        }}
        """
    )

    assert ascii_ok.ok, ascii_ok.diagnostics
    assert not unicode_ok.ok


def test_unicode_tensor_bind_is_rejected() -> None:
    ascii_ok = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State left = |0>
            State right = |1>
            (a, b) = left *|* right
    State left = |0>
    State right = |0>
            measure a
        }
        """
    )
    unicode_ok = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            State left = |0>
            State right = |1>
            (a, b) = left {TENSOR} right
    State left = |0>
    State right = |0>
            measure a
        }}
        """
    )

    assert ascii_ok.ok, ascii_ok.diagnostics
    assert not unicode_ok.ok


def test_postfix_dagger_is_rejected_but_adjoint_call_is_accepted() -> None:
    call_ok = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Operator A = adjoint(X)
            State<Int> observed = coin()
            measure observed
        }
        """
    )
    dagger_ok = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            Operator A = X{DAGGER}
            State<Int> observed = coin()
            measure observed
        }}
        """
    )

    assert call_ok.ok, call_ok.diagnostics
    assert not dagger_ok.ok


def test_unterminated_unicode_ket_is_lex_error() -> None:
    _, diagnostics = Lexer("|0").tokenize()

    assert any(diagnostic.get("code") == "LEX_ERROR" for diagnostic in diagnostics)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")
    print("OK - LISS-0069 Slice A Phase 2 Green")
