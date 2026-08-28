"""Provider-neutral measurement-family readiness classification."""

from __future__ import annotations

from dataclasses import dataclass

from .pipeline import compile_source
from .quantum_semantic_ir import DynamicMeasurementRegion


_DYNAMIC_DIAGNOSTICS = frozenset(
    {
        "DYNAMIC_CAPABILITY_REQUIRED_ERROR",
        "DYNAMIC_UNSUPPORTED_FEATURE_ERROR",
    }
)


@dataclass(frozen=True, slots=True)
class MeasurementFamilyDecision:
    """Readiness result that never contains a finite artifact by implication."""

    family: str
    semantic_role: str
    lane: str
    source_id: str
    status: str
    diagnostics: tuple[str, ...]
    dynamic_region_count: int
    terminal_collapse_substitution: bool
    artifact: object | None
    qasm: str | None


def _dynamic_diagnostics(compiled) -> tuple[str, ...]:
    """Retain only the existing capability diagnostics for dynamic targets."""

    return tuple(
        diagnostic["code"]
        for diagnostic in compiled.diagnostics
        if diagnostic.get("code") in _DYNAMIC_DIAGNOSTICS
    )


def _has_terminal_measurement(semantic_ir) -> bool:
    return any(
        node.kind == "Measure" and node.role_lane == "terminal_classical"
        for node in semantic_ir.nodes
    )


def _dynamic_rejection(
    *, source_id: str, region_count: int, diagnostics: tuple[str, ...]
) -> MeasurementFamilyDecision:
    return MeasurementFamilyDecision(
        family="measurement",
        semantic_role="dynamic_measurement_feedback",
        lane="dynamic_measurement",
        source_id=source_id,
        status="rejected",
        diagnostics=diagnostics,
        dynamic_region_count=region_count,
        terminal_collapse_substitution=False,
        artifact=None,
        qasm=None,
    )


def _terminal_acceptance(source_id: str) -> MeasurementFamilyDecision:
    return MeasurementFamilyDecision(
        family="measurement",
        semantic_role="terminal_measurement",
        lane="terminal_classical",
        source_id=source_id,
        status="accepted",
        diagnostics=(),
        dynamic_region_count=0,
        terminal_collapse_substitution=False,
        artifact=None,
        qasm=None,
    )


def classify_for_qpu(source: str, *, source_id: str) -> MeasurementFamilyDecision:
    """Classify terminal or dynamic measurement from canonical Semantic IR."""

    compiled = compile_source(source)
    semantic_ir = compiled.scientific_semantic_ir
    quantum_ir = compiled.quantum_semantic_ir

    if semantic_ir is None:
        raise ValueError("measurement realization deferred")

    dynamic_regions = tuple(
        region
        for region in (quantum_ir.regions if quantum_ir is not None else ())
        if isinstance(region, DynamicMeasurementRegion)
    )
    if dynamic_regions:
        return _dynamic_rejection(
            source_id=source_id,
            region_count=len(dynamic_regions),
            diagnostics=_dynamic_diagnostics(compiled),
        )

    if _has_terminal_measurement(semantic_ir):
        return _terminal_acceptance(source_id)

    raise ValueError("measurement realization deferred")
