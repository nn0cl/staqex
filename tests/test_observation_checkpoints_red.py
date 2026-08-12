"""Acceptance tests for the LISS-0044 observation contract."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def _api():
    from compiler.staqex.observation import (
        CheckpointIdentity,
        ObservationReport,
        ObservationRequest,
        ObservationValidationError,
        SnapshotCapability,
    )

    return (
        CheckpointIdentity,
        ObservationReport,
        ObservationRequest,
        ObservationValidationError,
        SnapshotCapability,
    )


def test_portable_observation_request_and_report_keep_job_provenance():
    CheckpointIdentity, ObservationReport, ObservationRequest, _, _ = _api()

    checkpoint = CheckpointIdentity(name="after_prepare", stage="prepare")
    request = ObservationRequest(
        checkpoint=checkpoint,
        observable="energy(H)",
        projection="expectation",
        target_lane="qpu",
        source_formula="H = electronic_energy(geometry)",
    )
    report = ObservationReport(
        request=request,
        job_id="job-001",
        values={"expectation": -1.1, "uncertainty": 0.02},
        provenance={"target": "qpu", "shots": 1000},
    )

    assert report.job_id == "job-001"
    assert report.request.checkpoint.name == "after_prepare"
    assert report.portable is True
    assert report.provenance["shots"] == 1000


def test_simulator_snapshot_requires_explicit_simulator_capability():
    CheckpointIdentity, _, ObservationRequest, _, SnapshotCapability = _api()

    request = ObservationRequest(
        checkpoint=CheckpointIdentity(name="debug", stage="Evolve"),
        observable="state",
        projection="density_snapshot",
        target_lane="simulator",
        capability=SnapshotCapability("density_snapshot", lane="simulator"),
        source_formula="Evolve psi under H",
    )

    assert request.portable is False
    assert request.capability.name == "density_snapshot"


def test_qpu_snapshot_is_rejected_as_non_portable():
    CheckpointIdentity, _, ObservationRequest, ObservationValidationError, SnapshotCapability = _api()

    try:
        ObservationRequest(
            checkpoint=CheckpointIdentity(name="qpu-debug", stage="Evolve"),
            observable="state",
            projection="state_vector",
            target_lane="qpu",
            capability=SnapshotCapability("state_vector", lane="simulator"),
            source_formula="Evolve psi under H",
        )
    except ObservationValidationError as error:
        assert error.code == "OBSERVATION_QPU_SNAPSHOT_UNSUPPORTED"
    else:
        raise AssertionError("QPU state snapshots must be rejected")


def test_empty_observation_plan_does_not_insert_hidden_jobs_or_measurements():
    _, _, _, _, _ = _api()
    from compiler.staqex.observation import plan_observations

    plan = plan_observations(program_id="bell", requests=())

    assert plan.requests == ()
    assert plan.inserted_measurements == 0
    assert plan.additional_jobs == 0


def test_extra_resource_cost_is_explicit_in_the_observation_plan():
    CheckpointIdentity, _, ObservationRequest, _, _ = _api()
    from compiler.staqex.observation import plan_observations

    request = ObservationRequest(
        checkpoint=CheckpointIdentity(name="energy", stage="final"),
        observable="energy(H)",
        projection="expectation",
        target_lane="qpu",
        source_formula="expectation(H)",
        extra_shots=2000,
        separate_job=True,
    )
    plan = plan_observations(program_id="ising", requests=(request,))

    assert plan.additional_jobs == 1
    assert plan.additional_shots == 2000


if __name__ == "__main__":
    tests = [
        test_portable_observation_request_and_report_keep_job_provenance,
        test_simulator_snapshot_requires_explicit_simulator_capability,
        test_qpu_snapshot_is_rejected_as_non_portable,
        test_empty_observation_plan_does_not_insert_hidden_jobs_or_measurements,
        test_extra_resource_cost_is_explicit_in_the_observation_plan,
    ]
    failures = 0
    for test in tests:
        try:
            test()
        except Exception as error:
            failures += 1
            print(f"FAIL {test.__name__}: {type(error).__name__}: {error}")
    print(f"Observation contract: {len(tests) - failures} passed, {failures} failed")
    raise SystemExit(1 if failures else 0)
