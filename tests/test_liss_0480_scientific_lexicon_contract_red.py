"""AT-TDD Phase 1 Red: LISS-0480 scientific lexicon contract."""

from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex.lexer import Lexer


SPEC = (
    Path(__file__).resolve().parents[1]
    / "docs/specs/staqex-v1-quantum-mental-model-follow-up.md"
)


def test_v1_lexicon_matrix_is_explicit_and_does_not_hide_proposals() -> None:
    text = SPEC.read_text(encoding="utf-8")

    assert "### 3.4 LISS-0480 v1 lexicon contract" in text
    for row in (
        "| `psi` |",
        "| `phi` |",
        "| `rho` |",
        "| `hbar` |",
        "| `cm` |",
        "| `controlled` |",
        "| `superpose` |",
    ):
        assert row in text
    assert "does not reserve `d`, `del`, `sum`, `prod`" in text
    assert "canonical_spelling" in text and "written_spelling" in text


def test_display_alias_has_one_canonical_token_and_written_form_provenance() -> None:
    tokens, diagnostics = Lexer("psi ψ").tokenize()

    assert not diagnostics
    names = [token for token in tokens if token.lexeme in {"psi", "ψ"}]
    assert len(names) == 2
    assert {token.meta["canonical_spelling"] for token in names} == {"psi"}
    assert {token.meta["written_spelling"] for token in names} == {"psi", "ψ"}


def test_alias_and_canonical_declaration_collision_is_deterministic() -> None:
    _tokens, diagnostics = Lexer("State psi = |0> State ψ = |1>").tokenize()

    assert not any(diagnostic.get("code") == "LEX_ERROR" for diagnostic in diagnostics)
    collision = [
        diagnostic
        for diagnostic in diagnostics
        if diagnostic.get("code") == "LEXICON_COLLISION"
    ]
    assert len(collision) == 1
    assert collision[0]["canonical_spelling"] == "psi"
    assert collision[0]["written_spelling"] == "ψ"


def test_unsupported_scientific_spelling_is_actionable() -> None:
    _tokens, diagnostics = Lexer("Ψ").tokenize()

    unsupported = [
        diagnostic
        for diagnostic in diagnostics
        if diagnostic.get("code") == "LEXICON_UNSUPPORTED_SPELLING"
    ]
    assert len(unsupported) == 1
    assert unsupported[0]["written_spelling"] == "Ψ"
    assert unsupported[0]["suggestion"] in {"psi", "ψ"}
