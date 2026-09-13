"""Phase 1 Red contracts for LISS-0552 / ADR 0220.

Local source acceptance remains distinct from finite-QPU projection readiness.
The source deliberately uses ``inner`` because it is valid local algebra while
it has no approved finite operation projection.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.backend.qasm.emitter import QASM3Emitter  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402


def _locally_valid_inner_source(*, trace_leftovers: bool = True) -> str:
    terminal = (
        "Measure viewed tracing_out phi, psi"
        if trace_leftovers
        else "Measure viewed"
    )
    return f"""
    package t
    pub fn main() -> Unit {{
        State phi = |0>
        State psi = |0>
        State overlap = inner(phi, psi)
        State viewed = Inspect(overlap)
        {terminal}
    }}
    """


def _diagnostics_by_code(compiled) -> dict[str, dict]:
    return {str(diagnostic["code"]): diagnostic for diagnostic in compiled.diagnostics}


def test_local_acceptance_names_qsem_obligations_without_target_readiness() -> None:
    compiled = compile_source(_locally_valid_inner_source())

    assert compiled.local_ok is True
    assert compiled.ok is True


def test_qsem_obligations_identify_their_finite_projection_scope() -> None:
    compiled = compile_source(_locally_valid_inner_source())
    assert compiled.ok is True

    diagnostics = _diagnostics_by_code(compiled)
    for code in (
        "QSEM_FINITE_EVIDENCE_MISSING",
        "QSEM_APPROXIMATION_OBLIGATION_MISSING",
    ):
        assert diagnostics[code]["severity"] == "advisory"
        assert diagnostics[code]["phase"] == "quantum-semantic-lowering"
        assert diagnostics[code]["blocking_scope"] == "finite-projection"


def test_unconsumed_linear_state_remains_a_local_hard_failure() -> None:
    compiled = compile_source(_locally_valid_inner_source(trace_leftovers=False))

    assert "LINEAR_IMPLICIT_DISCARD" in _diagnostics_by_code(compiled)
    assert compiled.local_ok is False
    assert compiled.ok is False


def test_qpu_ir_rejects_unprojected_algebraic_operation_with_provenance() -> None:
    compiled = compile_source(_locally_valid_inner_source())

    assert compiled.ok is True
    assert compiled.qpu_ir is not None
    assert (
        compiled.qpu_ir["projection_error"]
        == "E_QPU_CANONICAL_PROJECTION_UNAVAILABLE:semantic_operation_projection_unavailable"
    )
    assert compiled.qpu_ir["instructions"] == ()
    assert compiled.qpu_ir["source_node_ids"]


def test_qasm_rejection_for_unprojected_algebraic_operation_is_atomic() -> None:
    compiled = compile_source(_locally_valid_inner_source())
    assert compiled.unit is not None

    emitted = QASM3Emitter(route=False).emit_unit(
        compiled.unit,
        semantic_ir=compiled.scientific_semantic_ir,
    )

    assert emitted.ok is False
    assert emitted.qasm == ""
    assert emitted.circuit is not None
    assert emitted.circuit.reject_code == "E_QPU_CANONICAL_PROJECTION_UNAVAILABLE"
    assert emitted.circuit.provenance is not None
    assert (
        emitted.circuit.provenance["reason"]
        == "semantic_operation_projection_unavailable"
    )
    assert emitted.circuit.provenance["source_node_id"] in compiled.qpu_ir[
        "source_node_ids"
    ]
    assert emitted.circuit.gates == []
    assert emitted.circuit.allocation_started is False
    assert emitted.circuit.allocated_qubits == ()
    assert emitted.circuit.partial_program is None
