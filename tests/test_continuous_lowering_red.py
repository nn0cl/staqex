"""AT-TDD Red/Green: discretization bridge numerical lowering (LISS-0111)."""

from __future__ import annotations

import math
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.run import run_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compile_source(source).diagnostics}


_BRIDGE_PROGRAM = """
theory HarmonicOscillator { Operator H = 5.272859e-20 * (X * X + P * P) }
discretization PositionGrid {
    domain = Position
    basis = UniformGrid
    resolution = 8
    boundary = Periodic
    approximation = FiniteDifference(order = 2)
}
use PositionGrid for HarmonicOscillator.H as discrete_H
pub fn main() -> Unit {
    Operator H = discrete_H
    State psi = wavepacket(-pi, pi, 8, 0.0, 1.0)
    State psi = Evolve { psi under H for 0.1.fs }.run()
    Measure psi
}
"""

_DIRECT_GRID_PROGRAM = """
pub fn main() -> Unit {
    State psi = wavepacket(-pi, pi, 8, 0.0, 1.0)
    Operator H_grid = 5.272859e-20 * (X * X + P * P)
    State psi = Evolve { psi under H_grid for 0.1.fs }.run()
    Measure psi
}
"""


def test_bridge_lowering_produces_finite_grid_hamiltonian() -> None:
    compiled = compile_source(_BRIDGE_PROGRAM)

    assert compiled.ok, compiled.diagnostics
    assert compiled.grid_hamiltonians is not None
    assert "discrete_H" in compiled.grid_hamiltonians
    grid = compiled.grid_hamiltonians["discrete_H"]
    assert grid.sealed is True
    assert len(grid.xs) == 8
    assert len(grid.matrix) == 8
    assert all(len(row) == 8 for row in grid.matrix)


def test_bridge_alias_evolve_runs_on_kernel() -> None:
    result = run_source(_BRIDGE_PROGRAM, seed=7)

    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert abs(sum(abs(w.amp) ** 2 for w in result.eval.joint.worlds) - 1.0) < 1e-9


def test_non_mvp_discretization_contract_is_rejected_at_lowering() -> None:
    codes = _codes(
        """
        theory HarmonicOscillator { Operator H = X + P }
        discretization MomentumGrid {
            domain = Momentum
            basis = UniformGrid
            resolution = 8
            boundary = Periodic
            approximation = FiniteDifference(order = 2)
        }
        use MomentumGrid for HarmonicOscillator.H as discrete_H
        pub fn main() -> Unit {
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert "DISCRETIZATION_LOWERING_ERROR" in codes


def test_bridge_evolve_matches_direct_grid_hamiltonian() -> None:
    bridge = run_source(_BRIDGE_PROGRAM, seed=11)
    direct = run_source(_DIRECT_GRID_PROGRAM, seed=11)

    assert bridge.compile_ok, bridge.diagnostics
    assert direct.compile_ok, direct.diagnostics
    bridge_marginal = bridge.eval.joint.amplitude_marginal("psi")
    direct_marginal = direct.eval.joint.amplitude_marginal("psi")
    assert set(bridge_marginal) == set(direct_marginal)
    for key in bridge_marginal:
        assert abs(abs(bridge_marginal[key]) - abs(direct_marginal[key])) < 1e-6


def test_lowering_grid_matches_periodic_uniform_abscissae() -> None:
    compiled = compile_source(_BRIDGE_PROGRAM)
    grid = compiled.grid_hamiltonians["discrete_H"]
    expected = [
        -math.pi + (2.0 * math.pi) * index / 8.0 for index in range(8)
    ]
    assert len(grid.xs) == len(expected)
    for actual, want in zip(grid.xs, expected):
        assert abs(actual - want) < 1e-12


if __name__ == "__main__":
    test_bridge_lowering_produces_finite_grid_hamiltonian()
    test_bridge_alias_evolve_runs_on_kernel()
    test_non_mvp_discretization_contract_is_rejected_at_lowering()
    test_bridge_evolve_matches_direct_grid_hamiltonian()
    test_lowering_grid_matches_periodic_uniform_abscissae()
    print("OK — continuous lowering tests")
