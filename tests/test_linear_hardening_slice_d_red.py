"""AT-TDD Phase 1 Red: LISS-0114 Slice D — DensityState linear carrier set."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source
from compiler.staqex.typecheck import Ty


def _codes(diags: list[dict]) -> set[str]:
    return {str(d.get("code", "")) for d in diags}


_DENSITY = """
package t
pub fn main() -> Unit {{
    DensityState<Qubit> {name} = DensityState(
        RawMatrix([
            [1.0, 0.0],
            [0.0, 0.0]
        ])
    )
    {tail}
}}
"""


def test_linear_carrier_kinds_include_density_state() -> None:
    """R4: module-level linear carriers must include DensityState, not State-only."""
    from compiler.staqex import hir as hir_mod

    assert hasattr(hir_mod, "LINEAR_CARRIER_KINDS")
    assert "State" in hir_mod.LINEAR_CARRIER_KINDS
    assert "DensityState" in hir_mod.LINEAR_CARRIER_KINDS
    assert hasattr(hir_mod, "is_linear_carrier_ty")
    assert hir_mod.is_linear_carrier_ty(Ty(kind="State", payload="Int"))
    assert hir_mod.is_linear_carrier_ty(
        Ty(kind="Object", payload="DensityState")
    )
    assert not hir_mod.is_linear_carrier_ty(
        Ty(kind="Classical", payload="Int")
    )


def test_density_state_implicit_discard_hard_fails() -> None:
    compiled = compile_source(
        _DENSITY.format(
            name="leftover",
            tail="State<Int> q = Coin()\n    Measure q",
        )
    )
    assert "LINEAR_IMPLICIT_DISCARD" in _codes(compiled.diagnostics), (
        f"expected DensityState discard, got {compiled.diagnostics}"
    )
    assert compiled.ok is False


def test_density_state_alias_is_duplicate_use() -> None:
    compiled = compile_source(
        _DENSITY.format(
            name="d",
            tail=(
                "DensityState<Qubit> alias = d\n"
                "    State<Int> q = Coin()\n"
                "    Measure q"
            ),
        )
    )
    assert "LINEAR_DUPLICATE_USE" in _codes(compiled.diagnostics), (
        f"expected DensityState alias duplicate, got {compiled.diagnostics}"
    )
    assert compiled.ok is False


def test_density_state_measure_consumes() -> None:
    compiled = compile_source(
        _DENSITY.format(name="rho", tail="Measure rho")
    )
    assert "LINEAR_IMPLICIT_DISCARD" not in _codes(compiled.diagnostics), (
        f"measured DensityState must not discard, got {compiled.diagnostics}"
    )
    linear = {
        c
        for c in _codes(compiled.diagnostics)
        if c.startswith("LINEAR_") or c == "UNCOMPUTE_WITNESS_MISSING"
    }
    assert not linear, f"unexpected linear diagnostics: {compiled.diagnostics}"


def main() -> None:
    test_linear_carrier_kinds_include_density_state()
    print("PASS test_linear_carrier_kinds_include_density_state")
    test_density_state_implicit_discard_hard_fails()
    print("PASS test_density_state_implicit_discard_hard_fails")
    test_density_state_alias_is_duplicate_use()
    print("PASS test_density_state_alias_is_duplicate_use")
    test_density_state_measure_consumes()
    print("PASS test_density_state_measure_consumes")
    print("OK - LISS-0114 Slice D Phase 1 Red")


if __name__ == "__main__":
    main()
