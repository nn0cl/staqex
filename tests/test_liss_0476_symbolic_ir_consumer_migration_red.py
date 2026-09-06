"""LISS-0476 / WP-0107 Phase 1 Red contracts.

These tests describe the remaining non-explicit ``symbolic_ir`` migration.
They intentionally fail until the compile pipeline stops constructing a live
Symbolic IR compatibility projection for migrated consumers.
"""

from __future__ import annotations

from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import compiler.staqex.pipeline as pipeline_module
from compiler.staqex.pipeline import compile_path


ORDINARY_GATE = REPO / "tests/fixtures/semantic_consumer_migration/ordinary_gate.sqx"


def test_non_explicit_compile_does_not_expose_symbolic_ir_authority() -> None:
    compiled = compile_path(ORDINARY_GATE)

    assert compiled.ok, compiled.diagnostics
    assert compiled.scientific_semantic_ir is not None
    assert compiled.semantic_inspection is not None
    assert compiled.execution_authority == "scientific_semantic_ir"
    assert compiled.symbolic_ir is None


def test_non_explicit_consumers_do_not_rebuild_symbolic_ir(monkeypatch) -> None:
    def fail_if_called(*_args, **_kwargs):
        raise AssertionError(
            "migrated non-explicit consumers must not call build_symbolic_ir"
        )

    monkeypatch.setattr(pipeline_module, "build_symbolic_ir", fail_if_called)
    compiled = compile_path(ORDINARY_GATE)

    assert compiled.ok, compiled.diagnostics
    assert compiled.semantic_inspection is not None


def test_inspection_is_compile_owned_and_preserves_source_provenance() -> None:
    compiled = compile_path(ORDINARY_GATE)

    assert compiled.scientific_semantic_ir is not None
    assert compiled.semantic_inspection is not None
    inspection = compiled.semantic_inspection
    canonical = compiled.scientific_semantic_ir

    assert inspection.structural_tree is canonical.nodes
    assert inspection.source_node_ids == tuple(node.node_id for node in canonical.nodes)
    assert all(node.provenance.source == "sqx" for node in inspection.structural_tree)
    assert canonical.source_id.endswith("ordinary_gate.sqx")


def test_exact_symbolic_inspection_has_no_finite_or_collapse_artifact() -> None:
    compiled = compile_path(ORDINARY_GATE)

    assert compiled.semantic_inspection is not None
    inspection = compiled.semantic_inspection

    assert inspection.exactness in {"exact", "unresolved"}
    assert inspection.allocation_record is None
    assert inspection.collapse_record is None
