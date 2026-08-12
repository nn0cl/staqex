"""Acceptance tests for the quantum composition surface boundary.

The accepted design keeps ``mix``, ``superpose``, ``controlled``, and dynamic
feed-forward in distinct semantic lanes. These tests intentionally describe
the next contract; the ``superpose`` lane is not implemented yet.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {
        str(diagnostic.get("code", ""))
        for diagnostic in compile_source(source).diagnostics
    }


def test_superpose_has_a_distinct_coherent_lane() -> None:
    """A coherent composition must not fall back to the mixture lane."""

    compiled = compile_source(
        """
        theory Ising {
          operator H = Z[0]
        }
        experiment coherent() {
          State control = |+>
          State psi = |0>
          State result = superpose(control) {
            0 -> psi,
            1 -> psi,
          }
          measure result
        }
        """
    )

    assert compiled.state_transform_plan is not None
    kinds = [step.kind for step in compiled.state_transform_plan.steps]
    assert "CoherentSuperposition" in kinds
    assert "Mixture" not in kinds


def test_when_has_no_compatibility_fallback_to_mix() -> None:
    codes = _codes(
        """
        theory Ising {
          operator H = Z[0]
        }
        experiment legacy() {
          State control = |+>
          State result = when (control) {
            0 -> |0>,
            1 -> |1>,
          }
          measure result
        }
        """
    )

    assert "RETIRED_KEYWORD" in codes


if __name__ == "__main__":
    test_superpose_has_a_distinct_coherent_lane()
    test_when_has_no_compatibility_fallback_to_mix()
    print("GREEN — quantum composition surface boundary")
