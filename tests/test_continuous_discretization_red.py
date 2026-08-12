"""AT-TDD Phase 1 Red: explicit continuous discretization (LISS-0036)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compile_source(source).diagnostics}


def test_discretization_contract_is_explicit_and_order_independent() -> None:
    compiled = compile_source(
        """
        package t
        theory Oscillator { Operator H = X + P }
        discretization PositionGrid {
            approximation = FiniteDifference(order = 2)
            boundary = Periodic
            resolution = 64
            basis = UniformGrid
            domain = Position
        }
        pub fn main() -> Unit {
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert compiled.ok, compiled.diagnostics
    assert compiled.discretization_contracts is not None
    contract = compiled.discretization_contracts["PositionGrid"]
    assert contract.domain == "Position"
    assert contract.basis == "UniformGrid"
    assert contract.resolution == "64"
    assert contract.boundary == "Periodic"
    assert contract.approximation == "FiniteDifference(order = 2)"


def test_continuous_lowering_without_contract_is_rejected() -> None:
    codes = _codes(
        """
        package t
        theory Oscillator {
            continuous_operator H = derivative(Position)
        }
        pub fn main() -> Unit {
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert "DISCRETIZATION_REQUIRED_ERROR" in codes


def test_discretization_bridge_preserves_theory_and_contract_provenance() -> None:
    compiled = compile_source(
        """
        package t
        use PositionGrid for HarmonicOscillator.H as discrete_H
        discretization PositionGrid {
            domain = Position
            basis = UniformGrid
            resolution = 64
            boundary = Periodic
            approximation = FiniteDifference(order = 2)
            error_bound = Unbounded
        }
        theory HarmonicOscillator { Operator H = X + P }
        pub fn main() -> Unit {
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert compiled.ok, compiled.diagnostics
    bridge = compiled.discretization_bridges["discrete_H"]
    assert bridge.contract == "PositionGrid"
    assert bridge.source == "HarmonicOscillator.H"
    assert compiled.symbolic_ir["resolved"]["discretizations"] == [
        {"alias": "discrete_H", "contract": "PositionGrid", "source": "HarmonicOscillator.H"}
    ]


def test_discretization_bridge_requires_known_contract_and_operator() -> None:
    codes = _codes(
        """
        package t
        use MissingGrid for HarmonicOscillator.H as discrete_H
        theory HarmonicOscillator { Operator H = X + P }
        pub fn main() -> Unit {
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert "DISCRETIZATION_BRIDGE_ERROR" in codes


if __name__ == "__main__":
    test_discretization_contract_is_explicit_and_order_independent()
    test_continuous_lowering_without_contract_is_rejected()
    test_discretization_bridge_preserves_theory_and_contract_provenance()
    test_discretization_bridge_requires_known_contract_and_operator()
    print("OK — continuous discretization Red tests")
