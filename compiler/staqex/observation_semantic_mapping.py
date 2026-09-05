"""Read-only mapping from observation meaning to Scientific Semantic IR."""

from __future__ import annotations

from dataclasses import dataclass

from .ast_nodes import Call, StateBind, Var
from .pipeline import compile_source


@dataclass(frozen=True, slots=True)
class MappingProvenance:
    source_id: str
    source_node_id: str


@dataclass(frozen=True, slots=True)
class ObservationMapping:
    kind: str
    semantic_role: str
    role_lane: str
    source_node_id: str
    provenance: MappingProvenance
    exactness: str
    dimensions: str
    projection_loss: str | None
    collapses: bool


@dataclass(frozen=True, slots=True)
class ObservationSemanticMapping:
    source_id: str
    semantic_authority: str
    operations: tuple[ObservationMapping, ...]
    finite_artifact: object | None
    provider_payload: object | None
    projection_loss: str | None


@dataclass(frozen=True, slots=True)
class _ObservationPolicy:
    semantic_role: str
    role_lane: str
    collapses: bool


_POLICIES = {
    "Inspect": _ObservationPolicy("diagnostic_view", "diagnostic", False),
    "Measure": _ObservationPolicy(
        "terminal_measurement", "terminal_classical", True
    ),
    "Project": _ObservationPolicy("projection", "semantic", False),
}


def _map_node(node, *, source_id: str, semantic_kind: str | None = None) -> ObservationMapping:
    kind = semantic_kind or node.kind
    policy = _POLICIES.get(kind)
    if policy is None:
        raise ValueError(f"unsupported observation semantic node: {node.kind}")

    return ObservationMapping(
        kind=kind.lower(),
        semantic_role=policy.semantic_role,
        role_lane=policy.role_lane,
        source_node_id=node.provenance.source_node_id,
        provenance=MappingProvenance(
            source_id=source_id,
            source_node_id=node.provenance.source_node_id,
        ),
        exactness=node.exactness,
        dimensions=node.dimensions,
        projection_loss=None,
        collapses=policy.collapses,
    )


def _map_project_calls(compiled, *, source_id: str) -> tuple[ObservationMapping, ...]:
    statements = getattr(getattr(getattr(compiled.unit, "main", None), "body", None), "stmts", ())
    result = []
    for statement in statements:
        expression = getattr(statement, "expr", None)
        if not isinstance(statement, StateBind) or not isinstance(expression, Call):
            continue
        if not isinstance(expression.callee, Var) or expression.callee.name.lower() != "project":
            continue
        node = next(
            (
                candidate for candidate in compiled.scientific_semantic_ir.nodes
                if candidate.kind == "Call"
                and candidate.provenance.line == expression.span.line
                and candidate.provenance.col == expression.span.col
            ),
            None,
        )
        if node is None:
            continue
        result.append(_map_node(node, source_id=source_id, semantic_kind="Project"))
    return tuple(result)


def map_source(source: str, *, source_id: str) -> ObservationSemanticMapping:
    """Map source observation nodes without realizing or executing them."""

    compiled = compile_source(source)
    semantic_ir = compiled.scientific_semantic_ir
    if semantic_ir is None:
        raise ValueError("unsupported observation semantic mapping")

    operations = tuple(
        _map_node(node, source_id=source_id)
        for node in semantic_ir.nodes
        if node.kind in {"Inspect", "Measure"}
    )
    operations += _map_project_calls(compiled, source_id=source_id)
    positions = {node.provenance.source_node_id: node.provenance.line for node in semantic_ir.nodes}
    operations = tuple(sorted(operations, key=lambda operation: positions[operation.source_node_id]))
    if not operations:
        raise ValueError("unsupported observation semantic mapping")

    return ObservationSemanticMapping(
        source_id=source_id,
        semantic_authority="scientific_semantic_ir",
        operations=operations,
        finite_artifact=None,
        provider_payload=None,
        projection_loss=None,
    )
