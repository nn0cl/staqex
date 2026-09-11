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
    processed_event_keys: tuple[tuple[str, int, int], ...] = ()


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


@dataclass(frozen=True)
class WorkflowEvent:
    job_id: str
    plan_revision: int
    sequence: int
    kind: str


@dataclass(frozen=True)
class EventApplicationResult:
    status: str
    plan: WorkflowPlan
    diagnostic: Diagnostic | None = None


def _rejected(plan: WorkflowPlan, code: str, message: str) -> TransitionResult:
    return TransitionResult(
        status="rejected",
        plan_identity=plan.identity,
        diagnostic=Diagnostic(code=code, message=message),
    )


def _same_identity(left: PlanIdentity, right: PlanIdentity) -> bool:
    return left == right


def _identity_is_current(plan: WorkflowPlan, result: JobResultEnvelope) -> bool:
    return _same_identity(plan.identity, result.plan_identity) and _same_identity(
        plan.identity, plan.approval.plan_identity
    )


def _approval_is_current(plan: WorkflowPlan, *, now: str) -> bool:
    return not plan.approval.cancelled and now < plan.approval.expires_at


def apply_job_result(
    plan: WorkflowPlan,
    result: JobResultEnvelope,
    *,
    now: str,
) -> TransitionResult:
    """Adopt a completed result only when the Unit A contract is current."""

    if not _identity_is_current(plan, result):
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
    if not _approval_is_current(plan, now=now):
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


def _event_key(event: WorkflowEvent) -> tuple[str, int, int]:
    return (event.job_id, event.plan_revision, event.sequence)


def _event_revision_is_stale(plan: WorkflowPlan, event: WorkflowEvent) -> bool:
    return event.plan_revision < plan.identity.revision


def _completed_plan(plan: WorkflowPlan, key: tuple[str, int, int]) -> WorkflowPlan:
    return WorkflowPlan(
        identity=plan.identity,
        state="completed",
        approval=plan.approval,
        processed_event_keys=plan.processed_event_keys + (key,),
    )


def _event_rejected(plan: WorkflowPlan, code: str, message: str) -> EventApplicationResult:
    return EventApplicationResult(
        status="rejected",
        plan=plan,
        diagnostic=Diagnostic(code=code, message=message),
    )


def apply_event(plan: WorkflowPlan, event: WorkflowEvent) -> EventApplicationResult:
    """Apply one provider-neutral event without reapplying duplicate events."""

    key = _event_key(event)
    if key in plan.processed_event_keys:
        return _event_rejected(
            plan,
            "WORKFLOW_DUPLICATE_EVENT",
            "the event has already been applied to this Plan",
        )
    if _event_revision_is_stale(plan, event):
        return _event_rejected(
            plan,
            "WORKFLOW_STALE_RESULT",
            "the event belongs to an older Plan revision",
        )
    if event.kind == "timeout-after-cancel":
        return _event_rejected(
            plan,
            "WORKFLOW_TIMEOUT_CANCEL_RACE",
            "timeout and cancellation reached the same Job boundary",
        )
    if event.kind != "job-completed":
        return _event_rejected(
            plan,
            "WORKFLOW_STALE_RESULT",
            "event kind is not adoptable by Unit B",
        )
    return EventApplicationResult(
        status="completed",
        plan=_completed_plan(plan, key),
    )


def request_fallback(plan: WorkflowPlan, *, reason: str) -> TransitionResult:
    """Reject implicit fallback; a fallback must be a separately approved Plan."""

    return _rejected(
        plan,
        "WORKFLOW_FALLBACK_REQUIRES_NEW_PLAN",
        f"fallback reason {reason!r} requires a new Plan and approval",
    )
