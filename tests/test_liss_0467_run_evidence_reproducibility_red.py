"""AT-TDD Phase 1 Red: LISS-0467 reproducibility evidence envelope."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def _api():
    from compiler.staqex.evidence_envelope import (  # noqa: PLC0415
        EvidenceRequirements,
        build_evidence_envelope,
    )

    return EvidenceRequirements, build_evidence_envelope


def _fields(**overrides):
    fields = {
        "source_fingerprint": "sha256:source",
        "semantic_fingerprint": "sha256:semantic",
        "artifact_fingerprint": "sha256:artifact",
        "target_profile": "fake-qpu",
        "provider_id": "fake",
        "device_id": "fake-device",
        "job_id": "job-1",
        "compiler_version": "0.1-test",
        "sdk_version": None,
        "shots": 100,
        "seed": 7,
        "calibration": {"kind": "not-provided"},
        "noise": {"kind": "not-provided"},
        "started_at": "2026-08-28T00:00:00Z",
        "completed_at": "2026-08-28T00:00:01Z",
        "cost": {"kind": "unknown"},
        "capability_profile": "fake-profile-v1",
        "baseline": {"kind": "simulator", "fingerprint": "sha256:baseline"},
        "tolerance": {"metric": "total_variation", "maximum": 0.05},
        "drift_policy": "inconclusive-on-unexplained-drift",
        "evidence_kind": "fake",
        "physical_execution_claimed": False,
    }
    fields.update(overrides)
    return fields


def test_complete_envelope_links_source_to_result_and_is_versioned() -> None:
    Requirements, build = _api()
    envelope = build(
        _fields(),
        requirements=Requirements(version="evidence-v1"),
    )

    assert envelope.status == "complete"
    assert envelope.version == "evidence-v1"
    assert envelope.source_fingerprint == "sha256:source"
    assert envelope.semantic_fingerprint == "sha256:semantic"
    assert envelope.artifact_fingerprint == "sha256:artifact"
    assert envelope.job_id == "job-1"
    assert envelope.shots == 100
    assert envelope.baseline["fingerprint"] == "sha256:baseline"


def test_missing_identity_or_result_link_is_incomplete_not_reproducible() -> None:
    Requirements, build = _api()
    fields = _fields(job_id=None, artifact_fingerprint=None)
    envelope = build(fields, requirements=Requirements(version="evidence-v1"))

    assert envelope.status == "incomplete"
    assert {"ARTIFACT_FINGERPRINT_MISSING", "JOB_ID_MISSING"} <= set(
        envelope.diagnostic_codes
    )
    assert envelope.physical_execution_claimed is False


def test_simulator_baseline_and_statistical_tolerance_do_not_claim_physical_fidelity() -> None:
    Requirements, build = _api()
    envelope = build(
        _fields(
            evidence_kind="simulator",
            physical_execution_claimed=False,
            baseline={"kind": "simulator", "fingerprint": "sha256:baseline"},
        ),
        requirements=Requirements(version="evidence-v1"),
    )

    assert envelope.status == "complete"
    assert envelope.evidence_kind == "simulator"
    assert envelope.physical_execution_claimed is False
    assert envelope.fidelity_claim == "not-established"
    assert envelope.tolerance["maximum"] == 0.05


def test_unexplained_drift_is_inconclusive_and_does_not_invent_calibration() -> None:
    Requirements, build = _api()
    envelope = build(
        _fields(calibration=None, drift_observed=True),
        requirements=Requirements(version="evidence-v1"),
    )

    assert envelope.status == "inconclusive"
    assert "DRIFT_UNEXPLAINED" in envelope.diagnostic_codes
    assert envelope.calibration is None
    assert envelope.fidelity_claim == "not-established"


if __name__ == "__main__":
    tests = [
        test_complete_envelope_links_source_to_result_and_is_versioned,
        test_missing_identity_or_result_link_is_incomplete_not_reproducible,
        test_simulator_baseline_and_statistical_tolerance_do_not_claim_physical_fidelity,
        test_unexplained_drift_is_inconclusive_and_does_not_invent_calibration,
    ]
    for test in tests:
        test()
    print("OK — LISS-0467 Red contract")
