"""AT-TDD Phase 1 Red tests for the terminal POVM contract."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.host import run_source  # noqa: E402


def _main(body: str) -> str:
    return f"""
    package t
    pub fn main() -> Unit {{
        {body}
    }}
    """


def _codes(result) -> set[str]:
    return {diagnostic.get("code") for diagnostic in result.diagnostics}


def test_terminal_povm_measures_pure_state() -> None:
    result = run_source(
        _main(
            """
            State<Qubit> psi = |0>
            POVM<Qubit> z_basis = ComputationalBasis()
            Measure psi with z_basis
            """
        )
    )

    assert result.status == "succeeded", result.diagnostics
    assert result.measurements[0].marginal == {0: 1.0}


def test_terminal_povm_measures_density_state_without_raw_matrix() -> None:
    result = run_source(
        _main(
            """
            DensityState<Qubit> rho = DensityState(
                RawMatrix([[0.25, 0.0], [0.0, 0.75]])
            )
            POVM<Qubit> z_basis = ComputationalBasis()
            Measure rho with z_basis
            """
        )
    )

    assert result.status == "succeeded", result.diagnostics
    assert result.measurements[0].marginal == {0: 0.25, 1: 0.75}
    assert result.metadata["state_type"] == "DensityState"
    assert "density_matrix" not in result.metadata


def test_povm_domain_mismatch_is_hard_rejected() -> None:
    result = run_source(
        _main(
            """
            DensityState<Qubit> rho = DensityState(
                RawMatrix([[1.0, 0.0], [0.0, 0.0]])
            )
            POVM<Position> position_basis = ComputationalBasis()
            Measure rho with position_basis
            """
        )
    )

    assert result.status == "failed"
    assert "POVM_DOMAIN_MISMATCH" in _codes(result)


if __name__ == "__main__":
    for test in (
        test_terminal_povm_measures_pure_state,
        test_terminal_povm_measures_density_state_without_raw_matrix,
        test_povm_domain_mismatch_is_hard_rejected,
    ):
        test()
    print("OK — POVM measurement contract Red tests")
