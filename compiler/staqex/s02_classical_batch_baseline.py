"""Provider-neutral classical batch baseline and feasibility oracle for S02."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from types import MappingProxyType
from typing import Any, Mapping


_METHOD = "greedy-feasible-v1"
_PARTIAL_BATCH_LIMIT = "partial"


@dataclass(frozen=True)
class BatchDiagnostic:
    code: str
    message: str


@dataclass(frozen=True)
class BatchProfile:
    profile_id: str
    candidate_set_id: str
    batch_size: int
    budget: int
    max_per_diversity_group: int
    objective: str


@dataclass(frozen=True)
class SelectionResult:
    status: str
    method: str
    candidate_set_id: str
    feasible: bool
    selected_candidate_ids: tuple[str, ...]
    score: float | None
    diagnostic: BatchDiagnostic | None = None
    candidate_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class ComparisonResult:
    status: str
    diagnostic: BatchDiagnostic | None = None


def _candidate_ids(candidates: tuple[Mapping[str, Any], ...]) -> tuple[str, ...]:
    return tuple(str(candidate["candidate_id"]) for candidate in candidates)


def _diagnostic(code: str, message: str) -> BatchDiagnostic:
    return BatchDiagnostic(code=code, message=message)


def _quarantined_comparison(code: str, message: str) -> ComparisonResult:
    return ComparisonResult(
        status="quarantine",
        diagnostic=_diagnostic(code, message),
    )


def _within_hard_constraints(
    selected: tuple[Mapping[str, Any], ...],
    profile: BatchProfile,
    *,
    require_full_batch: bool,
) -> bool:
    if require_full_batch and len(selected) != profile.batch_size:
        return False
    if len(selected) > profile.batch_size:
        return False
    if any(not bool(candidate.get("stock")) for candidate in selected):
        return False
    if sum(int(candidate["cost"]) for candidate in selected) > profile.budget:
        return False
    groups: dict[str, int] = {}
    for candidate in selected:
        group = str(candidate["diversity_group"])
        groups[group] = groups.get(group, 0) + 1
    return all(count <= profile.max_per_diversity_group for count in groups.values())


def _score(selected: tuple[Mapping[str, Any], ...]) -> float:
    return sum(float(candidate["predicted_ic50_nM"]) for candidate in selected)


def _no_feasible(
    profile: BatchProfile,
    candidate_ids: tuple[str, ...],
) -> SelectionResult:
    return SelectionResult(
        status="no-feasible-plan",
        method="enumeration",
        candidate_set_id=profile.candidate_set_id,
        feasible=False,
        selected_candidate_ids=(),
        score=None,
        diagnostic=_diagnostic(
            "BATCH_NO_FEASIBLE_PLAN",
            "no candidate subset satisfies every hard constraint",
        ),
        candidate_ids=candidate_ids,
    )


def enumerate_batches(
    candidates: tuple[Mapping[str, Any], ...],
    profile: BatchProfile,
) -> SelectionResult:
    """Evaluate every fixed-size candidate subset as the reference oracle."""

    candidate_ids = _candidate_ids(candidates)
    if len(set(candidate_ids)) != len(candidate_ids):
        return SelectionResult(
            status="quarantine",
            method="enumeration",
            candidate_set_id=profile.candidate_set_id,
            feasible=False,
            selected_candidate_ids=(),
            score=None,
            diagnostic=_diagnostic(
                "BATCH_CANDIDATE_SET_MISMATCH",
                "candidate IDs must be unique",
            ),
            candidate_ids=candidate_ids,
        )

    feasible = [
        subset
        for subset in combinations(candidates, profile.batch_size)
        if _within_hard_constraints(subset, profile, require_full_batch=True)
    ]
    if not feasible:
        return _no_feasible(profile, candidate_ids)

    selected = min(
        feasible,
        key=lambda subset: (
            _score(subset),
            tuple(str(item["candidate_id"]) for item in subset),
        ),
    )
    return SelectionResult(
        status="accepted",
        method="enumeration",
        candidate_set_id=profile.candidate_set_id,
        feasible=True,
        selected_candidate_ids=tuple(str(item["candidate_id"]) for item in selected),
        score=_score(selected),
        candidate_ids=candidate_ids,
    )


def greedy_baseline(
    candidates: tuple[Mapping[str, Any], ...],
    profile: BatchProfile,
) -> SelectionResult:
    """Select low predicted IC50 candidates while preserving hard constraints."""

    candidate_ids = _candidate_ids(candidates)
    selected: list[Mapping[str, Any]] = []
    for candidate in sorted(
        candidates,
        key=lambda item: (float(item["predicted_ic50_nM"]), str(item["candidate_id"])),
    ):
        proposed = tuple(selected + [candidate])
        if _within_hard_constraints(proposed, profile, require_full_batch=False):
            selected.append(candidate)

    chosen = tuple(selected)
    if not _within_hard_constraints(chosen, profile, require_full_batch=True):
        return _no_feasible(profile, candidate_ids)
    return SelectionResult(
        status="accepted",
        method=_METHOD,
        candidate_set_id=profile.candidate_set_id,
        feasible=True,
        selected_candidate_ids=tuple(str(item["candidate_id"]) for item in chosen),
        score=_score(chosen),
        candidate_ids=candidate_ids,
    )


def compare_selections(
    oracle: SelectionResult,
    baseline: SelectionResult,
) -> ComparisonResult:
    """Compare results only when candidate set, feasibility, and score agree."""

    if oracle.candidate_set_id != baseline.candidate_set_id or (
        oracle.candidate_ids
        and baseline.candidate_ids
        and oracle.candidate_ids != baseline.candidate_ids
    ):
        return _quarantined_comparison(
            "BATCH_CANDIDATE_SET_MISMATCH",
            "oracle and baseline used different candidate sets",
        )
    if oracle.feasible != baseline.feasible:
        return _quarantined_comparison(
            "BATCH_CONSTRAINT_MISMATCH",
            "oracle and baseline disagree on feasibility",
        )
    if oracle.score != baseline.score:
        return _quarantined_comparison(
            "BATCH_SCORE_MISMATCH",
            "oracle and baseline scores differ",
        )
    if oracle.selected_candidate_ids != baseline.selected_candidate_ids:
        return _quarantined_comparison(
            "BATCH_CONSTRAINT_MISMATCH",
            "oracle and baseline selected different feasible batches",
        )
    return ComparisonResult(status="matched")
