"""Acceptance tests for H1 operation characteristics."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _plan(source: str):
    compiled = compile_source(source)
    assert not compiled.diagnostics
    assert compiled.state_transform_plan is not None
    return compiled.state_transform_plan


def test_h1_6_evolve_is_unitary_and_adjointable() -> None:
    plan = _plan(
        """
        theory Ising {
          operator H = Z[0]
        }
        experiment evolve_run() {
          prepare |0>
          Evolve under H for 0.7
          Measure
        }
        """
    )

    Evolve = next(step for step in plan.steps if step.kind == "Evolve")
    assert {"Unitary", "Adj"}.issubset(set(Evolve.characteristics))
    assert "Channel" not in Evolve.characteristics


def test_h1_6_coherent_control_is_controllable() -> None:
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

    assert not compiled.diagnostics
    assert compiled.state_transform_plan is not None
    controlled = next(
        step
        for step in compiled.state_transform_plan.steps
        if step.kind == "CoherentControl"
    )
    assert {"Unitary", "Ctl"}.issubset(set(controlled.characteristics))
    assert compiled.quantum_semantic_ir is not None
    assert any(
        type(region).__name__ == "CoherentControlRegion"
        for region in compiled.quantum_semantic_ir.regions
    )


def test_h1_6_observe_and_measure_are_not_transform_characteristics() -> None:
    plan = _plan(
        """
        theory Ising {
          operator H = Z[0]
        }
        experiment observe_run() {
          prepare |0>
          observable energy = expect(H)
          Measure
        }
        """
    )

    for kind in ("Observe", "TerminalMeasure"):
        step = next(item for item in plan.steps if item.kind == kind)
        assert "Unitary" not in step.characteristics
        assert "Channel" not in step.characteristics


if __name__ == "__main__":
    test_h1_6_evolve_is_unitary_and_adjointable()
    test_h1_6_coherent_control_is_controllable()
    test_h1_6_observe_and_measure_are_not_transform_characteristics()
    print("OK — H1-6 operation characteristics Red tests")
