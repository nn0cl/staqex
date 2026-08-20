"""Phase 1 Red contracts for honest finite-target capability rejection."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex.backend.qasm.lower import EvolutionTargetProfile, lower_unit_to_circuit
from compiler.staqex.backend.qasm.emitter import QASM3Emitter
from compiler.staqex.pipeline import compile_path


LIMIT = REPO / "tests/fixtures/capability_rejection/ideal_limit.sqx"
PRODUCT = REPO / "tests/fixtures/capability_rejection/non_unitary_product.sqx"
OVERFLOW = REPO / "tests/fixtures/capability_rejection/resource_overflow.sqx"


def _assert_empty_target(circuit, code: str) -> None:
    assert circuit.reject_code == code
    assert circuit.gates == []
    assert circuit.n_qubits == 0
    assert circuit.allocation_started is False
    assert circuit.allocated_qubits == ()
    assert circuit.partial_program is None


def test_liss_0451_limit_rejection_uses_accepted_code_and_empty_artifacts() -> None:
    compiled = compile_path(LIMIT)
    assert compiled.unit is not None, compiled.diagnostics
    circuit = lower_unit_to_circuit(compiled.unit, target_profile=EvolutionTargetProfile())
    _assert_empty_target(circuit, "EVOLUTION_REALIZATION_REQUIRED")
    assert circuit.provenance["reason"] == "missing_finite_realization"
    assert circuit.provenance["source_node_id"]


def test_liss_0451_non_unitary_product_rejection_is_provenance_bearing() -> None:
    compiled = compile_path(PRODUCT)
    assert compiled.unit is not None, compiled.diagnostics
    circuit = lower_unit_to_circuit(compiled.unit, target_profile=EvolutionTargetProfile())
    _assert_empty_target(circuit, "E_QPU_UNSUPPORTED_CAPABILITY")
    assert circuit.provenance["reason"] == "non_unitary_target"
    assert circuit.provenance["source_node_id"]


def test_liss_0451_resource_overflow_precedes_allocation() -> None:
    compiled = compile_path(OVERFLOW)
    assert compiled.unit is not None, compiled.diagnostics
    circuit = lower_unit_to_circuit(
        compiled.unit,
        target_profile=EvolutionTargetProfile(resource_budget_qubits=2),
    )
    _assert_empty_target(circuit, "EVOLUTION_TARGET_UNSUPPORTED")
    assert circuit.provenance["reason"] == "resource_budget_exceeded_before_allocation"
    assert circuit.provenance["target_plan"] is None


def test_liss_0451_unresolved_rotation_uses_exact_code() -> None:
    source = """
    package fixtures.capability_rejection
    pub fn main() -> Unit {
        QubitRegister<1> register = system()
        State q = |0>
        State q = apply(rx(unbound_name), q)
        Measure q
    }
    """
    from compiler.staqex.pipeline import compile_source

    compiled = compile_source(source)
    assert compiled.ok, compiled.diagnostics
    emitted = QASM3Emitter(route=False).emit_unit(compiled.unit)
    assert emitted.circuit is not None
    assert emitted.circuit.reject_code == "QASM_ROTATION_ANGLE_UNRESOLVED"
    assert emitted.circuit.provenance["reason"] == "parameter_unresolved"


if __name__ == "__main__":
    for test in (
        test_liss_0451_limit_rejection_uses_accepted_code_and_empty_artifacts,
        test_liss_0451_non_unitary_product_rejection_is_provenance_bearing,
        test_liss_0451_resource_overflow_precedes_allocation,
        test_liss_0451_unresolved_rotation_uses_exact_code,
    ):
        test()
