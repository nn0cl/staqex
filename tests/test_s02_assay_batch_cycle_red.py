"""Phase 1 Red tests for WP-0139 / LISS-0522 D04."""

from __future__ import annotations

import importlib

import pytest


def _batch_module():
    try:
        return importlib.import_module("compiler.staqex.s02_assay_batch_cycle")
    except ModuleNotFoundError as error:
        pytest.fail("LISS-0522 D04 implementation is not present yet")
        raise AssertionError from error


def _snapshot(module, *, round_id: str = "round:001"):
    return module.AssaySnapshot(
        snapshot_id=f"assay:s02-{round_id}",
        round_id=round_id,
        cutoff="2026-09-01T00:00:00Z",
        source_hash="sha256:assay-001",
    )


def _candidates():
    return (
        {"candidate_id": "candidate:001", "predicted_ic50_nM": 1.0, "uncertainty": 0.1, "stock": True, "cost": 3},
        {"candidate_id": "candidate:002", "predicted_ic50_nM": 2.0, "uncertainty": 0.2, "stock": True, "cost": 3},
    )


def _approval(module, *, snapshot):
    return module.ApprovalPolicy(
        policy_revision="policy:s02-batch-v1",
        snapshot_id=snapshot.snapshot_id,
        model_revision="model:s02-v1",
        expires_at="2026-09-09T01:00:00Z",
    )


def test_d04_proposes_batch_with_reason_prediction_constraints_cost_and_approval_target() -> None:
    module = _batch_module()
    snapshot = _snapshot(module)

    result = module.create_batch_proposal(
        snapshot=snapshot,
        candidates=_candidates(),
        selected_candidate_ids=("candidate:001", "candidate:002"),
        approval=_approval(module, snapshot=snapshot),
        prospective_available=False,
    )

    assert result.status == "awaiting-approval"
    assert result.proposal.selected_candidate_ids == (
        "candidate:001",
        "candidate:002",
    )
    assert result.proposal.selection_reasons
    assert result.proposal.predictions
    assert result.proposal.constraint_verdict == "feasible"
    assert result.proposal.cost == 6
    assert result.proposal.prospective_evidence == "unavailable"


def test_d04_rejects_future_round_labels_during_proposal_generation() -> None:
    module = _batch_module()
    snapshot = _snapshot(module)

    result = module.create_batch_proposal(
        snapshot=snapshot,
        candidates=_candidates(),
        selected_candidate_ids=("candidate:001", "candidate:002"),
        approval=_approval(module, snapshot=snapshot),
        future_labels={"candidate:001": 0.8},
        prospective_available=False,
    )

    assert result.status == "rejected"
    assert result.diagnostic.code == "ASSAY_FUTURE_LABEL_VISIBLE"


def test_d04_rejects_approval_bound_to_a_different_snapshot() -> None:
    module = _batch_module()
    snapshot = _snapshot(module)
    approval = _approval(module, snapshot=_snapshot(module, round_id="round:000"))

    result = module.create_batch_proposal(
        snapshot=snapshot,
        candidates=_candidates(),
        selected_candidate_ids=("candidate:001", "candidate:002"),
        approval=approval,
        prospective_available=False,
    )

    assert result.status == "rejected"
    assert result.diagnostic.code == "ASSAY_STALE_APPROVAL"


def test_d04_rejects_candidate_stock_change_before_approval() -> None:
    module = _batch_module()
    snapshot = _snapshot(module)
    candidates = list(_candidates())
    candidates[1] = {**candidates[1], "stock": False}

    result = module.create_batch_proposal(
        snapshot=snapshot,
        candidates=tuple(candidates),
        selected_candidate_ids=("candidate:001", "candidate:002"),
        approval=_approval(module, snapshot=snapshot),
        prospective_available=False,
    )

    assert result.status == "rejected"
    assert result.diagnostic.code == "ASSAY_CANDIDATE_STATE_CHANGED"


def test_d04_ingests_frozen_follow_up_round_as_a_new_snapshot_revision() -> None:
    module = _batch_module()
    first = _snapshot(module)
    follow_up = _snapshot(module, round_id="round:002")

    result = module.ingest_follow_up_round(
        previous_snapshot=first,
        follow_up_snapshot=follow_up,
        observed_results={"candidate:001": 0.8},
    )

    assert result.status == "new-snapshot"
    assert result.snapshot.snapshot_id == "assay:s02-round:002"
    assert result.snapshot.revision == 2
