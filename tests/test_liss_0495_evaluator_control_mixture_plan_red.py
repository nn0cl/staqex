"""AT-TDD Phase 1 Red: LISS-0495 control-mixture plan contract."""

from __future__ import annotations

import io
from pathlib import Path
import sys

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402
from compiler.staqex import scientific_semantic_ir  # noqa: E402


SOURCE = """
package liss0495
pub fn main() -> Unit {
    State bit = Coin()
    State result = Mix (bit) {
        0 -> |0>,
        else -> |1>,
    }
    Measure result
}
"""


def _compiled():
    compiled = compile_source(SOURCE)
    assert compiled.ok, compiled.diagnostics
    assert compiled.unit is not None
    assert compiled.scientific_semantic_ir is not None
    return compiled


def _plan(compiled):
    builder = getattr(scientific_semantic_ir, "build_runtime_execution_plan", None)
    assert builder is not None
    return builder(compiled.scientific_semantic_ir)


def test_control_mixture_plan_is_classified_explicitly() -> None:
    plan = _plan(_compiled())

    assert plan.family == "control_mixture"


def test_control_mixture_conserves_control_and_branch_provenance() -> None:
    plan = _plan(_compiled())

    assert plan.controls
    for control in plan.controls:
        assert control.control_source_node_id
        assert control.branch_rules
        assert control.authority == "scientific_semantic_ir"
        assert control.provenance


def test_canonical_execution_uses_control_mixture_executor(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    compiled = _compiled()

    def legacy_path_must_not_run(*args: object, **kwargs: object) -> object:
        raise AssertionError("control mixture must not use legacy AST body")

    monkeypatch.setattr(Evaluator, "_run_legacy_ast_body", legacy_path_must_not_run)
    executor = getattr(Evaluator, "_execute_control_mixture_plan", None)
    assert executor is not None, "control mixture executor must be explicit"
    result = Evaluator(seed=0).run_canonical_unit(
        compiled.unit,
        semantic_ir=compiled.scientific_semantic_ir,
        stdout=io.StringIO(),
    )

    assert result.measure is not None


def test_control_mixture_preserves_all_eligible_worldlines_until_measure() -> None:
    compiled = _compiled()
    result = Evaluator(seed=0).run_canonical_unit(
        compiled.unit,
        semantic_ir=compiled.scientific_semantic_ir,
        stdout=io.StringIO(),
    )

    assert len(result.joint.worlds) >= 2
    assert result.measure is not None
