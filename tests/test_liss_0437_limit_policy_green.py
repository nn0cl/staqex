"""Phase 2 Green checks for ADR 0210 policy provenance."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.backend.qasm.lower import EvolutionTargetProfile, lower_unit_to_circuit
from compiler.staqex.pipeline import compile_source


def test_direct_limit_rejects_even_when_target_policy_is_supplied() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        Energy scale = 1.0.eV to J
        Operator H = scale * X
        Time dur = 0.6.fs
        Operator U_t = Limit N -> Infinity {
            (I - i * H * dur / (N * hbar)) ^ N
        }
        State psi = |0>
        State result = Evolve() { U_t * psi }.run()
        Measure result
    }
    """
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    circuit = lower_unit_to_circuit(
        compiled.unit,
        target_profile=EvolutionTargetProfile(
            limit_realization_method="suzuki",
            limit_order=2,
            limit_steps=8,
            limit_error_budget=1e-9,
        ),
    )
    assert circuit.reject_code == "EVOLUTION_REALIZATION_REQUIRED"
    assert circuit.provenance
    assert circuit.provenance["realization_policy"] == "finite_policy_required"
    assert circuit.provenance["limit_method"] == "suzuki"
    assert circuit.provenance["limit_order"] == 2
    assert circuit.provenance["limit_steps"] == 8
    assert circuit.provenance["limit_error_budget"] == 1e-9
    assert circuit.provenance["capability_rejection_or_null"] == (
        "EVOLUTION_REALIZATION_REQUIRED"
    )
    assert circuit.n_qubits == 0
    assert not circuit.gates
    assert circuit.partial_program is None


def test_invalid_limit_policy_remains_fail_closed() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        Operator H = X
        Time dur = 0.6.fs
        Operator U_t = Limit N -> Infinity {
            (I - i * H * dur / (N * hbar)) ^ N
        }
        Measure |0>
    }
    """
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    circuit = lower_unit_to_circuit(
        compiled.unit,
        target_profile=EvolutionTargetProfile(
            limit_realization_method="suzuki",
            limit_order=0,
            limit_steps=0,
            limit_error_budget=0.0,
        ),
    )
    assert circuit.reject_code == "EVOLUTION_REALIZATION_REQUIRED"
    assert circuit.n_qubits == 0
    assert not circuit.gates
    assert circuit.provenance["realization_policy"] == "finite_policy_required"


if __name__ == "__main__":
    test_direct_limit_rejects_even_when_target_policy_is_supplied()
    test_invalid_limit_policy_remains_fail_closed()
    print("GREEN: 2/2 Limit policy checks passed")
