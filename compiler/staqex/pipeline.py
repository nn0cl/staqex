"""Compiler pipeline: Lexer → Parser → Early Collapse → Typecheck."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import replace
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping

from .ast_nodes import (
    Call,
    CompilationUnit,
    DiscretizationBridgeDecl,
    DiscretizationDecl,
    DynamicQpuStmt,
    ExprStmt,
    MatchStmt,
    Measure,
    MeasureExpr,
    StateBind,
    WhenExpr,
    ScientificScopeDecl,
    ScientificScopeContract,
)
from .finite_binder import IDENTITY_ACTING_SPACE_UNDETERMINED
from .early_collapse import check_early_collapse
from .lexer import Lexer
from .modules import load_module_graph, merge_modules
from .source_port import SourcePort
from .nested_when import check_nested_when
from .parser import ParseError, Parser
from .physical_axioms import check_physical_axioms
from .symbolic_ir import build_symbolic_ir
from .scientific_scopes import resolve_scientific_scopes
from .workflow_surface import WorkflowContract, resolve_workflow_contracts
from .continuous_lowering import GridHamiltonian, lower_discretization_bridges
from .discretization import DiscretizationBridge, DiscretizationContract, resolve_discretization_bridges, resolve_discretization_contracts
from .mixed_state import MixedStateContract, resolve_mixed_state_contracts
from .measurement import POVMContract, resolve_measurement_contracts
from .qpu_ir import build_qpu_ir, qpu_ir_diagnostics
from .hir import build_hir
from .physics_ir import PhysicsModule
from .h1_authoring import H1PlanStep, H1StateTransformPlan
from .physics_ir import SourceOrigin
from .physics_ir_lower import lower_hir_to_physics_ir, verify_lowered_physics_ir
from .quantum_semantic_ir import (
    QuantumSemanticInput,
    QuantumSemanticModule,
    ProjectorRegion,
    TimingRegion,
    DynamicMeasurementRegion,
    DynamicControlRegion,
    ActingFactor,
    ActingSpace,
    RegionValidity,
    SemanticId,
    SemanticOrigin,
    lower_physics_to_quantum_semantic_ir,
)
from .typecheck import TypeChecker
from .unitarity_check import check_unitarity

HARD_CODES = {
    "FORBIDDEN_KEYWORD",
    "RETIRED_KEYWORD",
    "RETIRED_OPERATOR_INDEX_SYNTAX",
    "EARLY_COLLAPSE_ERROR",
    "NESTED_WHEN_ERROR",
    "INTERFER_INDEPENDENT_STATE_ERROR",
    "EXPECT_CLASSICAL_ONLY_ERROR",
    "TYPE_MISMATCH",
    "COIN_IN_EVOLVE_ERROR",
    "NON_UNITARY_TRANSFORM_ERROR",
    "PREDICATE_PROJECTOR_ERROR",
    "CANNOT_MEASURE_CLASSICAL_VALUE_ERROR",
    "COEFFICIENT_IN_QUANTUM_POSITION",
    "PARSE_ERROR",
    "LEX_ERROR",
    "TYPE_NOT_STATE",
    "DIMENSION_MISMATCH_ERROR",
    "LOCAL_DIMENSION_TYPE_ERROR",
    "UNSUPPORTED_LOCAL_DIMENSION",
    "TOPLEVEL_EXECUTION_ERROR",
    "PRODUCT_BIND_ERROR",
    "PRODUCT_ARITY_ERROR",
    "PRODUCT_TYPE_MISMATCH",
    "MODULE_NOT_FOUND_ERROR",
    "MODULE_CYCLE_ERROR",
    "IMMUTABLE_ASSIGNMENT_ERROR",
    "ENUM_TYPE_MISMATCH",
    "WHEN_NONEXHAUSTIVE",
    "ACCESS_CONTROL_VIOLATION_ERROR",
    "PRIVATE_ACCESS_VIOLATION_ERROR",
    "MODULE_PRIVATE_ACCESS_ERROR",
    "MAIN_RETURN_ERROR",
    "RETURN_NOT_TERMINAL",
    "MISSING_RETURN_STATEMENT",
    "INIT_RETURN_ERROR",
    "LEXICAL_SCOPE_ERROR",
    "PACKAGE_NOT_EXPORTED_ERROR",
    "MAIN_RETURN_TYPE_ERROR",
    "MISSING_RETURN_TYPE",
    "MAIN_RESULT_ERROR",
    "RETURN_TYPE_MISMATCH",
    "MISSING_RETURN_VALUE",
    "MEASURE_IN_FUNCTION_ERROR",
    "SNAPSHOT_IN_FUNCTION_ERROR",
    "HOST_TYPE_IN_KERNEL_ERROR",
    "UNSUPPORTED_QPEX_VERSION",
    "FOR_EACH_DYNAMIC_BOUND_ERROR",
    "FOR_EACH_MEASURE_ERROR",
    "QPU_CLASSICAL_CONTROL_ERROR",
    "PARAMETER_CONTROL_ERROR",
    "PARAMETER_TYPE_ERROR",
    "STATIC_REGISTER_TYPE_ERROR",
    "STATIC_HILBERT_SURFACE_ERROR",
    "STATIC_HILBERT_RESOURCE_ERROR",
    "QFT_REGISTER_TYPE_ERROR",
    "QFT_RESOURCE_ERROR",
    "EVOLVE_UNTIL_BOUND_ERROR",
    "EVOLVE_UNTIL_EFFECT_ERROR",
    "EVOLVE_UNTIL_MAX_STEPS_ERROR",
    "PIPE_EFFECT_ERROR",
    "PIPE_CALLABLE_ERROR",
    "PIPE_TYPE_ERROR",
    "EFFECT_DECLARATION_ERROR",
    "EFFECT_VIOLATION_ERROR",
    "EFFECT_MEASURE_RETURN_ERROR",
    "IMPL_COHERENCE_ERROR",
    "IMPL_VISIBILITY_ERROR",
    "SYSTEM_EXPRESSION_ERROR",
    "SUZUKI_ORDER_ERROR",
    "SUZUKI_POLICY_ERROR",
    "DYNAMIC_CAPABILITY_REQUIRED_ERROR",
    "DYNAMIC_UNSUPPORTED_FEATURE_ERROR",
    "SEMANTIC_CARRIER_MISMATCH_ERROR",
    "PHASE_TYPE_VISIBILITY_ERROR",
    "SEMANTIC_CARRIER_OPERATION_ERROR",
    "BINDER_RESOURCE_ERROR",
    "MATHEMATICAL_BINDER_EFFECT_ERROR",
    "BINDER_DOMAIN_ERROR",
    "BINDER_INDEX_OUT_OF_BOUNDS",
    "BINDER_LOWERING_UNSUPPORTED",
    "BINDER_GUARD_UNSUPPORTED",
    "BINDER_GUARD_TYPE_ERROR",
    "BINDER_GUARD_SCOPE_ERROR",
    IDENTITY_ACTING_SPACE_UNDETERMINED,
    "OPERATOR_ALGEBRA_TYPE_ERROR",
    "OPERATOR_DOMAIN_ERROR",
    "SECOND_QUANTIZATION_TYPE_ERROR",
    "FERMION_MAPPING_REQUIRED_ERROR",
    "SECOND_QUANTIZATION_MAPPING_UNSUPPORTED",
    "PHASE_SCOPE_DEPENDENCY_ERROR",
    "PHASE_SCOPE_CYCLE_ERROR",
    "PHASE_SCOPE_DIRECTION_ERROR",
    "PHASE_SCOPE_REFERENCE_ERROR",
    "WORKFLOW_SURFACE_ERROR",
    "DISCRETIZATION_REQUIRED_ERROR",
    "DISCRETIZATION_CONTRACT_ERROR",
    "DISCRETIZATION_BRIDGE_ERROR",
    "DISCRETIZATION_LOWERING_ERROR",
    "MIXED_STATE_TYPE_ERROR",
    "MALFORMED_DENSITY_STATE",
    "INCOMPLETE_KRAUS_CHANNEL",
    "INVALID_LINDBLAD_JUMP_SET",
    "LINDBLAD_JUMP_DIMENSION_ERROR",
    "SYMBOLIC_JUMP_LOWERING_REQUIRED",
    "POVM_DOMAIN_MISMATCH",
    "INVALID_POVM_EFFECT",
    "INCOMPLETE_POVM",
    "MID_CIRCUIT_MEASUREMENT_REQUIRES_DYNAMIC_LANE",
    "OBSERVATION_CAPABILITY_UNSUPPORTED",
    # LISS-0114 Slice A: linear-use diagnostics hard-fail the compile.
    "LINEAR_DUPLICATE_USE",
    "LINEAR_IMPLICIT_DISCARD",
    "UNCOMPUTE_WITNESS_MISSING",
    # LISS-0200: was hard only in run.py; now single source of truth.
    "CONFIG_HARVEST_COLLISION_ERROR",
    "BASIS_MISMATCH_ERROR",
    "TARGET_CAPABILITY_REJECT",
    "NON_HERMITIAN_OPERATOR_ERROR",
    "H1_MEASURE_NOT_TERMINAL",
    # LISS-0322 / ADR 0192: closed constraint-predicate vocabulary.
    "S02_UNKNOWN_CONSTRAINT_PREDICATE",
    # LISS-0329: reject a repeated predicate name in feasible(...).
    "S02_DUPLICATE_CONSTRAINT_PREDICATE",
    # LISS-0381 / ADR 0193: malformed `dynamic qpu within …` timing clause.
    "DYNAMIC_TIMING_INTENT_MALFORMED",
}

# Backward-compatible alias (older docs / local patches).
_HARD_CODES = HARD_CODES


@dataclass
class CompileResult:
    unit: CompilationUnit | None
    diagnostics: list[dict[str, Any]]
    checker: TypeChecker | None = None
    symbolic_ir: dict[str, Any] | None = None
    scope_contracts: Mapping[str, ScientificScopeContract] | None = None
    workflow_contracts: Mapping[str, WorkflowContract] | None = None
    discretization_contracts: Mapping[str, DiscretizationContract] | None = None
    discretization_bridges: Mapping[str, DiscretizationBridge] | None = None
    grid_hamiltonians: Mapping[str, GridHamiltonian] | None = None
    mixed_state_contracts: Mapping[str, MixedStateContract] | None = None
    povm_contracts: Mapping[str, POVMContract] | None = None
    qpu_ir: Mapping[str, Any] | None = None
    physics_ir: PhysicsModule | None = None
    quantum_semantic_ir: QuantumSemanticModule | None = None
    state_transform_plan: H1StateTransformPlan | None = None

    @property
    def ok(self) -> bool:
        return not any(d.get("code") in HARD_CODES for d in self.diagnostics)


def _soft_physics_ir(
    hir: Any,
    unit: CompilationUnit,
) -> tuple[PhysicsModule, list[dict[str, Any]]]:
    """Lower HIR to Physics IR for CompileResult; diagnostics stay non-hard."""

    physics_ir = lower_hir_to_physics_ir(hir, unit=unit)
    return physics_ir, list(verify_lowered_physics_ir(physics_ir))


def _soft_quantum_semantic_input(
    physics_ir: PhysicsModule,
) -> QuantumSemanticInput:
    """Slice F soft-wire input: Physics IR only; never invent finite carriers."""

    return QuantumSemanticInput(
        physics_module=physics_ir,
        finite_carrier_evidence=(),
        linear_resource_evidence=(),
        lane="StaticKernel",
        exactness=(),
    )


def _soft_quantum_semantic_ir(
    physics_ir: PhysicsModule,
) -> tuple[QuantumSemanticModule, list[dict[str, Any]]]:
    """Lower Physics IR to Quantum Semantic IR; QSEM_* diagnostics stay non-hard."""

    result = lower_physics_to_quantum_semantic_ir(
        _soft_quantum_semantic_input(physics_ir)
    )
    return result.module, list(result.diagnostics)


def _surface_transform_plan(unit: CompilationUnit) -> H1StateTransformPlan | None:
    """Expose the reviewed transform categories for ordinary Kernel programs."""

    main = unit.main
    if main is None:
        return None
    steps: list[H1PlanStep] = []

    def origin(span: Any) -> SourceOrigin:
        return SourceOrigin(source_id="sqx", line=span.line, col=span.col)

    def visit_expr(expr: Any) -> None:
        if isinstance(expr, WhenExpr):
            steps.append(
                H1PlanStep(
                    kind="Mixture",
                    source_tokens=("mix",),
                    origin=origin(expr.span),
                )
            )
            visit_expr(expr.ctrl)
            for arm in expr.arms:
                visit_expr(arm.body)
            return
        if isinstance(expr, Call):
            callee = expr.callee
            if hasattr(callee, "name") and callee.name == "controlled":
                steps.append(
                    H1PlanStep(
                        kind="CoherentControl",
                        source_tokens=("controlled",),
                        origin=origin(expr.span),
                        characteristics=("Unitary", "Ctl"),
                    )
                )
            elif hasattr(callee, "name") and callee.name == "project":
                steps.append(
                    H1PlanStep(
                        kind="Projector",
                        source_tokens=("project", "onto"),
                        origin=origin(expr.span),
                    )
                )
            for arg in expr.args:
                visit_expr(arg)
            for _, value in expr.kwargs or ():
                visit_expr(value)
            return
    for statement in main.body.stmts:
        if isinstance(statement, StateBind):
            visit_expr(statement.expr)
        elif isinstance(statement, ExprStmt):
            visit_expr(statement.expr)
        elif isinstance(statement, Measure):
            steps.append(
                H1PlanStep(
                    kind="TerminalMeasure",
                    source_tokens=("measure",),
                    origin=origin(statement.span),
                )
            )
    return H1StateTransformPlan(steps=tuple(steps)) if steps else None


# LISS-0322 / ADR 0192 Decision 2: closed constraint-predicate vocabulary.
# Extending this set is a future ADR amendment, not a silent addition.
_S02_KNOWN_CONSTRAINT_PREDICATES = frozenset(
    {"exactly_selected", "pairwise_compatible", "diversity_at_least"}
)


def _append_selection_projector_region(
    unit: CompilationUnit,
    module: QuantumSemanticModule,
) -> tuple[QuantumSemanticModule, list[dict[str, Any]]]:
    """Retain an explicit S02 Projector witness in the semantic boundary.

    ADR 0192: `constraint_ref` is derived from the actual recognized
    predicate names in the `project ... onto feasible(...)` target, not a
    hardcoded literal. An unrecognized predicate name -- or a target that is
    not a call to `feasible` at all -- is a S02_UNKNOWN_CONSTRAINT_PREDICATE
    diagnostic, not silent acceptance into a generic region.
    """

    diagnostics: list[dict[str, Any]] = []
    predicate_names: set[str] = set()
    has_projector = False

    def visit(expr: Any) -> None:
        nonlocal has_projector
        if isinstance(expr, Call):
            if hasattr(expr.callee, "name") and expr.callee.name == "project":
                has_projector = True
                if len(expr.args) >= 2:
                    _collect_feasible_predicates(expr.args[1], diagnostics, predicate_names)
            for arg in expr.args:
                visit(arg)
            for _, value in expr.kwargs or ():
                visit(value)
        elif isinstance(expr, WhenExpr):
            visit(expr.ctrl)
            for arm in expr.arms:
                visit(arm.body)

    if unit.main is None:
        return module, diagnostics
    for statement in unit.main.body.stmts:
        if isinstance(statement, StateBind):
            visit(statement.expr)
    if not has_projector:
        return module, diagnostics
    if diagnostics:
        # An unrecognized predicate was found: fail closed, no region.
        return module, diagnostics

    origin = SemanticOrigin(source_id="sqx", line=1, col=1)
    space_id = SemanticId("space", "s02", len(module.acting_spaces))
    input_id = SemanticId("value", "s02", len(module.values))
    output_id = SemanticId("value", "s02", len(module.values) + 1)
    region_id = SemanticId("region", "s02", len(module.regions))
    space = ActingSpace(
        space_id=space_id,
        factors=(
            ActingFactor(
                factor_id=SemanticId("factor", "s02", 0),
                dimension=2,
                label="selection",
            ),
        ),
        total_dimension=2,
        origin=origin,
    )
    constraint_ref = "S02.feasible:" + ",".join(sorted(predicate_names))
    region = ProjectorRegion(
        region_id=region_id,
        input_value_id=input_id,
        output_value_id=output_id,
        input_space_id=space_id,
        output_space_id=space_id,
        validity=RegionValidity("Declared"),
        origin=origin,
        constraint_ref=constraint_ref,
    )
    return (
        replace(
            module,
            roots=module.roots + (region_id,),
            region_roots=module.region_roots + (region_id,),
            origins=module.origins + (origin,),
            acting_spaces=module.acting_spaces + (space,),
            regions=module.regions + (region,),
        ),
        diagnostics,
    )


def _append_dynamic_timing_regions(
    unit: CompilationUnit,
    module: QuantumSemanticModule,
) -> QuantumSemanticModule:
    """Retain ADR 0193 TimingRegion witnesses for `dynamic qpu within <name>`.

    One TimingRegion per DynamicQpuStmt that carries a non-None timing_intent.
    Absent `within` produces no TimingRegion. The dynamic lane remains
    non-executable; this is inspectable provenance only.
    """
    if unit.main is None:
        return module

    added_regions: list[TimingRegion] = []
    added_spaces: list[ActingSpace] = []
    added_origins: list[SemanticOrigin] = []
    added_roots: list[SemanticId] = []
    region_index = len(module.regions)
    space_index = len(module.acting_spaces)
    value_index = len(module.values)

    for statement in unit.main.body.stmts:
        if not isinstance(statement, DynamicQpuStmt) or not statement.timing_intent:
            continue
        space, region, origin = _make_timing_region_witness(
            timing_intent=statement.timing_intent,
            span_line=statement.span.line,
            span_col=statement.span.col,
            region_index=region_index,
            space_index=space_index,
            value_index=value_index,
        )
        added_regions.append(region)
        added_spaces.append(space)
        added_origins.append(origin)
        added_roots.append(region.region_id)
        region_index += 1
        space_index += 1
        value_index += 2

    if not added_regions:
        return module

    return replace(
        module,
        roots=module.roots + tuple(added_roots),
        region_roots=module.region_roots + tuple(added_roots),
        origins=module.origins + tuple(added_origins),
        acting_spaces=module.acting_spaces + tuple(added_spaces),
        regions=module.regions + tuple(added_regions),
    )


def _make_timing_region_witness(
    *,
    timing_intent: str,
    span_line: int,
    span_col: int,
    region_index: int,
    space_index: int,
    value_index: int,
) -> tuple[ActingSpace, TimingRegion, SemanticOrigin]:
    """Build one Declared TimingRegion + placeholder acting space."""
    origin = SemanticOrigin(source_id="sqx", line=span_line, col=span_col)
    space_id = SemanticId("space", "dyn_timing", space_index)
    input_id = SemanticId("value", "dyn_timing", value_index)
    output_id = SemanticId("value", "dyn_timing", value_index + 1)
    region_id = SemanticId("region", "dyn_timing", region_index)
    space = ActingSpace(
        space_id=space_id,
        factors=(
            ActingFactor(
                factor_id=SemanticId("factor", "dyn_timing", space_index),
                dimension=2,
                label="dynamic_timing",
            ),
        ),
        total_dimension=2,
        origin=origin,
    )
    region = TimingRegion(
        region_id=region_id,
        input_value_id=input_id,
        output_value_id=output_id,
        input_space_id=space_id,
        output_space_id=space_id,
        validity=RegionValidity("Declared"),
        origin=origin,
        timing_intent=timing_intent,
    )
    return space, region, origin


def _append_dynamic_mid_circuit_regions(
    unit: CompilationUnit,
    module: QuantumSemanticModule,
) -> QuantumSemanticModule:
    """Retain ADR 0197 mid-circuit / feed-forward QSem witnesses.

    Source form inside `dynamic qpu`:
      Controller<Bit> bit = measure q
      match bit { 0 => { … } 1 => { … } }

    Emits DynamicMeasurementRegion and (when match is present)
    DynamicControlRegion paired by measurement_region_id. Capability
    rejection remains in typecheck; this is inspectable provenance only.
    """
    if unit.main is None:
        return module

    added_regions: list[DynamicMeasurementRegion | DynamicControlRegion] = []
    added_spaces: list[ActingSpace] = []
    added_origins: list[SemanticOrigin] = []
    added_roots: list[SemanticId] = []
    next_region = len(module.regions)
    next_space = len(module.acting_spaces)
    next_value = len(module.values)
    next_token = 0

    for statement in unit.main.body.stmts:
        if not isinstance(statement, DynamicQpuStmt):
            continue
        controller_measurements: dict[str, DynamicMeasurementRegion] = {}
        for body_stmt in statement.body.stmts:
            bind_name = _controller_measure_bind_name(body_stmt)
            if bind_name is not None:
                space, measurement, origin = _make_dynamic_measurement_witness(
                    span_line=body_stmt.span.line,
                    span_col=body_stmt.span.col,
                    region_index=next_region,
                    space_index=next_space,
                    value_index=next_value,
                    token_index=next_token,
                )
                controller_measurements[bind_name] = measurement
                added_regions.append(measurement)
                added_spaces.append(space)
                added_origins.append(origin)
                added_roots.append(measurement.region_id)
                next_region += 1
                next_space += 1
                next_value += 2
                next_token += 1
                continue

            if not isinstance(body_stmt, MatchStmt):
                continue
            measurement = controller_measurements.get(body_stmt.scrutinee)
            if measurement is None:
                continue
            control, control_origin = _make_dynamic_control_witness(
                measurement=measurement,
                span_line=body_stmt.span.line,
                span_col=body_stmt.span.col,
                region_index=next_region,
                value_index=next_value,
            )
            added_regions.append(control)
            added_origins.append(control_origin)
            added_roots.append(control.region_id)
            next_region += 1
            next_value += 1

    if not added_regions:
        return module

    return replace(
        module,
        roots=module.roots + tuple(added_roots),
        region_roots=module.region_roots + tuple(added_roots),
        origins=module.origins + tuple(added_origins),
        acting_spaces=module.acting_spaces + tuple(added_spaces),
        regions=module.regions + tuple(added_regions),
    )


def _controller_measure_bind_name(statement: object) -> str | None:
    """Return the Controller name for `Controller<…> name = measure …`, else None."""
    if not isinstance(statement, StateBind):
        return None
    if statement.ty is None or statement.ty.name != "Controller":
        return None
    if not isinstance(statement.expr, MeasureExpr):
        return None
    if not statement.names:
        return None
    return statement.names[0]


def _make_dynamic_measurement_witness(
    *,
    span_line: int,
    span_col: int,
    region_index: int,
    space_index: int,
    value_index: int,
    token_index: int,
) -> tuple[ActingSpace, DynamicMeasurementRegion, SemanticOrigin]:
    """Build one DynamicMeasurementRegion + placeholder acting space."""
    origin = SemanticOrigin(source_id="sqx", line=span_line, col=span_col)
    space_id = SemanticId("space", "dyn_mid", space_index)
    input_id = SemanticId("value", "dyn_mid", value_index)
    post_id = SemanticId("value", "dyn_mid", value_index + 1)
    region_id = SemanticId("region", "dyn_mid", region_index)
    token_id = SemanticId("dynamic_token", "dyn_mid", token_index)
    # Placeholder branch slots kept finite for correlation metadata.
    branch_ids = (
        SemanticId("region", "dyn_mid_branch", region_index * 2),
        SemanticId("region", "dyn_mid_branch", region_index * 2 + 1),
    )
    space = ActingSpace(
        space_id=space_id,
        factors=(
            ActingFactor(
                factor_id=SemanticId("factor", "dyn_mid", space_index),
                dimension=2,
                label="dynamic_mid_circuit",
            ),
        ),
        total_dimension=2,
        origin=origin,
    )
    region = DynamicMeasurementRegion(
        region_id=region_id,
        input_value_id=input_id,
        post_measure_value_id=post_id,
        input_space_id=space_id,
        output_space_id=space_id,
        token_id=token_id,
        outcome_domain=("0", "1"),
        branch_region_ids=branch_ids,
        required_capability="DynamicMeasurementFeedback",
        origin=origin,
    )
    return space, region, origin


def _make_dynamic_control_witness(
    *,
    measurement: DynamicMeasurementRegion,
    span_line: int,
    span_col: int,
    region_index: int,
    value_index: int,
) -> tuple[DynamicControlRegion, SemanticOrigin]:
    """Build one DynamicControlRegion paired to a measurement witness."""
    origin = SemanticOrigin(source_id="sqx", line=span_line, col=span_col)
    # Reuse the measurement's branch ids so the pair stays correlated.
    control = DynamicControlRegion(
        region_id=SemanticId("region", "dyn_mid", region_index),
        measurement_region_id=measurement.region_id,
        post_measure_value_id=measurement.post_measure_value_id,
        token_id=measurement.token_id,
        branch_region_ids=measurement.branch_region_ids,
        merge_region_id=SemanticId("region", "dyn_mid_merge", region_index),
        output_value_id=SemanticId("value", "dyn_mid", value_index),
        origin=origin,
    )
    return control, origin


def _collect_feasible_predicates(
    target: Any,
    diagnostics: list[dict[str, Any]],
    predicate_names: set[str],
) -> None:
    """Validate a `project ... onto <target>` target against ADR 0192's
    closed predicate vocabulary, recording unknown names as a fail-closed
    diagnostic instead of silently accepting them."""

    if not (isinstance(target, Call) and hasattr(target.callee, "name")):
        diagnostics.append(
            {
                "code": "S02_UNKNOWN_CONSTRAINT_PREDICATE",
                "line": target.span.line,
                "col": target.span.col,
                "message": "`project ... onto` target is not a recognized "
                "constraint predicate call",
            }
        )
        return
    if target.callee.name != "feasible":
        diagnostics.append(
            {
                "code": "S02_UNKNOWN_CONSTRAINT_PREDICATE",
                "line": target.span.line,
                "col": target.span.col,
                "message": f"`{target.callee.name}` is not a recognized "
                "constraint predicate wrapper; expected `feasible(...)`",
            }
        )
        return
    for name, _value in target.kwargs or ():
        if name not in _S02_KNOWN_CONSTRAINT_PREDICATES:
            diagnostics.append(
                {
                    "code": "S02_UNKNOWN_CONSTRAINT_PREDICATE",
                    "line": target.span.line,
                    "col": target.span.col,
                    "message": f"`{name}` is not a recognized S02 "
                    "constraint predicate (expected one of "
                    f"{sorted(_S02_KNOWN_CONSTRAINT_PREDICATES)})",
                }
            )
            continue
        if name in predicate_names:
            diagnostics.append(
                {
                    "code": "S02_DUPLICATE_CONSTRAINT_PREDICATE",
                    "line": target.span.line,
                    "col": target.span.col,
                    "message": f"`{name}` is given more than once in "
                    "`feasible(...)`",
                }
            )
            continue
        predicate_names.add(name)


def _soft_lane_diagnostics(unit: CompilationUnit) -> list[dict[str, Any]]:
    """ADR 0178: soft warn when circuit constructs appear under experiment lane."""
    from .ast_nodes import ForEachStmt

    lane = unit.lane or "experiment"
    if lane == "circuit":
        return []
    out: list[dict[str, Any]] = []

    def walk_block(block: Any) -> None:
        if block is None:
            return
        for stmt in getattr(block, "stmts", []) or []:
            if isinstance(stmt, ForEachStmt):
                out.append(
                    {
                        "code": "LANE_SOFT_CIRCUIT_IN_EXPERIMENT",
                        "line": getattr(stmt.span, "line", 1),
                        "col": getattr(stmt.span, "col", 1),
                        "message": (
                            "`forEach` is a circuit-lane construct; mark the source "
                            "with `// staqex-lane: circuit` (ADR 0178 soft diagnostic)"
                        ),
                    }
                )
            body = getattr(stmt, "body", None)
            if body is not None:
                walk_block(body)

    if unit.main is not None:
        walk_block(unit.main.body)
    return out


def _analyze_unit(unit: CompilationUnit, diags: list[dict[str, Any]]) -> CompileResult:
    diags.extend(check_early_collapse(unit))
    diags.extend(check_nested_when(unit))
    diags.extend(check_physical_axioms(unit))
    diags.extend(check_unitarity(unit))
    diags.extend(_soft_lane_diagnostics(unit))

    checker = TypeChecker()
    diags.extend(checker.check_unit(unit))
    scope_decls = tuple(
        declaration
        for declaration in unit.decls
        if isinstance(declaration, ScientificScopeDecl)
    )
    scope_contracts, scope_diags = resolve_scientific_scopes(
        scope_decls,
        unit_decls=unit.decls,
    )
    diags.extend(scope_diags)
    workflow_contracts, workflow_diags = resolve_workflow_contracts(
        scope_decls
    )
    diags.extend(workflow_diags)
    discretization_contracts, discretization_diags = resolve_discretization_contracts(
        tuple(
            declaration
            for declaration in unit.decls
            if isinstance(declaration, DiscretizationDecl)
        )
    )
    diags.extend(discretization_diags)
    discretization_bridges, bridge_diags = resolve_discretization_bridges(
        tuple(
            declaration
            for declaration in unit.decls
            if isinstance(declaration, DiscretizationBridgeDecl)
        ),
        discretization_contracts,
        tuple(
            declaration
            for declaration in unit.decls
            if isinstance(declaration, ScientificScopeDecl)
        ),
    )
    diags.extend(bridge_diags)
    grid_hamiltonians, lowering_diags = lower_discretization_bridges(
        discretization_bridges,
        discretization_contracts,
        tuple(
            declaration
            for declaration in unit.decls
            if isinstance(declaration, ScientificScopeDecl)
        ),
    )
    diags.extend(lowering_diags)
    mixed_state_contracts, mixed_state_diags = resolve_mixed_state_contracts(unit)
    diags.extend(mixed_state_diags)
    povm_contracts, povm_diags = resolve_measurement_contracts(unit)
    diags.extend(povm_diags)

    symbolic_ir = build_symbolic_ir(unit)
    diags.extend(qpu_ir_diagnostics(unit))
    qpu_ir = build_qpu_ir(unit, symbolic_ir)

    # LISS-0114 Slice A: fold HirLinearVerifier into compile diagnostics.
    hir = build_hir(
        checker,
        scope_contracts=MappingProxyType(scope_contracts),
        unit=unit,
    )
    diags.extend(hir.linear_diagnostics)

    physics_ir, physics_diags = _soft_physics_ir(hir, unit)
    diags.extend(physics_diags)
    quantum_semantic_ir, qsem_diags = _soft_quantum_semantic_ir(physics_ir)
    diags.extend(qsem_diags)
    quantum_semantic_ir, projector_diags = _append_selection_projector_region(
        unit, quantum_semantic_ir
    )
    diags.extend(projector_diags)
    quantum_semantic_ir = _append_dynamic_timing_regions(unit, quantum_semantic_ir)
    quantum_semantic_ir = _append_dynamic_mid_circuit_regions(
        unit, quantum_semantic_ir
    )

    return CompileResult(
        unit=unit,
        diagnostics=diags,
        checker=checker,
        symbolic_ir=symbolic_ir,
        scope_contracts=MappingProxyType(scope_contracts),
        workflow_contracts=MappingProxyType(workflow_contracts),
        discretization_contracts=MappingProxyType(discretization_contracts),
        discretization_bridges=MappingProxyType(discretization_bridges),
        grid_hamiltonians=MappingProxyType(grid_hamiltonians),
        mixed_state_contracts=MappingProxyType(mixed_state_contracts),
        povm_contracts=MappingProxyType(povm_contracts),
        qpu_ir=qpu_ir,
        physics_ir=physics_ir,
        quantum_semantic_ir=quantum_semantic_ir,
        state_transform_plan=_surface_transform_plan(unit),
    )


def compile_source(source: str) -> CompileResult:
    from .experiment_profile import detect_lane, has_experiment_profile
    from .h1_authoring import analyze_h1_source, is_h1_unit

    lexer = Lexer(source)
    tokens, lex_diags = lexer.tokenize()
    diags: list[dict[str, Any]] = list(lex_diags)

    unit: CompilationUnit | None = None
    try:
        parser = Parser(
            tokens,
            experiment_profile=has_experiment_profile(source),
        )
        unit = parser.parse()
        diags.extend(parser.diagnostics)
    except ParseError as e:
        diags.append(
            {
                "code": getattr(e, "code", None) or "PARSE_ERROR",
                "line": e.line,
                "col": e.col,
                "message": e.message,
            }
        )
        return CompileResult(unit=None, diagnostics=diags)

    if unit is not None:
        unit.lane = detect_lane(source)
        if is_h1_unit(unit):
            analysis = analyze_h1_source(source, unit=unit)
            return CompileResult(
                unit=unit,
                diagnostics=diags + analysis.diagnostics,
                symbolic_ir={"surface": "h1-hamiltonian-authoring"},
                physics_ir=analysis.physics_ir,
                state_transform_plan=analysis.state_transform_plan,
                quantum_semantic_ir=analysis.quantum_semantic_ir,
            )
    return _analyze_unit(unit, diags)


def compile_path(
    entry: str | Path,
    *,
    source_port: SourcePort | None = None,
) -> CompileResult:
    """Compile an entry `.sqx` file with ADR 0054 user-module import linking."""
    path = Path(entry)
    graph = load_module_graph(path, source_port=source_port)
    diags: list[dict[str, Any]] = list(graph.diagnostics)
    if any(d.get("code") in _HARD_CODES for d in diags):
        return CompileResult(unit=None, diagnostics=diags)

    unit = merge_modules(path.resolve(), graph)
    diags = list(graph.diagnostics)
    if unit is None:
        diags.append(
            {
                "code": "MODULE_NOT_FOUND_ERROR",
                "line": 1,
                "col": 1,
                "message": f"failed to merge modules for {path}",
            }
        )
        return CompileResult(unit=None, diagnostics=diags)

    if any(d.get("code") in _HARD_CODES for d in diags):
        return CompileResult(unit=unit, diagnostics=diags, checker=None)

    return _analyze_unit(unit, diags)


def analyze_source(source: str) -> list[dict[str, Any]]:
    """Drop-in for spec-verification compile_gate (same diagnostic dict shape)."""
    return compile_source(source).diagnostics
