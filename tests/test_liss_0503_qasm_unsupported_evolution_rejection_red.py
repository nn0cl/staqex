"""AT-TDD Phase 1 Red: LISS-0503 unsupported evolution rejection."""
from pathlib import Path
import sys
REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path: sys.path.insert(0, str(REPO))
from compiler.staqex.backend.qasm.emitter import QASM3Emitter
from compiler.staqex.pipeline import compile_source

SOURCE = """
package liss0503
pub fn main() -> Unit {
    Operator H = X
    State psi = |0>
    State result = Evolve() { H * psi }.run()
    Measure result
}
"""

def _emitted():
    compiled = compile_source(SOURCE)
    assert compiled.unit is not None and compiled.scientific_semantic_ir is not None
    return QASM3Emitter(route=False).emit_unit(compiled.unit, semantic_ir=compiled.scientific_semantic_ir)

def test_unsupported_evolution_is_not_successful():
    assert not _emitted().ok

def test_unsupported_evolution_rejects_with_canonical_provenance():
    assert _emitted().circuit.reject_code == "E_QPU_CANONICAL_PROVENANCE"

def test_unsupported_evolution_rejection_is_atomic():
    emitted = _emitted()
    assert emitted.qasm == ""
    assert emitted.circuit.gates == []
    assert emitted.circuit.allocation_started is False

def test_unsupported_evolution_rejection_is_provider_neutral():
    assert "provider" not in repr(_emitted().circuit).lower()
