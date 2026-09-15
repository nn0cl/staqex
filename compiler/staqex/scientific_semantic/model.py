"""Immutable Scientific Semantic IR data model."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, NamedTuple

@dataclass(frozen=True, slots=True)
class CanonicalQpuOperation:
    """Source-derived operation intent consumed by the QPU projection."""

    kind: str
    provenance: tuple[tuple[str, Any], ...]
    source_node_id: str
    opcode: str | None = None
    qubits: tuple[int, ...] = ()
    parameter: str | float | None = None
    size: int | None = None
    control: int | None = None
    control_width: int | None = None
    target_offset: int = 0
    inverse: bool = False

    def provenance_map(self) -> dict[str, Any]:
        return dict(self.provenance)


@dataclass(frozen=True, slots=True)
class CanonicalQpuProjection:
    logical_qubits: int
    operations: tuple[CanonicalQpuOperation, ...]
    projection_error: str | None = None


class SemanticProvenance(NamedTuple):
    source: str
    line: int
    col: int
    source_node_id: str


@dataclass(frozen=True, slots=True)
class SemanticNode:
    node_id: str
    kind: str
    children: tuple[str, ...]
    role_lane: str
    type: str
    dimensions: str
    exactness: str
    intent: str
    provenance: SemanticProvenance
    meaning_kind: str = "expression"
    state_role: str = "unspecified"
    child_source_node_ids: tuple[str, ...] = ()
    control_source_node_id: str | None = None
    branch_rules: tuple[tuple[tuple[str, Any], ...], ...] = ()
    phase_metadata: tuple[tuple[str, Any], ...] = ()
    branch_relationship: str | None = None
    product_kind: str | None = None


@dataclass(frozen=True, slots=True)
class SemanticRelation:
    kind: str
    node_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RuntimePlanNode:
    """Internal execution-plan node projected from one semantic node."""

    source_node_id: str
    kind: str
    authority: str
    provenance: SemanticProvenance


@dataclass(frozen=True, slots=True)
class RuntimeTransformationNode:
    """Internal pure-transformation edge projected from canonical nodes."""

    input_source_node_ids: tuple[str, ...]
    output_source_node_id: str
    authority: str
    provenance: SemanticProvenance


@dataclass(frozen=True, slots=True)
class RuntimeControlNode:
    """Internal single-level control/mixture node from canonical meaning."""

    source_node_id: str
    control_source_node_id: str
    branch_rules: tuple[tuple[tuple[str, Any], ...], ...]
    authority: str
    provenance: SemanticProvenance


@dataclass(frozen=True, slots=True)
class RuntimeEvolutionNode:
    """Internal local-evolution node projected from canonical meaning."""

    source_node_id: str
    input_source_node_ids: tuple[str, ...]
    output_source_node_id: str
    hamiltonian_source_node_id: str
    duration_source_node_id: str
    authority: str
    provenance: SemanticProvenance
    realization_status: str


@dataclass(frozen=True, slots=True)
class RuntimeBinderNode:
    """Internal operator-binder node projected from canonical meaning."""

    source_node_id: str
    binder_kind: str
    domain_source_node_id: str
    body_source_node_id: str
    output_source_node_id: str
    authority: str
    provenance: SemanticProvenance
    realization_status: str


@dataclass(frozen=True, slots=True)
class RuntimeCallableNode:
    """Internal local callable/object invocation projected from meaning."""

    declaration_source_node_ids: tuple[str, ...]
    invocation_source_node_ids: tuple[str, ...]
    receiver_source_node_id: str
    output_source_node_id: str
    authority: str
    provenance: SemanticProvenance
    execution_status: str


@dataclass(frozen=True, slots=True)
class RuntimeDynamicLaneNode:
    """Internal dynamic-region node projected from canonical meaning."""

    region_source_node_id: str
    controller_source_node_id: str
    control_source_node_ids: tuple[str, ...]
    wire_source_node_ids: tuple[str, ...]
    authority: str
    provenance: SemanticProvenance
    execution_status: str


@dataclass(frozen=True, slots=True)
class RuntimeExecutionPlan:
    """Non-public runtime plan; never a replacement semantic authority."""

    semantic_identity: "ScientificSemanticIR"
    authority: str
    source_id: str
    nodes: tuple[RuntimePlanNode, ...]
    family: str = "state_measurement"
    transformations: tuple[RuntimeTransformationNode, ...] = ()
    controls: tuple[RuntimeControlNode, ...] = ()
    evolutions: tuple[RuntimeEvolutionNode, ...] = ()
    binders: tuple[RuntimeBinderNode, ...] = ()
    callables: tuple[RuntimeCallableNode, ...] = ()
    dynamic_lanes: tuple[RuntimeDynamicLaneNode, ...] = ()


@dataclass(frozen=True, slots=True)
class FiniteRealizationRecord:
    source_node_id: str
    source_name: str | None
    realized_name: str | None
    method: str | None
    order: int | None
    steps: int | None
    error_budget: float | None
    provenance: tuple[tuple[str, Any], ...]


@dataclass(frozen=True, slots=True)
class ScientificSemanticIR:
    schema: str
    authority: str
    nodes: tuple[SemanticNode, ...]
    relations: tuple[SemanticRelation, ...]
    source_id: str = "<memory>"
    has_explicit_realize: bool = False
    qpu_projection: CanonicalQpuProjection | None = None
    lowering_policy: dict[str, Any] | None = None
    explicit_evolution: dict[str, Any] | None = None
    binder_lowering: dict[str, Any] | None = None
    binder_source_node_ids: tuple[str, ...] = ()
    binder_provenance: tuple[tuple[tuple[str, Any], ...], ...] = ()
    symbolic_operator_provenance: tuple[tuple[str, str, tuple[tuple[str, Any], ...]], ...] = ()
    projection_errors: tuple[str, ...] = ()
    source_unit_identity: int | None = None
    realize_source_node_id: str | None = None
    finite_realization_record: FiniteRealizationRecord | None = None
    ideal_meaning: "IdealMeaning | None" = None
    observation_contracts: dict[str, dict[str, Any]] = field(default_factory=dict)
    measurement_envelopes: dict[str, dict[str, Any]] = field(default_factory=dict)
    observation_mappings: dict[str, dict[str, Any]] = field(default_factory=dict)
    observation_algebra: dict[str, dict[str, Any]] = field(default_factory=dict)
    povm_observation_requests: dict[str, dict[str, Any]] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class IdealMeaning:
    """Stable source-owned identity for ideal meaning before target projection."""

    source_fingerprint: str


@dataclass(frozen=True, slots=True)
class SemanticInspectionResult:
    source_node_ids: tuple[str, ...]
    structural_tree: tuple[SemanticNode, ...]
    role_lanes: tuple[str, ...]
    type_dimensions: tuple[tuple[str, str], ...]
    exactness: str
    intent: str
    allocation_record: None = None
    collapse_record: None = None

    @property
    def schema(self) -> str:
        return "ssc-semantic-v1"

@dataclass(frozen=True, slots=True)
class SemanticRejection:
    code: str
    source_node_ids: tuple[str, ...]
    spans: tuple[tuple[int, int], ...]
    message_key: str
    artifacts: None = None

@dataclass(frozen=True, slots=True)
class RealizationProvenance:
    realize_source_node_id: str


