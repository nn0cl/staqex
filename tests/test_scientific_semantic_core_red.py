"""LISS-0444 / WP-0107 Phase 1 Red acceptance contract.

These tests intentionally fail until the source-derived Scientific Semantic IR
and its consumer boundaries are implemented. Phase 1 creates the acceptance
contract only; it does not alter production compiler paths.
"""

from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path
from types import MappingProxyType

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex.pipeline import compile_source
from compiler.staqex.backend.qasm.emitter import QASM3Emitter
from compiler.staqex.qpu_ir import (
    QpuInstruction,
    QpuProgram,
    _attach_canonical_provenance,
)
from compiler.staqex.scientific_semantic_ir import (
    ScientificSemanticIR,
    SemanticNode,
    SemanticRelation,
)
from compiler.staqex.hir import build_hir
from compiler.staqex.physics_equation import Coefficient, EquationNode, Unit
from compiler.staqex.physics_ir import SourceOrigin
from compiler.staqex.physics_ir_lower import lower_hir_to_physics_ir


ROOT = Path(__file__).parent / "fixtures" / "semantic_core"

CORPUS = {
    "SSC-001": "classical_relation.sqx",
    "SSC-002": "unit_relation.sqx",
    "SSC-003": "binder_relation.sqx",
    "SSC-004": "state_operator.sqx",
    "SSC-005": "hamiltonian_evolution.sqx",
    "SSC-006": "symbolic_inspection.sqx",
    "SSC-007": "explicit_realize.sqx",
    "SSC-008": "invalid_boundaries.sqx",
    "SSC-009": "dynamic_measurement.sqx",
}

PROOF_TESTS = {
    "SSC-PROOF-AST-01": "test_ast_is_not_consumer_authority",
    "SSC-PROOF-HIR-01": "test_hir_retains_identity_and_structure",
    "SSC-PROOF-PHYS-01": "test_physics_ir_is_projection_only",
    "SSC-PROOF-EQ-01": "test_caller_equationnode_cannot_satisfy_source_acceptance",
    "SSC-PROOF-SYM-01": "test_symbolic_projection_conserves_nodes",
    "SSC-PROOF-QSEM-01": "test_quantum_projection_requires_canonical_input",
    "SSC-PROOF-PLAN-01": "test_algorithm_plan_requires_realize",
    "SSC-PROOF-EVAL-01": "test_evaluator_has_no_independent_semantic_dispatch",
    "SSC-PROOF-QASM-01": "test_qasm_rejects_direct_limit_and_partial_artifacts",
    "SSC-PROOF-H1-01": "test_h1_cannot_create_second_semantic_dialect",
    "SSC-PROOF-QPU-01": "test_qpu_ir_requires_canonical_projection",
    "SSC-PROOF-BINDER-01": "test_finite_binder_requires_canonical_binder",
    "SSC-PROOF-BOUNDARY-01": "test_state_and_realization_boundaries_are_structural",
}


def _source(case_id: str) -> str:
    return (ROOT / CORPUS[case_id]).read_text(encoding="utf-8")


def _compile(case_id: str):
    return compile_source(_source(case_id))


def test_semantic_core_corpus_is_named_and_complete() -> None:
    assert set(CORPUS) == {f"SSC-{index:03d}" for index in range(1, 10)}
    assert all((ROOT / filename).is_file() for filename in CORPUS.values())


def test_proof_ids_have_explicit_test_targets() -> None:
    assert PROOF_TESTS["SSC-PROOF-BOUNDARY-01"].startswith("test_")
    assert len(PROOF_TESTS) == 13


def test_ast_is_not_consumer_authority() -> None:
    compiled = _compile("SSC-001")
    assert compiled.scientific_semantic_ir is not None


def test_hir_retains_identity_and_structure() -> None:
    compiled = _compile("SSC-002")
    assert compiled.scientific_semantic_ir.nodes


def test_physics_ir_is_projection_only() -> None:
    compiled = _compile("SSC-004")
    assert compiled.scientific_semantic_ir.authority == "scientific_semantic_ir"


