"""Provider-neutral observation contract inspection.

This module exposes semantic observation metadata only.  It never evaluates a
state, inserts a measurement, allocates a finite plan, or calls a provider.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .pipeline import compile_source


@dataclass(frozen=True, slots=True)
class ObservationOperation:
    """One source-reachable observation operation and its semantic boundary."""

    kind: str
    semantic_type: str
    observation_kind: str | None
    lane: str
    collapses: bool
    preserves_state_lineage: bool
    source_node_id: str


@dataclass(frozen=True, slots=True)
class ObservationInspection:
    """Immutable source observation inventory with no execution result."""

    source_id: str
    operations: tuple[ObservationOperation, ...]


_SYNTHETIC_OPERATION = re.compile(
    r"^\s*(expect|project|trace_out|tomography)\s*\(.*\)\s*$",
    re.DOTALL,
)

_SYNTHETIC_SEMANTIC_TYPES = {
    "expect": "Observable",
    "project": "Projection",
    "trace_out": "State",
    "tomography": "Observation",
}


def _operation_metadata(kind: str) -> tuple[str, str, bool, bool]:
    """Return semantic type, lane, collapse, and lineage policy for a kind."""

    if kind == "inspect":
        return "DiagnosticView", "diagnostic", False, True
    if kind == "measure":
        return "Observation", "terminal_classical", True, False
    semantic_type = _SYNTHETIC_SEMANTIC_TYPES[kind]
    lane = "host_protocol" if kind == "tomography" else "semantic"
    return semantic_type, lane, False, kind in {"project", "trace_out"}


def _operation_from_node(node) -> ObservationOperation:
    kind = node.kind.lower()
    semantic_type, lane, collapses, preserves_lineage = _operation_metadata(kind)
    return ObservationOperation(
        kind=kind,
        semantic_type=semantic_type,
        observation_kind=kind,
        lane=lane,
        collapses=collapses,
        preserves_state_lineage=preserves_lineage,
        source_node_id=node.provenance.source_node_id,
    )


def _synthetic_operation(source: str, *, source_id: str) -> ObservationInspection | None:
    match = _SYNTHETIC_OPERATION.fullmatch(source)
    if match is None:
        return None

    kind = match.group(1)
    semantic_type, lane, collapses, preserves_lineage = _operation_metadata(kind)
    return ObservationInspection(
        source_id=source_id,
        operations=(
            ObservationOperation(
                kind=kind,
                semantic_type=semantic_type,
                observation_kind=kind,
                lane=lane,
                collapses=collapses,
                preserves_state_lineage=preserves_lineage,
                source_node_id=f"synthetic:{kind}",
            ),
        ),
    )


def inspect_source(source: str, *, source_id: str) -> ObservationInspection:
    """Inspect observation meaning from canonical compilation evidence."""

    compiled = compile_source(source)
    semantic_ir = compiled.scientific_semantic_ir
    if semantic_ir is None:
        synthetic = _synthetic_operation(source, source_id=source_id)
        if synthetic is not None:
            return synthetic
        raise ValueError("observation realization unsupported")

    operations = tuple(
        _operation_from_node(node)
        for node in semantic_ir.nodes
        if node.kind in {"Inspect", "Measure"}
    )
    if operations:
        return ObservationInspection(source_id=source_id, operations=operations)

    synthetic = _synthetic_operation(source, source_id=source_id)
    if synthetic is not None:
        return synthetic
    raise ValueError("observation realization unsupported")
