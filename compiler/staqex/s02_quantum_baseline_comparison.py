"""Provider-neutral comparison of the S02 classical and quantum lanes."""

from __future__ import annotations

from dataclasses import dataclass


_LINEAGE_FIELDS = (
    "snapshot_id",
    "candidate_set_id",
    "profile_id",
    "baseline_revision",
    "artifact_id",
    "encoding_id",
    "manifest_id",
)
_CANDIDATE_LINEAGE_FIELDS = {"candidate_set_id", "profile_id"}


@dataclass(frozen=True)
class LaneDiagnostic:
    code: str
    message: str


@dataclass(frozen=True)
class LaneResult:
    lane: str
    status: str
    selected_candidate_ids: tuple[str, ...]
    feasible: bool
    objective: float | None
    decoded_valid: bool
    cost: object | None = None
    diagnostic: LaneDiagnostic | None = None
    snapshot_id: str = ""
    candidate_set_id: str = ""
    profile_id: str = ""
    baseline_revision: str = ""
    artifact_id: str = ""
    encoding_id: str = ""
    manifest_id: str = ""


@dataclass(frozen=True)
class CostBreakdown:
    queue: float | None
    encode: float | None
    execute: float | None
    decode: float | None

    @property
    def total(self) -> float | None:
        values = (self.queue, self.encode, self.execute, self.decode)
        if any(value is None for value in values):
            return None
        return sum(value for value in values if value is not None)


@dataclass(frozen=True)
class ComparisonInput:
    problem_id: str
    snapshot_id: str
    candidate_set_id: str
    profile_id: str
    baseline_revision: str
    quantum_artifact_id: str
    classical: LaneResult
    quantum: LaneResult
    cost: CostBreakdown
    objective_tolerance: float
    encoding_id: str = "encoding:s02-one-bit-v1"
    manifest_id: str = "manifest:s02-d05-v1"


@dataclass(frozen=True)
class ComparisonResult:
    status: str
    selected_candidate_ids: tuple[str, ...] = ()
    feasibility_match: bool = False
    objective_gap: float | None = None
    cost: CostBreakdown | None = None
    quantum_advantage: str = "not-established"
    classical_fallback_selected_candidate_ids: tuple[str, ...] = ()
    diagnostic: LaneDiagnostic | None = None
    snapshot_id: str = ""
    profile_id: str = ""
    quantum_artifact_id: str = ""
    encoding_id: str = ""
    manifest_id: str = ""


def _quarantine(code: str, message: str) -> ComparisonResult:
    return ComparisonResult(
        status="quarantine",
        diagnostic=LaneDiagnostic(code=code, message=message),
    )


def _inconclusive(
    lane: LaneResult,
    *,
    classical: LaneResult,
    cost: CostBreakdown | None,
) -> ComparisonResult:
    diagnostic = lane.diagnostic or LaneDiagnostic(
        code="QUANTUM_COMPARISON_INCONCLUSIVE",
        message="quantum lane did not produce a comparable result",
    )
    return ComparisonResult(
        status="inconclusive",
        cost=cost,
        diagnostic=diagnostic,
        classical_fallback_selected_candidate_ids=classical.selected_candidate_ids,
    )


def _validate_quantum_lane(lane: LaneResult) -> ComparisonResult | None:
    if not lane.decoded_valid:
        return _quarantine(
            "QUANTUM_DECODE_INVALID",
            "quantum terminal output cannot be decoded safely",
        )
    if not lane.feasible:
        return _quarantine(
            "QUANTUM_CONSTRAINT_VIOLATION",
            "quantum terminal output violates a hard constraint",
        )
    return None


def _validate_cost(cost: CostBreakdown) -> bool:
    return cost.total is not None


def _same_selection(classical: LaneResult, quantum: LaneResult) -> bool:
    return classical.selected_candidate_ids == quantum.selected_candidate_ids


def _lineage_diagnostic(field_name: str, message: str) -> LaneDiagnostic:
    code = (
        "QUANTUM_CANDIDATE_SET_MISMATCH"
        if field_name in _CANDIDATE_LINEAGE_FIELDS
        else "QUANTUM_BASELINE_MISMATCH"
    )
    return LaneDiagnostic(code=code, message=message)


