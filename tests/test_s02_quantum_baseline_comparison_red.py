"""Phase 1 Red contracts for WP-0158 / LISS-0541 D05."""

from __future__ import annotations

import importlib

import pytest


def _comparison_module():
    try:
        return importlib.import_module(
            "compiler.staqex.s02_quantum_baseline_comparison"
        )
    except ModuleNotFoundError as error:
        pytest.fail("LISS-0541 D05 comparison implementation is not present yet")
        raise AssertionError from error


def _lane(
    module,
    *,
    lane: str = "classical",
    status: str = "accepted",
    selected=None,
    feasible=True,
    objective=3.0,
    cost=None,
    diagnostic=None,
    snapshot_id="assay:s02-round-001",
    candidate_set_id="candidates:s02-fixture-v1",
    profile_id="batch:s02-v1",
    baseline_revision="greedy-feasible-v1",
    artifact_id="artifact:s02-d05-q01-v1",
    encoding_id="encoding:s02-one-bit-v1",
    manifest_id="manifest:s02-d05-v1",
):
    return module.LaneResult(
        lane=lane,
        status=status,
        selected_candidate_ids=(
            ("candidate:001", "candidate:002") if selected is None else selected
        ),
        feasible=feasible,
        objective=objective,
        decoded_valid=(status == "accepted"),
        cost=cost,
        diagnostic=diagnostic,
        snapshot_id=snapshot_id,
        candidate_set_id=candidate_set_id,
        profile_id=profile_id,
        baseline_revision=baseline_revision,
        artifact_id=artifact_id,
        encoding_id=encoding_id,
        manifest_id=manifest_id,
    )


def _comparison_input(module, *, quantum=None, classical=None, cost=None):
    return module.ComparisonInput(
        problem_id="problem:s02-batch-v1",
        snapshot_id="assay:s02-round-001",
        candidate_set_id="candidates:s02-fixture-v1",
        profile_id="batch:s02-v1",
        baseline_revision="greedy-feasible-v1",
        quantum_artifact_id="artifact:s02-d05-q01-v1",
        classical=(classical or _lane(module)),
        quantum=(quantum or _lane(module, lane="quantum")),
        cost=cost or module.CostBreakdown(queue=0.0, encode=1.0, execute=2.0, decode=1.0),
        objective_tolerance=1e-12,
    )


def test_d05_accepts_matching_classical_and_quantum_lanes_with_separate_cost() -> None:
    module = _comparison_module()

    result = module.compare_baseline_and_quantum(_comparison_input(module))

    assert result.status == "matched"
    assert result.selected_candidate_ids == ("candidate:001", "candidate:002")
    assert result.feasibility_match is True
    assert result.objective_gap == 0.0
    assert result.cost.total == 4.0
    assert result.quantum_advantage == "not-established"


def test_d05_quarantines_candidate_set_mismatch_before_claiming_comparison() -> None:
    module = _comparison_module()
    quantum = _lane(module, lane="quantum", selected=("candidate:001", "candidate:003"))

    result = module.compare_baseline_and_quantum(_comparison_input(module, quantum=quantum))

    assert result.status == "quarantine"
    assert result.diagnostic.code == "QUANTUM_CANDIDATE_SET_MISMATCH"


def test_d05_quarantines_snapshot_or_artifact_lineage_mismatch() -> None:
    module = _comparison_module()
    quantum = _lane(
        module,
        lane="quantum",
        snapshot_id="assay:s02-round-000",
        artifact_id="artifact:s02-d05-q01-other",
    )

    result = module.compare_baseline_and_quantum(_comparison_input(module, quantum=quantum))

    assert result.status == "quarantine"
    assert result.diagnostic.code in {
        "QUANTUM_CANDIDATE_SET_MISMATCH",
        "QUANTUM_BASELINE_MISMATCH",
    }


def test_d05_preserves_comparison_lineage_identity_in_a_matched_result() -> None:
    module = _comparison_module()

    result = module.compare_baseline_and_quantum(_comparison_input(module))

    assert result.snapshot_id == "assay:s02-round-001"
    assert result.profile_id == "batch:s02-v1"
    assert result.quantum_artifact_id == "artifact:s02-d05-q01-v1"
    assert result.encoding_id == "encoding:s02-one-bit-v1"
    assert result.manifest_id == "manifest:s02-d05-v1"


def test_d05_rejects_invalid_quantum_decode_or_constraint_verdict() -> None:
    module = _comparison_module()
    quantum = _lane(module, lane="quantum", feasible=False, status="accepted")

    result = module.compare_baseline_and_quantum(_comparison_input(module, quantum=quantum))

    assert result.status == "quarantine"
    assert result.diagnostic.code in {
        "QUANTUM_DECODE_INVALID",
        "QUANTUM_CONSTRAINT_VIOLATION",
    }


def test_d05_retains_quantum_runtime_rejection_as_inconclusive() -> None:
    module = _comparison_module()
    quantum = _lane(
        module,
        lane="quantum",
        status="rejected",
        selected=(),
        feasible=False,
        objective=None,
        diagnostic=module.LaneDiagnostic(
            code="QUANTUM_RUNTIME_REJECTED", message="runtime is unsupported"
        ),
    )

    result = module.compare_baseline_and_quantum(_comparison_input(module, quantum=quantum))

    assert result.status == "inconclusive"
    assert result.diagnostic.code == "QUANTUM_RUNTIME_REJECTED"
    assert result.classical_fallback_selected_candidate_ids == (
        "candidate:001",
        "candidate:002",
    )
    assert result.quantum_advantage == "not-established"


def test_d05_does_not_treat_missing_quantum_cost_as_zero() -> None:
    module = _comparison_module()
    quantum = _lane(module, lane="quantum")
    incomplete_cost = module.CostBreakdown(
        queue=None, encode=1.0, execute=2.0, decode=1.0
    )

    result = module.compare_baseline_and_quantum(
        _comparison_input(module, quantum=quantum, cost=incomplete_cost)
    )

    assert result.status == "inconclusive"
    assert result.diagnostic.code == "QUANTUM_COST_MISSING"
    assert result.cost is None
