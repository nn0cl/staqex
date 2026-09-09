"""Provider-neutral Unit A lifecycle transitions for scientific workflow plans."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlanIdentity:
    plan_id: str
    snapshot_id: str
    content_hash: str
    revision: int


@dataclass(frozen=True)
class ApprovalBinding:
    approval_id: str
    plan_identity: PlanIdentity
    policy_revision: str
    expires_at: str
    cancelled: bool = False


@dataclass(frozen=True)
class WorkflowPlan:
    identity: PlanIdentity
    state: str
    approval: ApprovalBinding


@dataclass(frozen=True)
class JobResultEnvelope:
    job_id: str
    plan_identity: PlanIdentity
    status: str


@dataclass(frozen=True)
class Diagnostic:
    code: str
    message: str


@dataclass(frozen=True)
class TransitionResult:
    status: str
    plan_identity: PlanIdentity
    diagnostic: Diagnostic | None = None


def _rejected(plan: WorkflowPlan, code: str, message: str) -> TransitionResult:
    return TransitionResult(
        status="rejected",
        plan_identity=plan.identity,
        diagnostic=Diagnostic(code=code, message=message),
    )


def _same_identity(left: PlanIdentity, right: PlanIdentity) -> bool:
    return left == right


def apply_job_result(
    plan: WorkflowPlan,
    result: JobResultEnvelope,
    *,
    now: str,
) -> TransitionResult:
    """Adopt a completed result only when the Unit A contract is current."""

    if not _same_identity(plan.identity, result.plan_identity) or not _same_identity(
        plan.identity, plan.approval.plan_identity
    ):
        return _rejected(
            plan,
            "WORKFLOW_PLAN_IDENTITY_MISMATCH",
            "job result and approval do not bind to the current plan",
        )
    if result.status != "completed":
        return _rejected(
            plan,
            "WORKFLOW_STALE_RESULT",
            "only a completed result can be adopted",
        )
    if plan.approval.cancelled:
        return _rejected(
            plan,
            "WORKFLOW_APPROVAL_CANCELLED",
            "approval was cancelled before result adoption",
        )
    if now >= plan.approval.expires_at:
        return _rejected(
            plan,
            "WORKFLOW_APPROVAL_EXPIRED",
            "approval expired before result adoption",
        )
    if plan.state not in {"awaiting-approval", "approved"}:
        return _rejected(
            plan,
            "WORKFLOW_PLAN_IDENTITY_MISMATCH",
            "completed Job does not imply an approved Plan",
        )
    return TransitionResult(status="accepted-for-plan", plan_identity=plan.identity)
