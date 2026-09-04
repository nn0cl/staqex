"""AT-TDD Phase 1 Red: LISS-0494 pure-transformation plan contract."""

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
package liss0494
fn add_one(s: State<Int>) -> State<Int> {
    return s + 1
}
pub fn main() -> Unit {
    State a = |0>
    State b = a |> add_one
    Measure b
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


def test_pure_transformation_plan_is_classified_explicitly() -> None:
    plan = _plan(_compiled())

    assert plan.family == "pure_transformation"


def test_pure_transformation_conserves_input_output_identity_and_provenance() -> None:
    plan = _plan(_compiled())

    assert plan.transformations
    for transformation in plan.transformations:
        assert transformation.input_source_node_ids
        assert transformation.output_source_node_id
        assert transformation.authority == "scientific_semantic_ir"
        assert transformation.provenance


def test_canonical_execution_uses_pure_transformation_executor(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    compiled = _compiled()

    def legacy_path_must_not_run(*args: object, **kwargs: object) -> object:
        raise AssertionError("pure transformation must not use legacy AST body")

    monkeypatch.setattr(Evaluator, "_run_legacy_ast_body", legacy_path_must_not_run)
    executor = getattr(Evaluator, "_execute_pure_transformation_plan", None)
    assert executor is not None, "pure transformation executor must be explicit"
    result = Evaluator(seed=0).run_canonical_unit(
        compiled.unit,
        semantic_ir=compiled.scientific_semantic_ir,
        stdout=io.StringIO(),
    )

    assert result.measure is not None


def test_pure_transformation_preserves_state_until_terminal_measure() -> None:
    compiled = _compiled()
    result = Evaluator(seed=0).run_canonical_unit(
        compiled.unit,
        semantic_ir=compiled.scientific_semantic_ir,
        stdout=io.StringIO(),
    )

    assert result.joint.worlds
    assert result.measure is not None
