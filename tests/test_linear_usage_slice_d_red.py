"""AT-TDD Phase 1 Red: LISS-0075 Slice D — build_hir linear wiring + e2e."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source


def _codes(diags: list[dict] | tuple) -> set[str]:
    return {str(d.get("code", "")) for d in diags}


def test_build_hir_attaches_linear_diagnostics() -> None:
    """build_hir(unit=...) must expose linear verifier diagnostics on HirModule."""
    from compiler.staqex.hir import build_hir

    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State<Int> leftover = Coin()
            State<Int> q = Coin()
            Measure q
        }
        """
    )
    # LISS-0114: discard hard-fails CompileResult.ok; checker remains for HIR.
    assert compiled.unit is not None and compiled.checker is not None, compiled.diagnostics
    hir = build_hir(
        compiled.checker,
        scope_contracts=compiled.scope_contracts,
        unit=compiled.unit,
    )
    assert hasattr(hir, "linear_diagnostics"), "HirModule must expose linear_diagnostics"
    assert "LINEAR_IMPLICIT_DISCARD" in _codes(hir.linear_diagnostics), (
        f"expected discard via build_hir, got {hir.linear_diagnostics}"
    )


def test_e2e_linear_suite_covers_a_b_c() -> None:
    """End-to-end: duplicate, discard, and witnessed uncompute via build_hir."""
    from compiler.staqex.hir import build_hir

    # A: alias duplicate
    a = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State<Int> q = Coin()
            State<Int> alias = q
            Measure alias
        }
        """
    )
    assert a.unit is not None and a.checker is not None, a.diagnostics
    hir_a = build_hir(a.checker, scope_contracts=a.scope_contracts, unit=a.unit)
    assert "LINEAR_DUPLICATE_USE" in _codes(hir_a.linear_diagnostics)

    # B: implicit discard
    b = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State<Int> leftover = Coin()
            State<Int> q = Coin()
            Measure q
        }
        """
    )
    assert b.unit is not None and b.checker is not None, b.diagnostics
    hir_b = build_hir(b.checker, scope_contracts=b.scope_contracts, unit=b.unit)
    assert "LINEAR_IMPLICIT_DISCARD" in _codes(hir_b.linear_diagnostics)

    # C: uncompute witness on HirDecl + clean diagnostics for that root
    c = compile_source(
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
    assert c.ok, c.diagnostics
    hir_c = build_hir(c.checker, scope_contracts=c.scope_contracts, unit=c.unit)
    assert "Uncompute" in hir_c.declarations["reset_ancilla"].effects
    assert "LINEAR_IMPLICIT_DISCARD" not in _codes(hir_c.linear_diagnostics)


def main() -> None:
    test_build_hir_attaches_linear_diagnostics()
    print("PASS test_build_hir_attaches_linear_diagnostics")
    test_e2e_linear_suite_covers_a_b_c()
    print("PASS test_e2e_linear_suite_covers_a_b_c")
    print("OK - LISS-0075 Slice D Phase 1 Red")


if __name__ == "__main__":
    main()
