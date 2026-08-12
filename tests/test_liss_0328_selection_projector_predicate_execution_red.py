"""AT-TDD: LISS-0328 real `project ... onto feasible(...)` Projector
execution (ADR 0194 Follow-up item 2)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.host import run_source  # noqa: E402

_MAIN = """
package t
pub fn main() -> Unit {{
    State selection = prepare_selection(3)
    State feasible_selection = project selection onto feasible({predicates})
    measure feasible_selection
}}
"""


def _run(predicates: str, inputs: dict | None = None):
    settings: dict = {"target": "local", "seed": 0}
    if inputs is not None:
        settings["inputs"] = inputs
    return run_source(_MAIN.format(predicates=predicates), settings=settings)


def test_exactly_selected_filters_to_matching_patterns() -> None:
    result = _run("exactly_selected = 2")

    assert result.status == "succeeded", result.diagnostics
    pattern = result.measurements[0].value
    assert not result.measurements[0].vacuum
    assert sum(pattern) == 2


def test_pairwise_compatible_rejects_an_incompatible_pair() -> None:
    compat = [
        [True, False, True],
        [False, True, True],
        [True, True, True],
    ]
    result = _run(
        "exactly_selected = 2, pairwise_compatible = true",
        inputs={"pairwise_compatible": compat},
    )

    assert result.status == "succeeded", result.diagnostics
    pattern = result.measurements[0].value
    assert not result.measurements[0].vacuum
    assert not (pattern[0] == 1 and pattern[1] == 1)


def test_diversity_at_least_rejects_a_below_threshold_pair() -> None:
    diversity = [
        [0.0, 1.0, 5.0],
        [1.0, 0.0, 5.0],
        [5.0, 5.0, 0.0],
    ]
    result = _run(
        "exactly_selected = 2, diversity_at_least = 2.0",
        inputs={"diversity_at_least": diversity},
    )

    assert result.status == "succeeded", result.diagnostics
    pattern = result.measurements[0].value
    assert not result.measurements[0].vacuum
    assert not (pattern[0] == 1 and pattern[1] == 1)


def test_missing_required_host_input_fails_closed() -> None:
    result = _run("pairwise_compatible = true")

    assert result.status == "failed"
    codes = {d.get("code") for d in result.diagnostics}
    assert "HOST_INPUT_BINDING_MISSING" in codes


def test_unsatisfiable_constraint_produces_vacuum_not_a_silent_pass() -> None:
    result = _run("exactly_selected = 5")

    assert result.status == "succeeded", result.diagnostics
    assert result.measurements[0].vacuum
