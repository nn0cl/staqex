"""Future Green acceptance tests for finite formal-Limit realization.

These tests are intentionally kept failing until the separately approved
finite-realization implementation phase. They are not Phase 1 Red tests.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.backend.qasm.lower import EvolutionTargetProfile, lower_unit_to_circuit
from compiler.staqex.pipeline import compile_source


_SOURCE = """
package t
pub fn main() -> Unit {
    Energy scale = 1.0.eV to J
    Operator H = scale * X
    Time dur = 0.6.fs
    Operator U_formal = Limit N -> Infinity {
        (I - i * H * dur / (N * hbar)) ^ N
    }
    Operator U_t = Realize(
        source = U_formal,
        method = "suzuki",
        order = 2,
        steps = 4,
        error_budget = 1e-6
    )
    State psi = |0>
    State result = Evolve() { U_t * psi }.run()
    Measure result
}
"""


def test_product_policy_rejects_non_unitary_qpu_gate_synthesis() -> None:
    compiled = compile_source(_SOURCE.replace('method = "suzuki"', 'method = "product"'))
    assert compiled.unit is not None, compiled.diagnostics
    circuit = lower_unit_to_circuit(
        compiled.unit,
        target_profile=EvolutionTargetProfile(
            limit_realization_method="product",
            limit_steps=4,
            limit_error_budget=1e-6,
        ),
    )
    assert circuit.reject_code == "EVOLUTION_TARGET_UNSUPPORTED"
    assert not circuit.gates
    assert circuit.provenance
    assert circuit.provenance["realization_kind"] == "rejected"
    assert circuit.provenance["realization_policy"] == "explicit_realize"
    assert circuit.provenance["source_transform"] == "Limit product of infinitesimal steps"
    assert circuit.provenance["limit_method"] == "product"
    assert circuit.provenance["limit_steps"] == 4
    assert circuit.provenance["limit_error_budget"] == 1e-6
    assert circuit.provenance["approximation_order_or_null"] is None
    assert circuit.provenance["approximation_steps_or_null"] == 4
    assert circuit.provenance["error_budget_or_null"] == 1e-6
    assert circuit.provenance["capability_rejection_or_null"] == (
        "EVOLUTION_PRODUCT_NOT_UNITARY_QPU"
    )


def test_product_realization_does_not_require_suzuki_order() -> None:
    source = _SOURCE.replace(
        '        method = "suzuki",\n        order = 2,\n',
        '        method = "product",\n',
    )
    compiled = compile_source(source)
    assert compiled.ok, compiled.diagnostics
    circuit = lower_unit_to_circuit(
        compiled.unit,
        target_profile=EvolutionTargetProfile(
            limit_realization_method="product",
            limit_steps=4,
            limit_error_budget=1e-6,
        ),
    )
    assert circuit.reject_code == "EVOLUTION_TARGET_UNSUPPORTED"
    assert circuit.provenance["capability_rejection_or_null"] == (
        "EVOLUTION_PRODUCT_NOT_UNITARY_QPU"
    )


def test_suzuki_policy_realizes_finite_limit_with_error_evidence() -> None:
    compiled = compile_source(_SOURCE)
    assert compiled.unit is not None, compiled.diagnostics
    circuit = lower_unit_to_circuit(
        compiled.unit,
        target_profile=EvolutionTargetProfile(
            limit_realization_method="suzuki",
            limit_order=2,
            limit_steps=4,
            limit_error_budget=1e-6,
        ),
    )
    assert circuit.reject_code is None
    assert circuit.gates
    assert circuit.provenance
    assert circuit.provenance["realization_kind"] == "approximate"
    assert circuit.provenance["limit_method"] == "suzuki"
    assert circuit.provenance["limit_order"] == 2
    assert circuit.provenance["limit_steps"] == 4
    assert circuit.provenance["limit_error_budget"] == 1e-6
    assert circuit.provenance["resource_estimate_or_null"]["qubits"] > 0
    assert circuit.provenance["source_transform"] == "Limit product of infinitesimal steps"
    assert "exp(-i" not in " ".join(circuit.notes)
    assert "Suzuki S2 steps=4" in " ".join(circuit.notes)


if __name__ == "__main__":
    tests = [
        test_product_policy_rejects_non_unitary_qpu_gate_synthesis,
        test_product_realization_does_not_require_suzuki_order,
        test_suzuki_policy_realizes_finite_limit_with_error_evidence,
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
        print(f"GREEN: {len(tests)}/{len(tests)} finite realization checks passed")
    else:
        print(f"RED: {len(failures)}/{len(tests)} failing")
