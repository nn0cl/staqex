"""AT-TDD: LISS-0148 Basis<N> binder domain expansion (ADR 0118)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.finite_binder import lower_finite_binder_operators  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {d.get("code", "") for d in compile_source(source).diagnostics}


def test_basis_binder_domain_lowers() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        QubitRegister<2> register = system()
        Operator H = Sigma (i In Basis<2>) { Z[i] }
        State a = |0>
        Measure a
    }
    """
    codes = _codes(source)
    assert "PARSE_ERROR" not in codes, codes
    assert "BINDER_DOMAIN_ERROR" not in codes, codes
    compiled = compile_source(source)
    assert compiled.unit is not None
    lowered, diags = lower_finite_binder_operators(compiled.unit)
    assert not diags, diags
    assert "H" in lowered


def test_rev_basis_binder_domain_lowers() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        QubitRegister<2> register = system()
        Operator H = Sigma (i In rev(Basis<2>)) { Z[i] }
        State a = |0>
        Measure a
    }
    """
    codes = _codes(source)
    assert "BINDER_DOMAIN_ERROR" not in codes, codes
    compiled = compile_source(source)
    assert compiled.unit is not None
    lowered, diags = lower_finite_binder_operators(compiled.unit)
    assert not diags, diags
    assert "H" in lowered


def test_energy_level_binder_domain_still_deferred() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            QubitRegister<2> register = system()
            Operator H = Sigma (i In EnergyLevel<2>) { Z[i] }
            State a = |0>
            Measure a
        }
        """
    )
    assert "BINDER_DOMAIN_ERROR" in codes


if __name__ == "__main__":
    test_basis_binder_domain_lowers()
    print("PASS test_basis_binder_domain_lowers")
    test_rev_basis_binder_domain_lowers()
    print("PASS test_rev_basis_binder_domain_lowers")
    test_energy_level_binder_domain_still_deferred()
    print("PASS test_energy_level_binder_domain_still_deferred")
