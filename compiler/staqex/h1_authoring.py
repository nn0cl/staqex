"""Source-backed semantic boundary for the H1 authoring surface.

The H1 boundary recognizes the reviewed theory/experiment markers, builds
structured operator metadata, and preserves an ordered State Transformer plan.
Numerical execution and target lowering remain outside this module.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from types import MappingProxyType

from .ast_nodes import (
    ExperimentDecl,
    H1CoherentControl,
    H1DynamicControl,
    H1Evolve,
    H1Measure,
    H1Mixture,
    H1OperatorDecl,
    H1Observable,
    H1Prepare,
    H1RealizeDecl,
    H1Superposition,
    H1TraceOut,
    H1Uncompute,
    OpBin,
    OpIndexed,
    OpPauli,
    OpVar,
    TheoryDecl,
)
from .target_capability import FakePhysicalTargetPort
from .physics_ir import OperatorAtom, PhysicsModule, PhysicsNode, SourceOrigin
from .quantum_semantic_ir import (
    ActingFactor,
    ActingSpace,
    CoherentControlRegion,
    QuantumSemanticModule,
    RegionValidity,
    SemanticId,
    SemanticLane,
    SemanticOrigin,
    SCHEMA_VERSION,
    UncomputeObligation,
)


_THEORY = re.compile(r"\btheory\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{")
_EXPERIMENT = re.compile(r"\bexperiment\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:\([^)]*\))?\s*\{")
_BOUNDARY = re.compile(r"\bboundary\s+(?:=\s*)?([A-Za-z_][A-Za-z0-9_]*)")
_H1_SCOPE = "h1"
_UNCOMPUTE_WITNESS_TOKEN = "witness"


@dataclass(frozen=True)
class H1Analysis:
    diagnostics: list[dict[str, object]]
    physics_ir: PhysicsModule
    state_transform_plan: "H1StateTransformPlan | None" = None
    quantum_semantic_ir: QuantumSemanticModule | None = None


@dataclass(frozen=True)
class H1PlanStep:
    """One ordered, source-backed H1 state-transform operation."""

    kind: str
    source_tokens: tuple[str, ...]
    origin: SourceOrigin
    characteristics: tuple[str, ...] = ()


@dataclass(frozen=True)
class H1StateTransformPlan:
    """Provider-neutral H1 experiment plan before numerical lowering."""

    steps: tuple[H1PlanStep, ...]


_PLAN_STEP_KINDS = {
    H1Prepare: "Prepare",
    H1Evolve: "Evolve",
    H1Observable: "Observe",
    H1Measure: "TerminalMeasure",
    H1Mixture: "Mixture",
    H1Superposition: "CoherentSuperposition",
    H1CoherentControl: "CoherentControl",
    H1TraceOut: "TraceOut",
    H1Uncompute: "Uncompute",
}

_PLAN_STEP_CHARACTERISTICS = {
    "Evolve": ("Unitary", "Adj"),
    "CoherentControl": ("Unitary", "Ctl"),
    "Uncompute": ("Adj",),
}


def is_h1_unit(unit: object) -> bool:
    """Identify H1 from formal AST ownership, not source-text heuristics."""

    declarations = getattr(unit, "decls", ())
    return any(
        isinstance(declaration, (TheoryDecl, ExperimentDecl))
        for declaration in declarations
    )


def _source_origin(source: str, theory: re.Match[str]) -> SourceOrigin:
    line = source.count("\n", 0, theory.start()) + 1
    col = theory.start() - source.rfind("\n", 0, theory.start())
    return SourceOrigin(source_id="h1", line=line, col=col)


def _diagnostic(
    code: str,
    origin: SourceOrigin,
    message: str,
) -> dict[str, object]:
    return {
        "code": code,
        "line": origin.line,
        "col": origin.col,
        "message": message,
    }


def _step_origin(step: object, fallback: SourceOrigin) -> SourceOrigin:
    span = getattr(step, "span", None)
    if span is None:
        return fallback
    return SourceOrigin(source_id=fallback.source_id, line=span.line, col=span.col)


def _plan_step_kind(statement: object) -> str | None:
    for statement_type, kind in _PLAN_STEP_KINDS.items():
        if isinstance(statement, statement_type):
            return kind
    return None


def _has_explicit_uncompute_witness(statement: H1Uncompute) -> bool:
    """Recognize the reviewed witness marker without parsing its payload yet."""

    return _UNCOMPUTE_WITNESS_TOKEN in statement.source_tokens


def _build_state_transform_plan(
    experiment: ExperimentDecl,
    fallback_origin: SourceOrigin,
) -> tuple[H1StateTransformPlan | None, list[dict[str, object]]]:
    steps: list[H1PlanStep] = []
    diagnostics: list[dict[str, object]] = []
    measured = False
    for statement in experiment.body:
        if isinstance(statement, H1DynamicControl):
            origin = _step_origin(statement, fallback_origin)
            diagnostics.append(
                _diagnostic(
                    "H1_DYNAMIC_CONTROL_REQUIRES_DYNAMIC_LANE",
                    origin,
                    "measurement-dependent control requires the Dynamic QPU lane",
                )
            )
            continue
        if isinstance(statement, H1Uncompute) and not _has_explicit_uncompute_witness(
            statement
        ):
            origin = _step_origin(statement, fallback_origin)
            diagnostics.append(
                _diagnostic(
                    "UNCOMPUTE_WITNESS_MISSING",
                    origin,
                    "H1 uncompute requires an explicit reversible witness",
                )
            )
            continue
        kind = _plan_step_kind(statement)
        if kind is None:
            continue
        if kind == "TerminalMeasure":
            measured = True

        if measured and kind != "TerminalMeasure":
            origin = _step_origin(statement, fallback_origin)
            diagnostics.append(
                _diagnostic(
                    "H1_MEASURE_NOT_TERMINAL",
                    origin,
                    "H1 terminal measure must be the final experiment operation",
                )
            )
            continue
        steps.append(
            H1PlanStep(
                kind=kind,
                source_tokens=tuple(statement.source_tokens),
                origin=_step_origin(statement, fallback_origin),
                characteristics=_PLAN_STEP_CHARACTERISTICS.get(kind, ()),
            )
        )

    if diagnostics:
        return None, diagnostics
    return H1StateTransformPlan(steps=tuple(steps)), diagnostics


def _coherent_control_semantic_ir(
    origin: SourceOrigin,
) -> QuantumSemanticModule:
    """Create the smallest provider-neutral semantic control witness."""

    semantic_origin = _semantic_origin(origin)
    space_id = SemanticId("space", _H1_SCOPE, 0)
    control_id = SemanticId("factor", _H1_SCOPE, 0)
    target_id = SemanticId("factor", _H1_SCOPE, 1)
    region_id = SemanticId("region", _H1_SCOPE, 0)
    space = ActingSpace(
        space_id=space_id,
        factors=(
            ActingFactor(factor_id=control_id, dimension=2, label="control"),
            ActingFactor(factor_id=target_id, dimension=2, label="target"),
        ),
        total_dimension=4,
        origin=semantic_origin,
    )
    region = CoherentControlRegion(
        region_id=region_id,
        input_value_id=SemanticId("value", _H1_SCOPE, 0),
        output_value_id=SemanticId("value", _H1_SCOPE, 1),
        input_space_id=space_id,
        output_space_id=space_id,
        validity=RegionValidity("Declared"),
        origin=semantic_origin,
        control_factor_ids=(control_id,),
        target_factor_ids=(target_id,),
    )
    return QuantumSemanticModule(
        schema_version=SCHEMA_VERSION,
        roots=(region_id,),
        region_roots=(region_id,),
        origins=(semantic_origin,),
        acting_spaces=(space,),
        regions=(region,),
        lane=SemanticLane("StaticKernel"),
    )


def _semantic_origin(origin: SourceOrigin) -> SemanticOrigin:
    """Translate Physics IR provenance into the Semantic IR provenance type."""

    return SemanticOrigin(
        source_id=origin.source_id,
        line=origin.line,
        col=origin.col,
    )


def _has_uncompute(experiment: ExperimentDecl) -> bool:
    return any(isinstance(statement, H1Uncompute) for statement in experiment.body)


def _uncompute_semantic_ir(origin: SourceOrigin) -> QuantumSemanticModule:
    semantic_origin = _semantic_origin(origin)
    resource_id = SemanticId("factor", _H1_SCOPE, 0)
    obligation = UncomputeObligation(
        obligation_id=SemanticId("uncompute_obligation", _H1_SCOPE, 0),
        resource_id=resource_id,
        witness_ref="h1.witness",
        origin=semantic_origin,
    )
    return QuantumSemanticModule(
        schema_version=SCHEMA_VERSION,
        origins=(semantic_origin,),
        uncompute_obligations=(obligation,),
        lane=SemanticLane("StaticKernel"),
    )


def _has_coherent_control(experiment: ExperimentDecl) -> bool:
    return any(
        isinstance(statement, H1CoherentControl)
        for statement in experiment.body
    )


def _operator_atoms(expression: object, origin: SourceOrigin) -> tuple[OperatorAtom, ...]:
    atoms: list[OperatorAtom] = []

    def visit(node: object) -> None:
        if isinstance(node, OpBin):
            visit(node.lhs)
            visit(node.rhs)
        elif isinstance(node, OpIndexed):
            base = node.base
            symbol = base.kind if isinstance(base, OpPauli) else type(base).__name__
            atoms.append(
                OperatorAtom(
                    symbol=str(symbol),
                    index=getattr(node.index, "name", getattr(node.index, "value", None)),
                    source_order=len(atoms),
                    origin=origin,
                )
            )
        elif isinstance(node, OpPauli):
            atoms.append(
                OperatorAtom(
                    symbol=node.kind,
                    index=node.site,
                    source_order=len(atoms),
                    origin=origin,
                )
            )
        elif isinstance(node, OpVar):
            atoms.append(
                OperatorAtom(
                    symbol=node.name,
                    index=None,
                    source_order=len(atoms),
                    origin=origin,
                )
            )

    visit(expression)
    return tuple(atoms)


def _operator_names(expression: object) -> frozenset[str]:
    """Return identifiers referenced by the parsed operator expression."""

    names: set[str] = set()

    def visit(node: object) -> None:
        if isinstance(node, OpBin):
            visit(node.lhs)
            visit(node.rhs)
        elif isinstance(node, OpIndexed):
            visit(node.base)
            visit(node.index)
        elif isinstance(node, OpPauli):
            return
        elif isinstance(node, OpVar):
            names.add(node.name)

    visit(expression)
    return frozenset(names)


def _operator_diagnostics(
    operator: H1OperatorDecl,
    origin: SourceOrigin,
) -> list[dict[str, object]]:
    referenced_names = _operator_names(operator.expression)
    used_dimensions = {
        operator.parameter_types[name]
        for name in operator.parameter_types
        if name in referenced_names
    }
    diagnostics: list[dict[str, object]] = []
    if len(used_dimensions) > 1:
        diagnostics.append(
            _diagnostic(
                "DIMENSION_MISMATCH_ERROR",
                origin,
                f"operator `{operator.name}` combines incompatible dimensions",
            )
        )
    # The binder spelling is still a lexical compatibility boundary until the
    # H1 binder AST is introduced; preserve the reviewed `sum(i, ...)` form.
    if (
        "i" in referenced_names
        and "i" not in operator.parameter_types
        and "sum" not in operator.source_tokens
    ):
        diagnostics.append(
            _diagnostic(
                "NON_HERMITIAN_OPERATOR_ERROR",
                origin,
                f"Hamiltonian `{operator.name}` is not Hermitian",
            )
        )
    return diagnostics


def _h1_basis_mismatch_diagnostics(
    theory_decl: TheoryDecl,
    experiment_decl: ExperimentDecl | None,
    origin: SourceOrigin,
) -> list[dict[str, object]]:
    """Real AST-correlated check: a state evolved under this theory's
    operator must have been `prepare`d over this theory's declared basis or
    coordinate, not merely co-occur textually with it (LISS-0326)."""

    domain_name = (
        theory_decl.basis.name
        if theory_decl.basis is not None
        else theory_decl.coordinate.name
        if theory_decl.coordinate is not None
        else None
    )
    if domain_name is None or experiment_decl is None:
        return []

    prepares = [stmt for stmt in experiment_decl.body if isinstance(stmt, H1Prepare)]
    evolves = [stmt for stmt in experiment_decl.body if isinstance(stmt, H1Evolve)]

    diagnostics: list[dict[str, object]] = []
    for evolve in evolves:
        if evolve.theory_name != theory_decl.name:
            continue
        prepare = next(
            (stmt for stmt in prepares if stmt.state_name == evolve.state_name),
            None,
        )
        bound = prepare.bound_to if prepare is not None else None
        if bound != (theory_decl.name, domain_name):
            diagnostics.append(
                _diagnostic(
                    "BASIS_MISMATCH_ERROR",
                    origin,
                    f"state carrier `{evolve.state_name}` is incompatible with "
                    f"basis/coordinate `{domain_name}` declared by theory "
                    f"`{theory_decl.name}`",
                )
            )
    return diagnostics


def _h1_target_capability_diagnostics(
    theory_decl: TheoryDecl,
    unit: object | None,
    origin: SourceOrigin,
) -> list[dict[str, object]]:
    """Real capability-registry check: a declared `coordinate ... Lattice<N>`
    site count must not exceed the named `realize qpu:<target>`'s actual
    `max_logical_qubits`, instead of matching a fixed literal (LISS-0326)."""

    if theory_decl.coordinate is None or theory_decl.coordinate.size is None:
        return []
    realize_decl = next(
        (
            declaration
            for declaration in getattr(unit, "decls", ())
            if isinstance(declaration, H1RealizeDecl)
        ),
        None,
    )
    if realize_decl is None:
        return []
    try:
        profile = FakePhysicalTargetPort().load_profile(realize_decl.target)
    except KeyError:
        return []
    if theory_decl.coordinate.size > profile.max_logical_qubits:
        return [
            _diagnostic(
                "TARGET_CAPABILITY_REJECT",
                origin,
                f"target `{realize_decl.target}` cannot realize a "
                f"{theory_decl.coordinate.size}-site H1 model",
            )
        ]
    return []


def analyze_h1_source(source: str, unit: object | None = None) -> H1Analysis:
    """Build the smallest source-backed H1 semantic snapshot."""

    theory = _THEORY.search(source)
    experiment = _EXPERIMENT.search(source)
    assert theory is not None and experiment is not None
    origin = _source_origin(source, theory)
    metadata: dict[str, str] = {
        "surface": "h1-hamiltonian-authoring",
        "theory": theory.group(1),
        "experiment": experiment.group(1),
    }

    boundary = _BOUNDARY.search(source)
    if boundary is not None:
        metadata["boundary"] = boundary.group(1)

    theory_decls = [
        declaration
        for declaration in getattr(unit, "decls", ())
        if isinstance(declaration, TheoryDecl)
    ]
    theory_decl = next(
        (declaration for declaration in theory_decls if declaration.name == theory.group(1)),
        None,
    )
    experiment_decls = [
        declaration
        for declaration in getattr(unit, "decls", ())
        if isinstance(declaration, ExperimentDecl)
    ]
    experiment_decl = next(
        (declaration for declaration in experiment_decls if declaration.name == experiment.group(1)),
        None,
    )
    nodes: list[PhysicsNode] = []
    node = PhysicsNode(
        node_id=f"h1:theory:{theory.group(1)}",
        kind="H1Theory",
        structure=("theory", theory.group(1), "operator-authoring"),
        origin=origin,
    )
    nodes.append(node)
    diagnostics: list[dict[str, object]] = []
    state_transform_plan = None
    quantum_semantic_ir = None

    if experiment_decl is not None:
        state_transform_plan, plan_diagnostics = _build_state_transform_plan(
            experiment_decl,
            origin,
        )
        diagnostics.extend(plan_diagnostics)
        if _has_coherent_control(experiment_decl):
            quantum_semantic_ir = _coherent_control_semantic_ir(origin)
        elif _has_uncompute(experiment_decl):
            quantum_semantic_ir = _uncompute_semantic_ir(origin)

    if theory_decl is not None:
        for operator in theory_decl.operators:
            diagnostics.extend(_operator_diagnostics(operator, origin))
            nodes.append(
                PhysicsNode(
                    node_id=f"h1:operator:{theory_decl.name}.{operator.name}",
                    kind="H1Operator",
                    structure=("operator", "h1", "structured"),
                    origin=origin,
                    typed_reference=operator.type_ref,
                    atoms=_operator_atoms(operator.expression, origin)
                    if operator.expression is not None
                    else (),
                )
            )

    if theory_decl is not None:
        diagnostics.extend(
            _h1_basis_mismatch_diagnostics(theory_decl, experiment_decl, origin)
        )
        diagnostics.extend(
            _h1_target_capability_diagnostics(theory_decl, unit, origin)
        )

    physics_ir = PhysicsModule(
        spaces=(),
        nodes=tuple(nodes),
        origins=(origin,),
        source_origin=origin,
        metadata=MappingProxyType(metadata),
    )
    return H1Analysis(
        diagnostics=diagnostics,
        physics_ir=physics_ir,
        state_transform_plan=state_transform_plan,
        quantum_semantic_ir=quantum_semantic_ir,
    )
