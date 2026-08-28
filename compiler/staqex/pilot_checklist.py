"""Human-gated pilot checklist; this module never submits a job."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping


@dataclass(frozen=True)
class PilotChecklist:
    program_id: str
    target_profile: str
    device_id: str
    shots: int
    cost_limit: int
    artifact_fingerprint: str | None
    dry_run_reviewed: bool
    credential_check_passed: bool
    cancellation_plan_ready: bool
    evidence_plan_ready: bool
    human_approval: bool
    audit_fields: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class PilotChecklistResult:
    status: str
    diagnostic_codes: tuple[str, ...]
    submit_allowed: bool
    physical_execution_claimed: bool
    required_confirmation: str
    audit_fields: dict[str, str]
    execution_label: str
    network_called: bool = False


def _diagnostics(checklist: PilotChecklist) -> list[str]:
    diagnostics: list[str] = []
    if not checklist.artifact_fingerprint or not checklist.dry_run_reviewed:
        diagnostics.append("DRY_RUN_REVIEW_REQUIRED")
    if not checklist.credential_check_passed:
        diagnostics.append("CREDENTIAL_CHECK_FAILED")
    if not checklist.cancellation_plan_ready:
        diagnostics.append("CANCELLATION_PLAN_REQUIRED")
    if not checklist.evidence_plan_ready:
        diagnostics.append("EVIDENCE_PLAN_REQUIRED")
    if checklist.shots <= 0:
        diagnostics.append("SHOTS_GUARD_INVALID")
    if checklist.cost_limit <= 0:
        diagnostics.append("COST_GUARD_INVALID")
    if not checklist.target_profile or not checklist.device_id:
        diagnostics.append("TARGET_CONFIG_INVALID")
    if not checklist.human_approval:
        diagnostics.append("REAL_TIME_HUMAN_APPROVAL_REQUIRED")
    return diagnostics


def _audit_fields(checklist: PilotChecklist) -> dict[str, str]:
    return {
        "program_id": checklist.program_id,
        "target_profile": checklist.target_profile,
        "artifact_fingerprint": checklist.artifact_fingerprint or "missing",
        "credential_state": "passed" if checklist.credential_check_passed else "failed",
        "human_approval": "approved" if checklist.human_approval else "pending",
        **dict(checklist.audit_fields),
    }


def evaluate_pilot_checklist(checklist: PilotChecklist) -> PilotChecklistResult:
    diagnostics = _diagnostics(checklist)
    audit_fields = _audit_fields(checklist)
    blocking = tuple(
        code for code in diagnostics if code != "REAL_TIME_HUMAN_APPROVAL_REQUIRED"
    )
    if blocking:
        return PilotChecklistResult(
            status="rejected",
            diagnostic_codes=tuple(diagnostics),
            submit_allowed=False,
            physical_execution_claimed=False,
            required_confirmation="real-time-human",
            audit_fields=audit_fields,
            execution_label="not-authorized",
        )
    if not checklist.human_approval:
        return PilotChecklistResult(
            status="ready-for-human-approval",
            diagnostic_codes=tuple(diagnostics),
            submit_allowed=False,
            physical_execution_claimed=False,
            required_confirmation="real-time-human",
            audit_fields=audit_fields,
            execution_label="pending-observed-execution",
        )
    return PilotChecklistResult(
        status="authorized",
        diagnostic_codes=(),
        submit_allowed=True,
        physical_execution_claimed=False,
        required_confirmation="real-time-human",
        audit_fields=audit_fields,
        execution_label="pending-observed-execution",
    )


__all__ = ["PilotChecklist", "PilotChecklistResult", "evaluate_pilot_checklist"]
