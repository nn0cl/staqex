"""AT-TDD Phase 1 Red: LISS-0498 callable/object runtime-plan contract."""

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
package liss0498
class Box {
    Float x = 3.0
    pub fn doubled() -> Float { return this.x + this.x }
}
pub fn main() -> Unit {
    Box b = Box()
    Float y = b.doubled()
    State observed = Coin()
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


def test_callable_plan_is_classified_explicitly() -> None:
    plan = _plan(_compiled())

    assert plan.family == "callable"


def test_callable_plan_conserves_declaration_invocation_and_receiver_provenance() -> None:
    plan = _plan(_compiled())

    assert plan.callables
    for callable_node in plan.callables:
        assert callable_node.declaration_source_node_ids
        assert callable_node.invocation_source_node_ids
        assert callable_node.receiver_source_node_id
        assert callable_node.output_source_node_id
        assert callable_node.authority == "scientific_semantic_ir"
        assert callable_node.provenance
        assert callable_node.execution_status


def test_canonical_execution_uses_callable_executor(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    compiled = _compiled()

    def legacy_path_must_not_run(*args: object, **kwargs: object) -> object:
        raise AssertionError("callable/object mechanics must not use legacy AST body")

    monkeypatch.setattr(Evaluator, "_run_legacy_ast_body", legacy_path_must_not_run)
    executor = getattr(Evaluator, "_execute_callable_plan", None)
    assert executor is not None, "callable executor must be explicit"


def test_callable_plan_does_not_implicitly_create_target_realization() -> None:
    plan = _plan(_compiled())

    assert not getattr(plan, "has_implicit_realization", False)
