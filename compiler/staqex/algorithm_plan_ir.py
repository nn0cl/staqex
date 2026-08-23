"""Provider-neutral Algorithm Plan IR for LISS-0083.

This module records realization decisions and obligations. It does not emit
gates, choose providers, run numerical methods, or expand symbolic resources.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


Diagnostic = dict[str, Any]


@dataclass(frozen=True)
class PlanOrigin:
    source_id: str
    physics_id: str
    upstream_ids: tuple[str, ...]
    transform_id: str


@dataclass(frozen=True)
class ApproximationObligation:
    obligation_id: str
    status: str
    bound: str | None
    estimate: str | None
    disposition: str


@dataclass(frozen=True)
class RealizationDecision:
    decision_id: str
    kind: str
    selected: str
    alternatives: tuple[str, ...]
    assumptions: tuple[str, ...]
    rejection_reasons: tuple[str, ...]
    policy_provenance: str


@dataclass(frozen=True)
class ResourceExpr:
    resource_id: str
    logical_dimensions: tuple[str, ...]
    ancillas: str
    depth: str
    operations: str
    measurements: str
    classical_latency: str
    simulator_memory: str
    target_materialization: str
    multiplicity: str


@dataclass(frozen=True)
class PlanNode:
    node_id: str
    semantic_id: str
    origin: PlanOrigin
    exactness: str
    obligation_id: str | None
    decision_ids: tuple[str, ...]
    resource_id: str
    operation_kind: str


@dataclass(frozen=True)
class ConsumerProjection:
    consumer: str
    plan_id: str
    requested_fields: tuple[str, ...]


@dataclass(frozen=True)
class AlgorithmPlanModule:
    schema_version: int
    plan_id: str
    nodes: tuple[PlanNode, ...]
    obligations: tuple[ApproximationObligation, ...]
    decisions: tuple[RealizationDecision, ...]
    resources: tuple[ResourceExpr, ...]
    repetitions: tuple[str, ...]
    witnesses: tuple[str, ...]
    # Compatibility view for existing source/provenance callers. The module
    # remains the single executable plan authority.
    provenance: Any | None = None


def _diagnostic(code: str, message: str, **details: Any) -> Diagnostic:
    return {"code": code, "message": message, **details}


def _origin_complete(origin: PlanOrigin) -> bool:
    return bool(
        origin.source_id
        and origin.physics_id
        and origin.upstream_ids
        and origin.transform_id
    )


def _has_approximation_evidence(obligation: ApproximationObligation | None) -> bool:
    return bool(obligation and (obligation.bound or obligation.estimate))


def _has_realization_evidence(decision: RealizationDecision) -> bool:
    return bool(
        decision.selected
        and decision.alternatives
        and decision.assumptions
        and all(decision.rejection_reasons)
        and decision.policy_provenance
    )


def _contains_forbidden_policy(decision: RealizationDecision) -> bool:
    return (
        "runtime" in decision.selected
        or any("provider." in item for item in decision.alternatives)
        or any("runtime" in item for item in decision.assumptions)
    )


def _verify_obligations(
    module: AlgorithmPlanModule,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    obligations = {item.obligation_id: item for item in module.obligations}
    for node in module.nodes:
        if node.exactness != "approximate":
            continue
        obligation = obligations.get(node.obligation_id)
        if not _has_approximation_evidence(obligation):
            diagnostics.append(
                _diagnostic(
                    "ALGORITHM_PLAN_APPROXIMATION_INVALID",
                    "approximate plan node requires a bound or estimate",
                    node_id=node.node_id,
                )
            )
        if obligation is None or not obligation.disposition:
            diagnostics.append(
                _diagnostic(
                    "ALGORITHM_PLAN_APPROXIMATION_INVALID",
                    "approximate plan node requires an explicit disposition",
                    node_id=node.node_id,
                )
            )
        if obligation is None or obligation.status == "unresolved":
            diagnostics.append(
                _diagnostic(
                    "ALGORITHM_PLAN_OBLIGATION_UNCLOSED",
                    "unresolved approximation obligation cannot be closed",
                    node_id=node.node_id,
                )
            )
    return diagnostics


def _verify_decisions(module: AlgorithmPlanModule) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    decisions = {item.decision_id: item for item in module.decisions}
    for node in module.nodes:
        for decision_id in node.decision_ids:
            decision = decisions.get(decision_id)
            if decision is None:
                diagnostics.append(
                    _diagnostic(
                        "ALGORITHM_PLAN_REALIZATION_INVALID",
                        "plan node references an unknown realization decision",
                        node_id=node.node_id,
                    )
                )
                continue
            if not _has_realization_evidence(decision):
                diagnostics.append(
                    _diagnostic(
                        "ALGORITHM_PLAN_REALIZATION_INVALID",
                        "realization decision lacks review evidence",
                        decision_id=decision.decision_id,
                    )
                )
            if _contains_forbidden_policy(decision):
                diagnostics.append(
                    _diagnostic(
                        "ALGORITHM_PLAN_POLICY_INVALID",
                        "runtime-adaptive and provider-specific policy is forbidden",
                        decision_id=decision.decision_id,
                    )
                )
    return diagnostics


def verify_algorithm_plan(module: AlgorithmPlanModule) -> list[Diagnostic]:
    """Return deterministic diagnostics for the provider-neutral plan contract."""

    diagnostics: list[Diagnostic] = []
    for node in module.nodes:
        if not _origin_complete(node.origin):
            diagnostics.append(
                _diagnostic(
                    "ALGORITHM_PLAN_PROVENANCE_INCOMPLETE",
                    "plan node provenance is incomplete",
                    node_id=node.node_id,
                )
            )
    diagnostics.extend(_verify_obligations(module))
    diagnostics.extend(_verify_decisions(module))
    diagnostics.sort(key=lambda item: item["code"])
    return diagnostics


def project_algorithm_plan(
    module: AlgorithmPlanModule,
    projection: ConsumerProjection,
) -> ConsumerProjection:
    """Validate the requested consumer-neutral view without mutating ``module``."""

    if projection.plan_id != module.plan_id:
        raise ValueError("projection plan_id does not match the source plan")
    if projection.consumer not in module.witnesses:
        raise ValueError("consumer is not a declared plan witness")
    return projection
