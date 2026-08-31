"""AT-TDD Phase 1 Red: LISS-0488 canonical Physics IR projection."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex.pipeline import compile_source
from compiler.staqex import physics_ir_lower
from compiler.staqex.scientific_semantic_ir import semantic_fingerprint


SOURCE = (REPO / "tests/fixtures/semantic_consumer_migration/physics_ir_projection.sqx").read_text(
    encoding="utf-8"
)


def _compiled():
    compiled = compile_source(SOURCE)
    assert compiled.ok, compiled.diagnostics
    assert compiled.scientific_semantic_ir is not None
    return compiled


def _project(compiled):
    project = getattr(physics_ir_lower, "build_physics_projection", None)
    assert callable(project), "Physics IR must expose the canonical projection API"
    return project(compiled.scientific_semantic_ir)


def test_projection_preserves_canonical_identity_and_semantic_fields() -> None:
    compiled = _compiled()
    projection = _project(compiled)
    assert projection.metadata["semantic_authority"] == "scientific_semantic_ir"
    assert tuple(node.node_id for node in projection.nodes) == tuple(
        node.node_id for node in compiled.scientific_semantic_ir.nodes
    )


def test_caller_owned_semantic_ir_cannot_be_projection_authority() -> None:
    compiled = _compiled()
    caller_owned = replace(compiled.scientific_semantic_ir, source_id="caller.sqx")
    project = getattr(physics_ir_lower, "build_physics_projection", None)
    assert callable(project), "projection API must validate compile-owned identity"
    try:
        project(caller_owned, expected=compiled.scientific_semantic_ir)
    except (TypeError, ValueError):
        return
    raise AssertionError("caller-owned semantic IR must not authorize projection")


def test_lossy_projection_returns_diagnostic_without_partial_artifact() -> None:
    compiled = _compiled()
    projection = _project(compiled)
    assert projection.module is None
    assert projection.diagnostics


def test_exact_semantics_do_not_create_finite_artifacts() -> None:
    compiled = _compiled()
    projection = _project(compiled)
    assert projection.finite_plan is None
    assert projection.allocation is None


def test_equation_dto_metadata_remains_diagnostic_only() -> None:
    compiled = _compiled()
    projection = _project(compiled)
    assert projection.metadata["equation_dto_role"] == "diagnostic_only"
    assert projection.metadata["injected_equation_authorized"] is False


def test_same_semantic_snapshot_projects_once_with_stable_fingerprint() -> None:
    compiled = _compiled()
    first = _project(compiled)
    second = _project(compiled)
    assert semantic_fingerprint(compiled.scientific_semantic_ir) == semantic_fingerprint(
        compiled.scientific_semantic_ir
    )
    assert first.fingerprint == second.fingerprint
