"""AT-TDD Phase 1 Red: LISS-0075 Slice C — uncompute witness + Uncompute effect."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source


def _load():
    from compiler.staqex.hir import HirLinearVerifier, build_hir

    return HirLinearVerifier, build_hir


def _codes(diags: list[dict]) -> set[str]:
    return {str(d.get("code", "")) for d in diags}


def _verify(source: str) -> tuple[list[dict], object]:
    HirLinearVerifier, build_hir = _load()
    compiled = compile_source(source)
    # LISS-0114: intentional linear violations hard-fail ok; HIR still available.
    assert compiled.unit is not None and compiled.checker is not None, compiled.diagnostics
    hir = build_hir(
        compiled.checker,
        scope_contracts=compiled.scope_contracts,
        unit=compiled.unit,
    )
    diags = HirLinearVerifier().verify(hir, unit=compiled.unit)
    return diags, hir


def test_reset_to_ket0_counts_as_uncomputation() -> None:
    """Same-name rebind to |0> consumes the root without Measure (static witness)."""
    diags, _ = _verify(
        """
        package t
        pub fn main() -> Unit {
            State<Int> ancilla = Coin()
            State<Int> ancilla = |0>
            State<Int> q = Coin()
            Measure q
        }
        """
    )
    assert "LINEAR_IMPLICIT_DISCARD" not in _codes(diags), (
        f"uncomputed ancilla must not be discarded, got {diags}"
    )


def test_declared_uncompute_without_witness_is_rejected() -> None:
    """effects { Uncompute } without a static witness → UNCOMPUTE_WITNESS_MISSING."""
    diags, _ = _verify(
        """
        package t
        fn claim_uncompute() -> State<Int> effects { Uncompute } {
            State<Int> ancilla = Coin()
            return ancilla
        }
        pub fn main() -> Unit {
            State<Int> q = Coin()
            Measure q
        }
        """
    )
    assert "UNCOMPUTE_WITNESS_MISSING" in _codes(diags), (
        f"expected UNCOMPUTE_WITNESS_MISSING, got {diags}"
    )


def test_build_hir_records_uncompute_effect_when_witnessed() -> None:
    """Static uncompute witness is recorded on HirDecl.effects as Uncompute."""
    _, build_hir = _load()
    compiled = compile_source(
        """
        package t
        fn reset_ancilla() -> State<Int> {
            State<Int> ancilla = Coin()
            State<Int> ancilla = |0>
            return ancilla
        }
        pub fn main() -> Unit {
            State<Int> q = Coin()
            Measure q
        }
        """
    )
    assert compiled.ok, compiled.diagnostics
    hir = build_hir(
        compiled.checker,
        scope_contracts=compiled.scope_contracts,
        unit=compiled.unit,
    )
    decl = hir.declarations["reset_ancilla"]
    assert "Uncompute" in decl.effects, (
        f"expected Uncompute in effects, got {decl.effects}"
    )


def main() -> None:
    test_reset_to_ket0_counts_as_uncomputation()
    print("PASS test_reset_to_ket0_counts_as_uncomputation")
    test_declared_uncompute_without_witness_is_rejected()
    print("PASS test_declared_uncompute_without_witness_is_rejected")
    test_build_hir_records_uncompute_effect_when_witnessed()
    print("PASS test_build_hir_records_uncompute_effect_when_witnessed")
    print("OK - LISS-0075 Slice C Phase 1 Red")


if __name__ == "__main__":
    main()
