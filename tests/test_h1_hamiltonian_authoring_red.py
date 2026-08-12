"""Acceptance tests for the H1 Hamiltonian-authoring slice.

The assertions are the reviewed Phase 1 contract; the current Phase 2
boundary implementation makes them Green.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _compile(source: str):
    return compile_source(source)


def _assert_accepts(source: str) -> None:
    compiled = _compile(source)
    assert not compiled.diagnostics, [
        {
            "code": diagnostic.get("code"),
            "message": diagnostic.get("message"),
        }
        for diagnostic in compiled.diagnostics
    ]


def test_h1_typed_theory_parameters_and_hamiltonian_expression() -> None:
    _assert_accepts(
        """
        theory Ising {
          parameter J: Energy
          parameter h: Energy
          operator H(J, h) = -J * (Z[0] * Z[1]) - h * (X[0] + X[1])
        }

        experiment run(J = 1.0, h = 0.5) {
          State psi = |+>
          psi |> Evolve under Ising.H(J, h) for 0.7
          Measure psi
        }
        """
    )


def test_h1_indexed_operator_sum_lowers_with_domain_metadata() -> None:
    compiled = _compile(
        """
        theory Chain {
          coordinate site: Lattice<4> with boundary Periodic
          parameter J: Energy
          operator H(J) = -J * sum(site.neighbor(i, j), Z[i] * Z[j])
        }

        experiment run(J = 1.0) {
          State psi = prepare plus over Chain.site
          psi |> Evolve under Chain.H(J) for 0.7
          Measure psi
        }
        """
    )
    assert not compiled.diagnostics
    assert compiled.physics_ir is not None
    assert compiled.physics_ir.source_origin is not None
    assert compiled.physics_ir.metadata["boundary"] == "Periodic"


def test_h1_observable_is_not_terminal_measurement() -> None:
    _assert_accepts(
        """
        theory Ising {
          operator H = Z[0] * Z[1]
        }

        experiment run() {
          State psi = |+> *|* |+>
          psi |> Evolve under Ising.H for 0.7
          observable energy = expect(Ising.H, psi)
          Measure psi
        }
        """
    )


def test_h1_basis_mismatch_is_a_physics_diagnostic() -> None:
    compiled = _compile(
        """
        theory PositionModel {
          basis position_grid = UniformGrid(-1.0, 1.0, 8)
          operator H = PositionOperator
        }

        experiment run() {
          State spin = |+>
          spin |> Evolve under PositionModel.H for 0.7
          Measure spin
        }
        """
    )
    codes = {str(diagnostic.get("code", "")) for diagnostic in compiled.diagnostics}
    assert "BASIS_MISMATCH_ERROR" in codes


def test_h1_invalid_target_rejects_without_rewriting_the_model() -> None:
    compiled = _compile(
        """
        theory LargeModel {
          coordinate site: Lattice<128>
          operator H = sum(site, Z[i])
        }

        experiment run() {
          State psi = prepare plus over LargeModel.site
          psi |> Evolve under LargeModel.H for 0.7
          Measure psi
        }

        realize qpu:NH5_REFERENCE
        """
    )
    codes = {str(diagnostic.get("code", "")) for diagnostic in compiled.diagnostics}
    assert "TARGET_CAPABILITY_REJECT" in codes
    assert "SILENT_GATE_REWRITE" not in codes


if __name__ == "__main__":
    for test in (
        test_h1_typed_theory_parameters_and_hamiltonian_expression,
        test_h1_indexed_operator_sum_lowers_with_domain_metadata,
        test_h1_observable_is_not_terminal_measurement,
        test_h1_basis_mismatch_is_a_physics_diagnostic,
        test_h1_invalid_target_rejects_without_rewriting_the_model,
    ):
        test()
