"""Phase 3 Red acceptance tests for LISS-0437 residual workstreams.

These tests intentionally describe the next approved boundaries only:
formal-Limit provenance, binder-aware target provenance, and the full S02
blackboard derivation. They must remain Red until their separate workstreams
receive implementation approval.
"""

from __future__ import annotations

import sys
import json
import hashlib
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.backend.qasm.lower import (  # noqa: E402
    EvolutionTargetProfile,
    lower_unit_to_circuit,
)
from compiler.staqex.pipeline import compile_source  # noqa: E402


def test_limit_preserves_typed_evolution_provenance_before_realization() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        Energy scale = 1.0.eV to J
        Operator H = scale * Sigma (i In 0..7) { Z[i] }
        Time dur = 0.6.fs
        Operator U_t = Limit N -> Infinity {
            (I - i * H * dur / (N * hbar)) ^ N
        }
        Measure |0>
    }
    """
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    assert "EVOLUTION_REALIZATION_REQUIRED" in {
        d.get("code") for d in compiled.diagnostics
    }
    provenance = getattr(compiled, "evolution_provenance", None)
    assert provenance, "Limit must preserve typed source provenance before realization"
    for field in (
        "source_span",
        "source_transform",
        "state_shape",
        "realization_kind",
        "realization_policy",
        "approximation_order_or_null",
        "approximation_steps_or_null",
        "error_budget_or_null",
        "resource_estimate_or_null",
        "capability_rejection_or_null",
    ):
        assert field in provenance
    assert provenance["source_transform"] == "Limit product of infinitesimal steps"
    assert provenance["state_shape"] == "Operator"
    assert provenance["realization_kind"] == "rejected"
    assert provenance["realization_policy"] == "finite_policy_required"
    assert provenance["capability_rejection_or_null"] == "EVOLUTION_REALIZATION_REQUIRED"
    assert provenance["source_span"]
    assert provenance["approximation_order_or_null"] is None
    assert provenance["approximation_steps_or_null"] is None
    assert provenance["error_budget_or_null"] is None
    assert provenance["resource_estimate_or_null"] is None
    assert provenance["capability_rejection_or_null"] == "EVOLUTION_REALIZATION_REQUIRED"
    circuit = lower_unit_to_circuit(compiled.unit)
    assert circuit.reject_code == "EVOLUTION_REALIZATION_REQUIRED"
    assert not circuit.gates
    assert circuit.n_qubits == 0
    assert circuit.n_bits == 0
    assert getattr(circuit, "allocation_started", False) is False
    assert getattr(circuit, "allocated_qubits", ()) == ()
    assert getattr(circuit, "partial_program", None) is None


def test_binder_qpu_rejection_exposes_typed_provenance_and_budget() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        State psi = |0>
        Energy scale = 1.0.eV to J
        Operator H = scale * Sigma (i In 0..7) { Z[i] }
        Time dt = 0.1.fs
        Operator U = exp(-i * H * dt / hbar)
        State result = Evolve() { U * psi }.run()
        Measure result
    }
    """
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    circuit = lower_unit_to_circuit(
        compiled.unit,
        target_profile=EvolutionTargetProfile(
            suzuki_order=2,
            suzuki_steps=1,
            realization_mode="approximate",
            resource_budget_qubits=64,
            capability_limitations=("binder_register_mapping_missing",),
            register_mapping={},
        ),
    )
    provenance = getattr(circuit, "provenance", None)
    assert provenance, (
        "QPU rejection must retain the typed target provenance envelope"
    )
    for field in (
        "source_span",
        "source_transform",
        "state_shape",
        "realization_kind",
        "realization_policy",
        "binder_kind",
        "binder_domain",
        "bound_symbols",
        "acting_register",
        "operator_family",
        "register_mapping",
        "approximation_order_or_null",
        "approximation_steps_or_null",
        "error_budget_or_null",
        "resource_estimate_or_null",
        "resource_budget",
        "capability_rejection_or_null",
    ):
        assert field in provenance
    assert circuit.reject_code == "EVOLUTION_TARGET_UNSUPPORTED"
    assert not circuit.gates
    assert circuit.n_qubits == 0
    assert provenance["realization_kind"] == "rejected"
    assert provenance["approximation_order_or_null"] == 2
    assert provenance["approximation_steps_or_null"] == 1
    assert provenance["error_budget_or_null"] is None or isinstance(
        provenance["error_budget_or_null"], (int, float)
    )
    assert isinstance(provenance["resource_estimate_or_null"]["qubits"], int)
    assert provenance["binder_kind"] == "Sigma"
    assert provenance["binder_domain"] == "0..7"
    assert provenance["bound_symbols"] == ["i"]
    assert provenance["acting_register"] == "missing"
    assert provenance["operator_family"] == "PauliSum"
    assert provenance["register_mapping"] == "missing"
    assert provenance["resource_estimate_or_null"]["qubits"] <= provenance["resource_budget"]["qubits"]
    assert isinstance(provenance["resource_estimate_or_null"]["gates"], int)
    assert provenance["resource_budget"] == {"qubits": 64}
    assert provenance["capability_rejection_or_null"] == "binder_register_mapping_missing"
    assert getattr(circuit, "allocation_started", False) is False
    assert getattr(circuit, "allocated_qubits", ()) == ()
    assert getattr(circuit, "partial_program", None) is None