def test_caller_equationnode_cannot_satisfy_source_acceptance() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Operator H = X + Z
            State psi = |0>
            Measure psi
        }
        """
    )
    assert compiled.checker is not None
    assert compiled.unit is not None
    hir = build_hir(compiled.checker, unit=compiled.unit)
    origin = SourceOrigin(source_id="caller.sqx", line=1, col=1)
    unit = Unit(symbol="J", dimensions=(1, 1, -2), origin=origin)
    equation = EquationNode(
        kind="equality",
        left="H",
        right="omega * N",
        coefficients=(Coefficient(expression="omega", unit=unit, origin=origin),),
        origin=origin,
    )
    lowered = lower_hir_to_physics_ir(
        hir,
        unit=compiled.unit,
        equations=(equation,),
    )
    assert equation in lowered.nodes
    assert equation not in compiled.scientific_semantic_ir.nodes


def test_symbolic_projection_conserves_nodes() -> None:
    compiled = _compile("SSC-006")
    inspection = compiled.semantic_inspection
    assert inspection.allocation_record is None
    assert inspection.collapse_record is None


def test_quantum_projection_requires_canonical_input() -> None:
    compiled = _compile("SSC-004")
    assert compiled.quantum_semantic_ir.source_node_ids


def test_algorithm_plan_requires_realize() -> None:
    compiled = _compile("SSC-007")
    assert compiled.algorithm_plan.provenance.realize_source_node_id


def test_identifier_named_realize_does_not_create_a_finite_plan() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Operator Realize = X
            State psi = |0>
            Measure psi
        }
        """
    )
    assert compiled.algorithm_plan is None


def test_evaluator_has_no_independent_semantic_dispatch() -> None:
    compiled = _compile("SSC-005")
    assert compiled.execution_authority == "scientific_semantic_ir"


def test_qasm_rejects_direct_limit_and_partial_artifacts() -> None:
    compiled = _compile("SSC-008")
    rejection = compiled.semantic_rejection
    assert rejection is not None
    assert rejection.artifacts is None


def test_h1_cannot_create_second_semantic_dialect() -> None:
    compiled = _compile("SSC-001")
    assert compiled.h1_authority is None


def test_qpu_ir_requires_canonical_projection() -> None:
    compiled = _compile("SSC-007")
    expected = tuple(node.node_id for node in compiled.scientific_semantic_ir.nodes)
    assert compiled.qpu_ir.source_node_ids == expected
    assert compiled.qpu_ir["provenance"] == [
        node.provenance for node in compiled.scientific_semantic_ir.nodes
    ]


def test_qpu_instructions_retain_canonical_source_node_provenance() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            QubitRegister<1> reg = system()
            ForEach q in reg {
                apply(H, q)
            }
        }
        """
    )
    assert compiled.ok, compiled.diagnostics
    instructions = compiled.qpu_ir["instructions"]
    assert instructions
    canonical_ids = set(compiled.qpu_ir.source_node_ids)
    assert all(instruction.provenance["source_node_id"] in canonical_ids for instruction in instructions)


def test_qasm_without_canonical_projection_rejects_atomically() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            QubitRegister<1> reg = system()
        }
        """
    )
    assert compiled.ok, compiled.diagnostics
    emitted = QASM3Emitter(route=False).emit_unit(compiled.unit)
    assert not emitted.ok
    assert emitted.qasm == ""
    assert emitted.circuit is not None
    assert emitted.circuit.reject_code == "E_QPU_CANONICAL_PROJECTION_UNAVAILABLE"
    assert emitted.circuit.gates == []
    assert emitted.circuit.allocation_started is False
    assert emitted.circuit.allocated_qubits == ()
    assert emitted.circuit.partial_program is None


