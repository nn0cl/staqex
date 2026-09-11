"""Provider-neutral S02 next-assay proposal and snapshot cycle."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
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
    approval_id: str = "approval:s02-batch-v1"


@dataclass(frozen=True)
class BatchProposal:
    plan_id: str
    snapshot_id: str
    model_revision: str
    policy_revision: str
    approval_hash: str
    deadline: str
    selected_candidate_ids: tuple[str, ...]
    selection_reasons: tuple[str, ...]
    predictions: tuple[float, ...]
    uncertainties: tuple[float, ...]
    provenance: tuple[tuple[str, str], ...]
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
    diagnostic: Diagnostic | None = None


def _rejected(code: str, message: str) -> ProposalResult:
    return ProposalResult(
        status="rejected",
        diagnostic=Diagnostic(code=code, message=message),
    )


def _proposal_hash(values: Mapping[str, Any]) -> str:
    encoded = json.dumps(values, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _parse_timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include a timezone")
    return parsed


def _approval_hash(approval: ApprovalPolicy) -> str:
    return _proposal_hash(
        {
            "approval_id": approval.approval_id,
            "policy_revision": approval.policy_revision,
            "snapshot_id": approval.snapshot_id,
            "model_revision": approval.model_revision,
            "expires_at": approval.expires_at,
        }
    )


def _candidate_is_selected(
    candidate: Mapping[str, Any], selected_ids: set[str]
) -> bool:
    return str(candidate["candidate_id"]) in selected_ids


def _candidate_provenance(
    candidate: Mapping[str, Any]
) -> tuple[str, str] | None:
    source_hash = candidate.get("source_hash")
    license_name = candidate.get("license")
    if not source_hash or not license_name:
        return None
    return str(source_hash), str(license_name)


def _candidate_model_matches(
    candidate: Mapping[str, Any], approval: ApprovalPolicy
) -> bool:
    return candidate.get("model_revision") in (None, approval.model_revision)


def _validate_proposal_inputs(
    *,
    snapshot: AssaySnapshot,
    candidates: tuple[Mapping[str, Any], ...],
    selected_candidate_ids: tuple[str, ...],
    approval: ApprovalPolicy,
    future_labels: Mapping[str, float] | None,
    as_of: str | None,
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
    if as_of is not None and _parse_timestamp(as_of) >= _parse_timestamp(
        approval.expires_at
    ):
        return _rejected(
            "ASSAY_STALE_APPROVAL",
            "approval has expired before proposal creation",
        )
    selected_ids = set(selected_candidate_ids)
    if len(selected_ids) != len(selected_candidate_ids):
        return _rejected(
            "ASSAY_DUPLICATE_ROUND",
            "a candidate cannot be selected more than once in a proposal",
        )
    for candidate in candidates:
        if not _candidate_is_selected(candidate, selected_ids):
            continue
        if _candidate_provenance(candidate) is None:
            return _rejected(
                "ASSAY_MISSING_PROVENANCE",
                "selected candidate provenance is incomplete",
            )
        if not _candidate_model_matches(candidate, approval):
            return _rejected(
                "ASSAY_STALE_APPROVAL",
                "selected candidate uses a different model revision",
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


def _proposal_observations(
    selected: list[Mapping[str, Any]],
) -> tuple[tuple[float, ...], tuple[tuple[str, str], ...]]:
    uncertainties = tuple(float(candidate["uncertainty"]) for candidate in selected)
    provenance = tuple(
        (str(candidate["source_hash"]), str(candidate["license"]))
        for candidate in selected
    )
    return uncertainties, provenance


def _proposal_content(
    *,
    snapshot: AssaySnapshot,
    approval: ApprovalPolicy,
    selected_candidate_ids: tuple[str, ...],
    predictions: tuple[float, ...],
    cost: int,
    uncertainties: tuple[float, ...],
    provenance: tuple[tuple[str, str], ...],
    approval_hash: str,
) -> str:
    return _proposal_hash(
        {
            "plan_id": f"plan:{snapshot.round_id}:assay-batch",
            "snapshot_id": snapshot.snapshot_id,
            "model_revision": approval.model_revision,
            "policy_revision": approval.policy_revision,
            "approval_hash": approval_hash,
            "deadline": approval.expires_at,
            "selected_candidate_ids": selected_candidate_ids,
            "predictions": predictions,
            "uncertainties": uncertainties,
            "provenance": provenance,
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
    as_of: str | None = None,
) -> ProposalResult:
    """Create a human-approval proposal from one immutable assay snapshot."""

    rejection = _validate_proposal_inputs(
        snapshot=snapshot,
        candidates=candidates,
        selected_candidate_ids=selected_candidate_ids,
        approval=approval,
        future_labels=future_labels,
        as_of=as_of,
    )
    if rejection is not None:
        return rejection

    selected = _selected_candidates(candidates, selected_candidate_ids)
    predictions = tuple(float(candidate["predicted_ic50_nM"]) for candidate in selected)
    uncertainties, provenance = _proposal_observations(selected)
    reasons = _selection_reasons(selected)
    cost = sum(int(candidate["cost"]) for candidate in selected)
    approval_hash = _approval_hash(approval)
    plan_id = f"plan:{snapshot.round_id}:assay-batch"
    content_hash = _proposal_content(
        snapshot=snapshot,
        approval=approval,
        selected_candidate_ids=selected_candidate_ids,
        predictions=predictions,
        cost=cost,
        uncertainties=uncertainties,
        provenance=provenance,
        approval_hash=approval_hash,
    )
    return ProposalResult(
        status="awaiting-approval",
        proposal=BatchProposal(
            plan_id=plan_id,
            snapshot_id=snapshot.snapshot_id,
            model_revision=approval.model_revision,
            policy_revision=approval.policy_revision,
            approval_hash=approval_hash,
            deadline=approval.expires_at,
            selected_candidate_ids=selected_candidate_ids,
            selection_reasons=reasons,
            predictions=predictions,
            uncertainties=uncertainties,
            provenance=provenance,
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

    if follow_up_snapshot.round_id == previous_snapshot.round_id:
        return SnapshotResult(
            status="rejected",
            snapshot=previous_snapshot,
            diagnostic=Diagnostic(
                code="ASSAY_DUPLICATE_ROUND",
                message="follow-up round duplicates the previous round",
            ),
        )
    if follow_up_snapshot.revision != previous_snapshot.revision + 1:
        raise ValueError("follow-up snapshot revision must advance exactly once")
    if not observed_results:
        raise ValueError("follow-up round requires observed results")
    return SnapshotResult(status="new-snapshot", snapshot=follow_up_snapshot)
