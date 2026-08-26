"""AT-TDD: LISS-0140 binder honesty — no silent deferred carriers / unbound J[i]."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {d.get("code", "") for d in compile_source(source).diagnostics}


def test_energy_level_binder_domain_is_hard_diagnosed() -> None:
    """Basis expansion shipped (LISS-0148); other carriers remain honesty-only."""
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            QubitRegister<2> register = system()
            Operator H = Sigma (i In EnergyLevel<2>) { Z[i] }
            State a = |0>
            State b = |0>
            State (a, b) = Evolve { (a, b) under H for 0.1 using Suzuki(order = 2, steps = 2) }.run()
            Measure a
        }
        """
    )
    assert "BINDER_DOMAIN_ERROR" in codes


def test_unbound_indexed_coefficient_is_hard_diagnosed() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            QubitRegister<2> register = system()
            Operator H = Sigma (i In 0..0) { J[i] * Z[i] * Z[next(i)] }
            State a = |0>
            State b = |0>
            State (a, b) = Evolve { (a, b) under H for 0.1 using Suzuki(order = 2, steps = 2) }.run()
            Measure a
        }
        """
    )
    assert "BINDER_LOWERING_UNSUPPORTED" in codes


if __name__ == "__main__":
    test_energy_level_binder_domain_is_hard_diagnosed()
    print("PASS test_energy_level_binder_domain_is_hard_diagnosed")
    test_unbound_indexed_coefficient_is_hard_diagnosed()
    print("PASS test_unbound_indexed_coefficient_is_hard_diagnosed")
