"""Phase 1 Red contracts for ideal meaning versus finite realization."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex.backend.qasm.lower import EvolutionTargetProfile, lower_unit_to_circuit
from compiler.staqex.pipeline import compile_path


IDEAL = REPO / "tests/fixtures/ideal_realization/ideal_limit.sqx"
EXACT = REPO / "tests/fixtures/ideal_realization/exact_exponential.sqx"
REALIZED = REPO / "tests/fixtures/ideal_realization/explicit_realize.sqx"


def test_limit_has_its_own_ideal_semantic_identity() -> None:
    compiled = compile_path(IDEAL)
    assert compiled.unit is not None, compiled.diagnostics
    assert compiled.scientific_semantic_ir is not None
    assert any(node.kind == "Limit" for node in compiled.scientific_semantic_ir.nodes)


def test_limit_preserved_before_target_rejection() -> None:
    compiled = compile_path(IDEAL)
    assert compiled.unit is not None, compiled.diagnostics
    assert compiled.scientific_semantic_ir is not None
    circuit = lower_unit_to_circuit(compiled.unit, target_profile=EvolutionTargetProfile())
    assert circuit.reject_code == "EVOLUTION_REALIZATION_REQUIRED"
    assert circuit.provenance["reason"] == "missing_finite_realization"
    assert circuit.gates == []
    assert circuit.n_qubits == 0
    assert circuit.partial_program is None


def test_exact_exponential_has_its_own_semantic_identity() -> None:
    compiled = compile_path(EXACT)
    assert compiled.ok, compiled.diagnostics
    assert compiled.unit is not None
    assert compiled.scientific_semantic_ir is not None
    assert any(node.kind == "EvolveExpr" for node in compiled.scientific_semantic_ir.nodes)
    assert any(
        node.kind == "ExactExponential"
        for node in compiled.scientific_semantic_ir.nodes
    )


def test_exact_exponential_preserved_without_gates() -> None:
    compiled = compile_path(EXACT)
    assert compiled.ok, compiled.diagnostics
    assert compiled.unit is not None
    circuit = lower_unit_to_circuit(
        compiled.unit,
        target_profile=EvolutionTargetProfile(),
    )
    assert circuit.reject_code == "E_QPU_CANONICAL_FINITE_EVOLUTION_UNSUPPORTED"
    assert circuit.gates == []
    assert compiled.scientific_semantic_ir.qpu_projection is None


def test_realize_provenance_is_source_owned() -> None:
    compiled = compile_path(REALIZED)
    assert compiled.scientific_semantic_ir is not None
    record = compiled.scientific_semantic_ir.finite_realization_record
    assert record is not None
    assert record.source_name == "U_formal"
    assert record.realized_name == "U_qpu"
    assert record.method == "suzuki"
    assert record.order == 2
    assert record.steps == 8
    assert record.error_budget == 1e-6
    assert dict(record.provenance)["source_node_id"] == record.source_node_id


if __name__ == "__main__":
    for test in (
        test_limit_has_its_own_ideal_semantic_identity,
        test_limit_preserved_before_target_rejection,
        test_exact_exponential_has_its_own_semantic_identity,
        test_exact_exponential_preserved_without_gates,
        test_realize_provenance_is_source_owned,
    ):
        test()
