"""AT-TDD Phase 1 Red: LISS-0496 evolution plan contract."""

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
package liss0496
pub fn main() -> Unit {
    State evolved = Evolve (0) times 1 { 0 }
    Measure evolved
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


def test_evolution_plan_is_classified_explicitly() -> None:
    plan = _plan(_compiled())

    assert plan.family == "evolution"


def test_evolution_conserves_sources_and_realization_evidence() -> None:
    plan = _plan(_compiled())

    assert plan.evolutions
    for evolution in plan.evolutions:
        assert evolution.input_source_node_ids
        assert evolution.output_source_node_id
        assert evolution.hamiltonian_source_node_id
        assert evolution.duration_source_node_id
        assert evolution.authority == "scientific_semantic_ir"
        assert evolution.provenance
        assert evolution.realization_status


def test_canonical_execution_uses_evolution_executor(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    compiled = _compiled()

    def legacy_path_must_not_run(*args: object, **kwargs: object) -> object:
        raise AssertionError("evolution must not use legacy AST body")

    monkeypatch.setattr(Evaluator, "_run_legacy_ast_body", legacy_path_must_not_run)
    executor = getattr(Evaluator, "_execute_evolution_plan", None)
    assert executor is not None, "evolution executor must be explicit"
    result = Evaluator(seed=0).run_canonical_unit(
        compiled.unit,
        semantic_ir=compiled.scientific_semantic_ir,
        stdout=io.StringIO(),
    )

    assert result.measure is not None


def test_evolution_does_not_implicitly_create_target_realization() -> None:
    plan = _plan(_compiled())

    assert not getattr(plan, "has_implicit_realization", False)