def test_qpu_budget_rejection_is_distinct_from_mapping_rejection() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        State psi = |0>
        Energy scale = 1.0.eV to J
        Operator H = scale * Sigma (i In 0..7) { Z[i] }
        Time dt = 0.1.fs
        Operator U = exp(-i * H * dt / hbar)
        State result = Evolve() { U * psi }.run()
        Measure result
    }
    """
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    circuit = lower_unit_to_circuit(
        compiled.unit,
        target_profile=EvolutionTargetProfile(
            suzuki_order=2,
            suzuki_steps=1,
            realization_mode="approximate",
            resource_budget_qubits=0,
            register_mapping={"Sigma": "q[0..7]"},
        ),
    )
    assert circuit.reject_code == "EVOLUTION_TARGET_UNSUPPORTED"
    assert getattr(circuit, "provenance", None) is None
    assert getattr(circuit, "n_qubits", None) == 0
    assert not circuit.gates
    assert getattr(circuit, "allocation_started", False) is False
    assert getattr(circuit, "allocated_qubits", ()) == ()
    assert getattr(circuit, "partial_program", None) is None


def test_qpu_incomplete_mapping_is_rejected_before_budget_check() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        State psi = |0>
        Energy scale = 1.0.eV to J
        Operator H = scale * Sigma (i In 0..7) { Z[i] }
        Time dt = 0.1.fs
        Operator U = exp(-i * H * dt / hbar)
        State result = Evolve() { U * psi }.run()
        Measure result
    }
    """
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    circuit = lower_unit_to_circuit(
        compiled.unit,
        target_profile=EvolutionTargetProfile(
            resource_budget_qubits=64,
            register_mapping={"Sigma": "q[0..3]"},
        ),
    )
    assert circuit.provenance
    assert (
        circuit.provenance["capability_rejection_or_null"]
        == "binder_register_mapping_missing"
    )
    assert circuit.n_qubits == 0
    assert not circuit.gates
    assert circuit.allocation_started is False


