"""LISS-0444 finite canonical instruction projection — Phase 2 Green coverage."""

from __future__ import annotations

from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import compiler.staqex.backend.qasm.emitter as emitter_module
import compiler.staqex.backend.qasm.lower as lower_module
from compiler.staqex.backend.qasm.emitter import QASM3Emitter
from compiler.staqex.pipeline import compile_source
from compiler.staqex.qpu_ir import QpuInstruction, QpuProgram, instruction_fingerprint


def _suzuki_source() -> str:
    return """
    package t
    pub fn main() -> Unit {
        Operator H = X + Z
        State psi = |0>
        State evolved = Evolve { psi under H for 1.0.s using Suzuki(order = 2, steps = 2) }.run()
        State psi = |0>
        Measure evolved
    }
    """


def _binder_source() -> str:
    return """
    package t
    pub fn main() -> Unit {
        QubitRegister<4> register = system()
        Operator H = Sigma (i In 0..2) { 1.0545718e-19 * Z[i] * Z[next(i)] }
        State a = |+>
        State b = |0>
        State c = |0>
        State d = |0>
        State (a, b, c, d) = Evolve { (a, b, c, d) under H for 0.1.fs using Suzuki(order = 2, steps = 2) }.run()
        State b = |0>
        State c = |0>
        State d = |0>
        Measure a
    }
    """


def test_finite_suzuki_produces_canonical_qpu_instructions() -> None:
    compiled = compile_source(_suzuki_source())

    assert compiled.ok, compiled.diagnostics
    gates = [
        instruction
        for instruction in compiled.qpu_ir["instructions"]
        if instruction.opcode != "Measure"
    ]
    assert gates
    assert all(
        instruction.opcode in {"H", "X", "Y", "Z", "CX", "RX", "RY", "RZ"}
        and instruction.qubits
        and instruction.provenance["source_node_id"] in compiled.qpu_ir.source_node_ids
        for instruction in gates
    )
    assert all(instruction.provenance.get("comment") for instruction in gates)
    evolve_ids = {
        node.node_id
        for node in compiled.qpu_ir["canonical_semantic_ir"].nodes
        if node.kind == "EvolveExpr"
    }
    assert evolve_ids
    assert {instruction.provenance["source_node_id"] for instruction in gates} == evolve_ids
    comments = {instruction.provenance["comment"] for instruction in gates}
    assert any("suzuki S2 step 1/2" in comment for comment in comments)
    assert any("suzuki S2 step 2/2" in comment for comment in comments)
    assert any(instruction.parameter is not None for instruction in gates)


def test_finite_binder_produces_canonical_qpu_instructions() -> None:
    compiled = compile_source(_binder_source())

    assert compiled.qpu_ir["binder_lowering"]
    gates = [
        instruction
        for instruction in compiled.qpu_ir["instructions"]
        if instruction.opcode != "Measure"
    ]
    assert gates
    assert all(
        instruction.qubits
        and instruction.provenance["source_node_id"] in compiled.qpu_ir.source_node_ids
        for instruction in gates
    )
    assert all(instruction.provenance.get("comment") for instruction in gates)


def test_invalid_finite_suzuki_does_not_fall_back_to_ast_lowering(monkeypatch) -> None:
    source = _suzuki_source().replace("order = 2", "order = 3")
    compiled = compile_source(source)

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("invalid finite Suzuki must not use AST fallback")

    monkeypatch.setattr(lower_module, "lower_unit_to_circuit", fail_if_called)
    emitted = QASM3Emitter(route=False).emit_unit(compiled.unit)

    assert not emitted.ok
    assert emitted.qasm == ""
    assert emitted.circuit.reject_code == "E_QPU_CANONICAL_FINITE_EVOLUTION_UNSUPPORTED"
    assert not compiled.qpu_ir["instructions"]
    assert compiled.qpu_ir.get("lowering_policy") is None


def test_recomputed_instruction_fingerprint_cannot_authorize_gate_mutation() -> None:
    compiled = compile_source(_suzuki_source())
    instructions = tuple(compiled.qpu_ir["instructions"])
    mutated = QpuInstruction(
        opcode=instructions[0].opcode,
        qubits=instructions[0].qubits,
        parameter=99.0,
        provenance=instructions[0].provenance,
    )
    replaced = (mutated, *instructions[1:])
    values = dict(compiled.qpu_ir)
    values["instructions"] = replaced
    values["instruction_fingerprint"] = instruction_fingerprint(replaced)

    emitted = QASM3Emitter(route=False).emit_qpu_program(QpuProgram(values))

    assert not emitted.ok
    assert emitted.qasm == ""
    assert emitted.circuit.reject_code == "E_QPU_CANONICAL_PROVENANCE"


def test_recomputed_instruction_fingerprint_cannot_authorize_measure_mutation() -> None:
    compiled = compile_source(_suzuki_source())
    instructions = tuple(compiled.qpu_ir["instructions"])
    measure = instructions[-1]
    mutated_measure = QpuInstruction(
        opcode=measure.opcode,
        qubits=measure.qubits,
        parameter=measure.parameter,
        provenance={**measure.provenance, "source_node_id": "tampered"},
    )
    replaced = (*instructions[:-1], mutated_measure)
    values = dict(compiled.qpu_ir)
    values["instructions"] = replaced
    values["instruction_fingerprint"] = instruction_fingerprint(replaced)

    emitted = QASM3Emitter(route=False).emit_qpu_program(QpuProgram(values))

    assert not emitted.ok
    assert emitted.qasm == ""
    assert emitted.circuit.reject_code == "E_QPU_CANONICAL_PROVENANCE"


def test_unresolved_finite_suzuki_order_is_fail_closed(monkeypatch) -> None:
    source = _suzuki_source().replace("order = 2", "order = unknown_order")
    compiled = compile_source(source)

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("unresolved finite Suzuki must not use AST fallback")

    monkeypatch.setattr(lower_module, "lower_unit_to_circuit", fail_if_called)
    emitted = QASM3Emitter(route=False).emit_unit(compiled.unit)

    assert not emitted.ok
    assert emitted.qasm == ""
    assert emitted.circuit.reject_code == "E_QPU_CANONICAL_FINITE_EVOLUTION_UNSUPPORTED"
    assert not compiled.qpu_ir["instructions"]


def test_finite_suzuki_qasm_does_not_use_compatibility_fallback(monkeypatch) -> None:
    compiled = compile_source(_suzuki_source())

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("finite Suzuki must be emitted from canonical instructions")

    monkeypatch.setattr(lower_module, "lower_unit_to_circuit", fail_if_called)
    emitted = QASM3Emitter(route=False).emit_unit(compiled.unit)

    assert emitted.ok, emitted.notes
    assert not any("COMPAT_LOWERING" in note for note in emitted.notes)


def test_finite_binder_qasm_does_not_use_compatibility_fallback(monkeypatch) -> None:
    compiled = compile_source(_binder_source())

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("finite binder must be emitted from canonical instructions")

    monkeypatch.setattr(lower_module, "lower_unit_to_circuit", fail_if_called)
    emitted = QASM3Emitter(route=False).emit_unit(compiled.unit)

    assert emitted.ok, emitted.notes
    assert not any("COMPAT_LOWERING" in note for note in emitted.notes)
