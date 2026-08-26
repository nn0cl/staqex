"""Phase 1 Red tests for LISS-0326: real BASIS_MISMATCH_ERROR /
TARGET_CAPABILITY_REJECT checks for H1 theories.

The two existing positive scenarios
(`tests/test_h1_hamiltonian_authoring_red.py::test_h1_basis_mismatch_is_a_physics_diagnostic`
and `::test_h1_invalid_target_rejects_without_rewriting_the_model`) already
cover "the diagnostic fires for the original fixture's exact wording" and are
not duplicated here. This file adds the negative-control scenarios that the
pre-fix substring heuristic gets wrong in both directions -- see the kernel
stub and placeholder registry's H1 authoring layer entry for the documented
false positive/negative evidence this closes.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {str(diagnostic.get("code", "")) for diagnostic in compile_source(source).diagnostics}


def test_renamed_identifiers_still_detect_basis_mismatch() -> None:
    """The pre-fix substring check only matched the literal spellings
    `basis position_grid` / `state spin`; a real mismatch under different
    names must still be caught."""

    codes = _codes(
        """
        theory PositionModel {
          basis grid_position = UniformGrid(-1.0, 1.0, 8)
          operator H = PositionOperator
        }

        experiment run() {
          State spin_carrier = |+>
          spin_carrier |> Evolve under PositionModel.H for 0.7
          Measure spin_carrier
        }
        """
    )

    assert "BASIS_MISMATCH_ERROR" in codes


def test_unrelated_cooccurrence_does_not_fire_basis_mismatch() -> None:
    """The pre-fix substring check fires on textual co-occurrence alone,
    even with no dependency between the theory's basis and the state."""

    codes = _codes(
        """
        theory PositionModel {
          basis position_grid = UniformGrid(-1.0, 1.0, 8)
          operator H = PositionOperator
        }

        experiment run() {
          State spin = |0>
          Measure spin
        }
        """
    )

    assert "BASIS_MISMATCH_ERROR" not in codes


def test_correctly_bound_state_does_not_fire_basis_mismatch() -> None:
    """A state prepared `over` the same theory's declared basis must not be
    flagged."""

    codes = _codes(
        """
        theory PositionModel {
          basis position_grid = UniformGrid(-1.0, 1.0, 8)
          operator H = PositionOperator
        }

        experiment run() {
          State psi = prepare plus over PositionModel.position_grid
          psi |> Evolve under PositionModel.H for 0.7
          Measure psi
        }
        """
    )

    assert "BASIS_MISMATCH_ERROR" not in codes


def test_small_coordinate_size_does_not_reject_a_real_target() -> None:
    """TARGET_CAPABILITY_REJECT must compare the declared coordinate size
    against the named target's real capacity, not fire on textual
    co-occurrence with an unrelated fixed literal."""

    codes = _codes(
        """
        theory SmallModel {
          coordinate site: Lattice<4>
          operator H = sum(site, Z[i])
        }

        experiment run() {
          State psi = prepare plus over SmallModel.site
          psi |> Evolve under SmallModel.H for 0.7
          Measure psi
        }

        realize qpu:NH5_REFERENCE
        """
    )

    assert "TARGET_CAPABILITY_REJECT" not in codes