def test_s02_source_contains_full_blackboard_derivation_before_numeric_migration() -> None:
    source_path = (
        _REPO
        / "examples"
        / "showcase"
        / "S02_drug_discovery"
        / "main_selection.sqx"
    )
    source = source_path.read_text(encoding="utf-8")
    assert "Operator H_obj" in source
    assert "Time dur" in source
    has_exp_form = "exp(-i * H_obj * dur / hbar)" in source
    has_limit_form = (
        "Operator U_dt" in source
        and "Limit N -> Infinity" in source
        and "(I - i * H_obj * dur / (N * hbar)) ^ N" in source
    )
    assert has_exp_form, "S02 currently selects the canonical executable exp form"
    if has_limit_form:
        assert "Operator U_dt" in source
        assert "(I - i * H_obj * dur / (N * hbar)) ^ N" in source
    else:
        assert "Limit N -> Infinity" not in source
    assert "State psi_final = Evolve()" in source
    assert "U_t * psi_sel" in source
    assert "Measure psi_final" in source
    for passage in (
        "State psi_sel =",
        "project psi_0 onto P_F",
        "||project psi_0 onto P_F||",
        "trace_out(psi_0)",
        'host("activity_weights")',
        'host("selectivity_weights")',
        "/ hbar",
    ):
        assert passage in source, passage
    if has_exp_form:
        propagator_position = source.index("exp(-i * H_obj * dur / hbar)")
    else:
        propagator_position = source.index("Limit N -> Infinity")
    positions = [
        source.index("Operator H_obj"),
        source.index("Time dur"),
        propagator_position,
        source.index("U_t * psi_sel"),
        source.index("Measure psi_final"),
    ]
    assert positions == sorted(positions), positions
    baseline = source_path.parent / "baseline" / "s02_explicit_evolution_baseline.json"
    assert baseline.exists(), "fixed-seed S02 baseline artifact is required"
    baseline_data = json.loads(baseline.read_text(encoding="utf-8"))
    for field in ("seed", "distribution", "benchmark_metrics", "source_sha256"):
        assert field in baseline_data
    assert baseline_data["seed"] == 0
    actual_sha = hashlib.sha256(source.encode("utf-8")).hexdigest()
    assert baseline_data["source_sha256"] == actual_sha
    assert baseline_data["distribution"]["terminal_selection"] == [0, 1, 1, 1, 1, 1, 0, 0]
    assert baseline_data["distribution"]["probability_min_documented"] == 1.4e-11
    assert baseline_data["distribution"]["probability_max_documented"] == 0.0399
    assert baseline_data["benchmark_metrics"]["reproducibility_verified"] is True
    assert baseline_data["status"] == "pre-migration-reference"
    assert baseline_data["source_sha256"] == (
        "aa2913616b71945ef4d54fef65eac170b76ea63c4f812642ad2df98b181e3511"
    )
    assert baseline_data["distribution"]["feasible_pattern_count"] == 25
    assert baseline_data["benchmark_metrics"]["shots"] == 20
    assert baseline_data["benchmark_metrics"]["infeasible_shots"] == 6
    assert baseline_data["benchmark_metrics"]["top_k_overlap"] == 0.33


def test_expanded_limit_is_preserved_and_not_silently_rewritten() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Energy scale = 1.0.eV to J
            Operator H = scale * X
            Time dur = 0.6.fs
            Operator U_t = Limit N -> Infinity {
                (I - i * H * dur / (N * hbar)) ^ N
            }
            Measure |0>
        }
        """
    )
    assert compiled.unit is not None, compiled.diagnostics
    assert "EVOLUTION_REALIZATION_REQUIRED" in {
        d.get("code") for d in compiled.diagnostics
    }
    assert "exp(-i" not in "".join(
        str(d.get("message", "")) for d in compiled.diagnostics
    )


if __name__ == "__main__":
    _tests = [
        test_limit_preserves_typed_evolution_provenance_before_realization,
        test_binder_qpu_rejection_exposes_typed_provenance_and_budget,
        test_qpu_budget_rejection_is_distinct_from_mapping_rejection,
        test_qpu_incomplete_mapping_is_rejected_before_budget_check,
        test_s02_source_contains_full_blackboard_derivation_before_numeric_migration,
        test_expanded_limit_is_preserved_and_not_silently_rewritten,
    ]
    _failures = []
    for _test in _tests:
        try:
            _test()
        except AssertionError as error:
            _failures.append(f"{_test.__name__}: AssertionError: {error}")
        except Exception as error:  # noqa: BLE001 - Red runner must collect all cases.
            _failures.append(f"{_test.__name__}: {type(error).__name__}: {error}")
    for _failure in _failures:
        print(f"RED: {_failure}")
    if not _failures:
        print(f"GREEN: {len(_tests)}/{len(_tests)} Phase 3 bounded checks passed")
    else:
        print(f"RED: {len(_failures)}/{len(_tests)} failing")
