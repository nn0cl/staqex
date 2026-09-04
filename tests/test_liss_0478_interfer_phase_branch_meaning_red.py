"""Phase 1 Red contracts for interfer/phase/branch meaning preservation."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex.backend.qasm.emitter import QASM3Emitter  # noqa: E402
from compiler.staqex.pipeline import compile_path  # noqa: E402


FIXTURE = REPO / "tests/fixtures/semantic_meaning/interfer_phase_branch.sqx"


def _compile_fixture():
    compiled = compile_path(FIXTURE)
    assert compiled.unit is not None, compiled.diagnostics
    assert compiled.scientific_semantic_ir is not None
    return compiled


def test_interfer_has_a_distinct_canonical_meaning() -> None:
    compiled = _compile_fixture()
    core = compiled.scientific_semantic_ir
    interfer = [node for node in core.nodes if node.kind == "Call"]
    assert len(interfer) == 1
    node = interfer[0]
    assert node.meaning_kind == "interference"
    assert node.state_role == "interference_state"
    assert node.intent == "interference"


def test_interfer_preserves_operand_identity_and_phase_metadata() -> None:
    compiled = _compile_fixture()
    core = compiled.scientific_semantic_ir
    node = next(node for node in core.nodes if node.kind == "Call")
    assert len(node.child_source_node_ids) == 2
    assert getattr(node, "phase_metadata", None) is not None
    assert getattr(node, "branch_relationship", None) is not None
    assert any(
        relation.kind == "interference" and node.node_id in relation.node_ids
        for relation in core.relations
    )


def test_unsupported_interfer_projection_is_atomic() -> None:
    compiled = _compile_fixture()
    emitted = QASM3Emitter(route=False).emit_unit(
        compiled.unit, semantic_ir=compiled.scientific_semantic_ir
    )
    assert emitted.ok is False
    assert emitted.qasm == ""
    assert emitted.circuit is not None
    assert emitted.circuit.reject_code == "E_QPU_CANONICAL_PROJECTION_UNAVAILABLE"
    assert emitted.circuit.gates == []
    assert emitted.circuit.allocation_started is False