def _lineage_mismatch(
    comparison: ComparisonInput,
    *,
    classical: LaneResult,
    quantum: LaneResult,
) -> LaneDiagnostic | None:
    for field_name in _LINEAGE_FIELDS:
        classical_value = getattr(classical, field_name)
        quantum_value = getattr(quantum, field_name)
        if classical_value != quantum_value:
            return _lineage_diagnostic(
                field_name,
                f"classical and quantum lanes disagree on {field_name}",
            )

    expected_values = {
        "snapshot_id": comparison.snapshot_id,
        "candidate_set_id": comparison.candidate_set_id,
        "profile_id": comparison.profile_id,
        "baseline_revision": comparison.baseline_revision,
        "artifact_id": comparison.quantum_artifact_id,
        "encoding_id": comparison.encoding_id,
        "manifest_id": comparison.manifest_id,
    }
    for field_name in _LINEAGE_FIELDS:
        expected_value = expected_values[field_name]
        actual_value = getattr(quantum, field_name)
        if expected_value != actual_value:
            return _lineage_diagnostic(
                field_name,
                f"quantum lane does not match comparison {field_name}",
            )
    return None


def _missing_cost_result(
    quantum: LaneResult,
    *,
    classical: LaneResult,
) -> ComparisonResult:
    return _inconclusive(
        LaneResult(
            lane="quantum",
            status="rejected",
            selected_candidate_ids=quantum.selected_candidate_ids,
            feasible=False,
            objective=None,
            decoded_valid=False,
            diagnostic=LaneDiagnostic(
                code="QUANTUM_COST_MISSING",
                message="quantum lane cost breakdown is incomplete",
            ),
        ),
        classical=classical,
        cost=None,
    )


def _matched_result(
    comparison: ComparisonInput,
    *,
    objective_gap: float,
) -> ComparisonResult:
    return ComparisonResult(
        status="matched",
        selected_candidate_ids=comparison.classical.selected_candidate_ids,
        feasibility_match=(
            comparison.classical.feasible == comparison.quantum.feasible
        ),
        objective_gap=objective_gap,
        cost=comparison.cost,
        snapshot_id=comparison.snapshot_id,
        profile_id=comparison.profile_id,
        quantum_artifact_id=comparison.quantum_artifact_id,
        encoding_id=comparison.encoding_id,
        manifest_id=comparison.manifest_id,
    )


def compare_baseline_and_quantum(comparison: ComparisonInput) -> ComparisonResult:
    """Compare two fixed lanes without converting failure into success."""

    classical = comparison.classical
    quantum = comparison.quantum
    lineage_error = _lineage_mismatch(
        comparison, classical=classical, quantum=quantum
    )
    if lineage_error is not None:
        return _quarantine(lineage_error.code, lineage_error.message)
    if quantum.status != "accepted":
        return _inconclusive(quantum, classical=classical, cost=None)
    if not _same_selection(classical, quantum):
        return _quarantine(
            "QUANTUM_CANDIDATE_SET_MISMATCH",
            "classical and quantum lanes selected different candidate identities",
        )

    invalid_quantum = _validate_quantum_lane(quantum)
    if invalid_quantum is not None:
        return invalid_quantum
    if not _validate_cost(comparison.cost):
        return _missing_cost_result(quantum, classical=classical)

    if classical.feasible != quantum.feasible:
        return _quarantine(
            "QUANTUM_CONSTRAINT_VIOLATION",
            "classical and quantum lanes disagree on feasibility",
        )
    if classical.objective is None or quantum.objective is None:
        return _inconclusive(quantum, classical=classical, cost=comparison.cost)

    objective_gap = abs(quantum.objective - classical.objective)
    if objective_gap > comparison.objective_tolerance:
        return _quarantine(
            "QUANTUM_BASELINE_MISMATCH",
            "quantum objective differs from the classical comparison lane",
        )
    return _matched_result(comparison, objective_gap=objective_gap)
