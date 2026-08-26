"""Dynamic QPU controller and feed-forward contracts (P0 Fake path).

Lane/escape verification, finite match + one-merge correlation, capability
obligations, and Fake execution under supplied outcomes. Does not import
Semantic IR builders, engine packages, credentials, or network clients.
Does not claim physical execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True, slots=True)
class ControllerValue:
    name: str
    value: str
    phase: str


@dataclass(frozen=True, slots=True)
class OutcomeToken:
    token_id: str
    joint_correlation_id: str
    outcome_domain: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class MatchPlan:
    token_id: str
    arms: tuple[tuple[str, str], ...]


@dataclass(frozen=True, slots=True)
class MergeObligation:
    joint_correlation_id: str
    required_merges: int
    recorded_merges: int


@dataclass(frozen=True, slots=True)
class DynamicCapabilityDemand:
    needs_reset: bool
    needs_reuse: bool
    needs_latency: bool


@dataclass(frozen=True, slots=True)
class DynamicDiagnostic:
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class DynamicExecRequest:
    lane: str
    profile_id: str
    tokens: tuple[OutcomeToken, ...]
    controllers: tuple[ControllerValue, ...]
    match_plan: MatchPlan
    merge_obligation: MergeObligation
    capability_demand: DynamicCapabilityDemand
    supplied_outcomes: Mapping[str, str]
    escapes_to_theory: bool
    controls_shape: bool
    selects_deployment: bool


@dataclass(frozen=True, slots=True)
class DynamicExecResult:
    status: str
    diagnostics: tuple[DynamicDiagnostic, ...]
    selected_arm: str | None
    consumed_tokens: tuple[str, ...]
    controller_bindings: Mapping[str, str]
    physical_execution_claimed: bool
    selected_alternative: str | None


# P0 Fake profiles: feedback-only. Latency remains reject-on-demand.
# LISS-0388 (ADR 0200 Decision 3) / LISS-0390 (ADR 0199 Amendment):
# "feedback-only" no longer means "no reuse, no reset" -- these are
# simulator-class profiles with no live hardware and no physical
# qubit-recycling constraint, so reuse and reset are both honestly
# supported once real Kernel execution (LISS-0387) exists.
_FEEDBACK_ONLY_PROFILES = frozenset({"SIM0_EXACT", "CH1_DIGITAL_RESEARCH"})


def _diag(code: str, message: str) -> DynamicDiagnostic:
    return DynamicDiagnostic(code=code, message=message)


def _lane_and_escape_diagnostics(
    request: DynamicExecRequest,
) -> list[DynamicDiagnostic]:
    diagnostics: list[DynamicDiagnostic] = []
    if request.lane != "dynamic":
        diagnostics.append(
            _diag(
                "DYN_STATIC_LANE_FORBIDDEN",
                "controller tokens are forbidden outside the dynamic lane",
            )
        )
    if request.escapes_to_theory:
        diagnostics.append(
            _diag(
                "DYN_THEORY_ESCAPE",
                "controller values must not escape into Theory",
            )
        )
    if request.controls_shape:
        diagnostics.append(
            _diag(
                "DYN_SHAPE_CONTROL",
                "controller values must not determine Hilbert shape",
            )
        )
    if request.selects_deployment:
        diagnostics.append(
            _diag(
                "DYN_DEPLOYMENT_SELECTION",
                "controller values must not select deployment backends",
            )
        )
    return diagnostics


def _merge_diagnostics(request: DynamicExecRequest) -> list[DynamicDiagnostic]:
    diagnostics: list[DynamicDiagnostic] = []
    token_joints = {token.joint_correlation_id for token in request.tokens}
    if request.merge_obligation.joint_correlation_id not in token_joints:
        diagnostics.append(
            _diag(
                "DYN_UNPAIRED_TOKEN",
                "merge obligation is not paired to a token joint correlation",
            )
        )
    if request.merge_obligation.recorded_merges > request.merge_obligation.required_merges:
        diagnostics.append(
            _diag(
                "DYN_DOUBLE_MERGE",
                "correlated post-measure joint may be merged at most once",
            )
        )
    if request.merge_obligation.recorded_merges < request.merge_obligation.required_merges:
        diagnostics.append(
            _diag(
                "DYN_MERGE_MISSING",
                "required merge was not recorded for the correlated joint",
            )
        )
    return diagnostics


def _capability_diagnostics(request: DynamicExecRequest) -> list[DynamicDiagnostic]:
    diagnostics: list[DynamicDiagnostic] = []
    if request.profile_id not in _FEEDBACK_ONLY_PROFILES:
        diagnostics.append(
            _diag(
                "DYN_PROFILE_UNKNOWN",
                f"unsupported dynamic profile {request.profile_id!r}",
            )
        )
        return diagnostics
    demand = request.capability_demand
    # LISS-0388 (ADR 0200 Decision 3) / LISS-0390 (ADR 0199 Amendment):
    # neither reuse nor reset is rejected on simulator-class profiles
    # (every profile in _FEEDBACK_ONLY_PROFILES today) -- a real local
    # simulator has no physical constraint against continuing to evolve a
    # measured wire or against trace-out-then-reprepare either.
    if demand.needs_latency:
        diagnostics.append(
            _diag(
                "DYN_CAPABILITY_LATENCY",
                "latency guarantees are unsupported on the P0 Fake profiles",
            )
        )
    return diagnostics


def verify_dynamic_request(
    request: DynamicExecRequest,
) -> list[DynamicDiagnostic]:
    diagnostics = _lane_and_escape_diagnostics(request)
    diagnostics.extend(_merge_diagnostics(request))
    diagnostics.extend(_capability_diagnostics(request))
    return diagnostics


def _select_arm(request: DynamicExecRequest) -> str:
    token = request.tokens[0]
    outcome = request.supplied_outcomes[token.token_id]
    for arm_outcome, arm_name in request.match_plan.arms:
        if arm_outcome == outcome:
            return arm_name
    raise KeyError(outcome)


def _reject_result(
    diagnostics: list[DynamicDiagnostic],
) -> DynamicExecResult:
    return DynamicExecResult(
        status="rejected",
        diagnostics=tuple(diagnostics),
        selected_arm=None,
        consumed_tokens=(),
        controller_bindings={},
        physical_execution_claimed=False,
        selected_alternative=None,
    )


def _accept_result(request: DynamicExecRequest) -> DynamicExecResult:
    token = request.tokens[0]
    outcome = request.supplied_outcomes[token.token_id]
    bindings = {controller.name: outcome for controller in request.controllers}
    return DynamicExecResult(
        status="accepted",
        diagnostics=(),
        selected_arm=_select_arm(request),
        consumed_tokens=(token.token_id,),
        controller_bindings=bindings,
        physical_execution_claimed=False,
        selected_alternative=None,
    )


class FakeDynamicExecutor:
    """Deterministic Fake execution under supplied outcomes only."""

    def execute(self, request: DynamicExecRequest) -> DynamicExecResult:
        diagnostics = verify_dynamic_request(request)
        if diagnostics:
            return _reject_result(diagnostics)
        return _accept_result(request)
