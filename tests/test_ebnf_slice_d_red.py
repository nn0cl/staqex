"""AT-TDD Phase 1 Red: LISS-0072 Slice D — EBNF catch-up and alignment gate."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_EBNF = _REPO / "docs" / "specs" / "grammar" / "staqex.ebnf"


def _grammar_text() -> str:
    return _EBNF.read_text(encoding="utf-8")


def test_grammar_documents_until_max_surface() -> None:
    grammar = _grammar_text()

    assert '"until"' in grammar
    assert '"max"' in grammar
    assert "until" in grammar and "max" in grammar


def test_grammar_documents_numeric_literal_separators() -> None:
    grammar = _grammar_text()

    assert "_" in grammar
    assert "1_000" in grammar or "separator" in grammar.lower()


def test_grammar_lists_scientific_scope_heads_and_modern_keywords() -> None:
    grammar = _grammar_text()

    for keyword in (
        '"namespace"',
        '"enum"',
        '"struct"',
        '"dynamic"',
        '"theory"',
        '"experiment"',
        '"workflow"',
        '"execution"',
        '"report"',
        '"system"',
    ):
        assert keyword in grammar, keyword


def test_grammar_lists_ascii_math_tokens() -> None:
    grammar = _grammar_text()

    assert '"<"' in grammar
    assert '">"' in grammar
    assert '"*|*"' in grammar
    assert "tensor_op" in grammar


def test_alignment_helper_matches_shipping_inventory() -> None:
    from tests.spec_verification.harness.ebnf_inventory import compare_grammar_to_shipping

    report = compare_grammar_to_shipping()
    assert not report.missing_from_grammar, report
    assert not report.extra_in_grammar, report


if __name__ == "__main__":
    failures = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except Exception as exc:  # noqa: BLE001 — Red harness
                failures += 1
                print(f"FAIL {name}: {type(exc).__name__}: {exc}")
    if failures:
        raise SystemExit(f"Red confirmed: {failures} failure(s)")
    print("OK - LISS-0072 Slice D Phase 1 Red")
