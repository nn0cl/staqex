"""AT-TDD Phase 1 Red: LISS-0075 Slice A — linear duplicate-use verifier."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source


def _load_linear_hir_api():
    """Slice A Green must export a HIR-level linear verifier."""
    from compiler.staqex.hir import HirLinearVerifier, build_hir

    return HirLinearVerifier, build_hir


def _diagnostic_codes(diags: list[dict]) -> set[str]:
    return {str(d.get("code", "")) for d in diags}


def test_linear_verifier_importable() -> None:
    """Slice A must expose an importable HIR linear verifier type."""
    HirLinearVerifier, _ = _load_linear_hir_api()
    verifier = HirLinearVerifier()
    assert verifier is not None
    assert hasattr(verifier, "verify")
    assert callable(verifier.verify)


def test_duplicate_quantum_use_emits_named_diagnostic() -> None:
    """Re-binding the same quantum state through an alias must be rejected."""
    HirLinearVerifier, build_hir = _load_linear_hir_api()
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State<Int> q = Coin()
            State<Int> alias = q
            Measure alias
        }
        """
    )
    # LISS-0114: linear codes hard-fail CompileResult.ok; checker remains.
    assert compiled.unit is not None and compiled.checker is not None, compiled.diagnostics

    hir = build_hir(
        compiled.checker,
        scope_contracts=compiled.scope_contracts,
        unit=compiled.unit,
    )
    diags = HirLinearVerifier().verify(hir, unit=compiled.unit)
    assert "LINEAR_DUPLICATE_USE" in _diagnostic_codes(diags), (
        f"expected LINEAR_DUPLICATE_USE, got {diags}"
    )


def test_single_quantum_consumption_is_accepted() -> None:
    """A single terminal consumption path must not trigger duplicate-use."""
    HirLinearVerifier, build_hir = _load_linear_hir_api()
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State<Int> q = Coin()
            Measure q
        }
        """
    )
    assert compiled.ok, compiled.diagnostics
    assert compiled.checker is not None

    hir = build_hir(
        compiled.checker,
        scope_contracts=compiled.scope_contracts,
        unit=compiled.unit,
    )
    diags = HirLinearVerifier().verify(hir, unit=compiled.unit)
    assert "LINEAR_DUPLICATE_USE" not in _diagnostic_codes(diags), (
        f"unexpected LINEAR_DUPLICATE_USE, got {diags}"
    )


def main() -> None:
    test_linear_verifier_importable()
    print("PASS test_linear_verifier_importable")
    test_duplicate_quantum_use_emits_named_diagnostic()
    print("PASS test_duplicate_quantum_use_emits_named_diagnostic")
    test_single_quantum_consumption_is_accepted()
    print("PASS test_single_quantum_consumption_is_accepted")
    print("OK - LISS-0075 Slice A Phase 1 Red")


if __name__ == "__main__":
    main()
