"""LISS-0478 / WP-0113 Phase 1 Red contracts."""

from __future__ import annotations

from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex.codegen_qasm import OpenQASM3Generator
from compiler.staqex.pipeline import compile_path


SPEC = REPO / "docs/specs/staqex-semantic-ir-meaning-preservation.md"
ISSUE = REPO / "docs/issues/LISS-0478-interfer-phase-branch-meaning.md"
FIXTURE = REPO / "tests/fixtures/semantic_meaning/interfer_phase_branch.sqx"


def test_interfer_phase_branch_contract_names_meaning_fields() -> None:
    text = SPEC.read_text(encoding="utf-8") + ISSUE.read_text(encoding="utf-8")
    for required in (
        "operand identity",
        "control/branch relationships",
        "phase\nmetadata",
        "exactness",
        "dimensions",
        "source provenance",
        "unsupported finite projection",
        "no artifact",
    ):
        assert required in text


def test_phase_and_interference_are_distinct_canonical_meanings() -> None:
    compiled = compile_path(FIXTURE)

    assert compiled.ok, compiled.diagnostics
    assert compiled.scientific_semantic_ir is not None
    meanings = {node.meaning_kind for node in compiled.scientific_semantic_ir.nodes}

    assert "phase" in meanings
    assert "interference" in meanings


def test_branch_control_and_child_identity_survive_projection() -> None:
    compiled = compile_path(FIXTURE)

    assert compiled.scientific_semantic_ir is not None
    mixtures = [
        node
        for node in compiled.scientific_semantic_ir.nodes
        if node.kind == "WhenExpr"
    ]
    assert len(mixtures) == 2
    assert all(node.control_source_node_id for node in mixtures)
    assert all(node.child_source_node_ids for node in mixtures)
    assert all(node.branch_rules for node in mixtures)


def test_unsupported_finite_projection_keeps_meaning_and_emits_no_artifact() -> None:
    compiled = compile_path(FIXTURE)

    assert compiled.scientific_semantic_ir is not None
    emitted = OpenQASM3Generator(route=False).generate_detailed(
        compiled.unit,
        semantic_ir=compiled.scientific_semantic_ir,
    )

    assert not emitted.ok
    assert emitted.circuit is not None
    assert emitted.circuit.reject_code == "E_QPU_CANONICAL_PROJECTION_UNAVAILABLE"
    assert emitted.qasm == ""
    assert emitted.circuit.gates == []
    assert emitted.circuit.allocation_started is False


def test_source_nodes_remain_inspectable_without_qpu_support() -> None:
    compiled = compile_path(FIXTURE)

    assert compiled.semantic_inspection is not None
    assert compiled.semantic_inspection.source_node_ids
    assert compiled.semantic_inspection.structural_tree
    assert compiled.semantic_rejection is None or compiled.semantic_rejection.artifacts is None
