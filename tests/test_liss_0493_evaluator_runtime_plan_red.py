"""AT-TDD Phase 1 Red: LISS-0493 internal runtime-plan contract."""

from __future__ import annotations

from dataclasses import replace
import io
from pathlib import Path
import sys

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator, KernelDiagnosticError  # noqa: E402
from compiler.staqex import scientific_semantic_ir  # noqa: E402


SOURCE = """
package liss0493
pub fn main() -> Unit {
    State a = Coin()
    Measure a
}
"""


def _compiled():
    compiled = compile_source(SOURCE)
    assert compiled.ok, compiled.diagnostics
    assert compiled.unit is not None
    assert compiled.scientific_semantic_ir is not None
    return compiled


def _build_plan(compiled):
    builder = getattr(scientific_semantic_ir, "build_runtime_execution_plan", None)
    assert builder is not None, "runtime plan must be built from ScientificSemanticIR"
    return builder(compiled.scientific_semantic_ir)


def test_runtime_plan_is_built_from_one_compile_owned_semantic_snapshot() -> None:
    compiled = _compiled()
    plan = _build_plan(compiled)

    assert plan.semantic_identity is compiled.scientific_semantic_ir
    assert plan.authority == "scientific_semantic_ir"


def test_runtime_plan_nodes_conserve_source_identity_and_provenance() -> None:
    compiled = _compiled()
    plan = _build_plan(compiled)

    assert plan.nodes
    assert all(node.source_node_id for node in plan.nodes)
    assert all(node.provenance for node in plan.nodes)
    assert all(node.authority == "scientific_semantic_ir" for node in plan.nodes)


def test_unresolved_semantic_meaning_fails_closed_without_partial_plan() -> None:
    compiled = _compiled()
    unresolved = replace(compiled.scientific_semantic_ir, authority="unresolved")

    with pytest.raises(KernelDiagnosticError):
        getattr(scientific_semantic_ir, "build_runtime_execution_plan")(unresolved)


def test_canonical_execution_does_not_dispatch_through_ast_top_level_runner(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    compiled = _compiled()

    def ast_dispatch_must_not_run(*args: object, **kwargs: object) -> object:
        raise AssertionError("canonical execution must consume the runtime plan")

    monkeypatch.setattr(Evaluator, "_run_unit_body", ast_dispatch_must_not_run)
    result = Evaluator(seed=0).run_canonical_unit(
        compiled.unit,
        semantic_ir=compiled.scientific_semantic_ir,
        stdout=io.StringIO(),
    )

    assert result.execution_authority == "scientific_semantic_ir"
    assert result.measure is not None


def test_first_family_does_not_use_legacy_runtime_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    compiled = _compiled()

    def legacy_fallback_must_not_run(*args: object, **kwargs: object) -> object:
        raise AssertionError("first runtime family must not use legacy fallback")

    monkeypatch.setattr(Evaluator, "_run_legacy_ast_body", legacy_fallback_must_not_run)
    result = Evaluator(seed=0).run_canonical_unit(
        compiled.unit,
        semantic_ir=compiled.scientific_semantic_ir,
        stdout=io.StringIO(),
    )

    assert result.measure is not None
