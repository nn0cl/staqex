"""Acceptance tests for ADR 0191 / WP-0094 ASCII quantum notation."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.lexer import Lexer  # noqa: E402
from compiler.staqex.stdlib.prelude import PRELUDE_COMBINATORS  # noqa: E402
from compiler.staqex.tokens import TokenKind  # noqa: E402


def test_tensor_alias_is_a_registered_quantum_combinator() -> None:
    """The documented alias must not remain a documentation-only promise."""

    assert "tensor" in PRELUDE_COMBINATORS


def test_unicode_quantum_punctuation_is_rejected_as_source() -> None:
    for source in ("ψ", "φ", "ρ", "⟨0|", "|0⟩", "⊗", "†"):
        _, diagnostics = Lexer(source).tokenize()

        assert diagnostics, f"expected ASCII-source rejection for {source!r}"


def test_fullwidth_ascii_identifier_is_rejected_as_source() -> None:
    _, diagnostics = Lexer("ｐsi").tokenize()

    assert diagnostics


def test_ascii_bra_is_accepted_only_as_one_primary_literal() -> None:
    tokens, diagnostics = Lexer("<psi|").tokenize()

    assert not diagnostics
    non_eof = [token for token in tokens if token.kind is not TokenKind.EOF]
    assert len(non_eof) == 1
    assert non_eof[0].kind is TokenKind.BRA
    assert non_eof[0].literal == "psi"


if __name__ == "__main__":
    for name, test in list(globals().items()):
        if name.startswith("test_") and callable(test):
            test()
            print(f"PASS {name}")
    print("OK - ADR 0191 / WP-0094 ASCII notation")
