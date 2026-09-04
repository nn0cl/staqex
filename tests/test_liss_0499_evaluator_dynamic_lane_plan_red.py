"""AT-TDD Phase 1 Red: LISS-0499 dynamic-lane runtime-plan contract."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex import scientific_semantic_ir  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402


SOURCE = """
package liss0499
pub fn main() -> Unit {
    dynamic qpu {
        State q = |0>
        Controller<Bit> bit = Measure q
        match bit {
            0 => { }
            1 => { }
        }
    }
    State<Int> observed = Coin()
    Measure observed
}
"""


def _compiled():
    compiled = compile_source(SOURCE)
    assert compiled.unit is not None
    assert compiled.scientific_semantic_ir is not None
    return compiled


def _plan(compiled):
    builder = getattr(scientific_semantic_ir, "build_runtime_execution_plan", None)
    assert builder is not None
    return builder(compiled.scientific_semantic_ir)


def test_dynamic_lane_plan_is_classified_explicitly() -> None:
    plan = _plan(_compiled())

    assert plan.family == "dynamic_lane"


def test_dynamic_lane_plan_conserves_region_controller_and_branch_provenance() -> None:
    plan = _plan(_compiled())

    assert plan.dynamic_lanes
    for lane in plan.dynamic_lanes:
        assert lane.region_source_node_id
        assert lane.controller_source_node_id
        assert lane.control_source_node_ids
        assert lane.authority == "scientific_semantic_ir"
        assert lane.provenance
        assert lane.execution_status


def test_canonical_execution_uses_dynamic_lane_executor(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    compiled = _compiled()

    def legacy_path_must_not_run(*args: object, **kwargs: object) -> object:
        raise AssertionError("dynamic lane must not use legacy AST body")

    monkeypatch.setattr(Evaluator, "_run_legacy_ast_body", legacy_path_must_not_run)
    executor = getattr(Evaluator, "_execute_dynamic_lane_plan", None)
    assert executor is not None, "dynamic-lane executor must be explicit"


def test_dynamic_lane_plan_does_not_implicitly_create_target_realization() -> None:
    plan = _plan(_compiled())

    assert not getattr(plan, "has_implicit_realization", False)
