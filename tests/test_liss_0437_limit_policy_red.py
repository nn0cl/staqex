"""Phase 1 Red tests for ADR 0210 formal-Limit finite realization policy."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.backend.qasm.lower import (  # noqa: E402
    EvolutionTargetProfile,
    lower_unit_to_circuit,
)
from compiler.staqex.pipeline import compile_source  # noqa: E402


_SOURCE = """
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


def test_target_profile_declares_explicit_limit_policy() -> None:
    profile = EvolutionTargetProfile(
        limit_realization_method="suzuki",
        limit_order=2,
        limit_steps=8,
        limit_error_budget=1e-9,
    )
    assert profile.limit_realization_method == "suzuki"
    assert profile.limit_order == 2
    assert profile.limit_steps == 8
    assert profile.limit_error_budget == 1e-9


def test_limit_source_remains_formal_until_policy_phase() -> None:
    compiled = compile_source(_SOURCE)
    assert compiled.unit is not None, compiled.diagnostics
    assert "EVOLUTION_REALIZATION_REQUIRED" in {
        diagnostic.get("code") for diagnostic in compiled.diagnostics
    }
    assert compiled.evolution_provenance
    assert compiled.evolution_provenance["source_transform"] == (
        "Limit product of infinitesimal steps"
    )
    assert "exp(-i" not in _SOURCE


def test_limit_without_policy_rejects_before_allocation() -> None:
    compiled = compile_source(_SOURCE)
    assert compiled.unit is not None, compiled.diagnostics
    circuit = lower_unit_to_circuit(
        compiled.unit,
        target_profile=EvolutionTargetProfile(),
    )
    assert circuit.reject_code == "EVOLUTION_REALIZATION_REQUIRED"
    assert circuit.provenance
    assert circuit.provenance["capability_rejection_or_null"] == (
        "EVOLUTION_REALIZATION_REQUIRED"
    )
    assert circuit.n_qubits == 0
    assert not circuit.gates
    assert circuit.allocation_started is False
    assert circuit.partial_program is None


if __name__ == "__main__":
    tests = [
        test_target_profile_declares_explicit_limit_policy,
        test_limit_source_remains_formal_until_policy_phase,
        test_limit_without_policy_rejects_before_allocation,
    ]
    failures: list[str] = []
    for test in tests:
        try:
            test()
        except AssertionError as error:
            failures.append(f"{test.__name__}: AssertionError: {error}")
        except Exception as error:  # noqa: BLE001 - Red runner collects all cases.
            failures.append(f"{test.__name__}: {type(error).__name__}: {error}")
    for failure in failures:
        print(f"RED: {failure}")
    if not failures:
        print(f"GREEN: {len(tests)}/{len(tests)} policy boundary checks passed")
    else:
        print(f"RED: {len(failures)}/{len(tests)} failing")
