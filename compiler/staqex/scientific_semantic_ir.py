"""Source-derived Scientific Semantic IR boundary for LISS-0444.

This first Green slice preserves source structure and provenance without
performing numerical evaluation or finite realization. Consumer projections
remain explicit and are not treated as alternate authorities.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
import hashlib
import json
from typing import TYPE_CHECKING, Any, NamedTuple

if TYPE_CHECKING:
    from .algorithm_plan_ir import AlgorithmPlanModule

from .ast_nodes import (
    BinOp,
    Call,
    EvolveExpr,
    ExprStmt,
    ForEachStmt,
    KetLit,
    LitFloat,
    LitInt,
    Measure,
    Inspect,
    StateBind,
    Var,
)
from .backend.qasm.trotter import (
    TrotterError,
    compile_hamiltonian,
    eval_time_expr,
    resolve_suzuki_order,
    resolve_suzuki_steps,
)
from .finite_binder import lower_finite_binder_operators, lower_finite_binders
from .backend.qasm.trotter import suzuki_gates
from .stdlib.prelude import PRELUDE_CONSTANTS

QPU_PROJECTION_MAX_QUBITS = 1024
MIXTURE_PROJECTION_REJECTION_CODE = "E_QPU_CANONICAL_PROJECTION_UNAVAILABLE"
MIXTURE_PROJECTION_REJECTION_REASON = "mixture_projection_unavailable"


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


def build_runtime_execution_plan(
    semantic_ir: ScientificSemanticIR,
) -> RuntimeExecutionPlan:
    """Project canonical semantic nodes into an internal runtime plan."""

    if not isinstance(semantic_ir, ScientificSemanticIR):
        raise ValueError("runtime plan requires ScientificSemanticIR")
    if semantic_ir.authority != "scientific_semantic_ir":
        from .runtime.evaluator import KernelDiagnosticError

        raise KernelDiagnosticError(
            "E_RUNTIME_PLAN_CANONICAL_AUTHORITY",
            "runtime plan requires canonical semantic authority",
        )
    if not semantic_ir.nodes:
        raise ValueError("runtime plan requires canonical nodes")
    nodes = tuple(
        RuntimePlanNode(
            source_node_id=node.node_id,
            kind=node.kind,
            authority=semantic_ir.authority,
            provenance=node.provenance,
        )
        for node in semantic_ir.nodes
    )
    semantic_nodes_by_id = {node.node_id: node for node in semantic_ir.nodes}
    semantic_node_ids = set(semantic_nodes_by_id)
    transformations = tuple(
        RuntimeTransformationNode(
            input_source_node_ids=tuple(
                child for child in node.children if child in semantic_node_ids
            ),
            output_source_node_id=node.node_id,
            authority=semantic_ir.authority,
            provenance=node.provenance,
        )
        for node in semantic_ir.nodes
        if node.kind == "Pipe"
    )
    controls = tuple(
        RuntimeControlNode(
            source_node_id=node.node_id,
            control_source_node_id=node.control_source_node_id or "",
            branch_rules=node.branch_rules,
            authority=semantic_ir.authority,
            provenance=node.provenance,
        )
        for node in semantic_ir.nodes
        if node.kind == "WhenExpr"
    )
    evolutions = tuple(
        RuntimeEvolutionNode(
            source_node_id=node.node_id,
            input_source_node_ids=tuple(node.children[:1]),
            output_source_node_id=node.node_id,
            hamiltonian_source_node_id=(node.children[1] if len(node.children) > 1 else node.node_id),
            duration_source_node_id=(node.children[2] if len(node.children) > 2 else node.node_id),
            authority=semantic_ir.authority,
            provenance=node.provenance,
            realization_status=(
                "target_profile_required"
                if semantic_ir.explicit_evolution is not None
                else "local_exact"
            ),
        )
        for node in semantic_ir.nodes
        if node.kind == "EvolveExpr"
    )
    binders = tuple(
        RuntimeBinderNode(
            source_node_id=node.node_id,
            binder_kind=node.kind,
            domain_source_node_id=next(
                (
                    child
                    for child in node.children
                    if semantic_nodes_by_id.get(child, None) is not None
                    and semantic_nodes_by_id[child].kind == "IndexDomain"
                ),
                node.node_id,
            ),
            body_source_node_id=next(
                (
                    child
                    for child in reversed(node.children)
                    if semantic_nodes_by_id.get(child, None) is not None
                    and semantic_nodes_by_id[child].kind
                    not in {"Span", "BinderOrigin", "IndexDomain"}
                ),
                node.node_id,
            ),
            output_source_node_id=node.node_id,
            authority=semantic_ir.authority,
            provenance=node.provenance,
            realization_status=(
                "target_profile_required"
                if semantic_ir.has_explicit_realize
                else "local_bounded_pending"
            ),
        )
        for node in semantic_ir.nodes
        if "Binder" in node.kind or node.kind in {"Sigma", "Pi"}
    )
    callables = _build_runtime_callable_nodes(semantic_ir, semantic_nodes_by_id)
    dynamic_lanes = _build_runtime_dynamic_lane_nodes(
        semantic_ir, semantic_nodes_by_id
    )
    family = (
        "dynamic_lane"
        if dynamic_lanes
        else "evolution"
        if evolutions
        else "control_mixture"
        if controls
        else "pure_transformation"
        if transformations
        else "binder"
        if binders
        else "callable"
        if callables
        else "state_measurement"
    )
    return RuntimeExecutionPlan(
        semantic_identity=semantic_ir,
        authority=semantic_ir.authority,
        source_id=semantic_ir.source_id,
        nodes=nodes,
        family=family,
        transformations=transformations,
        controls=controls,
        evolutions=evolutions,
        binders=binders,
        callables=callables,
        dynamic_lanes=dynamic_lanes,
    )


def _build_runtime_callable_nodes(
    semantic_ir: ScientificSemanticIR,
    semantic_nodes_by_id: dict[str, SemanticNode],
) -> tuple[RuntimeCallableNode, ...]:
    """Project local declarations and calls without adding execution policy."""
    declarations = tuple(
        node.node_id
        for node in semantic_ir.nodes
        if node.kind in {"FunDecl", "ClassDecl"}
    )
    if not declarations:
        return ()
    return tuple(
        RuntimeCallableNode(
            declaration_source_node_ids=declarations,
            invocation_source_node_ids=(invocation.node_id,),
            receiver_source_node_id=next(
                (
                    child
                    for child in invocation.children
                    if semantic_nodes_by_id.get(child, None) is not None
                    and semantic_nodes_by_id[child].kind == "Attr"
                ),
                invocation.node_id,
            ),
            output_source_node_id=invocation.node_id,
            authority=semantic_ir.authority,
            provenance=invocation.provenance,
            execution_status="local_bounded_pending",
        )
        for invocation in semantic_ir.nodes
        if invocation.kind == "Call"
    )


def _build_runtime_dynamic_lane_nodes(
    semantic_ir: ScientificSemanticIR,
    semantic_nodes_by_id: dict[str, SemanticNode],
) -> tuple[RuntimeDynamicLaneNode, ...]:
    """Project one-level dynamic regions without selecting a target profile."""
    regions = [node for node in semantic_ir.nodes if node.kind == "DynamicQpuStmt"]
    result: list[RuntimeDynamicLaneNode] = []
    for region in regions:
        region_nodes = [
            node
            for node in semantic_ir.nodes
            if node.node_id in set(region.children)
        ]
        controller = next(
            (
                node
                for node in region_nodes
                if node.kind == "StateBind"
                and any(
                    semantic_nodes_by_id.get(child, None) is not None
                    and semantic_nodes_by_id[child].kind == "MeasureExpr"
                    for child in node.children
                )
            ),
            region,
        )
        controls = tuple(
            node.node_id
            for node in region_nodes
            if node.kind == "MatchStmt"
        )
        wires = tuple(
            node.node_id
            for node in region_nodes
            if node.kind == "StateBind"
        )
        result.append(
            RuntimeDynamicLaneNode(
                region_source_node_id=region.node_id,
                controller_source_node_id=controller.node_id,
                control_source_node_ids=controls,
                wire_source_node_ids=wires,
                authority=semantic_ir.authority,
                provenance=region.provenance,
                execution_status="capability_profile_required",
            )
        )
    return tuple(result)


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


def _observation_input_name(expr: Any) -> str | None:
    """Return the source binding carried by a simple observation expression."""
    if isinstance(expr, Var):
        return expr.name
    if isinstance(expr, Inspect) and isinstance(expr.expr, Var):
        return expr.expr.name
    return None


@dataclass(frozen=True, slots=True)
class RealizationProvenance:
    realize_source_node_id: str


def semantic_fingerprint(core: ScientificSemanticIR) -> str:
    """Return a stable digest for the complete canonical semantic payload."""
    payload = {
        "schema": core.schema,
        "authority": core.authority,
        "has_explicit_realize": core.has_explicit_realize,
        "nodes": [
            {
                "node_id": node.node_id,
                "kind": node.kind,
                "children": node.children,
                "role_lane": node.role_lane,
                "type": node.type,
                "dimensions": node.dimensions,
                "exactness": node.exactness,
                "intent": node.intent,
                "provenance": node.provenance,
                "meaning_kind": node.meaning_kind,
                "state_role": node.state_role,
                "child_source_node_ids": node.child_source_node_ids,
                "control_source_node_id": node.control_source_node_id,
                "branch_rules": node.branch_rules,
                "phase_metadata": node.phase_metadata,
                "branch_relationship": node.branch_relationship,
            }
            for node in core.nodes
        ],
        "relations": [
            {"kind": relation.kind, "node_ids": relation.node_ids}
            for relation in core.relations
        ],
        "lowering_policy": core.lowering_policy,
        "explicit_evolution": core.explicit_evolution,
        "realize_source_node_id": core.realize_source_node_id,
        "finite_realization_record": core.finite_realization_record,
        "binder_lowering": core.binder_lowering,
        "binder_source_node_ids": core.binder_source_node_ids,
        "binder_provenance": core.binder_provenance,
        "projection_errors": core.projection_errors,
        "qpu_projection": None
        if core.qpu_projection is None
        else {
            "logical_qubits": core.qpu_projection.logical_qubits,
            "operations": [
                {
                    "kind": operation.kind,
                    "provenance": operation.provenance,
                    "source_node_id": operation.source_node_id,
                    "opcode": operation.opcode,
                    "qubits": operation.qubits,
                    "parameter": operation.parameter,
                    "size": operation.size,
                    "control": operation.control,
                    "control_width": operation.control_width,
                    "target_offset": operation.target_offset,
                    "inverse": operation.inverse,
                }
                for operation in core.qpu_projection.operations
            ],
            "projection_error": core.qpu_projection.projection_error,
        },
    }
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), default=str
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_scientific_semantic_ir(
    unit: Any, *, source_id: str = "<memory>"
) -> ScientificSemanticIR:
    """Build a structural, source-derived projection from the parsed unit."""

    nodes: list[SemanticNode] = []
    counter = 0
    source_node_ids: dict[int, str] = {}

    def is_quantum_exponential(call: Call) -> bool:
        if len(call.args) != 1:
            return False
        names: set[str] = set()

        def collect(value: Any) -> None:
            if isinstance(value, Var):
                names.add(value.name)
                return
            if isinstance(value, (tuple, list)):
                for item in value:
                    collect(item)
                return
            if hasattr(value, "__dataclass_fields__"):
                for field_name in value.__dataclass_fields__:
                    collect(getattr(value, field_name))

        collect(call.args[0])
        return "i" in names and len(names) >= 2

    def visit(value: Any, parent: str | None = None) -> None:
        nonlocal counter
        if value is None or isinstance(value, (str, int, float, bool, bytes)):
            return
        if isinstance(value, (tuple, list)):
            for item in value:
                visit(item, parent)
            return
        if not hasattr(value, "__dataclass_fields__"):
            return
        span = getattr(value, "span", None)
        counter += 1
        node_id = f"ssc:{counter}"
        source_node_ids[id(value)] = node_id
        name = type(value).__name__
        if isinstance(value, Call) and isinstance(value.callee, Var):
            if value.callee.name == "Limit":
                name = "Limit"
            elif value.callee.name == "exp" and is_quantum_exponential(value):
                name = "ExactExponential"
            elif value.callee.name == "phase":
                name = "PhaseExpr"
            elif value.callee.name == "interfer":
                name = "InterferenceExpr"
        role = _role_for(name)
        child_start = len(nodes)
        for field_name in value.__dataclass_fields__:
            visit(getattr(value, field_name), node_id)
        children = tuple(node.node_id for node in nodes[child_start:])
        control_source_node_id = None
        branch_rules: tuple[tuple[tuple[str, Any], ...], ...] = ()
        phase_metadata: tuple[tuple[str, Any], ...] = ()
        branch_relationship: str | None = None
        if name == "WhenExpr":
            control_value = value.ctrl
            if isinstance(control_value, Var) and unit.main is not None:
                for statement in unit.main.body.stmts:
                    if (
                        isinstance(statement, StateBind)
                        and statement.names
                        and statement.names[0] == control_value.name
                    ):
                        control_value = statement.expr
                        break
            control_source_node_id = source_node_ids.get(id(control_value))
            branch_rules = tuple(
                (
                    ("pattern", arm.pat),
                    ("is_else", arm.is_else),
                    ("source_node_id", source_node_ids.get(id(arm), "")),
                )
                for arm in value.arms
            )
        is_interfer = (
            isinstance(value, Call)
            and isinstance(value.callee, Var)
            and value.callee.name == "interfer"
        )
        if is_interfer:
            operand_ids = tuple(source_node_ids.get(id(arg), "") for arg in value.args)
            children = operand_ids
            phase_metadata = (("phase_role", "relative_phase"), ("exactness", "exact"))
            branch_relationship = "coherent_operand_superposition"
        nodes.append(
            SemanticNode(
                node_id=node_id,
                kind=name,
                children=children,
                role_lane="quantum" if is_interfer else role,
                type=_type_for(name),
                dimensions="unknown",
                exactness="exact"
                if name in {"Limit", "ExactExponential", "EvolveExpr"}
                else "unresolved",
                intent="interference" if is_interfer else _intent_for(name),
                provenance=SemanticProvenance(
                    "sqx",
                    getattr(span, "line", 0),
                    getattr(span, "col", 0),
                    node_id,
                ),
                meaning_kind="interference" if is_interfer else _meaning_kind(name),
                state_role="interference_state" if is_interfer else _state_role(name),
                child_source_node_ids=children,
                control_source_node_id=control_source_node_id,
                branch_rules=branch_rules,
                phase_metadata=phase_metadata,
                branch_relationship=branch_relationship,
            )
        )

    visit(unit)
    if not nodes:
        nodes.append(
            SemanticNode(
                "ssc:unit",
                "CompilationUnit",
                (),
                "mathematical",
                "Unit",
                "",
                "exact",
                "source",
                SemanticProvenance("sqx", 0, 0, "ssc:unit"),
            )
        )
    if any(node.meaning_kind == "interference" for node in nodes):
        relation_kind = "interference"
    elif any(node.kind == "WhenExpr" for node in nodes):
        relation_kind = "mixture"
    elif any("Binder" in node.kind or node.kind in {"Sigma", "Pi"} for node in nodes):
        relation_kind = "binder"
    else:
        relation_kind = "source"
    core = ScientificSemanticIR(
        schema="ssc-semantic-v1",
        authority="scientific_semantic_ir",
        source_id=source_id,
        nodes=tuple(nodes),
        relations=(SemanticRelation(relation_kind, tuple(node.node_id for node in nodes)),),
        has_explicit_realize=_has_realize_call(unit),
    )
    observation_contracts: dict[str, dict[str, Any]] = {}
    measurement_envelopes: dict[str, dict[str, Any]] = {}
    observation_mappings: dict[str, dict[str, Any]] = {}
    observation_algebra: dict[str, dict[str, Any]] = {}
    povm_observation_requests: dict[str, dict[str, Any]] = {}
    if unit.main is not None:
        povm_names = {
            statement.names[0]: statement.ty.args[0].name
            for statement in unit.main.body.stmts
            if (
                isinstance(statement, StateBind)
                and len(statement.names) == 1
                and statement.ty is not None
                and statement.ty.name == "POVM"
                and statement.ty.args
            )
        }
        state_domains = {
            statement.names[0]: statement.ty.args[0].name
            for statement in unit.main.body.stmts
            if (
                isinstance(statement, StateBind)
                and len(statement.names) == 1
                and statement.ty is not None
                and statement.ty.name in {"State", "DensityState"}
                and statement.ty.args
            )
        }
        for statement in unit.main.body.stmts:
            if isinstance(statement, StateBind) and statement.names and isinstance(statement.expr, Inspect):
                observation_contracts[statement.names[0]] = {
                    "kind": "DiagnosticView",
                    "collapse": False,
                    "sampling": False,
                    "lane": "StaticKernel",
                    "source_id": source_id,
                    "source_node_id": source_node_ids.get(id(statement), ""),
                }
                observation_mappings[statement.names[0]] = {
                    "role": "DiagnosticView",
                    "lane": "StaticKernel",
                    "source_id": source_id,
                    "provenance": {
                        "source_node_id": source_node_ids.get(id(statement), ""),
                        "line": statement.span.line,
                        "col": statement.span.col,
                    },
                    "exactness": "preserved",
                    "dimensions": "preserved",
                    "projection_loss": None,
                    "finite_artifact": False,
                }
                inner = statement.expr.expr
                composition = {
                    "outer": "inspect",
                    "inner": "inspect" if isinstance(inner, Inspect) else "state",
                    "sampling": False,
                }
                observation_algebra[statement.names[0]] = {
                    "operation_kind": "inspect",
                    "lane": "StaticKernel",
                    "sampling": False,
                    "collapse": False,
                    "lineage": {
                        "source_id": source_id,
                        "input": _observation_input_name(inner),
                    },
                    "projection_loss": None,
                    "finite_artifact": False,
                    "composition": composition,
                }
            if isinstance(statement, Measure) and isinstance(statement.expr, Var):
                measurement_envelopes[statement.expr.name] = {
                    "kind": "MeasurementEnvelope",
                    "collapse": True,
                    "sampling": True,
                    "lane": "StaticKernel",
                    "source_id": source_id,
                }
                if isinstance(statement.povm, Var) and statement.povm.name in povm_names:
                    povm_observation_requests[statement.expr.name] = {
                        "effect_set_id": statement.povm.name,
                        "effect_kind": "ComputationalBasis",
                        "state_domain": state_domains.get(statement.expr.name, "Unknown"),
                        "lane": "StaticKernel",
                        "sampling": True,
                        "collapse": True,
                        "post_state_identity": f"{statement.expr.name}:post_measurement",
                        "provenance": {
                            "source_id": source_id,
                            "source_node_id": source_node_ids.get(id(statement), ""),
                        },
                    }
            if (
                isinstance(statement, StateBind)
                and statement.names
                and isinstance(statement.expr, Call)
                and isinstance(statement.expr.callee, Var)
                and statement.expr.callee.name == "trace_out"
            ):
                observation_mappings[statement.names[0]] = {
                    "role": "ReducedState",
                    "lane": "StaticKernel",
                    "source_id": source_id,
                    "provenance": {
                        "source_node_id": source_node_ids.get(id(statement), ""),
                        "line": statement.span.line,
                        "col": statement.span.col,
                    },
                    "exactness": "preserved",
                    "dimensions": "reduced",
                    "projection_loss": "subsystem_reduction",
                    "finite_artifact": False,
                }
                observation_algebra[statement.names[0]] = {
                    "operation_kind": "trace_out",
                    "lane": "StaticKernel",
                    "sampling": False,
                    "collapse": False,
                    "lineage": {
                        "source_id": source_id,
                        "input": (
                            _observation_input_name(statement.expr.args[0])
                            if statement.expr.args
                            else None
                        ),
                    },
                    "projection_loss": "subsystem_reduction",
                    "finite_artifact": False,
                    "composition": {
                        "outer": "trace_out",
                        "inner": "state",
                        "sampling": False,
                    },
                }
    binder_lowering, binder_diagnostics = lower_finite_binders(unit)
    realize_source_node_id, finite_realization_record, realization_errors = (
        _build_finite_realization_record(unit, core)
    )
    result = ScientificSemanticIR(
        schema=core.schema,
        authority=core.authority,
        source_id=core.source_id,
        nodes=core.nodes,
        relations=core.relations,
        has_explicit_realize=core.has_explicit_realize,
        qpu_projection=_build_qpu_projection(unit, core),
        lowering_policy=_build_lowering_policy(unit, core),
        explicit_evolution=_build_explicit_evolution(unit, core),
        binder_lowering=binder_lowering or None,
        binder_source_node_ids=_binder_source_node_ids(unit, core),
        binder_provenance=_binder_provenance(unit, core),
        symbolic_operator_provenance=_symbolic_operator_provenance(unit, core),
        projection_errors=tuple(
            dict.fromkeys(
                (
                    *_projection_errors(unit, core, binder_diagnostics),
                    *realization_errors,
                )
            )
        ),
        source_unit_identity=id(unit),
        realize_source_node_id=realize_source_node_id,
        finite_realization_record=finite_realization_record,
        observation_contracts=observation_contracts,
        measurement_envelopes=measurement_envelopes,
        observation_mappings=observation_mappings,
        observation_algebra=observation_algebra,
        povm_observation_requests=povm_observation_requests,
    )
    ideal_payload = json.dumps(
        {
            "nodes": [
                (
                    node.node_id,
                    node.kind,
                    node.children,
                    node.role_lane,
                    node.type,
                    node.dimensions,
                    node.exactness,
                    node.intent,
                    node.provenance,
                    node.meaning_kind,
                    node.state_role,
                    node.child_source_node_ids,
                    node.control_source_node_id,
                    node.branch_rules,
                    node.phase_metadata,
                    node.branch_relationship,
                )
                for node in result.nodes
            ],
            "relations": result.relations,
        },
        sort_keys=True,
        default=str,
        separators=(",", ":"),
    ).encode("utf-8")
    return replace(
        result,
        ideal_meaning=IdealMeaning(hashlib.sha256(ideal_payload).hexdigest()),
    )


def _build_qpu_projection(unit: Any, core: ScientificSemanticIR) -> CanonicalQpuProjection:
    """Build the first canonical QPU operation slice from source structure."""
    register_sizes: dict[str, int] = {}
    parameter_bindings: dict[str, str] = {}
    operations: list[CanonicalQpuOperation] = []
    if unit.main is None:
        return CanonicalQpuProjection(0, ())

    for stmt in unit.main.body.stmts:
        if (
            isinstance(stmt, StateBind)
            and stmt.ty is not None
            and stmt.ty.name == "QubitRegister"
            and stmt.names
            and stmt.ty.args
            and stmt.ty.args[0].name.isdigit()
        ):
            register_sizes[stmt.names[0]] = int(stmt.ty.args[0].name)
        if (
            isinstance(stmt, StateBind)
            and stmt.ty is not None
            and stmt.ty.name == "Param"
            and stmt.names
            and isinstance(stmt.expr, Call)
            and isinstance(stmt.expr.callee, Var)
            and stmt.expr.callee.name == "parameter"
            and stmt.expr.args
            and hasattr(stmt.expr.args[0], "value")
        ):
            parameter_bindings[stmt.names[0]] = str(stmt.expr.args[0].value)

    def source_node_id(span: Any) -> str:
        matches = [
            node.node_id
            for node in core.nodes
            if node.provenance[1] == getattr(span, "line", 0)
            and node.provenance[2] == getattr(span, "col", 0)
        ]
        return matches[-1] if matches else ""

    def provenance(span: Any, source: str) -> tuple[tuple[str, Any], ...]:
        return (
            ("line", getattr(span, "line", 0)),
            ("col", getattr(span, "col", 0)),
            ("source", source),
            ("source_node_id", source_node_id(span)),
        )

    operations.extend(
        _finite_evolution_operations(
            unit,
            core,
            register_sizes=register_sizes,
        )
    )

    gate_names = {"H", "X", "Y", "Z", "S", "T", "CX", "RX", "RY", "RZ"}
    state_qubits: dict[str, int] = {}
    next_state_qubit = 0
    for stmt in unit.main.body.stmts:
        if isinstance(stmt, StateBind) and stmt.names:
            state_name = stmt.names[0]
            if isinstance(stmt.expr, KetLit):
                qubit = state_qubits.setdefault(state_name, next_state_qubit)
                next_state_qubit = max(next_state_qubit, qubit + 1)
                prep = {"+": ("H",), "1": ("X",), "-": ("X", "H")}.get(
                    stmt.expr.label
                )
                for opcode in prep or ():
                    operations.append(
                        CanonicalQpuOperation(
                            kind="gate",
                            provenance=provenance(stmt.span, f"KetLit.{opcode}"),
                            source_node_id=source_node_id(stmt.span),
                            opcode=opcode,
                            qubits=(qubit,),
                        )
                    )
            elif (
                isinstance(stmt.expr, Call)
                and isinstance(stmt.expr.callee, Var)
                and stmt.expr.callee.name == "apply"
                and len(stmt.expr.args) == 2
                and isinstance(stmt.expr.args[1], Var)
            ):
                target = stmt.expr.args[1].name
                qubit = state_qubits.get(target)
                gate_expr = stmt.expr.args[0]
                opcode: str | None = None
                parameter: str | float | None = None
                if isinstance(gate_expr, Var) and gate_expr.name.upper() in gate_names:
                    opcode = gate_expr.name.upper()
                elif isinstance(gate_expr, Call) and isinstance(gate_expr.callee, Var):
                    candidate = gate_expr.callee.name.upper()
                    if candidate in {"RX", "RY", "RZ"} and len(gate_expr.args) == 1:
                        opcode = candidate
                        arg = gate_expr.args[0]
                        try:
                            parameter = eval_time_expr(
                                arg,
                                {name: float(value) for name, value in PRELUDE_CONSTANTS.items()},
                            )
                        except (TrotterError, ValueError, TypeError):
                            if isinstance(arg, Var):
                                parameter = parameter_bindings.get(arg.name, arg.name)
                if qubit is not None and opcode is not None:
                    operations.append(
                        CanonicalQpuOperation(
                            kind="gate",
                            provenance=provenance(stmt.span, "apply"),
                            source_node_id=source_node_id(stmt.span),
                            opcode=opcode,
                            qubits=(qubit,),
                            parameter=parameter,
                        )
                    )
                    state_qubits[state_name] = qubit
            elif (
                isinstance(stmt.expr, Call)
                and isinstance(stmt.expr.callee, Var)
                and stmt.expr.callee.name == "cnot"
                and len(stmt.expr.args) == 2
                and all(isinstance(arg, Var) for arg in stmt.expr.args)
            ):
                control = state_qubits.get(stmt.expr.args[0].name)
                target = state_qubits.get(stmt.expr.args[1].name)
                if control is not None and target is not None:
                    operations.append(
                        CanonicalQpuOperation(
                            kind="gate",
                            provenance=provenance(stmt.span, "cnot"),
                            source_node_id=source_node_id(stmt.span),
                            opcode="CX",
                            qubits=(control, target),
                        )
                    )
                    state_qubits[state_name] = target
            elif (
                isinstance(stmt.expr, Call)
                and isinstance(stmt.expr.callee, Var)
                and stmt.expr.callee.name == "capply"
                and len(stmt.expr.args) == 3
                and all(isinstance(arg, Var) for arg in (stmt.expr.args[0], stmt.expr.args[2]))
            ):
                control = state_qubits.get(stmt.expr.args[0].name)
                target = state_qubits.get(stmt.expr.args[2].name)
                gate_expr = stmt.expr.args[1]
                opcode = None
                if isinstance(gate_expr, Var) and gate_expr.name.upper() in {"X", "Z"}:
                    opcode = {"X": "CX", "Z": "CZ"}[gate_expr.name.upper()]
                if control is not None and target is not None and opcode is not None:
                    operations.append(
                        CanonicalQpuOperation(
                            kind="gate",
                            provenance=provenance(stmt.span, "capply"),
                            source_node_id=source_node_id(stmt.span),
                            opcode=opcode,
                            qubits=(control, target),
                        )
                    )
                    state_qubits[state_name] = target
        if isinstance(stmt, ForEachStmt):
            count = register_sizes.get(getattr(stmt.collection, "name", ""))
            if count is None:
                continue
            for index in range(count):
                for body_stmt in stmt.body.stmts:
                    if not isinstance(body_stmt, ExprStmt) or not isinstance(body_stmt.expr, Call):
                        continue
                    call = body_stmt.expr
                    if not (isinstance(call.callee, Var) and call.callee.name == "apply"):
                        continue
                    if len(call.args) != 2:
                        continue
                    gate_expr = call.args[0]
                    opcode: str | None = None
                    parameter: str | float | None = None
                    if isinstance(gate_expr, Var) and gate_expr.name.upper() in gate_names:
                        opcode = gate_expr.name.upper()
                    elif isinstance(gate_expr, Call) and isinstance(gate_expr.callee, Var):
                        candidate = gate_expr.callee.name.upper()
                        if candidate in {"RX", "RY", "RZ"} and len(gate_expr.args) == 1:
                            opcode = candidate
                            arg = gate_expr.args[0]
                            if hasattr(arg, "value"):
                                parameter = float(arg.value)
                            elif isinstance(arg, Var):
                                parameter = parameter_bindings.get(arg.name, arg.name)
                    if opcode is not None:
                        operations.append(
                            CanonicalQpuOperation(
                                kind="gate",
                                provenance=provenance(body_stmt.span, "ForEach.apply"),
                                source_node_id=source_node_id(body_stmt.span),
                                opcode=opcode,
                                qubits=(index,),
                                parameter=parameter,
                            )
                        )
        elif isinstance(stmt, Measure):
            measured_qubit = (
                state_qubits.get(stmt.expr.name, 0)
                if isinstance(stmt.expr, Var)
                else 0
            )
            operations.append(
                CanonicalQpuOperation(
                    kind="measure",
                    provenance=provenance(stmt.span, "Measure"),
                    source_node_id=source_node_id(stmt.span),
                    qubits=(measured_qubit,),
                )
            )
        elif (
            isinstance(stmt, StateBind)
            and stmt.ty is not None
            and stmt.ty.name == "Operator"
            and isinstance(stmt.expr, Call)
            and isinstance(stmt.expr.callee, Var)
            and stmt.expr.callee.name in {"qft", "iqft"}
            and stmt.expr.args
        ):
            register = getattr(stmt.expr.args[0], "name", "")
            size = register_sizes.get(register)
            if size is not None and size <= QPU_PROJECTION_MAX_QUBITS:
                operations.append(
                    CanonicalQpuOperation(
                        kind="qft",
                        provenance=provenance(stmt.span, stmt.expr.callee.name),
                        source_node_id=source_node_id(stmt.span),
                        size=size,
                        inverse=stmt.expr.callee.name == "iqft",
                    )
                )
        elif (
            isinstance(stmt, StateBind)
            and stmt.ty is not None
            and stmt.ty.name == "Operator"
            and isinstance(stmt.expr, Call)
            and isinstance(stmt.expr.callee, Var)
            and stmt.expr.callee.name in {"cqft", "ciqft"}
            and len(stmt.expr.args) == 2
        ):
            control_name = getattr(stmt.expr.args[0], "name", "")
            target_name = getattr(stmt.expr.args[1], "name", "")
            control_size = register_sizes.get(control_name)
            size = register_sizes.get(target_name)
            if (
                control_size == 1
                and size is not None
                and control_size + size <= QPU_PROJECTION_MAX_QUBITS
            ):
                operations.append(
                    CanonicalQpuOperation(
                        kind="cqft",
                        provenance=provenance(stmt.span, stmt.expr.callee.name),
                        source_node_id=source_node_id(stmt.span),
                        size=size,
                        control=0,
                        control_width=control_size,
                        target_offset=control_size,
                        inverse=stmt.expr.callee.name == "ciqft",
                    )
                )
    logical_qubits = max(
        sum(register_sizes.values()),
        next_state_qubit,
        max(
            (
                len(stmt.expr.seeds)
                for stmt in unit.main.body.stmts
                if isinstance(stmt, StateBind)
                and isinstance(stmt.expr, EvolveExpr)
            ),
            default=0,
        ),
    )
    projection_error = None
    if any(size > QPU_PROJECTION_MAX_QUBITS for size in register_sizes.values()):
        projection_error = (
            "E_QPU_RESOURCE_UNSUPPORTED: canonical QPU projection exceeds "
            f"{QPU_PROJECTION_MAX_QUBITS} logical qubits"
        )
    elif any(node.kind == "WhenExpr" for node in core.nodes):
        projection_error = (
            f"{MIXTURE_PROJECTION_REJECTION_CODE}:"
            f"{MIXTURE_PROJECTION_REJECTION_REASON}"
        )
    return CanonicalQpuProjection(logical_qubits, tuple(operations), projection_error)


def _finite_evolution_operations(
    unit: Any,
    core: ScientificSemanticIR,
    *,
    register_sizes: dict[str, int],
) -> list[CanonicalQpuOperation]:
    """Derive finite Suzuki gates before the QPU consumer boundary.

    This is source-to-canonical projection work: the QPU consumer receives
    only the returned operations and never re-reads the AST. The accepted
    `using Suzuki(...)` surface is finite already; this helper does not infer
    a policy or create a Realize boundary.
    """
    if unit.main is None:
        return []
    op_env = {
        stmt.names[0]: stmt.expr
        for stmt in unit.main.body.stmts
        if isinstance(stmt, StateBind)
        and stmt.ty is not None
        and stmt.ty.name == "Operator"
        and len(stmt.names) == 1
    }
    lowered_binders, _ = lower_finite_binder_operators(unit)
    op_env.update(lowered_binders)
    scalars: dict[str, float] = {name: float(value) for name, value in PRELUDE_CONSTANTS.items()}
    for stmt in unit.main.body.stmts:
        if (
            isinstance(stmt, StateBind)
            and stmt.ty is not None
            and stmt.ty.name in {"Float", "Int"}
            and len(stmt.names) == 1
            and isinstance(stmt.expr, (LitFloat, LitInt))
        ):
            scalars[stmt.names[0]] = float(stmt.expr.value)
    result: list[CanonicalQpuOperation] = []
    for stmt in unit.main.body.stmts:
        if not (
            isinstance(stmt, StateBind)
            and isinstance(stmt.expr, EvolveExpr)
            and stmt.expr.hamiltonian is not None
            and stmt.expr.suzuki is not None
            and stmt.expr.duration is not None
        ):
            continue
        expr = stmt.expr
        source_id = _source_node_id_for_span(core, expr.span)
        try:
            n_qubits = max(1, len(expr.seeds), register_sizes.get("register", 0))
            terms = compile_hamiltonian(
                expr.hamiltonian,
                env=op_env,
                scalars=scalars,
                n_qubits=n_qubits,
            )
            duration = eval_time_expr(expr.duration, scalars)
            order = resolve_suzuki_order(expr.suzuki.order, scalars)
            steps = resolve_suzuki_steps(expr.suzuki, terms, duration, scalars)
            gates = suzuki_gates(
                terms,
                duration,
                tuple(range(len(expr.seeds))),
                steps=steps,
                order=order,
            )
        except (TrotterError, ValueError, TypeError):
            continue
        provenance = (
            ("line", expr.span.line),
            ("col", expr.span.col),
            ("source", "Evolve.Suzuki"),
            ("source_node_id", source_id),
        )
        opcode_map = {"h": "H", "x": "X", "y": "Y", "z": "Z", "rx": "RX", "ry": "RY", "rz": "RZ", "cx": "CX"}
        for gate in gates:
            opcode = opcode_map.get(gate.name)
            if opcode is None:
                continue
            gate_provenance = provenance + (("comment", gate.comment),)
            result.append(
                CanonicalQpuOperation(
                    kind="gate",
                    provenance=gate_provenance,
                    source_node_id=source_id,
                    opcode=opcode,
                    qubits=gate.qubits,
                    parameter=gate.angle,
                )
            )
    return result


def _build_lowering_policy(unit: Any, core: ScientificSemanticIR) -> dict[str, Any] | None:
    if unit.main is None:
        return None
    binds = [stmt for stmt in unit.main.body.stmts if isinstance(stmt, StateBind)]
    op_env: dict[str, Any] = {}
    scalars: dict[str, float] = {name: float(value) for name, value in PRELUDE_CONSTANTS.items()}
    evolves: list[EvolveExpr] = []
    for stmt in binds:
        if stmt.ty is not None and stmt.ty.name == "Operator" and len(stmt.names) == 1:
            op_env[stmt.names[0]] = stmt.expr
        elif stmt.ty is not None and stmt.ty.name in {"Float", "Int"} and len(stmt.names) == 1:
            if isinstance(stmt.expr, (LitFloat, LitInt)):
                scalars[stmt.names[0]] = float(stmt.expr.value)
        if isinstance(stmt.expr, EvolveExpr) and stmt.expr.suzuki is not None:
            evolves.append(stmt.expr)
    if not evolves:
        return None
    policy = evolves[0].suzuki
    assert policy is not None
    try:
        order = int(eval_time_expr(policy.order, scalars))
    except (TrotterError, TypeError, ValueError):
        return None
    if order not in {2, 4}:
        return None
    steps: int | None = None
    tolerance: float | None = None
    if isinstance(policy.steps, LitInt):
        steps = int(policy.steps.value)
    elif isinstance(policy.steps, Var):
        value = scalars.get(policy.steps.name)
        steps = int(value) if value is not None else None
    if isinstance(policy.tolerance, (LitInt, LitFloat)):
        tolerance = float(policy.tolerance.value)
    if steps is None and tolerance is not None:
        ev = evolves[0]
        if ev.duration is None or ev.hamiltonian is None:
            return None
        try:
            duration = eval_time_expr(ev.duration, scalars)
            terms = compile_hamiltonian(
                ev.hamiltonian,
                env=op_env,
                scalars=scalars,
                n_qubits=max(1, len(ev.seeds)),
            )
            steps = resolve_suzuki_steps(policy, terms, duration, scalars)
        except TrotterError:
            return None
    if steps is None:
        return None
    source_node_id = _source_node_id_for_span(core, evolves[0].span)
    return {
        "algorithm": "Suzuki",
        "order": order,
        "steps": steps,
        "error_mode": policy.error_mode if tolerance is not None else None,
        "tolerance_target": tolerance,
        "source_node_id": source_node_id,
        "source_span": (evolves[0].span.line, evolves[0].span.col),
        "provenance": {
            "source": "sqx",
            "line": evolves[0].span.line,
            "col": evolves[0].span.col,
            "source_node_id": source_node_id,
        },
    }


def _build_explicit_evolution(unit: Any, core: ScientificSemanticIR) -> dict[str, Any] | None:
    if unit.main is None:
        return None
    for stmt in unit.main.body.stmts:
        if not (
            isinstance(stmt, StateBind)
            and isinstance(stmt.expr, EvolveExpr)
            and stmt.expr.explicit_transform
        ):
            continue
        expr = stmt.expr
        source_node_id = _source_node_id_for_span(core, expr.span)
        return {
            "source_span": (expr.span.line, expr.span.col),
            "source_node_id": source_node_id,
            "provenance": {
                "source": "sqx",
                "line": expr.span.line,
                "col": expr.span.col,
                "source_node_id": source_node_id,
            },
            "source_node_kind": "EvolveExpr",
            "realization": "target_profile_required",
            "approximation_policy": "target_owned",
            "capability_decision": "deferred_to_target_lowering",
        }
    return None


def _source_node_id_for_span(core: ScientificSemanticIR, span: Any) -> str:
    matches = [
        node.node_id
        for node in core.nodes
        if node.provenance[1] == getattr(span, "line", 0)
        and node.provenance[2] == getattr(span, "col", 0)
    ]
    return matches[-1] if matches else ""


def _binder_source_node_ids(unit: Any, core: ScientificSemanticIR) -> tuple[str, ...]:
    if unit.main is None:
        return ()
    ids: list[str] = []
    for stmt in unit.main.body.stmts:
        if isinstance(stmt, StateBind) and stmt.ty is not None and stmt.ty.name == "Operator":
            node_id = _source_node_id_for_span(core, stmt.span)
            if node_id:
                ids.append(node_id)
    return tuple(dict.fromkeys(ids))


def _binder_provenance(
    unit: Any, core: ScientificSemanticIR
) -> tuple[tuple[tuple[str, Any], ...], ...]:
    if unit.main is None:
        return ()
    records: list[tuple[tuple[str, Any], ...]] = []
    for stmt in unit.main.body.stmts:
        if isinstance(stmt, StateBind) and stmt.ty is not None and stmt.ty.name == "Operator":
            node_id = _source_node_id_for_span(core, stmt.span)
            if node_id:
                records.append(
                    (
                        ("source", "sqx"),
                        ("line", stmt.span.line),
                        ("col", stmt.span.col),
                        ("source_node_id", node_id),
                    )
                )
    return tuple(records)


def _symbolic_operator_provenance(
    unit: Any, core: ScientificSemanticIR
) -> tuple[tuple[str, str, tuple[tuple[str, Any], ...]], ...]:
    """Retain source-derived operator aliases for compatibility views."""
    if unit.main is None:
        return ()
    records: list[tuple[str, str, tuple[tuple[str, Any], ...]]] = []
    for stmt in unit.main.body.stmts:
        if not (
            isinstance(stmt, StateBind)
            and stmt.ty is not None
            and stmt.ty.name == "Operator"
            and len(stmt.names) == 1
        ):
            continue
        node_id = _source_node_id_for_span(core, stmt.span)
        if node_id:
            records.append(
                (
                    stmt.names[0],
                    node_id,
                    (("line", stmt.span.line), ("col", stmt.span.col)),
                )
            )
    return tuple(records)


def _projection_errors(
    unit: Any,
    core: ScientificSemanticIR,
    binder_diagnostics: tuple[dict[str, Any], ...] = (),
) -> tuple[str, ...]:
    errors: list[str] = []
    if unit.main is None:
        return ()
    for stmt in unit.main.body.stmts:
        if isinstance(stmt, StateBind) and isinstance(stmt.expr, EvolveExpr):
            if (
                stmt.expr.suzuki is not None
                and _build_lowering_policy(unit, core) is None
                and not (
                    stmt.expr.hamiltonian is not None
                    and stmt.expr.duration is not None
                )
            ):
                errors.append("E_QPU_CANONICAL_POLICY_UNRESOLVED")
    finite_evolutions = tuple(
        stmt
        for stmt in unit.main.body.stmts
        if (
            isinstance(stmt, StateBind)
            and isinstance(stmt.expr, EvolveExpr)
            and stmt.expr.hamiltonian is not None
            and stmt.expr.suzuki is not None
            and stmt.expr.duration is not None
        )
    )
    scalar_values: dict[str, float] = {
        name: float(value) for name, value in PRELUDE_CONSTANTS.items()
    }
    for stmt in unit.main.body.stmts:
        if (
            isinstance(stmt, StateBind)
            and stmt.ty is not None
            and stmt.ty.name in {"Float", "Int"}
            and len(stmt.names) == 1
            and isinstance(stmt.expr, (LitFloat, LitInt))
        ):
            scalar_values[stmt.names[0]] = float(stmt.expr.value)
    for stmt in finite_evolutions:
        try:
            order = int(eval_time_expr(stmt.expr.suzuki.order, scalar_values))
        except (TrotterError, TypeError, ValueError):
            order = 0
        if order not in {2, 4}:
            errors.append("E_QPU_CANONICAL_FINITE_EVOLUTION_UNSUPPORTED")
    errors.extend(str(item.get("code", "E_QPU_CANONICAL_BINDER_UNRESOLVED")) for item in binder_diagnostics)
    return tuple(dict.fromkeys(errors))


def _register_sizes(unit: Any) -> dict[str, int]:
    """Return statically declared register widths for projection validation."""
    if unit.main is None:
        return {}
    return {
        stmt.names[0]: int(stmt.ty.args[0].name)
        for stmt in unit.main.body.stmts
        if (
            isinstance(stmt, StateBind)
            and stmt.ty is not None
            and stmt.ty.name == "QubitRegister"
            and stmt.names
            and stmt.ty.args
            and stmt.ty.args[0].name.isdigit()
        )
    }


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


def build_algorithm_plan(core: ScientificSemanticIR) -> "AlgorithmPlanModule | None":
    if not core.has_explicit_realize or core.realize_source_node_id is None:
        return None
    record = core.finite_realization_record
    if record is None:
        return None
    from .algorithm_plan_ir import (
        AlgorithmPlanModule,
        ApproximationObligation,
        PlanNode,
        PlanOrigin,
        RealizationDecision,
        ResourceExpr,
    )

    provenance = RealizationProvenance(core.realize_source_node_id)
    obligation = ApproximationObligation(
        obligation_id=f"{core.realize_source_node_id}:obligation",
        status="closed",
        bound=str(record.error_budget) if record.error_budget is not None else None,
        estimate=None,
        disposition="explicit_error_budget",
    )
    decision = RealizationDecision(
        decision_id=f"{core.realize_source_node_id}:decision",
        kind="finite_realization",
        selected=str(record.method or "unknown"),
        alternatives=("exact_symbolic",),
        assumptions=("source-visible Realize policy",),
        rejection_reasons=("provider/live execution is outside this plan",),
        policy_provenance="scientific_semantic_ir.finite_realization_record",
    )
    resource = ResourceExpr(
        resource_id=f"{core.realize_source_node_id}:resources",
        logical_dimensions=("source-declared",),
        ancillas="unspecified",
        depth="finite-policy-dependent",
        operations="finite-policy-dependent",
        measurements="terminal-only",
        classical_latency="unspecified",
        simulator_memory="unspecified",
        target_materialization="explicit Realize",
        multiplicity=str(record.steps) if record.steps is not None else "unspecified",
    )
    node = PlanNode(
        node_id=f"{core.realize_source_node_id}:node",
        semantic_id=core.realize_source_node_id,
        origin=PlanOrigin(
            source_id=record.source_node_id,
            physics_id=record.source_node_id,
            upstream_ids=(record.source_node_id,),
            transform_id="Realize",
        ),
        exactness="approximate",
        obligation_id=obligation.obligation_id,
        decision_ids=(decision.decision_id,),
        resource_id=resource.resource_id,
        operation_kind="finite_realization",
    )
    return AlgorithmPlanModule(
        schema_version=1,
        plan_id=core.realize_source_node_id,
        nodes=(node,),
        obligations=(obligation,),
        decisions=(decision,),
        resources=(resource,),
        repetitions=(),
        witnesses=("finite-qpu",),
        provenance=provenance,
    )


def _build_finite_realization_record(
    unit: Any, core: ScientificSemanticIR
) -> tuple[str | None, FiniteRealizationRecord | None, tuple[str, ...]]:
    """Build the source-owned finite realization record exactly once."""
    if unit.main is None:
        return None, None, ()
    realizes = [
        statement
        for statement in unit.main.body.stmts
        if isinstance(statement, StateBind)
        and isinstance(statement.expr, Call)
        and isinstance(statement.expr.callee, Var)
        and statement.expr.callee.name == "Realize"
    ]
    if not realizes:
        has_formal_limit = any(
            isinstance(statement, StateBind)
            and isinstance(statement.expr, Call)
            and isinstance(statement.expr.callee, Var)
            and statement.expr.callee.name == "Limit"
            for statement in unit.main.body.stmts
        )
        if has_formal_limit:
            return None, None, (
                "E_ALGORITHM_PLAN_CANONICAL_PROVENANCE:missing_realize_owner",
            )
        return None, None, ()
    if len(realizes) != 1:
        return None, None, (
            "E_ALGORITHM_PLAN_CANONICAL_PROVENANCE:multiple_realize_owners",
        )
    statement = realizes[0]
    source_node_id = _source_node_id_for_span(core, statement.expr.span)
    if not source_node_id:
        return None, None, (
            "E_ALGORITHM_PLAN_CANONICAL_PROVENANCE:missing_realize_owner",
        )
    kwargs = dict(statement.expr.kwargs or ())
    source = kwargs.get("source")
    source_name = source.name if isinstance(source, Var) else None

    def literal(name: str) -> Any:
        value = kwargs.get(name)
        return getattr(value, "value", None)

    if source_name is None or any(
        literal(name) is None
        for name in ("method", "order", "steps", "error_budget")
    ):
        return None, None, (
            "E_ALGORITHM_PLAN_CANONICAL_PROVENANCE:missing_finite_realization_record",
        )

    record = FiniteRealizationRecord(
        source_node_id=source_node_id,
        source_name=source_name,
        realized_name=statement.names[0] if statement.names else None,
        method=literal("method"),
        order=literal("order"),
        steps=literal("steps"),
        error_budget=literal("error_budget"),
        provenance=(
            ("source", "sqx"),
            ("line", statement.expr.span.line),
            ("col", statement.expr.span.col),
            ("source_node_id", source_node_id),
        ),
    )
    return source_node_id, record, ()


def _role_for(name: str) -> str:
    if "Measure" in name:
        return "terminal_classical"
    if name in {"Coin", "WhenExpr", "PhaseExpr", "InterferenceExpr"}:
        return "quantum"
    if name in {"Limit", "ExactExponential", "EvolveExpr"}:
        return "evolution"
    if "Operator" in name or "State" in name:
        return "quantum"
    if "Binder" in name or name in {"Sigma", "Pi"}:
        return "mathematical"
    return "classical"


def _type_for(name: str) -> str:
    if "State" in name or name in {
        "EvolveExpr",
        "Limit",
        "ExactExponential",
        "PhaseExpr",
        "InterferenceExpr",
    }:
        return "State<T>"
    if "Operator" in name:
        return "Operator"
    return "Unknown"


def _intent_for(name: str) -> str:
    if name == "Coin":
        return "coin_preparation"
    if name == "Limit":
        return "formal_evolution"
    if name == "EvolveExpr":
        return "evolution"
    if name == "ExactExponential":
        return "exact_evolution"
    if name == "PhaseExpr":
        return "phase_transform"
    if name == "InterferenceExpr":
        return "interference"
    if "Measure" in name:
        return "measurement"
    return "expression"


def _meaning_kind(name: str) -> str:
    if name == "Coin":
        return "coin"
    if name == "Limit":
        return "ideal_limit"
    if name == "ExactExponential":
        return "exact_exponential"
    if name == "WhenExpr":
        return "mixture"
    if name == "PhaseExpr":
        return "phase"
    if name == "InterferenceExpr":
        return "interference"
    if name in {"OpBin", "BinOp"}:
        return "mathematical_product"
    return "expression"


def _state_role(name: str) -> str:
    if name == "Coin":
        return "mixture_source"
    if name == "WhenExpr":
        return "mixed_state"
    if name in {"Limit", "ExactExponential", "EvolveExpr"}:
        return "evolution_operator"
    if name == "PhaseExpr":
        return "phase_transform"
    if name == "InterferenceExpr":
        return "interference"
    return "unspecified"


def _has_realize_call(value: Any) -> bool:
    """Recognize only the source call form ``Realize(...)``."""
    if value is None or isinstance(value, (str, int, float, bool, bytes)):
        return False
    if isinstance(value, (tuple, list)):
        return any(_has_realize_call(item) for item in value)
    if not hasattr(value, "__dataclass_fields__"):
        return False
    if type(value).__name__ == "Call":
        callee = getattr(value, "callee", None)
        if getattr(callee, "name", None) == "Realize":
            return True
    return any(
        _has_realize_call(getattr(value, field_name))
        for field_name in value.__dataclass_fields__
    )
