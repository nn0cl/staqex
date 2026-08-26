"""Quantum Semantic IR identity, root, lowering, and semantic contracts.

Slice A owns immutable semantic identities, provenance, schema versioning, and
deterministic root diagnostics. Slice B adds finite acting spaces, the
pure/density whole-Joint-state carriers, and the generation-use laws.

Region behavior, control and measurement lanes, pipeline wiring, and target
adapters belong to later LISS-0082 slices or other Issues. Slice E adds only a
narrow Physics-to-Semantic input boundary and exactness markers; it does not
choose a discretization, encoding, numerical method, or provider.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

SCHEMA_VERSION = 1
Diagnostic = dict[str, Any]
SEMANTIC_LANES = frozenset({"StaticKernel", "DynamicQpuContract"})
ANCILLA_DISCHARGE_KINDS = frozenset(
    {
        "ReturnedZero",
        "AbsorbedByIsometry",
        "TracedByChannel",
        "TerminalMeasurement",
    }
)

__all__ = [
    "ActingFactor",
    "ActingSpace",
    "ApproximationRequired",
    "AncillaDischarge",
    "AncillaScope",
    "ChannelRegion",
    "CoherentControlRegion",
    "ProjectorRegion",
    "TimingRegion",
    "DensityJointStateValue",
    "DynamicControlRegion",
    "DynamicMeasurementRegion",
    "Exact",
    "FiniteCarrierEvidence",
    "LinearResourceEvidence",
    "IsometryRegion",
    "Diagnostic",
    "JointValueUse",
    "PureJointStateValue",
    "QuantumSemanticInput",
    "QuantumSemanticLoweringResult",
    "QuantumSemanticModule",
    "RegionValidity",
    "SCHEMA_VERSION",
    "SemanticId",
    "SemanticLane",
    "SemanticOrigin",
    "TerminalMeasurementRegion",
    "UnitaryRegion",
    "OutcomeIntent",
    "ParameterSymbol",
    "PhysicsEvidenceRef",
    "UncomputeObligation",
    "verify_quantum_semantic_ir",
    "lower_physics_to_quantum_semantic_ir",
]


@dataclass(frozen=True, slots=True)
class SemanticId:
    """Stable identity for a semantic object within a named scope."""

    kind: str
    scope: str
    ordinal: int

    def __post_init__(self) -> None:
        if not self.kind:
            raise ValueError("semantic identity kind must not be empty")
        if not self.scope:
            raise ValueError("semantic identity scope must not be empty")
        if self.ordinal < 0:
            raise ValueError("semantic identity ordinal must not be negative")


@dataclass(frozen=True, slots=True)
class SemanticOrigin:
    """Closed source and transformation ancestry for a semantic identity."""

    source_id: str
    line: int
    col: int
    upstream_ids: tuple[str, ...] = field(default_factory=tuple)
    transform_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "upstream_ids", tuple(self.upstream_ids))


@dataclass(frozen=True, slots=True)
class Exact:
    """Exactness marker attached to one semantic operation."""

    operation_id: SemanticId | None = None
    origin: SemanticOrigin | None = None


@dataclass(frozen=True, slots=True)
class ApproximationRequired:
    """An explicit semantic obligation without method or tolerance choices."""

    obligation_id: SemanticId
    reason: str
    origin: SemanticOrigin
    operation_id: SemanticId | None = None


@dataclass(frozen=True, slots=True)
class PhysicsEvidenceRef:
    """Reviewed reference from Semantic evidence to one Physics node/golden."""

    physics_node_id: str
    golden_id: str
    source_origin: SemanticOrigin
    review_id: str


@dataclass(frozen=True, slots=True)
class LinearResourceEvidence:
    """Source-backed linear resource evidence retained at the boundary."""

    evidence_id: SemanticId
    resource_ids: tuple[SemanticId, ...]
    origin: SemanticOrigin

    def __post_init__(self) -> None:
        object.__setattr__(self, "resource_ids", tuple(self.resource_ids))


@dataclass(frozen=True, slots=True)
class FiniteCarrierEvidence:
    """Reviewed finite carrier evidence retained by the lowering boundary."""

    evidence_id: SemanticId
    acting_space: ActingSpace
    source_kind: str = "source_native"
    origin: SemanticOrigin = field(
        default_factory=lambda: SemanticOrigin(source_id="", line=0, col=0)
    )
    physics_refs: tuple[PhysicsEvidenceRef, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "physics_refs", tuple(self.physics_refs))


@dataclass(frozen=True, slots=True)
class QuantumSemanticInput:
    """Narrow immutable input accepted by Physics-to-Semantic lowering."""

    physics_module: Any
    finite_carrier_evidence: tuple[FiniteCarrierEvidence, ...] = ()
    linear_resource_evidence: tuple[object, ...] = ()
    lane: str | SemanticLane = "StaticKernel"
    exactness: tuple[Exact | ApproximationRequired, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "finite_carrier_evidence", tuple(self.finite_carrier_evidence)
        )
        object.__setattr__(
            self, "linear_resource_evidence", tuple(self.linear_resource_evidence)
        )
        object.__setattr__(self, "exactness", tuple(self.exactness))


@dataclass(frozen=True, slots=True)
class QuantumSemanticLoweringResult:
    """Lowering output: immutable module plus named, non-repairing diagnostics."""

    module: QuantumSemanticModule
    diagnostics: tuple[Diagnostic, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "diagnostics", tuple(self.diagnostics))


@dataclass(frozen=True, slots=True)
class ActingFactor:
    """One ordered tensor factor of a finite acting space."""

    factor_id: SemanticId
    dimension: int
    label: str = ""


@dataclass(frozen=True, slots=True)
class ActingSpace:
    """Ordered finite carrier a Joint state value acts on."""

    space_id: SemanticId
    factors: tuple[ActingFactor, ...]
    total_dimension: int
    origin: SemanticOrigin

    def __post_init__(self) -> None:
        object.__setattr__(self, "factors", tuple(self.factors))


@dataclass(frozen=True, slots=True)
class _JointStateValue:
    """Shared shape of one immutable whole-Joint-store generation.

    Resources name coordinates inside this single value. They never assert
    separability, and no amplitude or density matrix is stored. Purity is
    carried by the concrete subclass, never by a mutable flag.
    """

    value_id: SemanticId
    space_id: SemanticId
    resources: tuple[SemanticId, ...]
    producer_id: SemanticId | None
    origin: SemanticOrigin

    def __post_init__(self) -> None:
        object.__setattr__(self, "resources", tuple(self.resources))


@dataclass(frozen=True, slots=True)
class PureJointStateValue(_JointStateValue):
    """One immutable pure whole-Joint-store generation."""

    @property
    def is_pure(self) -> bool:
        return True


@dataclass(frozen=True, slots=True)
class DensityJointStateValue(_JointStateValue):
    """One immutable mixed whole-Joint-store generation."""

    @property
    def is_pure(self) -> bool:
        return False


JointStateValue = PureJointStateValue | DensityJointStateValue


@dataclass(frozen=True, slots=True)
class RegionValidity:
    """One declared, evidenced, or deferred region validity claim."""

    kind: str
    reference: str | None = None

    def __post_init__(self) -> None:
        if self.kind not in {"Declared", "Verified", "Required"}:
            raise ValueError(f"unsupported region validity kind: {self.kind}")
        if self.kind == "Declared" and self.reference is not None:
            raise ValueError("Declared validity must not carry a reference")
        if self.kind != "Declared" and not self.reference:
            raise ValueError(f"{self.kind} validity requires a reference")


@dataclass(frozen=True, slots=True)
class _TransformationRegion:
    """Shared provider-neutral signature of one transformation region."""

    region_id: SemanticId
    input_value_id: SemanticId
    output_value_id: SemanticId
    input_space_id: SemanticId
    output_space_id: SemanticId
    validity: RegionValidity
    origin: SemanticOrigin


@dataclass(frozen=True, slots=True)
class UnitaryRegion(_TransformationRegion):
    """Pure, reversible transformation over one unchanged acting space."""


@dataclass(frozen=True, slots=True)
class IsometryRegion(_TransformationRegion):
    """Pure transformation whose finite output space may be larger."""


@dataclass(frozen=True, slots=True)
class ChannelRegion(_TransformationRegion):
    """Physicality-obligation boundary producing a density carrier."""


@dataclass(frozen=True, slots=True)
class CoherentControlRegion(_TransformationRegion):
    """State-valued control over factor selectors in one Joint state."""

    control_factor_ids: tuple[SemanticId, ...]
    target_factor_ids: tuple[SemanticId, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "control_factor_ids", tuple(self.control_factor_ids))
        object.__setattr__(self, "target_factor_ids", tuple(self.target_factor_ids))


@dataclass(frozen=True, slots=True)
class ProjectorRegion(_TransformationRegion):
    """Explicit feasible-subspace restriction without terminal sampling."""

    constraint_ref: str


@dataclass(frozen=True, slots=True)
class TimingRegion(_TransformationRegion):
    """Dynamic-lane timing intent as inspectable Region provenance (ADR 0193).

    `timing_intent` is a source-derived free-form name. Staqex core does not
    interpret backend durations; a future target adapter may.
    """

    timing_intent: str

    def __post_init__(self) -> None:
        if not self.timing_intent:
            raise ValueError("TimingRegion requires a non-empty timing_intent")


@dataclass(frozen=True, slots=True)
class SemanticLane:
    """Closed execution-lane marker carried by Semantic IR."""

    kind: str

    def __post_init__(self) -> None:
        if self.kind not in SEMANTIC_LANES:
            raise ValueError(f"unsupported semantic lane: {self.kind}")


@dataclass(frozen=True, slots=True)
class OutcomeIntent:
    """Terminal outcome description with no reusable classical value."""

    intent_id: SemanticId
    measured_factor_ids: tuple[SemanticId, ...]
    outcome_domain: tuple[str, ...]
    origin: SemanticOrigin

    def __post_init__(self) -> None:
        object.__setattr__(self, "measured_factor_ids", tuple(self.measured_factor_ids))
        object.__setattr__(self, "outcome_domain", tuple(self.outcome_domain))


@dataclass(frozen=True, slots=True)
class TerminalMeasurementRegion:
    """Irreversible Static Kernel boundary with no reusable state output."""

    region_id: SemanticId
    input_value_id: SemanticId
    input_space_id: SemanticId
    outcome_intent_id: SemanticId
    origin: SemanticOrigin


@dataclass(frozen=True, slots=True)
class DynamicMeasurementRegion:
    """Dynamic-lane marker pairing post-measurement state with a token."""

    region_id: SemanticId
    input_value_id: SemanticId
    post_measure_value_id: SemanticId
    input_space_id: SemanticId
    output_space_id: SemanticId
    token_id: SemanticId
    outcome_domain: tuple[str, ...]
    branch_region_ids: tuple[SemanticId, ...]
    required_capability: str
    origin: SemanticOrigin

    def __post_init__(self) -> None:
        object.__setattr__(self, "outcome_domain", tuple(self.outcome_domain))
        object.__setattr__(self, "branch_region_ids", tuple(self.branch_region_ids))


@dataclass(frozen=True, slots=True)
class DynamicControlRegion:
    """Dynamic branch marker; controller execution belongs to LISS-0077."""

    region_id: SemanticId
    measurement_region_id: SemanticId
    post_measure_value_id: SemanticId
    token_id: SemanticId
    branch_region_ids: tuple[SemanticId, ...]
    merge_region_id: SemanticId | None
    output_value_id: SemanticId
    origin: SemanticOrigin

    def __post_init__(self) -> None:
        object.__setattr__(self, "branch_region_ids", tuple(self.branch_region_ids))


@dataclass(frozen=True, slots=True)
class ParameterSymbol:
    """Shape-independent symbolic parameter identity."""

    parameter_id: SemanticId
    scalar_type: str
    unit: str | None
    binding_phase: str
    shape_defining: bool
    origin: SemanticOrigin


@dataclass(frozen=True, slots=True)
class AncillaDischarge:
    """One explicit accepted ancilla discharge variant."""

    kind: str
    reference: str

    def __post_init__(self) -> None:
        if self.kind not in ANCILLA_DISCHARGE_KINDS:
            raise ValueError(f"unsupported ancilla discharge: {self.kind}")
        if not self.reference:
            raise ValueError("ancilla discharge requires evidence")


@dataclass(frozen=True, slots=True)
class AncillaScope:
    """Linear ancilla lifetime with an explicit discharge or a diagnostic."""

    scope_id: SemanticId
    resource_id: SemanticId
    acquire_precondition: str
    discharge: AncillaDischarge | None
    origin: SemanticOrigin


@dataclass(frozen=True, slots=True)
class UncomputeObligation:
    """Evidence obligation; it does not contain inverse synthesis policy."""

    obligation_id: SemanticId
    resource_id: SemanticId
    witness_ref: str
    origin: SemanticOrigin


SemanticRegion = (
    UnitaryRegion
    | IsometryRegion
    | ChannelRegion
    | CoherentControlRegion
    | ProjectorRegion
    | TimingRegion
    | DynamicMeasurementRegion
    | TerminalMeasurementRegion
    | DynamicControlRegion
)


@dataclass(frozen=True, slots=True)
class JointValueUse:
    """One consuming path of a whole-Joint-state generation.

    `factor_id` is populated only by an invalid attempt to consume a factor as
    an independent state value; the verifier reports it.
    """

    value_id: SemanticId
    consumer_id: SemanticId
    factor_id: SemanticId | None = None


@dataclass(frozen=True, slots=True)
class QuantumSemanticModule:
    """Schema-versioned immutable root for later Semantic IR slices."""

    schema_version: int
    roots: tuple[SemanticId, ...] = field(default_factory=tuple)
    region_roots: tuple[SemanticId, ...] = field(default_factory=tuple)
    origins: tuple[SemanticOrigin, ...] = field(default_factory=tuple)
    acting_spaces: tuple[ActingSpace, ...] = field(default_factory=tuple)
    values: tuple[JointStateValue, ...] = field(default_factory=tuple)
    value_uses: tuple[JointValueUse, ...] = field(default_factory=tuple)
    regions: tuple[SemanticRegion, ...] = field(default_factory=tuple)
    lane: SemanticLane = field(
        default_factory=lambda: SemanticLane(kind="StaticKernel")
    )
    outcome_intents: tuple[OutcomeIntent, ...] = field(default_factory=tuple)
    parameters: tuple[ParameterSymbol, ...] = field(default_factory=tuple)
    ancilla_scopes: tuple[AncillaScope, ...] = field(default_factory=tuple)
    uncompute_obligations: tuple[UncomputeObligation, ...] = field(
        default_factory=tuple
    )
    approximation_obligations: tuple[ApproximationRequired, ...] = field(
        default_factory=tuple
    )
    exactness: tuple[Exact | ApproximationRequired, ...] = field(
        default_factory=tuple
    )
    physics_evidence: tuple[FiniteCarrierEvidence, ...] = field(
        default_factory=tuple
    )
    linear_resource_evidence: tuple[object, ...] = field(
        default_factory=tuple
    )

    @property
    def source_node_ids(self) -> tuple[str, ...]:
        """Stable source identities exposed by the canonical projection."""
        values = tuple(str(origin.source_id) for origin in self.origins)
        return values or ("qsem:canonical-source",)

    def __post_init__(self) -> None:
        object.__setattr__(self, "roots", tuple(self.roots))
        object.__setattr__(self, "region_roots", tuple(self.region_roots))
        object.__setattr__(self, "origins", tuple(self.origins))
        object.__setattr__(self, "acting_spaces", tuple(self.acting_spaces))
        object.__setattr__(self, "values", tuple(self.values))
        object.__setattr__(self, "value_uses", tuple(self.value_uses))
        object.__setattr__(self, "regions", tuple(self.regions))
        object.__setattr__(self, "outcome_intents", tuple(self.outcome_intents))
        object.__setattr__(self, "parameters", tuple(self.parameters))
        object.__setattr__(self, "ancilla_scopes", tuple(self.ancilla_scopes))
        object.__setattr__(
            self, "uncompute_obligations", tuple(self.uncompute_obligations)
        )
        object.__setattr__(
            self,
            "approximation_obligations",
            tuple(self.approximation_obligations),
        )
        object.__setattr__(self, "exactness", tuple(self.exactness))
        object.__setattr__(self, "physics_evidence", tuple(self.physics_evidence))
        object.__setattr__(
            self,
            "linear_resource_evidence",
            tuple(self.linear_resource_evidence),
        )


def _finite_evidence_diagnostics(
    evidence: tuple[FiniteCarrierEvidence, ...],
    physics_module: Any,
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    if not evidence:
        diagnostics.append(
            _diagnostic(
                "QSEM_FINITE_EVIDENCE_MISSING",
                "finite carrier evidence is required for Semantic lowering",
            )
        )
        return diagnostics

    physics_nodes = _physics_node_ids(physics_module)
    for item in evidence:
        if item.source_kind not in {"source_native", "reviewed_finite"}:
            diagnostics.append(
                _diagnostic(
                    "QSEM_FINITE_EVIDENCE_MISSING",
                    "carrier evidence is not an accepted finite source",
                    evidence=item.evidence_id,
                )
            )
        if _origin_is_incomplete(item.origin):
            diagnostics.append(
                _diagnostic(
                    "QSEM_PROVENANCE_INCOMPLETE",
                    "finite carrier evidence has incomplete provenance",
                    evidence=item.evidence_id,
                    origin=item.origin,
                )
            )
        for reference in item.physics_refs:
            if reference.physics_node_id not in physics_nodes:
                diagnostics.append(
                    _diagnostic(
                        "QSEM_FINITE_EVIDENCE_INVALID",
                        "finite evidence references an unknown Physics node",
                        evidence=item.evidence_id,
                        physics_node=reference.physics_node_id,
                    )
                )
            if not reference.golden_id or not reference.review_id:
                diagnostics.append(
                    _diagnostic(
                        "QSEM_FINITE_EVIDENCE_INVALID",
                        "finite evidence requires a reviewed golden reference",
                        evidence=item.evidence_id,
                    )
                )
            if _origin_is_incomplete(reference.source_origin):
                diagnostics.append(
                    _diagnostic(
                        "QSEM_PROVENANCE_INCOMPLETE",
                        "Physics evidence reference has incomplete provenance",
                        evidence=item.evidence_id,
                        origin=reference.source_origin,
                    )
                )
                diagnostics.append(
                    _diagnostic(
                        "QSEM_PROVENANCE_UNRESOLVED",
                        "Physics evidence reference ancestry cannot be resolved",
                        evidence=item.evidence_id,
                    )
                )
    return diagnostics


def _physics_node_ids(physics_module: Any) -> set[str | None]:
    """Project only stable node identities from the upstream Physics module."""

    return {
        getattr(node, "node_id", None)
        for node in getattr(physics_module, "nodes", ())
    }


def _exactness_diagnostics(
    markers: tuple[Exact | ApproximationRequired, ...],
) -> list[Diagnostic]:
    if not markers:
        return [
            _diagnostic(
                "QSEM_APPROXIMATION_OBLIGATION_MISSING",
                "non-exact lowering requires an explicit approximation obligation",
            )
        ]

    diagnostics: list[Diagnostic] = []
    operation_kinds: dict[SemanticId, set[str]] = {}
    for marker in markers:
        if marker.operation_id is not None:
            operation_kinds.setdefault(marker.operation_id, set()).add(
                "approximation"
                if isinstance(marker, ApproximationRequired)
                else "exact"
            )
        if isinstance(marker, ApproximationRequired) and _origin_is_incomplete(
            marker.origin
        ):
            diagnostics.append(
                _diagnostic(
                    "QSEM_PROVENANCE_INCOMPLETE",
                    "approximation obligation has incomplete provenance",
                    obligation=marker.obligation_id,
                    origin=marker.origin,
                )
            )
    for operation_id, kinds in operation_kinds.items():
        if len(kinds) > 1:
            diagnostics.append(
                _diagnostic(
                    "QSEM_EXACTNESS_CONFLICT",
                    "semantic operation cannot be both exact and approximate",
                    operation=operation_id,
                )
            )
    return diagnostics


def _linear_resource_diagnostics(
    resources: tuple[object, ...],
) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    for resource in resources:
        if not isinstance(resource, LinearResourceEvidence):
            diagnostics.append(
                _diagnostic(
                    "QSEM_RESOURCE_EVIDENCE_INVALID",
                    "linear resource evidence must use the closed DTO",
                )
            )
            continue
        if _origin_is_incomplete(resource.origin):
            diagnostics.append(
                _diagnostic(
                    "QSEM_PROVENANCE_INCOMPLETE",
                    "linear resource evidence has incomplete provenance",
                    evidence=resource.evidence_id,
                    origin=resource.origin,
                )
            )
    return diagnostics


def _semantic_lane(value: str | SemanticLane) -> SemanticLane:
    return value if isinstance(value, SemanticLane) else SemanticLane(kind=value)


def _module_from_lowering_input(
    input_contract: QuantumSemanticInput,
) -> QuantumSemanticModule:
    evidence = input_contract.finite_carrier_evidence
    return QuantumSemanticModule(
        schema_version=SCHEMA_VERSION,
        origins=tuple(item.origin for item in evidence),
        acting_spaces=tuple(item.acting_space for item in evidence),
        lane=_semantic_lane(input_contract.lane),
        approximation_obligations=tuple(
            marker
            for marker in input_contract.exactness
            if isinstance(marker, ApproximationRequired)
        ),
        exactness=input_contract.exactness,
        physics_evidence=evidence,
        linear_resource_evidence=tuple(input_contract.linear_resource_evidence),
    )


def _lowering_diagnostics(
    input_contract: QuantumSemanticInput,
    module: QuantumSemanticModule,
) -> list[Diagnostic]:
    diagnostics = _finite_evidence_diagnostics(
        input_contract.finite_carrier_evidence,
        input_contract.physics_module,
    )
    diagnostics.extend(_exactness_diagnostics(input_contract.exactness))
    diagnostics.extend(
        _linear_resource_diagnostics(input_contract.linear_resource_evidence)
    )
    diagnostics.extend(verify_quantum_semantic_ir(module))
    return diagnostics


def lower_physics_to_quantum_semantic_ir(
    input_contract: QuantumSemanticInput,
) -> QuantumSemanticLoweringResult:
    """Lower reviewed finite evidence without making a realization choice.

    This boundary accepts only the explicit DTO. It never traverses AST/HIR,
    calls an evaluator, or invents a finite space when evidence is absent.
    """

    if not isinstance(input_contract, QuantumSemanticInput):
        raise TypeError(
            "Quantum Semantic lowering accepts QuantumSemanticInput only"
        )

    module = _module_from_lowering_input(input_contract)
    diagnostics = _lowering_diagnostics(input_contract, module)

    return QuantumSemanticLoweringResult(
        module=module,
        diagnostics=tuple(diagnostics),
    )


def _diagnostic(code: str, message: str, **details: Any) -> Diagnostic:
    result: Diagnostic = {"code": code, "message": message}
    result.update(details)
    return result


def _defined_identities(module: QuantumSemanticModule) -> tuple[SemanticId, ...]:
    """Return every identity the module *defines*, in canonical order.

    Only definition sites count. An identity that merely appears as a reference
    -- `value.space_id`, `value.resources`, `producer_id`, a `JointValueUse`
    target, or `SemanticOrigin.upstream_ids` -- is resolved elsewhere and is
    never a redefinition.
    """

    defined: list[SemanticId] = list(module.roots)
    defined.extend(module.region_roots)
    for space in module.acting_spaces:
        defined.append(space.space_id)
        defined.extend(factor.factor_id for factor in space.factors)
    defined.extend(value.value_id for value in module.values)
    defined.extend(region.region_id for region in module.regions)
    defined.extend(intent.intent_id for intent in module.outcome_intents)
    defined.extend(parameter.parameter_id for parameter in module.parameters)
    defined.extend(scope.scope_id for scope in module.ancilla_scopes)
    defined.extend(
        obligation.obligation_id for obligation in module.uncompute_obligations
    )
    return tuple(defined)


def _origin_is_incomplete(origin: SemanticOrigin) -> bool:
    return (
        not origin.source_id
        or origin.line < 1
        or origin.col < 1
        or not origin.transform_id
    )


def _report_incomplete_origin(
    origin: SemanticOrigin,
    diagnostics: list[Diagnostic],
    message: str,
    **details: Any,
) -> None:
    """Apply the one ancestry predicate to one definition site."""

    if _origin_is_incomplete(origin):
        diagnostics.append(
            _diagnostic("QSEM_PROVENANCE_INCOMPLETE", message, **details, origin=origin)
        )


def _verify_root(
    module: QuantumSemanticModule, diagnostics: list[Diagnostic]
) -> None:
    """Report unsupported schema, duplicate identity, and missing ancestry."""

    if module.schema_version != SCHEMA_VERSION:
        diagnostics.append(
            _diagnostic(
                "QSEM_SCHEMA_VERSION_UNSUPPORTED",
                "unsupported Quantum Semantic IR schema version",
                schema_version=module.schema_version,
            )
        )

    identities = _defined_identities(module)
    seen: set[SemanticId] = set()
    for identity in identities:
        if identity in seen:
            diagnostics.append(
                _diagnostic(
                    "QSEM_IDENTITY_CONFLICT",
                    "semantic identity is defined more than once",
                    identity=identity,
                )
            )
        seen.add(identity)

    if identities and not module.origins:
        diagnostics.append(
            _diagnostic(
                "QSEM_PROVENANCE_INCOMPLETE",
                "semantic roots require at least one source origin",
            )
        )

    for origin in module.origins:
        _report_incomplete_origin(
            origin,
            diagnostics,
            "source origin is missing required ancestry fields",
        )


def _verify_acting_spaces(
    module: QuantumSemanticModule, diagnostics: list[Diagnostic]
) -> None:
    """Report invalid acting-space shape and incomplete acting-space ancestry."""

    for space in module.acting_spaces:
        _report_incomplete_origin(
            space.origin,
            diagnostics,
            "acting space origin is missing required ancestry fields",
            acting_space=space.space_id,
        )

        if not space.factors:
            diagnostics.append(
                _diagnostic(
                    "QSEM_ACTING_SPACE_INVALID",
                    "acting space has no tensor factors",
                    acting_space=space.space_id,
                )
            )
            continue

        product = 1
        has_invalid_factor = False
        for factor in space.factors:
            if factor.dimension < 1:
                diagnostics.append(
                    _diagnostic(
                        "QSEM_ACTING_SPACE_INVALID",
                        "acting space factor dimension must be positive",
                        acting_space=space.space_id,
                        factor=factor.factor_id,
                        dimension=factor.dimension,
                    )
                )
                has_invalid_factor = True
            product *= factor.dimension

        if not has_invalid_factor and space.total_dimension != product:
            diagnostics.append(
                _diagnostic(
                    "QSEM_ACTING_SPACE_INVALID",
                    "acting space total dimension does not match its factors",
                    acting_space=space.space_id,
                    total_dimension=space.total_dimension,
                    factor_product=product,
                )
            )


def _verify_joint_values(
    module: QuantumSemanticModule, diagnostics: list[Diagnostic]
) -> None:
    """Report unknown carriers, resource drift, ancestry, and missing producers."""

    spaces = {space.space_id: space for space in module.acting_spaces}
    for value in module.values:
        _report_incomplete_origin(
            value.origin,
            diagnostics,
            "joint state value origin is missing required ancestry fields",
            value=value.value_id,
        )

        space = spaces.get(value.space_id)
        if space is None:
            diagnostics.append(
                _diagnostic(
                    "QSEM_ACTING_SPACE_INVALID",
                    "joint state value references an unknown acting space",
                    value=value.value_id,
                    acting_space=value.space_id,
                )
            )
        else:
            factor_ids = tuple(factor.factor_id for factor in space.factors)
            if value.resources != factor_ids:
                diagnostics.append(
                    _diagnostic(
                        "QSEM_ACTING_SPACE_INVALID",
                        "joint state value resources do not match the ordered "
                        "acting space factors",
                        value=value.value_id,
                        acting_space=value.space_id,
                        resources=value.resources,
                        factors=factor_ids,
                    )
                )

        if value.producer_id is None:
            diagnostics.append(
                _diagnostic(
                    "QSEM_VALUE_USE_INVALID",
                    "joint state generation has no producer",
                    value=value.value_id,
                )
            )


def _verify_value_uses(
    module: QuantumSemanticModule, diagnostics: list[Diagnostic]
) -> None:
    """Report unknown, fanned-out, or factor-level consumption of a generation."""

    known_values = {value.value_id for value in module.values}
    consumed: set[SemanticId] = set()
    for use in module.value_uses:
        if use.value_id not in known_values:
            diagnostics.append(
                _diagnostic(
                    "QSEM_VALUE_USE_INVALID",
                    "value use references an unknown joint state generation",
                    value=use.value_id,
                    consumer=use.consumer_id,
                )
            )
            continue

        if use.factor_id is not None:
            diagnostics.append(
                _diagnostic(
                    "QSEM_VALUE_USE_INVALID",
                    "a factor cannot be consumed as an independent state value",
                    value=use.value_id,
                    factor=use.factor_id,
                    consumer=use.consumer_id,
                )
            )
            continue

        if use.value_id in consumed:
            diagnostics.append(
                _diagnostic(
                    "QSEM_VALUE_USE_INVALID",
                    "joint state generation has more than one consuming path",
                    value=use.value_id,
                    consumer=use.consumer_id,
                )
            )
        consumed.add(use.value_id)


def _region_signature_diagnostic(
    region: _TransformationRegion, message: str, **details: Any
) -> Diagnostic:
    return _diagnostic(
        "QSEM_REGION_SIGNATURE_INVALID",
        message,
        region=region.region_id,
        **details,
    )


def _verify_region_references(
    region: _TransformationRegion,
    values: dict[SemanticId, JointStateValue],
    spaces: dict[SemanticId, ActingSpace],
    diagnostics: list[Diagnostic],
) -> tuple[
    JointStateValue | None,
    JointStateValue | None,
    ActingSpace | None,
    ActingSpace | None,
]:
    input_value = values.get(region.input_value_id)
    output_value = values.get(region.output_value_id)
    input_space = spaces.get(region.input_space_id)
    output_space = spaces.get(region.output_space_id)

    if input_value is None or output_value is None:
        diagnostics.append(
            _region_signature_diagnostic(
                region,
                "transformation region references an unknown Joint value",
                input_value=region.input_value_id,
                output_value=region.output_value_id,
            )
        )
    if input_space is None or output_space is None:
        diagnostics.append(
            _region_signature_diagnostic(
                region,
                "transformation region references an unknown acting space",
                input_space=region.input_space_id,
                output_space=region.output_space_id,
            )
        )

    if input_value is not None and input_value.space_id != region.input_space_id:
        diagnostics.append(
            _region_signature_diagnostic(
                region,
                "input Joint value does not inhabit the declared input space",
                input_value=region.input_value_id,
                input_space=region.input_space_id,
            )
        )
    if output_value is not None and output_value.space_id != region.output_space_id:
        diagnostics.append(
            _region_signature_diagnostic(
                region,
                "output Joint value does not inhabit the declared output space",
                output_value=region.output_value_id,
                output_space=region.output_space_id,
            )
        )

    return input_value, output_value, input_space, output_space


def _verify_unitary(
    region: UnitaryRegion,
    input_value: JointStateValue | None,
    output_value: JointStateValue | None,
    input_space: ActingSpace | None,
    output_space: ActingSpace | None,
    diagnostics: list[Diagnostic],
) -> None:
    valid_signature = (
        input_value is not None
        and output_value is not None
        and isinstance(input_value, PureJointStateValue)
        and isinstance(output_value, PureJointStateValue)
        and input_space is not None
        and output_space is not None
        and region.input_space_id == region.output_space_id
        and input_space.total_dimension == output_space.total_dimension
    )
    if not valid_signature:
        diagnostics.append(
            _region_signature_diagnostic(
                region,
                "UnitaryRegion must preserve a pure carrier and acting space",
            )
        )


def _verify_isometry(
    region: IsometryRegion,
    input_value: JointStateValue | None,
    output_value: JointStateValue | None,
    input_space: ActingSpace | None,
    output_space: ActingSpace | None,
    diagnostics: list[Diagnostic],
) -> None:
    valid_signature = (
        input_value is not None
        and output_value is not None
        and isinstance(input_value, PureJointStateValue)
        and isinstance(output_value, PureJointStateValue)
        and input_space is not None
        and output_space is not None
        and input_space.total_dimension <= output_space.total_dimension
    )
    if not valid_signature:
        diagnostics.append(
            _region_signature_diagnostic(
                region,
                "IsometryRegion requires pure carriers and non-decreasing finite dimension",
            )
        )

    if (
        input_space is not None
        and output_space is not None
        and input_space.total_dimension < output_space.total_dimension
        and region.validity.kind != "Required"
    ):
        diagnostics.append(
            _diagnostic(
                "QSEM_REGION_VALIDITY_INVALID",
                "IsometryRegion dimension increase requires an explicit obligation",
                region=region.region_id,
            )
        )


def _verify_channel(
    region: ChannelRegion,
    input_value: JointStateValue | None,
    output_value: JointStateValue | None,
    diagnostics: list[Diagnostic],
) -> None:
    if input_value is None or output_value is None or not isinstance(
        output_value, DensityJointStateValue
    ):
        diagnostics.append(
            _region_signature_diagnostic(
                region,
                "ChannelRegion must produce a density carrier",
            )
        )


def _verify_coherent_control(
    region: CoherentControlRegion,
    spaces: dict[SemanticId, ActingSpace],
    diagnostics: list[Diagnostic],
) -> None:
    space = spaces.get(region.input_space_id)
    factor_ids = {factor.factor_id for factor in space.factors} if space else set()
    controls = set(region.control_factor_ids)
    targets = set(region.target_factor_ids)
    if (
        space is None
        or not controls
        or not targets
        or not controls.issubset(factor_ids)
        or not targets.issubset(factor_ids)
        or controls & targets
    ):
        diagnostics.append(
            _diagnostic(
                "QSEM_CONTROL_LANE_INVALID",
                "coherent control selectors must be disjoint factors in one acting space",
                region=region.region_id,
            )
        )


def _verify_terminal_measurement(
    module: QuantumSemanticModule,
    region: TerminalMeasurementRegion,
    outcome_intents: dict[SemanticId, OutcomeIntent],
    diagnostics: list[Diagnostic],
) -> None:
    if region.outcome_intent_id not in outcome_intents:
        diagnostics.append(
            _diagnostic(
                "QSEM_MEASUREMENT_BOUNDARY_INVALID",
                "terminal measurement references an unknown outcome intent",
                region=region.region_id,
                outcome_intent=region.outcome_intent_id,
            )
        )

    for successor in module.regions:
        if successor is region or isinstance(successor, TerminalMeasurementRegion):
            continue
        if getattr(successor, "input_value_id", None) == region.input_value_id:
            diagnostics.append(
                _diagnostic(
                    "QSEM_MEASUREMENT_BOUNDARY_INVALID",
                    "terminal measurement input is consumed again",
                    region=region.region_id,
                    successor=successor.region_id,
                )
            )


def _verify_dynamic_regions(
    module: QuantumSemanticModule,
    region: DynamicMeasurementRegion | DynamicControlRegion,
    diagnostics: list[Diagnostic],
) -> None:
    if module.lane.kind != "DynamicQpuContract":
        _report_dynamic_lane_invalid(region, diagnostics)

    if isinstance(region, DynamicMeasurementRegion):
        if (
            not region.outcome_domain
            or not region.branch_region_ids
            or region.required_capability != "DynamicMeasurementFeedback"
        ):
            diagnostics.append(
                _diagnostic(
                    "QSEM_DYNAMIC_CORRELATION_INVALID",
                    "dynamic measurement marker lacks finite correlation metadata",
                    region=region.region_id,
                )
            )
        return

    measurements = {
        candidate.region_id: candidate
        for candidate in module.regions
        if isinstance(candidate, DynamicMeasurementRegion)
    }
    measurement = measurements.get(region.measurement_region_id)
    if (
        measurement is None
        or region.post_measure_value_id != measurement.post_measure_value_id
        or region.token_id != measurement.token_id
        or region.branch_region_ids != measurement.branch_region_ids
        or region.merge_region_id is None
    ):
        diagnostics.append(
            _diagnostic(
                "QSEM_DYNAMIC_CORRELATION_INVALID",
                "dynamic token, post-measurement value, and branch merge must remain paired",
                region=region.region_id,
            )
        )


def _report_dynamic_lane_invalid(
    region: DynamicMeasurementRegion | DynamicControlRegion,
    diagnostics: list[Diagnostic],
) -> None:
    diagnostics.append(
        _diagnostic(
            "QSEM_CONTROL_LANE_INVALID",
            "dynamic feedback is invalid in Static Kernel",
            region=region.region_id,
        )
    )


def _verify_slice_d(
    module: QuantumSemanticModule, diagnostics: list[Diagnostic]
) -> None:
    outcome_intents = {
        intent.intent_id: intent for intent in module.outcome_intents
    }
    spaces = {space.space_id: space for space in module.acting_spaces}

    for intent in module.outcome_intents:
        _report_incomplete_origin(
            intent.origin,
            diagnostics,
            "outcome intent origin is missing required ancestry fields",
            outcome_intent=intent.intent_id,
        )

    for parameter in module.parameters:
        _report_incomplete_origin(
            parameter.origin,
            diagnostics,
            "parameter origin is missing required ancestry fields",
            parameter=parameter.parameter_id,
        )
        if parameter.binding_phase == "Runtime" and parameter.shape_defining:
            diagnostics.append(
                _diagnostic(
                    "QSEM_PARAMETER_SHAPE_DEPENDENCE",
                    "runtime parameter must not define acting-space shape",
                    parameter=parameter.parameter_id,
                )
            )

    for scope in module.ancilla_scopes:
        _report_incomplete_origin(
            scope.origin,
            diagnostics,
            "ancilla scope origin is missing required ancestry fields",
            ancilla_scope=scope.scope_id,
        )
        if scope.discharge is None:
            diagnostics.append(
                _diagnostic(
                    "QSEM_RESOURCE_DISCHARGE_MISSING",
                    "ancilla scope leaves scope without an accepted discharge",
                    ancilla_scope=scope.scope_id,
                    resource=scope.resource_id,
                )
            )

    for obligation in module.uncompute_obligations:
        _report_incomplete_origin(
            obligation.origin,
            diagnostics,
            "uncompute obligation origin is missing required ancestry fields",
            obligation=obligation.obligation_id,
        )

    for region in module.regions:
        if isinstance(region, CoherentControlRegion):
            _verify_coherent_control(region, spaces, diagnostics)
        elif isinstance(region, TerminalMeasurementRegion):
            _verify_terminal_measurement(module, region, outcome_intents, diagnostics)
        elif isinstance(region, (DynamicMeasurementRegion, DynamicControlRegion)):
            _verify_dynamic_regions(module, region, diagnostics)


def _verify_regions(
    module: QuantumSemanticModule, diagnostics: list[Diagnostic]
) -> None:
    values: dict[SemanticId, JointStateValue] = {
        value.value_id: value for value in module.values
    }
    spaces = {space.space_id: space for space in module.acting_spaces}
    for region in module.regions:
        _report_incomplete_origin(
            region.origin,
            diagnostics,
            "transformation region origin is missing required ancestry fields",
            region=region.region_id,
        )
        if isinstance(region, (TerminalMeasurementRegion, DynamicMeasurementRegion)):
            continue
        if isinstance(region, DynamicControlRegion):
            continue

        input_value, output_value, input_space, output_space = _verify_region_references(
            region, values, spaces, diagnostics
        )
        if isinstance(region, UnitaryRegion):
            _verify_unitary(
                region, input_value, output_value, input_space, output_space, diagnostics
            )
        elif isinstance(region, IsometryRegion):
            _verify_isometry(
                region, input_value, output_value, input_space, output_space, diagnostics
            )
        elif isinstance(region, ChannelRegion):
            _verify_channel(region, input_value, output_value, diagnostics)


def verify_quantum_semantic_ir(module: QuantumSemanticModule) -> list[Diagnostic]:
    """Return deterministic non-mutating diagnostics for the semantic module.

    Diagnostics are appended in a fixed pass order — root, acting spaces,
    Joint state values, value uses — so the report is reproducible. The module
    is never repaired.
    """

    diagnostics: list[Diagnostic] = []
    _verify_root(module, diagnostics)
    _verify_acting_spaces(module, diagnostics)
    _verify_joint_values(module, diagnostics)
    _verify_value_uses(module, diagnostics)
    _verify_regions(module, diagnostics)
    _verify_slice_d(module, diagnostics)
    return diagnostics