def test_direct_qpu_consumption_rejects_noncanonical_authority() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            QubitRegister<1> reg = system()
            ForEach q in reg {
                apply(H, q)
            }
        }
        """
    )
    assert compiled.ok, compiled.diagnostics
    values = dict(compiled.qpu_ir.values)
    values["semantic_authority"] = "symbolic_ir"
    program = QpuProgram(MappingProxyType(values))
    emitted = QASM3Emitter(route=False).emit_qpu_program(program)
    assert not emitted.ok
    assert emitted.circuit.reject_code == "E_QPU_CANONICAL_PROVENANCE"


def test_direct_qpu_consumption_rejects_forged_source_identity() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            QubitRegister<1> reg = system()
            ForEach q in reg {
                apply(H, q)
            }
        }
        """
    )
    assert compiled.ok, compiled.diagnostics
    values = dict(compiled.qpu_ir.values)
    values["source_node_ids"] = ("forged:node",)
    values["provenance"] = [("sqx", 999, 999)]
    program = QpuProgram(MappingProxyType(values))
    emitted = QASM3Emitter(route=False).emit_qpu_program(program)
    assert not emitted.ok
    assert emitted.circuit.reject_code == "E_QPU_CANONICAL_PROVENANCE"


def test_direct_qpu_consumption_rejects_canonical_body_mutation() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            QubitRegister<1> reg = system()
            ForEach q in reg {
                apply(H, q)
            }
        }
        """
    )
    assert compiled.ok, compiled.diagnostics
    values = dict(compiled.qpu_ir.values)
    canonical = values["canonical_semantic_ir"]
    mutated_first = replace(canonical.nodes[0], kind="MutatedSemanticKind")
    values["canonical_semantic_ir"] = replace(
        canonical, nodes=(mutated_first, *canonical.nodes[1:])
    )
    program = QpuProgram(MappingProxyType(values))
    emitted = QASM3Emitter(route=False).emit_qpu_program(program)
    assert not emitted.ok
    assert emitted.circuit.reject_code == "E_QPU_CANONICAL_PROVENANCE"


def test_direct_qpu_consumption_rejects_instruction_projection_mutation() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            QubitRegister<1> reg = system()
            ForEach q in reg {
                apply(H, q)
            }
        }
        """
    )
    assert compiled.ok, compiled.diagnostics
    values = dict(compiled.qpu_ir.values)
    instruction = values["instructions"][0]
    values["instructions"] = (
        QpuInstruction(
            opcode="X",
            qubits=instruction.qubits,
            parameter=instruction.parameter,
            provenance=instruction.provenance,
        ),
        *values["instructions"][1:],
    )
    program = QpuProgram(MappingProxyType(values))

    emitted = QASM3Emitter(route=False).emit_qpu_program(program)

    assert not emitted.ok
    assert emitted.circuit.reject_code == "E_QPU_CANONICAL_PROVENANCE"


