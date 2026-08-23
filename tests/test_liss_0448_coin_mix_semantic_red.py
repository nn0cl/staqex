"""Phase 1 Red contracts for canonical Coin/Mix meaning and QPU rejection."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex.backend.qasm.emitter import QASM3Emitter
from compiler.staqex.backend.qasm.lower import lower_unit_to_circuit
from compiler.staqex.pipeline import compile_path, compile_source
from compiler.staqex.scientific_semantic_ir import semantic_fingerprint


FIXTURE = REPO / "tests/fixtures/canonical_coin_mix/mixture_semantics.sqx"
LEGACY_FIXTURE = REPO / "tests/fixtures/canonical_coin_mix/legacy_mix_fallback.sqx"
COIN_ONLY_FIXTURE = REPO / "tests/fixtures/canonical_coin_mix/coin_only.sqx"


def _compile_fixture():
    compiled = compile_path(FIXTURE)
    assert compiled.ok, compiled.diagnostics
    assert compiled.unit is not None
    assert compiled.scientific_semantic_ir is not None
    return compiled


def test_liss_0448_coin_builds_structural_semantic_node() -> None:
    compiled = _compile_fixture()
    coin_nodes = [
        node for node in compiled.scientific_semantic_ir.nodes if node.kind == "Coin"
    ]
    assert len(coin_nodes) == 1
    coin = coin_nodes[0]
    assert coin.meaning_kind == "coin"
    assert coin.state_role == "mixture_source"
    assert coin.role_lane == "quantum"
    assert coin.intent == "coin_preparation"
    assert coin.provenance.source_node_id == coin.node_id


def test_liss_0448_mix_preserves_branch_children_and_provenance() -> None:
    compiled = _compile_fixture()
    core = compiled.scientific_semantic_ir
    mixture = next(node for node in core.nodes if node.kind == "WhenExpr")
    arm_nodes = [node for node in core.nodes if node.kind == "WhenArm"]
    dirac_nodes = [node for node in core.nodes if node.kind == "Dirac"]

    assert mixture.meaning_kind == "mixture"
    assert mixture.state_role == "mixed_state"
    assert mixture.role_lane == "quantum"
    assert len(arm_nodes) == 2
    assert all(arm.node_id in mixture.child_source_node_ids for arm in arm_nodes)
    assert all(
        any(dirac.node_id in arm.children for arm in arm_nodes)
        for dirac in dirac_nodes
    )
    assert mixture.provenance.source_node_id == mixture.node_id
    assert any(
        relation.kind == "mixture" and mixture.node_id in relation.node_ids
        for relation in core.relations
    )


def test_liss_0448_mix_preserves_control_and_branch_rules() -> None:
    compiled = _compile_fixture()
    core = compiled.scientific_semantic_ir
    mixture = next(node for node in core.nodes if node.kind == "WhenExpr")
    coin = next(node for node in core.nodes if node.kind == "Coin")
    arm_nodes = [node for node in core.nodes if node.kind == "WhenArm"]
    dirac_by_id = {node.node_id: node for node in core.nodes if node.kind == "Dirac"}
    source_ordered_arms = sorted(
        arm_nodes,
        key=lambda arm: next(
            dirac_by_id[child_id].provenance.line
            for child_id in arm.children
            if child_id in dirac_by_id
        ),
    )
    assert [
        next(
            dirac_by_id[child_id].provenance.line
            for child_id in arm.children
            if child_id in dirac_by_id
        )
        for arm in source_ordered_arms
    ] == [6, 7]

    assert mixture.control_source_node_id == coin.node_id
    assert mixture.branch_rules == (
        (
            ("pattern", 0),
            ("is_else", False),
            ("source_node_id", source_ordered_arms[0].node_id),
        ),
        (
            ("pattern", None),
            ("is_else", True),
            ("source_node_id", source_ordered_arms[1].node_id),
        ),
    )


def test_liss_0448_branch_arms_retain_source_spans() -> None:
    compiled = _compile_fixture()
    arm_nodes = [
        node
        for node in compiled.scientific_semantic_ir.nodes
        if node.kind == "WhenArm"
    ]

    assert [(arm.provenance.line, arm.provenance.col) for arm in arm_nodes] == [
        (5, 5),
        (6, 5),
    ]


def test_liss_0448_legacy_mix_lowering_is_fail_closed() -> None:
    compiled = compile_path(LEGACY_FIXTURE)
    assert compiled.ok, compiled.diagnostics
    assert compiled.unit is not None

    circuit = lower_unit_to_circuit(compiled.unit)

    assert circuit.reject_code == "E_QPU_CANONICAL_PROJECTION_UNAVAILABLE"
    assert circuit.provenance is not None
    assert circuit.provenance["reason"] == "mixture_projection_unavailable"
    assert circuit.gates == []
    assert circuit.allocation_started is False


def test_liss_0448_legacy_coin_lowering_is_fail_closed() -> None:
    compiled = compile_path(COIN_ONLY_FIXTURE)
    assert compiled.ok, compiled.diagnostics
    assert compiled.unit is not None
    circuit = lower_unit_to_circuit(compiled.unit)

    assert circuit.reject_code == "E_QPU_CANONICAL_PROJECTION_UNAVAILABLE"
    assert circuit.gates == []
    assert circuit.allocation_started is False


def test_liss_0448_branch_changes_update_semantic_fingerprint() -> None:
    source = FIXTURE.read_text(encoding="utf-8")
    original = compile_source(source)
    pattern_mutated = compile_source(source.replace("0 -> Dirac(0)", "1 -> Dirac(0)", 1))
    else_mutated = compile_source(source.replace("else -> Dirac(1)", "1 -> Dirac(1)", 1))
    assert original.ok, original.diagnostics
    assert pattern_mutated.ok, pattern_mutated.diagnostics
    assert else_mutated.ok, else_mutated.diagnostics
    assert original.scientific_semantic_ir is not None
    assert pattern_mutated.scientific_semantic_ir is not None
    assert else_mutated.scientific_semantic_ir is not None
    original_fingerprint = semantic_fingerprint(original.scientific_semantic_ir)
    assert original_fingerprint != semantic_fingerprint(pattern_mutated.scientific_semantic_ir)
    assert original_fingerprint != semantic_fingerprint(else_mutated.scientific_semantic_ir)


def test_liss_0448_qpu_rejection_preserves_ideal_semantic_result() -> None:
    compiled = _compile_fixture()
    core = compiled.scientific_semantic_ir
    emitted = QASM3Emitter(route=False).emit_unit(compiled.unit, semantic_ir=core)

    assert any(node.kind == "WhenExpr" for node in core.nodes)
    assert core.ideal_meaning is not None
    assert emitted.ok is False
    assert emitted.qasm == ""
    assert emitted.circuit is not None
    assert emitted.circuit.reject_code == "E_QPU_CANONICAL_PROJECTION_UNAVAILABLE"
    assert emitted.circuit.provenance is not None
    assert emitted.circuit.provenance["reason"] == "mixture_projection_unavailable"
    mixture = next(node for node in core.nodes if node.kind == "WhenExpr")
    assert emitted.circuit.provenance["source_node_id"] == mixture.node_id
    assert set(emitted.circuit.provenance["branch_source_node_ids"]) == {
        node.node_id
        for node in core.nodes
        if node.kind == "WhenArm"
    }
    assert emitted.circuit.provenance["source_span"] == {
        "line": mixture.provenance.line,
        "col": mixture.provenance.col,
    }
    assert emitted.circuit.gates == []
    assert emitted.circuit.n_qubits == 0
    assert emitted.circuit.n_bits == 0
    assert emitted.circuit.allocation_started is False
    assert emitted.circuit.allocated_qubits == ()
    assert emitted.circuit.partial_program is None
    assert compiled.qpu_ir["instructions"] == ()
