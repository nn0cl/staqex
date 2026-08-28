"""Provider-neutral readiness boundary for continuous/open-system meaning."""

from __future__ import annotations

from dataclasses import dataclass

from .pipeline import compile_source


@dataclass(frozen=True, slots=True)
class ContinuousOpenSystemDecision:
    """Deferred QPU decision with simulator evidence kept non-physical."""

    family: str
    semantic_role: str
    source_id: str
    meaning_authority: str
    status: str
    reason: str
    discretization_inferred: bool
    numerical_method: str | None
    error_tolerance: str | None
    artifact: object | None
    qasm: str | None
    allocation: object | None
    provider_mapping: str | None
    evidence_kind: str
    physical_execution_claimed: bool


def _has_open_system_meaning(compiled) -> bool:
    """Use compiler-derived semantic evidence, never source-text matching."""

    semantic_ir = compiled.scientific_semantic_ir
    if semantic_ir is None or not compiled.mixed_state_contracts:
        return False

    has_terminal_measure = any(
        node.kind == "Measure" and node.role_lane == "terminal_classical"
        for node in semantic_ir.nodes
    )
    has_density_or_channel = any(
        contract.kind in {"DensityState", "Channel"}
        or contract.operation == "lindblad"
        for contract in compiled.mixed_state_contracts.values()
    )
    return has_terminal_measure and has_density_or_channel


def _deferred_decision(source_id: str) -> ContinuousOpenSystemDecision:
    """Build the stable, non-physical QPU deferral decision."""

    return ContinuousOpenSystemDecision(
        family="continuous/open-system",
        semantic_role="density/channel/evolution",
        source_id=source_id,
        meaning_authority="scientific_semantic_ir",
        status="deferred",
        reason="discretization_required",
        discretization_inferred=False,
        numerical_method=None,
        error_tolerance=None,
        artifact=None,
        qasm=None,
        allocation=None,
        provider_mapping=None,
        evidence_kind="cpu_or_simulator",
        physical_execution_claimed=False,
    )


def classify_for_qpu(source: str, *, source_id: str) -> ContinuousOpenSystemDecision:
    """Classify an open-system source and defer unauthorized QPU realization."""

    compiled = compile_source(source)
    if not _has_open_system_meaning(compiled):
        raise ValueError("continuous realization deferred")

    return _deferred_decision(source_id)
