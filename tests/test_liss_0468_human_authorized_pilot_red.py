"""AT-TDD Phase 1 Red: LISS-0468 human-authorized pilot checklist."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def _api():
    from compiler.staqex.pilot_checklist import (  # noqa: PLC0415
        PilotChecklist,
        evaluate_pilot_checklist,
    )

    return PilotChecklist, evaluate_pilot_checklist


def _checklist(**overrides):
    PilotChecklist, _ = _api()
    values = {
        "program_id": "bell-minimal",
        "target_profile": "fake-qpu",
        "device_id": "fake-device",
        "shots": 100,
        "cost_limit": 10,
        "artifact_fingerprint": "sha256:artifact",
        "dry_run_reviewed": True,
        "credential_check_passed": True,
        "cancellation_plan_ready": True,
        "evidence_plan_ready": True,
        "human_approval": False,
    }
    values.update(overrides)
    return PilotChecklist(**values)


def test_dry_run_checklist_is_ready_but_does_not_authorize_submission() -> None:
    _, evaluate = _api()
    result = evaluate(_checklist())

    assert result.status == "ready-for-human-approval"
    assert result.submit_allowed is False
    assert result.physical_execution_claimed is False
    assert result.required_confirmation == "real-time-human"
    assert result.audit_fields["artifact_fingerprint"] == "sha256:artifact"


def test_missing_artifact_review_or_safety_step_fails_closed() -> None:
    _, evaluate = _api()
    result = evaluate(
        _checklist(
            dry_run_reviewed=False,
            cancellation_plan_ready=False,
            evidence_plan_ready=False,
        )
    )

    assert result.status == "rejected"
    assert {
        "DRY_RUN_REVIEW_REQUIRED",
        "CANCELLATION_PLAN_REQUIRED",
        "EVIDENCE_PLAN_REQUIRED",
    } <= set(result.diagnostic_codes)
    assert result.submit_allowed is False


def test_shots_and_cost_guard_are_checked_before_any_real_action() -> None:
    _, evaluate = _api()
    result = evaluate(_checklist(shots=0, cost_limit=0))

    assert result.status == "rejected"
    assert "SHOTS_GUARD_INVALID" in result.diagnostic_codes
    assert "COST_GUARD_INVALID" in result.diagnostic_codes
    assert result.network_called is False
    assert result.submit_allowed is False


def test_real_submission_requires_explicit_real_time_human_confirmation() -> None:
    _, evaluate = _api()
    result = evaluate(_checklist(human_approval=False))

    assert "REAL_TIME_HUMAN_APPROVAL_REQUIRED" in result.diagnostic_codes
    assert result.submit_allowed is False

    approved = evaluate(_checklist(human_approval=True))
    assert approved.status == "authorized"
    assert approved.submit_allowed is True
    assert approved.physical_execution_claimed is False
    assert approved.execution_label == "pending-observed-execution"


def test_credential_failure_is_redacted_and_never_becomes_an_approval() -> None:
    _, evaluate = _api()
    result = evaluate(
        _checklist(
            credential_check_passed=False,
            audit_fields={"credential_state": "missing"},
        )
    )

    assert result.status == "rejected"
    assert "CREDENTIAL_CHECK_FAILED" in result.diagnostic_codes
    assert result.submit_allowed is False
    assert result.physical_execution_claimed is False
    assert all("secret" not in str(value).lower() for value in result.audit_fields.values())


if __name__ == "__main__":
    tests = [
        test_dry_run_checklist_is_ready_but_does_not_authorize_submission,
        test_missing_artifact_review_or_safety_step_fails_closed,
        test_shots_and_cost_guard_are_checked_before_any_real_action,
        test_real_submission_requires_explicit_real_time_human_confirmation,
        test_credential_failure_is_redacted_and_never_becomes_an_approval,
    ]
    for test in tests:
        test()
    print("OK — LISS-0468 Red contract")
