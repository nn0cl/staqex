"""Acceptance tests for the H1 ordered State Transformer plan."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


_SOURCE = """
theory Ising {
  parameter J: Energy
  operator H(J) = J * Z[0]
}
experiment quench(J = 1.0) {
  prepare |+>
  Evolve under H for 0.7
  observable energy = expect(H)
  Measure
}
"""


def test_h1_4_builds_ordered_state_transform_plan() -> None:
    compiled = compile_source(_SOURCE)

    assert not compiled.diagnostics
    plan = compiled.state_transform_plan
    assert plan is not None
    assert [step.kind for step in plan.steps] == [
        "Prepare",
        "Evolve",
        "Observe",
        "TerminalMeasure",
    ]
    assert all(step.origin.line > 0 for step in plan.steps)


def test_h1_4_rejects_operation_after_terminal_measure() -> None:
    compiled = compile_source(
        _SOURCE.replace(
            "  Measure\n",
            "  Measure\n  observable after_measure = expect(H)\n",
        )
    )

    assert "H1_MEASURE_NOT_TERMINAL" in {
        str(diagnostic.get("code", ""))
        for diagnostic in compiled.diagnostics
    }
    assert compiled.state_transform_plan is None


def test_h1_4_keeps_observe_distinct_from_terminal_measure() -> None:
    compiled = compile_source(_SOURCE)

    plan = compiled.state_transform_plan
    assert plan is not None
    observe_steps = [step for step in plan.steps if step.kind == "Observe"]
    measure_steps = [
        step for step in plan.steps if step.kind == "TerminalMeasure"
    ]
    assert len(observe_steps) == 1
    assert len(measure_steps) == 1


if __name__ == "__main__":
    test_h1_4_builds_ordered_state_transform_plan()
    test_h1_4_rejects_operation_after_terminal_measure()
    test_h1_4_keeps_observe_distinct_from_terminal_measure()
    print("OK — H1-4 State Transformer plan Red tests")
