"""Phase 1 Red tests for WP-0138 / LISS-0521 Unit A."""

from __future__ import annotations

import importlib

import pytest


def _lifecycle_module():
    try:
        return importlib.import_module("compiler.staqex.workflow_lifecycle")
    except ModuleNotFoundError as error:
        pytest.fail("LISS-0521 Unit A implementation is not present yet")
        raise AssertionError from error


def _identity(module, *, revision: int = 1, content_hash: str = "hash:plan-001"):
    return module.PlanIdentity(
        plan_id="plan:s02-round-001",
        snapshot_id="snapshot:s02-round-001",
        content_hash=content_hash,
        revision=revision,
    )


def _approval(module, *, expires_at: str = "2026-09-09T01:00:00Z", cancelled: bool = False):
    return module.ApprovalBinding(
        approval_id="approval:s02-policy-v1",
        plan_identity=_identity(module),
        policy_revision="policy:s02-v1",
        expires_at=expires_at,
        cancelled=cancelled,
    )


def _plan(module):
    return module.WorkflowPlan(
        identity=_identity(module),
        state="awaiting-approval",
        approval=_approval(module),
    )


def test_unit_a_accepts_completed_job_only_with_current_approval_and_identity() -> None:
    module = _lifecycle_module()
    plan = _plan(module)

    accepted = module.apply_job_result(
        plan,
        module.JobResultEnvelope(
            job_id="job:s02-fake-001",
            plan_identity=plan.identity,
            status="completed",
        ),
        now="2026-09-09T00:30:00Z",
    )

    assert accepted.status == "accepted-for-plan"
    assert accepted.plan_identity == plan.identity


def test_unit_a_rejects_expired_approval_without_adopting_job_result() -> None:
    module = _lifecycle_module()
    plan = _plan(module)

    result = module.apply_job_result(
        plan,
        module.JobResultEnvelope(
            job_id="job:s02-fake-001",
            plan_identity=plan.identity,
            status="completed",
        ),
        now="2026-09-09T01:00:01Z",
    )

    assert result.status == "rejected"
    assert result.diagnostic.code == "WORKFLOW_APPROVAL_EXPIRED"


def test_unit_a_rejects_cancelled_approval() -> None:
    module = _lifecycle_module()
    plan = module.WorkflowPlan(
        identity=_identity(module),
        state="awaiting-approval",
        approval=_approval(module, cancelled=True),
    )

    result = module.apply_job_result(
        plan,
        module.JobResultEnvelope(
            job_id="job:s02-fake-001",
            plan_identity=plan.identity,
            status="completed",
        ),
        now="2026-09-09T00:30:00Z",
    )

    assert result.status == "rejected"
    assert result.diagnostic.code == "WORKFLOW_APPROVAL_CANCELLED"


def test_unit_a_quarantines_stale_result_and_plan_identity_mismatch() -> None:
    module = _lifecycle_module()
    plan = _plan(module)
    stale_result = module.JobResultEnvelope(
        job_id="job:s02-fake-001",
        plan_identity=_identity(module, revision=0, content_hash="hash:old"),
        status="completed",
    )

    result = module.apply_job_result(
        plan,
        stale_result,
        now="2026-09-09T00:30:00Z",
    )

    assert result.status == "rejected"
    assert result.diagnostic.code in {
        "WORKFLOW_STALE_RESULT",
        "WORKFLOW_PLAN_IDENTITY_MISMATCH",
    }


def test_unit_a_never_treats_completed_job_as_adoptable_when_plan_is_not_approved() -> None:
    module = _lifecycle_module()
    plan = module.WorkflowPlan(
        identity=_identity(module),
        state="running",
        approval=_approval(module),
    )

    result = module.apply_job_result(
        plan,
        module.JobResultEnvelope(
            job_id="job:s02-fake-001",
            plan_identity=plan.identity,
            status="completed",
        ),
        now="2026-09-09T00:30:00Z",
    )

    assert result.status == "rejected"
    assert result.diagnostic.code == "WORKFLOW_PLAN_IDENTITY_MISMATCH"
