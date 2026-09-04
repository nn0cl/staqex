"""AT-TDD Phase 1 Red: LISS-0497 binder runtime-plan contract."""

from __future__ import annotations

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
package liss0497
pub fn main() -> Unit {
    QubitRegister<3> register = system()
    Operator H = Sigma (i In 0..1) { 1.0 * Z[i] * Z[next(i)] }
    State<Int> observed = Coin()
    Measure observed
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


def test_binder_plan_is_classified_explicitly() -> None:
    plan = _plan(_compiled())

    assert plan.family == "binder"


def test_binder_plan_conserves_domain_body_output_and_provenance() -> None:
    plan = _plan(_compiled())

    assert plan.binders
    for binder in plan.binders:
        assert binder.source_node_id
        assert binder.domain_source_node_id
        assert binder.body_source_node_id
        assert binder.output_source_node_id
        assert binder.authority == "scientific_semantic_ir"
        assert binder.provenance
        assert binder.realization_status


def test_canonical_execution_uses_binder_executor(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    compiled = _compiled()

    def legacy_path_must_not_run(*args: object, **kwargs: object) -> object:
        raise AssertionError("binder must not use legacy AST body")

    monkeypatch.setattr(Evaluator, "_run_legacy_ast_body", legacy_path_must_not_run)
    executor = getattr(Evaluator, "_execute_binder_plan", None)
    assert executor is not None, "binder executor must be explicit"


def test_binder_plan_does_not_implicitly_create_target_realization() -> None:
    plan = _plan(_compiled())

    assert not getattr(plan, "has_implicit_realization", False)
