"""Provider-neutral observation contract inspection.

This module exposes semantic observation metadata only.  It never evaluates a
state, inserts a measurement, allocates a finite plan, or calls a provider.
"""

from __future__ import annotations

from dataclasses import dataclass

from .ast_nodes import Call, StateBind, Var
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


_CALL_SEMANTIC_TYPES = {
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
    semantic_type = _CALL_SEMANTIC_TYPES[kind]
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


def _call_operations(compiled) -> tuple[ObservationOperation, ...]:
    main = getattr(compiled.unit, "main", None)
    statements = getattr(getattr(main, "body", None), "stmts", ())
    operations = []
    for statement in statements:
        expression = getattr(statement, "expr", None)
        if not isinstance(statement, StateBind) or not isinstance(expression, Call):
            continue
        if not isinstance(expression.callee, Var):
            continue
        kind = expression.callee.name.lower()
        if kind not in _CALL_SEMANTIC_TYPES:
            continue
        node = next(
            (
                node
                for node in compiled.scientific_semantic_ir.nodes
                if node.kind == "Call"
                and node.provenance.line == expression.span.line
                and node.provenance.col == expression.span.col
            ),
            None,
        )
        if node is None:
            continue
        semantic_type, lane, collapses, preserves_lineage = _operation_metadata(kind)
        operations.append(
            ObservationOperation(
                kind=kind,
                semantic_type=semantic_type,
                observation_kind=kind,
                lane=lane,
                collapses=collapses,
                preserves_state_lineage=preserves_lineage,
                source_node_id=node.provenance.source_node_id,
            )
        )
    return tuple(operations)


def inspect_source(source: str, *, source_id: str) -> ObservationInspection:
    """Inspect observation meaning from canonical compilation evidence."""

    compiled = compile_source(source)
    if not compiled.ok:
        raise ValueError("observation realization unsupported")
    semantic_ir = compiled.scientific_semantic_ir
    if semantic_ir is None:
        raise ValueError("observation realization unsupported")

    ir_operations = tuple(
        _operation_from_node(node)
        for node in semantic_ir.nodes
        if node.kind in {"Inspect", "Measure"}
    )
    operations = ir_operations + _call_operations(compiled)
    positions = {
        node.provenance.source_node_id: node.provenance.line
        for node in semantic_ir.nodes
    }
    operations = tuple(
        sorted(operations, key=lambda operation: positions[operation.source_node_id])
    )
    if operations:
        return ObservationInspection(source_id=source_id, operations=operations)
    raise ValueError("observation realization unsupported")
