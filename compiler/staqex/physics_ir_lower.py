"""HIR-to-Physics IR lowering for LISS-0115.

Consumes immutable Equation/Unit DTOs from LISS-0116 without editing the
frozen Physics IR DTO module. Slice D also exposes this API from
``compile_source`` as a soft ``CompileResult.physics_ir`` artifact.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from .physics_equation import EquationNode, verify_physics_equation
from .physics_ir import (
    PhysicsDiagnostic,
    PhysicsModule,
    PhysicsNode,
    SourceOrigin,
    build_physics_ir,
    verify_physics_ir,
)
from .scientific_semantic_ir import ScientificSemanticIR, semantic_fingerprint


PHYSICS_PROJECTION_LOSSY = "PHYSICS_PROJECTION_LOSSY"
PHYSICS_PROJECTION_AUTHORITY = "scientific_semantic_ir"


@dataclass(frozen=True, slots=True)
class PhysicsProjection:
    """Compile-owned, non-finite projection view of canonical semantics."""

    module: PhysicsModule | None
    nodes: tuple[Any, ...]
    metadata: dict[str, Any]
    diagnostics: tuple[str, ...] = ()
    finite_plan: None = None
    allocation: None = None
    fingerprint: str = ""


def build_physics_projection(
    semantic_ir: ScientificSemanticIR,
    *,
    expected: ScientificSemanticIR | None = None,
) -> PhysicsProjection:
    """Project canonical semantics without finiteization or execution."""

    if not isinstance(semantic_ir, ScientificSemanticIR):
        raise TypeError("Physics projection requires ScientificSemanticIR")
    if expected is not None and semantic_ir is not expected:
        raise ValueError("Physics projection requires the compile-owned semantic IR")

    fingerprint = semantic_fingerprint(semantic_ir)
    metadata = {
        "semantic_authority": PHYSICS_PROJECTION_AUTHORITY,
        "projection_schema": "physics-projection-v1",
        "equation_dto_role": "diagnostic_only",
        "injected_equation_authorized": False,
    }
    if not semantic_ir.nodes:
        return PhysicsProjection(
            module=None,
            nodes=(),
            metadata=metadata,
            diagnostics=(PHYSICS_PROJECTION_LOSSY,),
            fingerprint=fingerprint,
        )

    projected_nodes = tuple(_project_semantic_node(node) for node in semantic_ir.nodes)
    origins = tuple(node.origin for node in projected_nodes)
    module = PhysicsModule(
        spaces=(),
        nodes=projected_nodes,
        origins=origins,
        source_origin=origins[0] if origins else None,
        metadata=metadata,
    )
    return PhysicsProjection(
        module=module,
        nodes=semantic_ir.nodes,
        metadata=metadata,
        fingerprint=fingerprint,
    )


def _project_semantic_node(node: Any) -> Any:
    """Convert one canonical node while retaining its source-backed shape."""

    provenance = node.provenance
    origin = SourceOrigin(provenance.source, provenance.line, provenance.col)
    return PhysicsNode(
        node_id=node.node_id,
        kind=node.kind,
        structure=(
            node.children,
            node.role_lane,
            node.type,
            node.dimensions,
            node.exactness,
            node.intent,
            node.meaning_kind,
            node.state_role,
        ),
        origin=origin,
    )


def lower_hir_to_physics_ir(
    hir: Any,
    *,
    unit: Any = None,
    equations: Iterable[EquationNode] = (),
) -> PhysicsModule:
    """Lower HIR and explicit Equation DTOs into one immutable module.

    The existing A–B builder remains the source of declaration/operator/binder
    and channel nodes. Equation DTOs are appended in caller-provided order;
    their coefficient and unit references are retained as-is. The pipeline
    calls this without equations; callers may still pass EquationNode values
    explicitly. No parser, evaluator, or numerical method is involved.
    """

    equation_nodes = _equation_nodes(equations)
    base = build_physics_ir(hir, unit=unit)
    equation_origins = tuple(
        equation.origin for equation in equation_nodes if equation.origin is not None
    )
    return PhysicsModule(
        spaces=base.spaces,
        nodes=base.nodes + equation_nodes,
        origins=base.origins + equation_origins,
        source_origin=base.source_origin,
        metadata=_authority_metadata(base),
    )


def lower_physics_ir(
    hir: Any,
    *,
    unit: Any = None,
    equations: Iterable[EquationNode] = (),
) -> PhysicsModule:
    """Compatibility-oriented short name for the explicit lowering API."""

    return lower_hir_to_physics_ir(hir, unit=unit, equations=equations)


def verify_lowered_physics_ir(module: PhysicsModule) -> list[PhysicsDiagnostic]:
    """Verify base Physics IR and nested Equation/Unit provenance contracts."""

    diagnostics = list(verify_physics_ir(module))
    for node in module.nodes:
        if isinstance(node, EquationNode):
            diagnostics.extend(verify_physics_equation(node))
    return diagnostics


def _equation_nodes(
    equations: Iterable[EquationNode],
) -> tuple[EquationNode, ...]:
    normalized = tuple(equations)
    for equation in normalized:
        if not isinstance(equation, EquationNode):
            raise TypeError(
                "LISS-0115 lowering accepts EquationNode values only; "
                f"received {type(equation).__name__}"
            )
    return normalized


def _authority_metadata(base: PhysicsModule) -> dict[str, Any]:
    """Mark the source-derived semantic IR as the only execution authority."""

    metadata = dict(base.metadata)
    metadata.update(
        {
            "semantic_authority": "scientific_semantic_ir",
            "equation_dto_role": "diagnostic_only",
            "injected_equation_authorized": False,
        }
    )
    return metadata
