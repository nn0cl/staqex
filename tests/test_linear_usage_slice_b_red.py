"""AT-TDD Phase 1 Red: LISS-0075 Slice B — LINEAR_IMPLICIT_DISCARD."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source


def _load_api():
    from compiler.staqex.hir import HirLinearVerifier, build_hir

    return HirLinearVerifier, build_hir


def _codes(diags: list[dict]) -> set[str]:
    return {str(d.get("code", "")) for d in diags}


def _verify(source: str) -> list[dict]:
    HirLinearVerifier, build_hir = _load_api()
    compiled = compile_source(source)
    # LISS-0114: intentional linear violations hard-fail ok; HIR still available.
    assert compiled.unit is not None and compiled.checker is not None, compiled.diagnostics
    hir = build_hir(
        compiled.checker,
        scope_contracts=compiled.scope_contracts,
        unit=compiled.unit,
    )
    return HirLinearVerifier().verify(hir, unit=compiled.unit)


def test_implicit_discard_of_unused_ancilla_is_rejected() -> None:
    """State bound but never measured/consumed before scope exit → discard."""
    diags = _verify(
        """
        package t
        pub fn main() -> Unit {
            State<Int> ancilla = Coin()
            State<Int> q = Coin()
            Measure q
        }
        """
    )
    assert "LINEAR_IMPLICIT_DISCARD" in _codes(diags), (
        f"expected LINEAR_IMPLICIT_DISCARD for unused ancilla, got {diags}"
    )


def test_measured_state_is_not_discarded() -> None:
    """A State that is measured is a valid consumption, not a discard."""
    diags = _verify(
        """
        package t
        pub fn main() -> Unit {
            State<Int> q = Coin()
            Measure q
        }
        """
    )
    assert "LINEAR_IMPLICIT_DISCARD" not in _codes(diags), (
        f"unexpected LINEAR_IMPLICIT_DISCARD, got {diags}"
    )


def test_discard_diagnostic_names_the_binding() -> None:
    """Diagnostic message must identify the discarded binding."""
    diags = _verify(
        """
        package t
        pub fn main() -> Unit {
            State<Int> leftover = Coin()
            State<Int> q = Coin()
            Measure q
        }
        """
    )
    discard = [d for d in diags if d.get("code") == "LINEAR_IMPLICIT_DISCARD"]
    assert discard, f"expected LINEAR_IMPLICIT_DISCARD, got {diags}"
    assert any("leftover" in str(d.get("message", "")) for d in discard), (
        f"expected binding name in message, got {discard}"
    )


def main() -> None:
    test_implicit_discard_of_unused_ancilla_is_rejected()
    print("PASS test_implicit_discard_of_unused_ancilla_is_rejected")
    test_measured_state_is_not_discarded()
    print("PASS test_measured_state_is_not_discarded")
    test_discard_diagnostic_names_the_binding()
    print("PASS test_discard_diagnostic_names_the_binding")
    print("OK - LISS-0075 Slice B Phase 1 Red")


if __name__ == "__main__":
    main()
