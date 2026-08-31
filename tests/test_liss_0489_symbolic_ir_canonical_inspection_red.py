"""AT-TDD Phase 1 Red: LISS-0489 canonical symbolic inspection."""

from __future__ import annotations

from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex import pipeline
from compiler.staqex import symbolic_ir as symbolic_ir_module
from compiler.staqex.pipeline import compile_source


SOURCE = """
package t
pub fn main() -> Unit {
    Operator H = X + Z
    State psi = |0>
    Measure psi
}
"""


def _compiled():
    compiled = compile_source(SOURCE)
    assert compiled.ok, compiled.diagnostics
    assert compiled.scientific_semantic_ir is not None
    assert compiled.semantic_inspection is not None
    return compiled


def test_symbolic_view_shares_canonical_source_ids() -> None:
    compiled = _compiled()
    assert compiled.symbolic_ir is not None
    assert compiled.symbolic_ir["resolved"]["source_node_ids"] == list(
        compiled.semantic_inspection.source_node_ids
    )


def test_legacy_ast_symbolic_builder_is_not_used_as_authority(monkeypatch) -> None:
    calls = []
    original = symbolic_ir_module.build_symbolic_ir

    def record(unit):
        calls.append(unit)
        return original(unit)

    monkeypatch.setattr(symbolic_ir_module, "build_symbolic_ir", record)
    monkeypatch.setattr(pipeline, "build_symbolic_ir", record)
    _compiled()
    assert calls == [], "canonical inspection must not rebuild from the AST"


def test_symbolic_view_preserves_canonical_structure_and_provenance() -> None:
    compiled = _compiled()
    assert compiled.symbolic_ir is not None
    assert compiled.symbolic_ir["provenance"][0]["metadata"]["semantic_authority"] == (
        "scientific_semantic_ir"
    )


def test_exact_symbolic_inspection_has_no_finite_allocation_or_collapse() -> None:
    compiled = _compiled()
    assert compiled.semantic_inspection.allocation_record is None
    assert compiled.semantic_inspection.collapse_record is None
    assert compiled.symbolic_ir is not None
    assert compiled.symbolic_ir["resolved"]["approximations"] == []
    assert "allocation" not in compiled.symbolic_ir["resolved"]
    assert "finite_plan" not in compiled.symbolic_ir["resolved"]


def test_unresolved_canonical_meaning_publishes_no_partial_symbolic_artifact() -> None:
    compiled = _compiled()
    assert compiled.semantic_rejection is not None
    assert compiled.symbolic_ir is not None
    assert "finite_plan" not in compiled.symbolic_ir["resolved"]


def test_repeated_inspection_reuses_one_canonical_snapshot() -> None:
    compiled = _compiled()
    assert compiled.semantic_inspection is compiled.semantic_snapshot
    assert compiled.semantic_inspection.source_node_ids == tuple(
        node.node_id for node in compiled.scientific_semantic_ir.nodes
    )
