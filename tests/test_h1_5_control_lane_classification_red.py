"""Acceptance tests for H1 control-lane classification."""

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


def test_h1_5_when_is_classified_as_mixture_not_coherent_control() -> None:
    compiled = compile_source(
        """
        theory Ising {
          operator H = Z[0]
        }
        experiment classify() {
          Mix phase { Ground -> prepare |0>, Excited -> prepare |1> }
          Measure
        }
        """
    )

    assert compiled.state_transform_plan is not None
    kinds = [step.kind for step in compiled.state_transform_plan.steps]
    assert "Mixture" in kinds
    assert "CoherentControl" not in kinds
    assert "TerminalMeasure" in kinds


def test_h1_5_coherent_control_maps_to_semantic_region() -> None:
    compiled = compile_source(
        """
        theory Ising {
          operator H = Z[0]
        }
        experiment controlled() {
          prepare |00>
          capply(control, X, target)
          Measure
        }
        """
    )

    assert compiled.state_transform_plan is not None
    assert any(
        step.kind == "CoherentControl"
        for step in compiled.state_transform_plan.steps
    )
    assert compiled.quantum_semantic_ir is not None
    assert any(
        type(region).__name__ == "CoherentControlRegion"
        for region in compiled.quantum_semantic_ir.regions
    )


def test_h1_5_dynamic_feed_forward_is_rejected_in_static_kernel() -> None:
    codes = _codes(
        """
        theory Ising {
          operator H = Z[0]
        }
        experiment feedback() {
          prepare |0>
          Measure
          dynamic control measured -> correction
        }
        """
    )

    assert "H1_DYNAMIC_CONTROL_REQUIRES_DYNAMIC_LANE" in codes


if __name__ == "__main__":
    test_h1_5_when_is_classified_as_mixture_not_coherent_control()
    test_h1_5_coherent_control_maps_to_semantic_region()
    test_h1_5_dynamic_feed_forward_is_rejected_in_static_kernel()
    print("OK — H1-5 control-lane classification Red tests")
