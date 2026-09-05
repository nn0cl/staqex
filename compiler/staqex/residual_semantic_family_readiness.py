"""Provider-neutral readiness classification for residual meaning families.

The classifier is deliberately a read-only boundary.  It consumes the
source-derived Scientific Semantic IR, records an honest disposition, and
never creates an execution artifact or provider payload.
"""

from __future__ import annotations

from dataclasses import dataclass

from .measurement_family_readiness import classify_for_qpu as classify_measurement
from .pipeline import compile_source


@dataclass(frozen=True, slots=True)
class ResidualSemanticFamilyDecision:
    """Complete, observable disposition for one residual source family."""

    row_id: str
    family: str
    semantic_role: str
    finite_boundary: str
    status: str
    code: str | None
    reason: str
    source_id: str
    artifact: object | None
    qasm: str | None
    provider_mapping: str | None


@dataclass(frozen=True, slots=True)
class _ResidualContract:
    family: str
    semantic_role: str
    finite_boundary: str
    status: str
    code: str | None
    reason: str


_CONTRACTS = {
    "ideal_limit": _ResidualContract(
        family="ideal-limit",
        semantic_role="ideal_or_symbolic",
        finite_boundary="explicit_realize",
        status="deferred",
        code=None,
        reason="explicit_realize_required",
    ),
    "interference": _ResidualContract(
        family="interference",
        semantic_role="interference",
        finite_boundary="canonical_projection_only",
        status="rejected",
        code="E_QPU_CANONICAL_PROJECTION_UNAVAILABLE",
        reason="interference_projection_not_authorized",
    ),
    "observation": _ResidualContract(
        family="observation",
        semantic_role="inspection_or_observation",
        finite_boundary="terminal_measurement_or_explicit_observation_contract",
        status="deferred",
        code=None,
        reason="observation_contract_required",
    ),
}


def _decision_for_contract(
    row_id: str, source_id: str
) -> ResidualSemanticFamilyDecision:
    contract = _CONTRACTS[row_id]
    return ResidualSemanticFamilyDecision(
        row_id=row_id,
        family=contract.family,
        semantic_role=contract.semantic_role,
        finite_boundary=contract.finite_boundary,
        status=contract.status,
        code=contract.code,
        reason=contract.reason,
        source_id=source_id,
        artifact=None,
        qasm=None,
        provider_mapping=None,
    )


def _classify_measurement(source: str, *, source_id: str):
    decision = classify_measurement(source, source_id=source_id)
    return ResidualSemanticFamilyDecision(
        row_id="measurement",
        family=decision.family,
        semantic_role=decision.semantic_role,
        finite_boundary="terminal_measurement_or_dynamic_target_capability",
        status=decision.status,
        code=decision.diagnostics[0] if decision.diagnostics else None,
        reason=(
            "dynamic_measurement_unsupported"
            if decision.lane == "dynamic_measurement"
            else "terminal_measurement_contract"
        ),
        source_id=decision.source_id,
        artifact=decision.artifact,
        qasm=decision.qasm,
        provider_mapping=None,
    )


def classify_for_qpu(
    source: str, *, source_id: str
) -> ResidualSemanticFamilyDecision:
    """Classify residual meaning without inferring a finite realization."""

    compiled = compile_source(source)
    semantic_ir = compiled.scientific_semantic_ir
    if semantic_ir is None:
        raise ValueError("unsupported residual semantic family")

    nodes = tuple(semantic_ir.nodes)
    if any(node.meaning_kind == "ideal_limit" for node in nodes):
        return _decision_for_contract("ideal_limit", source_id)

    if any(node.meaning_kind == "interference" for node in nodes):
        return _decision_for_contract("interference", source_id)

    if any(node.kind == "Inspect" for node in nodes):
        return _decision_for_contract("observation", source_id)

    if any(node.kind == "Measure" for node in nodes):
        return _classify_measurement(source, source_id=source_id)

    raise ValueError("unsupported residual semantic family")
