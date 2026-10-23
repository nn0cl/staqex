"""Source-derived canonical IR construction and read-only views."""
from __future__ import annotations
from typing import Any
from .model import ScientificSemanticIR, SemanticInspectionResult, SemanticRejection

def build_scientific_semantic_ir(
    unit: Any, *args: Any, **kwargs: Any
) -> ScientificSemanticIR:
    from . import legacy as _legacy

    return _legacy.build_scientific_semantic_ir(unit, *args, **kwargs)

def build_inspection(core: ScientificSemanticIR) -> SemanticInspectionResult:
    return SemanticInspectionResult(
        source_node_ids=tuple(node.node_id for node in core.nodes),
        structural_tree=core.nodes,
        role_lanes=tuple(dict.fromkeys(node.role_lane for node in core.nodes)),
        type_dimensions=tuple((node.type, node.dimensions) for node in core.nodes),
        exactness="exact" if all(node.exactness == "exact" for node in core.nodes) else "unresolved",
        intent="source-derived",
    )

def build_rejection(core: ScientificSemanticIR, diagnostics: list[dict[str, Any]]) -> SemanticRejection | None:
    if not diagnostics:
        return None
    first = diagnostics[0]
    return SemanticRejection(
        code=str(first.get("code", "SSC_UNRESOLVED_MEANING")),
        source_node_ids=tuple(node.node_id for node in core.nodes),
        spans=tuple((node.provenance[1], node.provenance[2]) for node in core.nodes),
        message_key="semantic_rejection",
    )