def test_qasm_rejects_qpu_projection_error_without_legacy_fallback() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            QubitRegister<1> reg = system()
        }
        """
    )
    assert compiled.ok, compiled.diagnostics
    values = dict(compiled.qpu_ir.values)
    values["projection_error"] = "E_QPU_CANONICAL_PROVENANCE: test failure"
    values["instructions"] = ()
    program = QpuProgram(MappingProxyType(values))
    emitted = QASM3Emitter(route=False).emit_qpu_program(program)
    assert not emitted.ok
    assert emitted.qasm == ""


def test_explicit_evolution_projection_retains_source_identity_and_provenance() -> None:
    compiled = _compile("SSC-005")
    projection = compiled.qpu_ir["explicit_evolution"]

    assert projection["source_node_kind"] == "EvolveExpr"
    assert projection["source_node_id"] in compiled.qpu_ir.source_node_ids
    assert projection["provenance"]["source_node_id"] == projection["source_node_id"]
    assert projection["realization"] == "target_profile_required"


def test_explicit_evolution_projection_mutation_is_rejected_by_fingerprint() -> None:
    compiled = _compile("SSC-005")
    values = dict(compiled.qpu_ir.values)
    values["canonical_semantic_ir"].explicit_evolution["realization"] = "forged"
    program = QpuProgram(MappingProxyType(values))

    emitted = QASM3Emitter(route=False).emit_qpu_program(program)

    assert not emitted.ok
    assert emitted.circuit.reject_code == "E_QPU_CANONICAL_PROVENANCE"


def test_binder_projection_retains_source_identity_and_provenance() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            QubitRegister<3> register = system()
            Operator H = Sigma (i In 0..1) { 1.0 * Z[i] * Z[next(i)] }
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )
    assert compiled.ok, compiled.diagnostics
    lowering = compiled.qpu_ir["binder_lowering"]["H"]

    assert compiled.qpu_ir["binder_source_node_ids"]
    assert lowering["provenance"]["binder_variable"] == "i"
    assert all(
        dict(record)["source_node_id"] in compiled.qpu_ir.source_node_ids
        for record in compiled.qpu_ir["binder_provenance"]
    )


def test_binder_projection_mutation_is_rejected_by_fingerprint() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            QubitRegister<3> register = system()
            Operator H = Sigma (i In 0..1) { 1.0 * Z[i] * Z[next(i)] }
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )
    assert compiled.ok, compiled.diagnostics
    values = dict(compiled.qpu_ir.values)
    values["canonical_semantic_ir"].binder_lowering["H"]["expanded_terms"] = 999
    program = QpuProgram(MappingProxyType(values))

    emitted = QASM3Emitter(route=False).emit_qpu_program(program)

    assert not emitted.ok
    assert emitted.circuit.reject_code == "E_QPU_CANONICAL_PROVENANCE"


def test_canonical_cqft_projection_preserves_composite_shape_and_control() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            QubitRegister<1> ctrl = system()
            QubitRegister<3> reg = system()
            Operator F = cqft(ctrl, reg)
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )
    assert compiled.ok, compiled.diagnostics
    assert compiled.qpu_ir["hilbert_shape"]["logical_qubits"] == 4
    assert compiled.qpu_ir["qft"]["operations"][0]["operation"] == "cqft"
    assert compiled.qpu_ir["qft"]["operations"][0]["control"] == 0
    assert compiled.qpu_ir["qft"]["operations"][0]["target_offset"] == 1
    assert compiled.qpu_ir["instructions"]
    assert any(
        0 in instruction.qubits and 1 in instruction.qubits
        for instruction in compiled.qpu_ir["instructions"]
    )
    assert all(
        instruction.provenance["source_node_id"] in compiled.qpu_ir.source_node_ids
        for instruction in compiled.qpu_ir["instructions"]
    )


def test_canonical_qpu_projection_rejects_oversized_register_before_artifact() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            QubitRegister<2048> reg = system()
            ForEach q in reg {
                apply(H, q)
            }
        }
        """
    )
    assert compiled.qpu_ir["projection_error"].startswith("E_QPU_RESOURCE_UNSUPPORTED")
    emitted = QASM3Emitter(route=False).emit_qpu_program(compiled.qpu_ir)
    assert not emitted.ok
    assert emitted.qasm == ""


def test_unresolved_instruction_provenance_fails_at_qpu_projection_boundary() -> None:
    semantic_ir = ScientificSemanticIR(
        schema="ssc-semantic-v1",
        authority="scientific_semantic_ir",
        nodes=(
            SemanticNode(
                node_id="ssc:source",
                kind="ExprStmt",
                children=(),
                role_lane="classical",
                type="Unknown",
                dimensions="unknown",
                exactness="unresolved",
                intent="expression",
                provenance=("sqx", 1, 1),
            ),
        ),
        relations=(SemanticRelation("source", ("ssc:source",)),),
    )
    instruction = QpuInstruction(
        opcode="H",
        qubits=(0,),
        provenance={"line": 99, "col": 1, "source": "test"},
    )
    with pytest.raises(RuntimeError, match="does not resolve"):
        _attach_canonical_provenance((instruction,), semantic_ir)


def test_finite_binder_requires_canonical_binder() -> None:
    compiled = _compile("SSC-003")
    assert compiled.scientific_semantic_ir.relations[0].kind == "binder"


@pytest.mark.parametrize(
    "case_id",
    ["SSC-006", "SSC-007", "SSC-009"],
    ids=["SSC-PROOF-SYM-01", "SSC-PROOF-PLAN-01", "SSC-PROOF-QSEM-01"],
)
def test_state_and_realization_boundaries_are_structural(case_id: str) -> None:
    compiled = _compile(case_id)
    assert compiled.semantic_snapshot.schema == "ssc-semantic-v1"
