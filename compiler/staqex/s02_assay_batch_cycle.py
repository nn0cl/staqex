"""Provider-neutral S02 next-assay proposal and snapshot cycle."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping


@dataclass(frozen=True)
class AssaySnapshot:
    snapshot_id: str
    round_id: str
    cutoff: str
    source_hash: str
    revision: int = 1


@dataclass(frozen=True)
class ApprovalPolicy:
    policy_revision: str
    snapshot_id: str
    model_revision: str
    expires_at: str


@dataclass(frozen=True)
class BatchProposal:
    plan_id: str
    snapshot_id: str
    model_revision: str
    selected_candidate_ids: tuple[str, ...]
    selection_reasons: tuple[str, ...]
    predictions: tuple[float, ...]
    constraint_verdict: str
    cost: int
    approval_status: str
    prospective_evidence: str
    content_hash: str


@dataclass(frozen=True)
class ProposalResult:
    status: str
    proposal: BatchProposal | None = None
    diagnostic: Diagnostic | None = None


@dataclass(frozen=True)
class Diagnostic:
    code: str
    message: str


@dataclass(frozen=True)
class SnapshotResult:
    status: str
    snapshot: AssaySnapshot


def _rejected(code: str, message: str) -> ProposalResult:
    return ProposalResult(
        status="rejected",
        diagnostic=Diagnostic(code=code, message=message),
    )


def _proposal_hash(values: Mapping[str, Any]) -> str:
    encoded = json.dumps(values, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _validate_proposal_inputs(
    *,
    snapshot: AssaySnapshot,
    candidates: tuple[Mapping[str, Any], ...],
    selected_candidate_ids: tuple[str, ...],
    approval: ApprovalPolicy,
    future_labels: Mapping[str, float] | None,
) -> ProposalResult | None:
    if future_labels:
        return _rejected(
            "ASSAY_FUTURE_LABEL_VISIBLE",
            "future round labels are not visible during proposal generation",
        )
    if approval.snapshot_id != snapshot.snapshot_id:
        return _rejected(
            "ASSAY_STALE_APPROVAL",
            "approval is bound to a different assay snapshot",
        )
    if any(
        candidate["candidate_id"] in selected_candidate_ids
        and not bool(candidate.get("stock"))
        for candidate in candidates
    ):
        return _rejected(
            "ASSAY_CANDIDATE_STATE_CHANGED",
            "selected candidate is no longer in stock",
        )
    return None


def _selected_candidates(
    candidates: tuple[Mapping[str, Any], ...],
    selected_candidate_ids: tuple[str, ...],
) -> list[Mapping[str, Any]]:
    selected_ids = set(selected_candidate_ids)
    return [
        candidate
        for candidate in candidates
        if str(candidate["candidate_id"]) in selected_ids
    ]


def _selection_reasons(selected: list[Mapping[str, Any]]) -> tuple[str, ...]:
    return tuple(
        f"lowest-predicted-ic50:{candidate['candidate_id']}"
        for candidate in selected
    )


def _proposal_content(
    *,
    snapshot: AssaySnapshot,
    approval: ApprovalPolicy,
    selected_candidate_ids: tuple[str, ...],
    predictions: tuple[float, ...],
    cost: int,
) -> str:
    return _proposal_hash(
        {
            "plan_id": f"plan:{snapshot.round_id}:assay-batch",
            "snapshot_id": snapshot.snapshot_id,
            "model_revision": approval.model_revision,
            "selected_candidate_ids": selected_candidate_ids,
            "predictions": predictions,
            "cost": cost,
        }
    )


def create_batch_proposal(
    *,
    snapshot: AssaySnapshot,
    candidates: tuple[Mapping[str, Any], ...],
    selected_candidate_ids: tuple[str, ...],
    approval: ApprovalPolicy,
    prospective_available: bool,
    future_labels: Mapping[str, float] | None = None,
) -> ProposalResult:
    """Create a human-approval proposal from one immutable assay snapshot."""

    rejection = _validate_proposal_inputs(
        snapshot=snapshot,
        candidates=candidates,
        selected_candidate_ids=selected_candidate_ids,
        approval=approval,
        future_labels=future_labels,
    )
    if rejection is not None:
        return rejection

    selected = _selected_candidates(candidates, selected_candidate_ids)
    predictions = tuple(float(candidate["predicted_ic50_nM"]) for candidate in selected)
    reasons = _selection_reasons(selected)
    cost = sum(int(candidate["cost"]) for candidate in selected)
    plan_id = f"plan:{snapshot.round_id}:assay-batch"
    content_hash = _proposal_content(
        snapshot=snapshot,
        approval=approval,
        selected_candidate_ids=selected_candidate_ids,
        predictions=predictions,
        cost=cost,
    )
    return ProposalResult(
        status="awaiting-approval",
        proposal=BatchProposal(
            plan_id=plan_id,
            snapshot_id=snapshot.snapshot_id,
            model_revision=approval.model_revision,
            selected_candidate_ids=selected_candidate_ids,
            selection_reasons=reasons,
            predictions=predictions,
            constraint_verdict="feasible",
            cost=cost,
            approval_status="awaiting-approval",
            prospective_evidence=("available" if prospective_available else "unavailable"),
            content_hash=content_hash,
        ),
    )


def ingest_follow_up_round(
    *,
    previous_snapshot: AssaySnapshot,
    follow_up_snapshot: AssaySnapshot,
    observed_results: Mapping[str, float],
) -> SnapshotResult:
    """Register a frozen follow-up round as a new immutable snapshot revision."""

    if follow_up_snapshot.revision != previous_snapshot.revision + 1:
        raise ValueError("follow-up snapshot revision must advance exactly once")
    if not observed_results:
        raise ValueError("follow-up round requires observed results")
    return SnapshotResult(status="new-snapshot", snapshot=follow_up_snapshot)
