"""Phase 1 Red tests for WP-0138 / LISS-0521 Unit B."""

from __future__ import annotations

import importlib

import pytest


def _lifecycle_module():
    try:
        return importlib.import_module("compiler.staqex.workflow_lifecycle")
    except ModuleNotFoundError as error:
        pytest.fail("LISS-0521 Unit B implementation is not present yet")
        raise AssertionError from error


def _plan(module):
    identity = module.PlanIdentity(
        plan_id="plan:s02-round-001",
        snapshot_id="snapshot:s02-round-001",
        content_hash="hash:plan-001",
        revision=1,
    )
    approval = module.ApprovalBinding(
        approval_id="approval:s02-policy-v1",
        plan_identity=identity,
        policy_revision="policy:s02-v1",
        expires_at="2026-09-09T01:00:00Z",
    )
    return module.WorkflowPlan(identity=identity, state="approved", approval=approval)


def test_unit_b_deduplicates_the_same_event_without_reapplying_state() -> None:
    module = _lifecycle_module()
    plan = _plan(module)
    event = module.WorkflowEvent(
        job_id="job:s02-fake-001",
        plan_revision=1,
        sequence=1,
        kind="job-completed",
    )

    first = module.apply_event(plan, event)
    duplicate = module.apply_event(first.plan, event)

    assert first.status == "completed"
    assert duplicate.status == "rejected"
    assert duplicate.diagnostic.code == "WORKFLOW_DUPLICATE_EVENT"


def test_unit_b_keeps_late_events_stale_instead_of_overwriting_current_plan() -> None:
    module = _lifecycle_module()
    plan = _plan(module)
    late_event = module.WorkflowEvent(
        job_id="job:s02-fake-001",
        plan_revision=0,
        sequence=1,
        kind="job-completed",
    )

    result = module.apply_event(plan, late_event)

    assert result.status == "rejected"
    assert result.diagnostic.code == "WORKFLOW_STALE_RESULT"


def test_unit_b_records_timeout_cancel_race_as_a_diagnostic_outcome() -> None:
    module = _lifecycle_module()
    plan = _plan(module)
    event = module.WorkflowEvent(
        job_id="job:s02-fake-001",
        plan_revision=1,
        sequence=2,
        kind="timeout-after-cancel",
    )

    result = module.apply_event(plan, event)

    assert result.status == "rejected"
    assert result.diagnostic.code == "WORKFLOW_TIMEOUT_CANCEL_RACE"


def test_unit_b_requires_a_new_plan_for_fallback() -> None:
    module = _lifecycle_module()
    plan = _plan(module)

    result = module.request_fallback(plan, reason="provider-timeout")

    assert result.status == "rejected"
    assert result.diagnostic.code == "WORKFLOW_FALLBACK_REQUIRES_NEW_PLAN"
