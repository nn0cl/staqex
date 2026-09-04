"""Kernel evaluator — AST → Joint transformers + terminal measure."""

from __future__ import annotations

import cmath
import random
from dataclasses import dataclass, field, replace
from fractions import Fraction
from typing import TYPE_CHECKING, Any, Callable, Mapping, TextIO

if TYPE_CHECKING:
    from ..scientific_semantic_ir import ScientificSemanticIR

from ..continuous_field import (
    ContinuousFieldPort,
    ContinuousFieldValue,
    continuous_pipeline_ops,
)
from ..host_input_port import HostInputPort
from ..measure_sink_port import (
    MeasureSinkPort,
    TextIOMeasureSinkAdapter,
    resolve_measure_sink,
)
from ..rng_port import RngPort, StdlibRngAdapter
from ..ast_nodes import (
    AssignStmt,
    Attr,
    BinOp,
    BlockExpr,
    Call,
    ClassDecl,
    Coin,
    CompilationUnit,
    Dirac,
    DynamicQpuStmt,
    EnumDecl,
    EvolveExpr,
    Expr,
    ExprStmt,
    FunDecl,
    ForEachStmt,
    Hole,
    Inspect,
    KetLit,
    KetSumBinder,
    Lambda,
    LitBool,
    LitFloat,
    LitInt,
    LitString,
    ListExpr,
    MatchStmt,
    Measure,
    MeasureExpr,
    NormExpr,
    SetComprehension,
    OpBin,
    OpHop,
    OpLit,
    OpNumber,
    OpQuadrature,
    OpGridQuad,
    OpPauli,
    OpPow,
    OpVar,
    OpAttr,
    OpIndexed,
    OpBinder,
    OpIdentity,
    OpCall,
    Pipe,
    ResetStmt,
    ReturnStmt,
    Snapshot,
    Span,
    StateBind,
    StructDecl,
    TensorExpr,
    TupleExpr,
    UnitConvert,
    Vacuum,
    Var,
    WhenExpr,
    SuperposeExpr,
    UnaryNot,
)
from ..continuous_lowering import GridHamiltonian, GridHamiltonianRef
from ..finite_binder import operator_declared_space
from ..second_quantization import SecondQuantizationMappingError, resolve_mapping_expr
from ..stdlib import math_ops
from ..stdlib.io_ops import format_marginal_table, format_snapshot_csv
from .op_attr_elaboration import (
    OpAttrElaborationError,
    materialize_op_attrs,
    materialize_op_scalar_vars,
)
from .joint import EPS, Joint, sample_from_marginal
from .mixed_state import DensityStateValue, density_from_call, matrix_from_list
from .lindblad import evolve_lindblad
from .matrix import Matrix
from ..static_hilbert import MVP_MAX_LOGICAL_QUBITS
from ..kernel_literals import SECOND_QUANTIZED_FAMILIES as _SECOND_QUANTIZED_FAMILIES
from ..scientific_vocabulary import resolve_scientific_binding


@dataclass(frozen=True)
class EnumValue:
    """Runtime enum tag (ADR OOP)."""

    enum_name: str
    variant: str

    def __repr__(self) -> str:
        return f"{self.enum_name}.{self.variant}"


@dataclass
class StructValue:
    """Immutable value-type instance (copy-on-pass)."""

    struct_name: str
    fields: dict[str, Any]
    # ADR 0174: optional unit suffix per dimful field (parallel to scalar_units).
    field_units: dict[str, str] = field(default_factory=dict)

    def copy(self) -> "StructValue":
        return StructValue(
            struct_name=self.struct_name,
            fields={
                k: (v.copy() if isinstance(v, StructValue) else v)
                for k, v in self.fields.items()
            },
            field_units=dict(self.field_units),
        )


@dataclass
class ClassInstance:
    """Runtime object for ADR 0056 class instances (reference semantics)."""

    class_name: str
    fields: dict[str, Any]
    mutable: set[str] = field(default_factory=set)
    # ADR 0174: optional unit suffix per dimful field.
    field_units: dict[str, str] = field(default_factory=dict)


@dataclass
class PartialValue:
    """Immutable partial application (ADR 0123); ``None`` slots are holes."""

    fun_name: str
    slots: list[Expr | None]


@dataclass
class MeasureResult:
    value: Any | None
    vacuum: bool
    marginal: dict[Any, float]
    rng_calls: int
    sink: str | None = None
    output: str = ""


@dataclass
class EvalResult:
    joint: Joint
    measure: MeasureResult | None = None
    rng_calls_before_measure: int = 0
    logs: list[str] = field(default_factory=list)
    mixed_state_measured: bool = False
    execution_lane: str | None = None
    measurement_kind: str | None = None
    # ADR 0140: main body used measure-batched StateBind materialization.
    deferred_pushforward: bool = False
    deferred_binds_applied: int = 0
    # ADR 0141 / 0157: last algebraic pipe collapse evidence (if any).
    last_algebraic_fusion: tuple[float, float] | None = None
    last_poly_fusion: tuple[float, ...] | None = None
    # ADR 0159: CPU data-parallel world workers used for this run (1 = sequential).
    data_parallel_workers: int = 1
    # LISS-0389 (ADR 0198 Amendment): False when a dynamic-lane mid-circuit
    # collapse found a recorded controller binding physically unreachable
    # (the run vacuumed). True (default) when unchecked or all confirmed.
    dynamic_outcomes_confirmed: bool = True
    evolution_provenance: dict[str, Any] | None = None
    execution_authority: str | None = None
    source_id: str = "<memory>"


class KernelError(Exception):
    pass


class KernelDiagnosticError(KernelError):
    """Runtime failure with a stable diagnostic code (ADR 0079)."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        line: int = 0,
        col: int = 0,
        provenance: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.line = line
        self.col = col
        self.provenance = provenance


def _validate_canonical_semantic_ir(semantic_ir: ScientificSemanticIR | None) -> None:
    """Reject execution authority that is absent, synthetic, or mismatched."""

    from ..scientific_semantic_ir import ScientificSemanticIR

    if semantic_ir is None:
        raise KernelDiagnosticError(
            "E_EVALUATOR_CANONICAL_AUTHORITY",
            "canonical ScientificSemanticIR is required before execution",
        )
    if not isinstance(semantic_ir, ScientificSemanticIR):
        raise KernelDiagnosticError(
            "E_EVALUATOR_CANONICAL_AUTHORITY",
            "evaluator requires ScientificSemanticIR input",
        )
    if semantic_ir.authority != "scientific_semantic_ir":
        raise KernelDiagnosticError(
            "E_EVALUATOR_CANONICAL_AUTHORITY",
            "semantic input is not source-derived canonical authority",
        )
    source_id = semantic_ir.source_id
    is_local_path = source_id.startswith("/") and source_id.endswith(".sqx")
    if source_id not in {"sqx", "<memory>"} and not is_local_path:
        raise KernelDiagnosticError(
            "E_EVALUATOR_CANONICAL_AUTHORITY",
            "semantic source identity does not match the local compiler",
        )


@dataclass(frozen=True)
class ExplicitPropagator:
    """Runtime provenance for `exp(-i * H * duration / hbar)`.

    The source-level operator remains explicit; this small runtime value only
    records the already-written generator and duration so the Kernel can
    realize the expression without reintroducing an implicit Evolve policy.
    """

    hamiltonian: Expr
    duration: Expr


class Evaluator:
    """Discrete PMF Kernel (stance a). Pure stmts are Joint → Joint."""

    SOURCE_LINDBLAD_DT = 0.01

    def __init__(
        self,
        *,
        rng_port: RngPort | None = None,
        rng: random.Random | None = None,
        seed: int | None = None,
        measure_sink: MeasureSinkPort | None = None,
        inspect_sink: TextIO | None = None,
        grid_hamiltonians: dict[str, GridHamiltonian] | None = None,
        data_parallel_workers: int = 1,
        host_input: HostInputPort | None = None,
        continuous_field: ContinuousFieldPort | None = None,
    ) -> None:
        # ADR 0170: entropy comes from RngPort; StdlibRngAdapter owns Random.
        if rng_port is not None:
            self.rng: RngPort = rng_port
        elif rng is not None:
            self.rng = StdlibRngAdapter(rng=rng)
        else:
            self.rng = StdlibRngAdapter(seed=seed)
        # Host finiteize (ADR 0185) may reuse the run seed when not passed.
        self.seed = seed
        self.rng_calls = 0
        self._rng_calls_before_measure = 0
        self.last_algebraic_fusion: tuple[float, float] | None = None
        self.last_poly_fusion: tuple[float, ...] | None = None
        # ADR 0171: optional override for measure/snapshot/inspect emission.
        self.measure_sink = measure_sink
        self.inspect_sink = inspect_sink
        # ADR 0194: optional Host-computed structured classical input port.
        self.host_input = host_input
        # ADR 0204: optional Continuous-field Host injection port.
        self.continuous_field = continuous_field
        self.data_parallel_workers = max(1, int(data_parallel_workers))
        self.operators: dict[str, Any] = {}
        # Typed second-quantized locals (FermionOperator/BosonOperator/...)
        # keyed by name -> raw symbolic expr (create/annihilate atoms),
        # kept separate from self.operators until a mapping resolves them
        # into an ordinary Pauli OpExpr (LISS-0032, ADR 0093).
        self.second_quantized_operators: dict[str, Any] = {}
        # Classical scalars for Operator coefficients (Float J = 1.0 → OpVar J)
        # Seed prelude constants (ADR 0062: pi, …)
        from ..stdlib.prelude import PRELUDE_CONSTANTS

        self.scalars: dict[str, float | Fraction] = dict(PRELUDE_CONSTANTS)
        # ADR 0155: optional unit suffix for Type-First classical scalars.
        self.scalar_units: dict[str, str] = {}
        # ADR 0174: method/init frame units for params and local Mass binds.
        self._frame_units: dict[str, str] = {}
        self.funs: dict[str, FunDecl] = {}
        self.classes: dict[str, ClassDecl] = {}
        self.enums: dict[str, EnumDecl] = {}
        self.structs: dict[str, StructDecl] = {}
        self.objects: dict[str, Any] = {}  # ClassInstance | StructValue | EnumValue
        self._this: ClassInstance | None = None
        self._in_init: bool = False  # `fn init` may assign `val` fields once
        self.mixed_states: dict[str, DensityStateValue] = {}
        self.ket_labels: dict[str, str] = {}
        self.povms: dict[str, tuple[str, str]] = {}
        self.static_register_sizes: dict[str, int] = {}
        self.mixed_state_measured = False
        self.execution_lane: str | None = None
        self.grid_hamiltonians = dict(grid_hamiltonians or {})

    def _execute_unit(self, unit: CompilationUnit, *, stdout: TextIO | None = None) -> EvalResult:
        """Run evaluator mechanics without selecting a public authority lane."""

        from .joint import world_workers

        with world_workers(self.data_parallel_workers):
            result = self._run_legacy_ast_body(unit, stdout=stdout)
        return result

    def run_canonical_unit(
        self,
        unit: CompilationUnit,
        *,
        semantic_ir: ScientificSemanticIR | None = None,
        stdout: TextIO | None = None,
    ) -> EvalResult:
        """Run one unit after validating its compile-owned semantic authority."""

        _validate_canonical_semantic_ir(semantic_ir)
        from ..scientific_semantic_ir import build_runtime_execution_plan

        plan = build_runtime_execution_plan(semantic_ir)
        result = self._execute_runtime_plan(plan, unit, stdout=stdout)
        result.execution_authority = "scientific_semantic_ir"
        result.source_id = semantic_ir.source_id
        return result

    def _execute_runtime_plan(
        self, plan: Any, unit: CompilationUnit, *, stdout: TextIO | None = None
    ) -> EvalResult:
        """Execute the supported runtime-plan family.

        The first family owns only state bindings followed by terminal
        measurement.  Other families remain on the explicitly named legacy
        migration path until their own runtime-plan contract is approved.
        """
        if getattr(plan, "family", None) == "evolution":
            return self._execute_evolution_plan(plan, unit, stdout=stdout)
        if getattr(plan, "family", None) == "control_mixture":
            return self._execute_control_mixture_plan(plan, unit, stdout=stdout)
        if getattr(plan, "family", None) == "pure_transformation":
            return self._execute_pure_transformation_plan(plan, unit, stdout=stdout)
        if getattr(plan, "family", None) == "binder":
            return self._execute_binder_plan(plan, unit, stdout=stdout)
        if getattr(plan, "family", None) == "callable":
            return self._execute_callable_plan(plan, unit, stdout=stdout)
        if getattr(plan, "family", None) == "dynamic_lane":
            return self._execute_dynamic_lane_plan(plan, unit, stdout=stdout)
        if self._is_first_runtime_family(unit, plan):
            return self._execute_first_runtime_family(unit, stdout=stdout)
        return self._run_legacy_ast_body(unit, stdout=stdout)

    def _execute_pure_transformation_plan(
        self, plan: Any, unit: CompilationUnit, *, stdout: TextIO | None = None
    ) -> EvalResult:
        """Execute canonical pure transformations before terminal Measure."""
        self._require_runtime_plan_family(
            plan,
            "pure_transformation",
            "transformations",
        )
        return self._execute_deferred_state_measure_plan(unit, stdout=stdout)

    def _execute_control_mixture_plan(
        self, plan: Any, unit: CompilationUnit, *, stdout: TextIO | None = None
    ) -> EvalResult:
        """Execute canonical single-level control mixtures."""
        self._require_runtime_plan_family(plan, "control_mixture", "controls")
        # A diagnostic read is an explicit observation boundary.  The
        # control-mixture plan may still describe the surrounding mixture,
        # but it must not route a program containing Inspect through the
        # deferred State/Measure fast path.  Keep the read non-destructive and
        # let the established AST path preserve its observation semantics.
        if not self._main_deferred_eligible(unit.main.body.stmts if unit.main else []):
            return self._run_legacy_ast_body(unit, stdout=stdout)
        return self._execute_deferred_state_measure_plan(unit, stdout=stdout)

    @staticmethod
    def _require_runtime_plan_family(
        plan: Any, family: str, payload_name: str
    ) -> None:
        """Validate one plan family before entering shared runtime mechanics."""
        from ..scientific_semantic_ir import RuntimeExecutionPlan

        if not isinstance(plan, RuntimeExecutionPlan):
            raise KernelError(f"{family} execution requires a runtime plan")
        if getattr(plan, "family", None) != family:
            raise KernelError(f"runtime plan family must be {family}")
        if not getattr(plan, payload_name, ()):
            raise KernelError(f"{family} plan has no {payload_name} nodes")

    def _execute_evolution_plan(
        self, plan: Any, unit: CompilationUnit, *, stdout: TextIO | None = None
    ) -> EvalResult:
        """Execute canonical local evolution before terminal Measure."""
        self._require_runtime_plan_family(plan, "evolution", "evolutions")
        if not self._is_minimal_local_evolution(unit):
            return self._run_legacy_ast_body(unit, stdout=stdout)
        return self._execute_deferred_state_measure_plan(
            self._evolution_runtime_unit(unit), stdout=stdout
        )

    def _execute_binder_plan(
        self, plan: Any, unit: CompilationUnit, *, stdout: TextIO | None = None
    ) -> EvalResult:
        """Execute the bounded local State/Measure slice around an operator binder."""
        self._require_runtime_plan_family(plan, "binder", "binders")
        if unit.main is None or not self._main_deferred_eligible(unit.main.body.stmts):
            return self._run_legacy_ast_body(unit, stdout=stdout)
        return self._execute_deferred_state_measure_plan(
            self._binder_runtime_unit(unit), stdout=stdout
        )

    def _execute_callable_plan(
        self, plan: Any, unit: CompilationUnit, *, stdout: TextIO | None = None
    ) -> EvalResult:
        """Execute the bounded local callable/object State/Measure slice."""
        self._require_runtime_plan_family(plan, "callable", "callables")
        if not self._is_deferred_callable_eligible(unit):
            return self._run_legacy_ast_body(unit, stdout=stdout)
        return self._execute_deferred_state_measure_plan(unit, stdout=stdout)

    def _execute_dynamic_lane_plan(
        self, plan: Any, unit: CompilationUnit, *, stdout: TextIO | None = None
    ) -> EvalResult:
        """Execute dynamic lanes through the existing capability-gated path."""
        self._require_runtime_plan_family(plan, "dynamic_lane", "dynamic_lanes")
        return self._run_legacy_ast_body(unit, stdout=stdout)

    @staticmethod
    def _is_deferred_callable_eligible(unit: CompilationUnit) -> bool:
        """Keep class construction on its established compatibility path."""
        class_names = {
            declaration.qualified_name
            for declaration in unit.decls
            if isinstance(declaration, ClassDecl)
        }
        class_short_names = {name.rsplit(".", 1)[-1] for name in class_names}
        if unit.main is None:
            return False
        for statement in unit.main.body.stmts:
            if not isinstance(statement, StateBind):
                continue
            expression = statement.expr
            if not isinstance(expression, Call):
                continue
            callee = expression.callee
            if isinstance(callee, Var) and callee.name in class_short_names:
                return False
            if isinstance(callee, Attr) and callee.name in class_short_names:
                return False
        return True

    @staticmethod
    def _binder_runtime_unit(unit: CompilationUnit) -> CompilationUnit:
        """Keep the source operator declarations for deferred materialization.

        Binder plans still need named operators that are consumed by a later
        ``project`` or by a factory result.  The deferred executor handles
        those declarations as compile-time metadata; removing them here
        loses the source-level dependency chain before it can be resolved.
        """
        return unit

    @staticmethod
    def _unit_without_operator_declarations(unit: CompilationUnit) -> CompilationUnit:
        """Build the runtime payload without compile-time Operator declarations."""
        assert unit.main is not None
        return replace(
            unit,
            main=replace(
                unit.main,
                body=replace(
                    unit.main.body,
                    stmts=[
                        statement
                        for statement in unit.main.body.stmts
                        if not (
                            isinstance(statement, StateBind)
                            and statement.ty is not None
                            and statement.ty.name == "Operator"
                        )
                    ],
                ),
            ),
        )

    @staticmethod
    def _evolution_runtime_unit(unit: CompilationUnit) -> CompilationUnit:
        """Keep compile-time Operator declarations out of runtime bind steps."""
        return Evaluator._unit_without_operator_declarations(unit)

    @staticmethod
    def _is_minimal_local_evolution(unit: CompilationUnit) -> bool:
        """Keep Operator/Hamiltonian setup migration bounded to the first slice."""
        if unit.main is None:
            return False
        evolution_count = 0
        for statement in unit.main.body.stmts:
            if isinstance(statement, Measure):
                continue
            if not isinstance(statement, StateBind):
                return False
            if statement.ty is not None and statement.ty.name == "Operator":
                if not isinstance(statement.expr, OpPauli) and not Evaluator._explicit_propagator(statement.expr):
                    return False
                continue
            if isinstance(statement.expr, EvolveExpr):
                evolution_count += 1
                continue
            return False
        return evolution_count == 1

    @staticmethod
    def _is_first_runtime_family(unit: CompilationUnit, plan: Any) -> bool:
        """Return whether ``unit`` is fully covered by the first plan family."""
        from ..scientific_semantic_ir import RuntimeExecutionPlan

        if not isinstance(plan, RuntimeExecutionPlan):
            return False
        if unit.main is None:
            return False
        statements = unit.main.body.stmts
        if not Evaluator._main_deferred_eligible(statements):
            return False
        plan_kinds = {node.kind for node in plan.nodes}
        return "StateBind" in plan_kinds and "Measure" in plan_kinds

    def _execute_first_runtime_family(
        self, unit: CompilationUnit, *, stdout: TextIO | None = None
    ) -> EvalResult:
        """Execute the first State/Measure family through shared mechanics."""
        return self._execute_deferred_state_measure_plan(unit, stdout=stdout)

    def _execute_deferred_state_measure_plan(
        self, unit: CompilationUnit, *, stdout: TextIO | None = None
    ) -> EvalResult:
        """Run approved deferred State/Measure mechanics without dispatch.

        The statement list is used only as the syntax payload associated with
        the already-validated plan family.  Meaning, family eligibility, and
        authority come from ``RuntimeExecutionPlan`` and its semantic IR.
        """
        self._prepare_first_family_context(unit)
        inspect_stream = self.inspect_sink if self.inspect_sink is not None else stdout
        inspect_out: MeasureSinkPort | None = (
            TextIOMeasureSinkAdapter(inspect_stream)
            if inspect_stream is not None
            else None
        )
        stmts = unit.main.body.stmts
        logs: list[str] = []
        joint, measure_result, measurement_kind, deferred_binds_applied = (
            self._run_deferred_state_binds(
                Joint.unit(),
                stmts,
                logs=logs,
                inspect_out=inspect_out,
                stdout=stdout,
                interproc_trace=self._main_interproc_trace_eligible(stmts),
            )
        )
        return EvalResult(
            joint=joint,
            measure=measure_result,
            rng_calls_before_measure=self._rng_calls_before_measure,
            logs=logs,
            mixed_state_measured=self.mixed_state_measured,
            execution_lane=self.execution_lane,
            measurement_kind=measurement_kind,
            deferred_pushforward=True,
            deferred_binds_applied=deferred_binds_applied,
            last_algebraic_fusion=self.last_algebraic_fusion,
            last_poly_fusion=self.last_poly_fusion,
            data_parallel_workers=self.data_parallel_workers,
            dynamic_outcomes_confirmed=self._dynamic_outcomes_confirmed,
            evolution_provenance=self.evolution_provenance,
        )

    def _prepare_first_family_context(self, unit: CompilationUnit) -> None:
        """Initialize only the evaluator context needed by State/Measure."""
        from ..stdlib.prelude import PRELUDE_CONSTANTS

        self.funs = {}
        self.classes = {}
        self.enums = {}
        self.structs = {}
        self.objects = {}
        self.mixed_states = {}
        self.ket_labels = {}
        self.povms = {}
        self.static_register_sizes = {}
        self.operator_spaces = {}
        self.mixed_state_measured = False
        self.execution_lane = None
        self._dynamic_outcomes_confirmed = True
        self.evolution_provenance = None
        self._this = None
        self._unit = unit
        self.operators = {}
        self._compiled_operator_cache = {}
        self.scalars = dict(PRELUDE_CONSTANTS)
        self.scalar_units = {}
        self._frame_units = {}
        self._resolved_host_arrays = {}
        for statement in unit.main.body.stmts if unit.main is not None else ():
            if (
                isinstance(statement, StateBind)
                and statement.ty is not None
                and statement.ty.name == "Operator"
                and len(statement.names) == 1
            ):
                if isinstance(statement.expr, OpPauli):
                    self.operators[statement.names[0]] = statement.expr
                else:
                    propagator = self._explicit_propagator(statement.expr)
                    if propagator is not None:
                        self.operators[statement.names[0]] = propagator
        for declaration in unit.decls:
            if isinstance(declaration, FunDecl) and declaration.name != "main":
                self.funs[declaration.qualified_name] = declaration
                self.funs[declaration.name] = declaration
            elif isinstance(declaration, ClassDecl):
                self.classes[declaration.qualified_name] = declaration
                self.classes[declaration.name] = declaration
            elif isinstance(declaration, EnumDecl):
                self.enums[declaration.qualified_name] = declaration
                self.enums[declaration.name] = declaration
            elif isinstance(declaration, StructDecl):
                self.structs[declaration.qualified_name] = declaration
                self.structs[declaration.name] = declaration

    def _resolve_host_coefficient_arrays(self, unit: CompilationUnit) -> dict[str, Any]:
        """Wire HostInputPort into the ADR 0119 coefficient-tensor path
        (LISS-0406): resolve every `Float[N]...`/`Bool[N]... = host("key")`
        placeholder the source itself declares against `self.host_input`,
        fail closed on anything missing or malformed. LISS-0432: dtype now
        threads through to `CoefficientTensor` so a `Bool[N]…` array (e.g.
        the confirmed S02 step 2 design's `pairwise_compatible`) round-trips
        as `bool`, not silently coerced to `float`."""
        from ..finite_binder import _host_placeholder_keys, merge_host_coefficient_arrays
        from ..scientific_input import (
            CoefficientTensor,
            InputProvenance,
            ScientificInputValidationError,
        )

        placeholders = _host_placeholder_keys(unit)
        if not placeholders:
            return {}
        host_tensors: dict[str, Any] = {}
        for _local_name, (host_key, shape, dtype) in placeholders.items():
            if host_key in host_tensors:
                continue
            raw = self.host_input.get(host_key) if self.host_input is not None else None
            if raw is None:
                continue  # merge_host_coefficient_arrays reports HOST_COEFFICIENT_MISSING
            try:
                host_tensors[host_key] = CoefficientTensor(
                    name=host_key,
                    shape=shape,
                    values=raw,
                    provenance=InputProvenance(
                        source_formula="HostInputPort", input_id=host_key
                    ),
                    dtype=dtype,
                )
            except ScientificInputValidationError as error:
                raise KernelDiagnosticError(error.code, str(error)) from error
        arrays, diagnostics = merge_host_coefficient_arrays(unit, host_tensors)
        if diagnostics:
            first = diagnostics[0]
            raise KernelDiagnosticError(first["code"], first["message"])
        return arrays

    def _run_legacy_ast_body(
        self, unit: CompilationUnit, *, stdout: TextIO | None = None
    ) -> EvalResult:
        joint = Joint.unit()
        if unit.main is None:
            return EvalResult(
                joint=Joint.empty(),
                data_parallel_workers=self.data_parallel_workers,
            )

        self.funs = {}
        self.classes = {}
        self.enums = {}
        self.structs = {}
        self.objects = {}
        self.mixed_states = {}
        self.ket_labels = {}
        self.povms = {}
        self.static_register_sizes = {}
        self.operator_spaces: dict[str, int] = {}
        self.mixed_state_measured = False
        self.execution_lane = None
        # LISS-0389: True until a dynamic-lane mid-circuit collapse finds a
        # recorded controller binding physically unreachable (vacuumed).
        self._dynamic_outcomes_confirmed = True
        self.evolution_provenance = None
        self._this = None
        self._unit = unit
        self.operators = {
            alias: GridHamiltonianRef(alias) for alias in self.grid_hamiltonians
        }
        # LISS-0432: `self.operators[name]` never rebinds mid-run, so a
        # `project ... onto P` target compiled once via `compile_hamiltonian`
        # (e.g. LISS-0430's P_F) is safe to reuse for every later `project`
        # against the same name/width within this Evaluator instance --
        # avoids literally recompiling the identical matrix a second time
        # for the confirmed design's own `X / ||X||` literal repetition.
        self._compiled_operator_cache: dict[tuple[str, int], Any] = {}
        from ..finite_binder import lower_finite_binder_operators

        host_arrays = self._resolve_host_coefficient_arrays(unit)
        self._resolved_host_arrays = host_arrays
        lowered_binders, _ = lower_finite_binder_operators(unit, host_arrays=host_arrays)
        for stmt in unit.main.body.stmts:
            if (
                isinstance(stmt, StateBind)
                and stmt.ty is not None
                and stmt.ty.name == "QubitRegister"
                and len(stmt.names) == 1
                and len(stmt.ty.args) == 1
            ):
                try:
                    self.static_register_sizes[stmt.names[0]] = int(stmt.ty.args[0].name)
                except ValueError:
                    pass
        from ..stdlib.prelude import PRELUDE_CONSTANTS

        self.scalars = dict(PRELUDE_CONSTANTS)
        self.scalar_units = {}
        self._frame_units = {}
        for d in unit.decls:
            if isinstance(d, FunDecl) and d.name != "main":
                self.funs[d.qualified_name] = d
                self.funs[d.name] = d
            elif isinstance(d, ClassDecl):
                self.classes[d.qualified_name] = d
                self.classes[d.name] = d
            elif isinstance(d, EnumDecl):
                self.enums[d.qualified_name] = d
                self.enums[d.name] = d
            elif isinstance(d, StructDecl):
                self.structs[d.qualified_name] = d
                self.structs[d.name] = d

        measure_result: MeasureResult | None = None
        measurement_kind: str | None = None
        logs: list[str] = []
        inspect_stream = self.inspect_sink if self.inspect_sink is not None else stdout
        inspect_out: MeasureSinkPort | None = (
            TextIOMeasureSinkAdapter(inspect_stream)
            if inspect_stream is not None
            else None
        )
        deferred_pushforward = False
        deferred_binds_applied = 0

        stmts = unit.main.body.stmts
        interproc_trace = self._main_interproc_trace_eligible(stmts)
        if self._main_deferred_eligible(stmts):
            joint, measure_result, measurement_kind, deferred_binds_applied = (
                self._run_deferred_state_binds(
                    joint,
                    stmts,
                    logs=logs,
                    inspect_out=inspect_out,
                    stdout=stdout,
                    interproc_trace=interproc_trace,
                )
            )
            deferred_pushforward = True
            return EvalResult(
                joint=joint,
                measure=measure_result,
                rng_calls_before_measure=self._rng_calls_before_measure,
                logs=logs,
                mixed_state_measured=self.mixed_state_measured,
                execution_lane=self.execution_lane,
                measurement_kind=measurement_kind,
                deferred_pushforward=deferred_pushforward,
                deferred_binds_applied=deferred_binds_applied,
                last_algebraic_fusion=self.last_algebraic_fusion,
                last_poly_fusion=self.last_poly_fusion,
                data_parallel_workers=self.data_parallel_workers,
            )

        for stmt_i, stmt in enumerate(stmts):
            if isinstance(stmt, ReturnStmt):
                raise KernelError("`main` cannot return; use terminal `measure`")
            if isinstance(stmt, DynamicQpuStmt):
                # LISS-0387 (ADR 0200): Host has already Fake-gated this run
                # by the time the evaluator is reached (unchanged from
                # LISS-0383) — real execution proceeds unconditionally here.
                joint = self._run_dynamic_qpu_block(
                    joint, stmt, logs=logs, inspect_out=inspect_out
                )
                continue
            if isinstance(stmt, ForEachStmt):
                joint = self._run_foreach(joint, stmt)
                continue
            if isinstance(stmt, ExprStmt):
                if isinstance(stmt.expr, Call):
                    joint = self._bind_call(joint, "__expr_stmt", stmt.expr)
                    continue
                raise KernelError("unsupported expression statement")
            if isinstance(stmt, StateBind):
                if stmt.ty is not None and stmt.ty.name == "POVM":
                    self._bind_povm(stmt)
                    continue
                if stmt.ty is not None and stmt.ty.name == "DensityState":
                    self._bind_mixed_state(stmt)
                    continue
                if (
                    len(stmt.names) == 1
                    and isinstance(stmt.expr, KetLit)
                    and stmt.expr.label in {"0", "1"}
                    and (stmt.ty is None or stmt.ty.name == "State")
                ):
                    # LISS-0380: Ensemble may reference a named ket Var.
                    self.ket_labels[stmt.names[0]] = stmt.expr.label
                if stmt.ty is not None and stmt.ty.name == "QubitRegister":
                    # Static Hilbert shape is compile-time metadata; it has no
                    # runtime allocation or state coordinate in the Kernel.
                    continue
                if (
                    stmt.ty is not None
                    and stmt.ty.name in ("Float", "Bool")
                    and len(stmt.ty.args) >= 1
                ):
                    # LISS-0406/LISS-0432: `Float[N]…`/`Bool[N]…`
                    # coefficient-tensor declarations (ADR 0119, literal or
                    # `host("key")`-sourced) are compile-time coefficient
                    # data consumed only via the
                    # Operator sum-binder lowering above (host_arrays) --
                    # they have no live Joint/scalar role.
                    continue
                if stmt.ty is not None and stmt.ty.name == "Operator":
                    if len(stmt.names) != 1:
                        raise KernelError("Operator bind expects a single name")
                    declared_space = operator_declared_space(stmt.ty)
                    if declared_space is not None:
                        self.operator_spaces[stmt.names[0]] = declared_space
                    explicit_propagator = self._explicit_propagator(stmt.expr)
                    op_val = (
                        lowered_binders[stmt.names[0]]
                        if stmt.names[0] in lowered_binders
                        else explicit_propagator
                        if explicit_propagator is not None
                        else self._resolve_operator_expr(stmt.expr)
                    )
                    # LISS-0229: materialize outer(psi, phi) against the live Joint.
                    if (
                        isinstance(op_val, Call)
                        and isinstance(op_val.callee, Var)
                        and op_val.callee.name == "outer"
                    ):
                        op_val = self._materialize_outer(joint, op_val)
                    self.operators[stmt.names[0]] = op_val
                    continue
                # ADR 0180: inferred Operator bind `H = Z + …` (no type head).
                if (
                    stmt.ty is None
                    and len(stmt.names) == 1
                    and self._looks_like_operator_rhs(stmt.expr)
                ):
                    op_val = self._resolve_operator_expr(stmt.expr)
                    self.operators[stmt.names[0]] = op_val
                    continue
                if stmt.ty is not None and stmt.ty.name in _SECOND_QUANTIZED_FAMILIES:
                    if len(stmt.names) != 1:
                        raise KernelError("second-quantized bind expects a single name")
                    self._bind_second_quantized(stmt.names[0], stmt.ty.name, stmt.expr)
                    continue
                # Class / struct construction (typed or ADR 0180 inferred Call)
                if len(stmt.names) == 1 and isinstance(stmt.expr, Call):
                    tname = stmt.ty.name if stmt.ty is not None else None
                    if tname is None:
                        tname = self._expr_qualname(stmt.expr.callee)
                    if tname is not None and tname in self.classes:
                        self.objects[stmt.names[0]] = self._construct_instance(
                            tname, stmt.expr
                        )
                        continue
                    if tname is not None and tname in self.structs:
                        callee_name = self._expr_qualname(stmt.expr.callee)
                        if (
                            callee_name is not None
                            and callee_name != tname
                            and callee_name in self.funs
                        ):
                            # Struct-typed binding via a free function that
                            # returns the struct (not a direct `Point(...)`
                            # constructor call) -- LISS-0338's deferred gap.
                            val, _unit = self._eval_value_with_unit(stmt.expr, {})
                            self.objects[stmt.names[0]] = val
                            continue
                        self.objects[stmt.names[0]] = self._construct_struct(
                            tname, stmt.expr
                        )
                        continue
                if stmt.ty is not None and len(stmt.names) == 1:
                    tname = stmt.ty.name
                    if tname in self.enums:
                        val = self._eval_value(stmt.expr, {})
                        if not isinstance(val, EnumValue) or (
                            val.enum_name not in {tname, self.enums[tname].qualified_name}
                            and val.enum_name.split(".")[-1] != tname.split(".")[-1]
                        ):
                            raise KernelError(
                                f"ENUM_TYPE_MISMATCH: expected `{tname}`, got {val!r}"
                            )
                        self.objects[stmt.names[0]] = val
                        continue
                # Capture Type-First / ADR 0180 classical scalars for H coefficients
                # ADR 0184 / LISS-0305: classical multi-bind `J, h = 1.0, 0.5`.
                if (
                    stmt.ty is None
                    and len(stmt.names) >= 2
                    and isinstance(stmt.expr, TupleExpr)
                    and len(stmt.expr.items) == len(stmt.names)
                    and not stmt.via_state_keyword
                    and all(self._is_closed(it) for it in stmt.expr.items)
                ):
                    try:
                        for name, item in zip(stmt.names, stmt.expr.items):
                            val, unit = self._eval_value_with_unit(item, {})
                            if isinstance(val, Fraction):
                                self.scalars[name] = val
                            elif isinstance(val, int) and not isinstance(val, bool):
                                self.scalars[name] = val
                            else:
                                self.scalars[name] = float(val)
                            if unit is not None:
                                self.scalar_units[name] = unit
                            else:
                                self.scalar_units.pop(name, None)
                        continue
                    except (KernelError, TypeError, ValueError):
                        pass
                if (
                    (
                        stmt.ty is None
                        or (
                            stmt.ty.name not in {"State", "Operator", "Delta"}
                            and stmt.ty.name not in self.classes
                            and stmt.ty.name not in self.structs
                            and stmt.ty.name not in self.enums
                        )
                    )
                    and len(stmt.names) == 1
                    and self._is_closed(stmt.expr)
                    and not stmt.via_state_keyword
                ):
                    try:
                        val, unit = self._eval_value_with_unit(stmt.expr, {})
                        # ADR 0160: classical Type-First keeps Fraction; float only at State.
                        if isinstance(val, Fraction):
                            self.scalars[stmt.names[0]] = val
                        elif isinstance(val, int) and not isinstance(val, bool):
                            self.scalars[stmt.names[0]] = val
                        else:
                            self.scalars[stmt.names[0]] = float(val)
                        if unit is not None:
                            self.scalar_units[stmt.names[0]] = unit
                        else:
                            self.scalar_units.pop(stmt.names[0], None)
                        # Pure classical inferred bind: do not force Joint axis.
                        if stmt.ty is None:
                            continue
                    except (KernelError, TypeError, ValueError):
                        pass
                # LISS-0231 / LISS-0292: classical Type-First-returning free fn
                # with object args (e.g. road_m(qty)) — do not Joint-bind params.
                _classical_ret = {
                    "Float",
                    "Int",
                    "Bool",
                    "Mass",
                    "Time",
                    "Length",
                    "Current",
                    "Temperature",
                    "Energy",
                    "Frequency",
                    "Stiffness",
                    "Momentum",
                }
                if (
                    stmt.ty is not None
                    and stmt.ty.name in _classical_ret
                    and len(stmt.names) == 1
                    and isinstance(stmt.expr, Call)
                    and isinstance(stmt.expr.callee, Var)
                    and stmt.expr.callee.name in self.funs
                    and stmt.names[0] not in self.scalars
                ):
                    fun = self.funs[stmt.expr.callee.name]
                    if (
                        fun.return_type is not None
                        and fun.return_type.name in _classical_ret
                    ):
                        val, unit = self._eval_classical_user_fun_value(
                            fun, stmt.expr
                        )
                        if isinstance(val, Fraction):
                            self.scalars[stmt.names[0]] = val
                        elif isinstance(val, int) and not isinstance(val, bool):
                            self.scalars[stmt.names[0]] = val
                        else:
                            self.scalars[stmt.names[0]] = float(val)
                        if unit is not None:
                            self.scalar_units[stmt.names[0]] = unit
                        else:
                            self.scalar_units.pop(stmt.names[0], None)
                        joint = joint.bind_const(
                            stmt.names[0], self.scalars[stmt.names[0]]
                        )
                        continue
                joint = self._bind_names(
                    joint, stmt.names, stmt.expr, logs=logs, inspect_out=inspect_out
                )
                if interproc_trace and self._is_library_user_call(stmt.expr):
                    live = self._stmts_live_vars(stmts[stmt_i + 1 :])
                    joint = self._trace_out_dead_caller_coords(
                        joint, live, stmt.names
                    )
                # LISS-0137: method / joint-bound classical Float → scalars for
                # Operator coeffs and `evolve … for t` (empty-env _eval_value).
                if (
                    stmt.ty is not None
                    and stmt.ty.name
                    not in {
                        "State",
                        "Operator",
                        "Delta",
                        "POVM",
                        "DensityState",
                        "QubitRegister",
                    }
                    and stmt.ty.name not in self.classes
                    and stmt.ty.name not in self.structs
                    and stmt.ty.name not in self.enums
                    and len(stmt.names) == 1
                    and stmt.names[0] not in self.scalars
                ):
                    self._maybe_capture_classical_scalar(joint, stmt.names[0])
            elif isinstance(stmt, AssignStmt):
                self._exec_assign(stmt)
            elif isinstance(stmt, Snapshot):
                marg = self._expr_marginal(joint, stmt.expr)
                text = format_snapshot_csv(marg)
                self._emit_sink(stmt.sink, text, stdout=stdout)
                logs.append(f"snapshot:{stmt.sink}:{marg}")
            elif isinstance(stmt, Measure):
                self._rng_calls_before_measure = self.rng_calls
                measurement_kind = self._resolve_measurement_kind(stmt.povm)
                joint = self._apply_measure_tracing_out(joint, stmt)
                mixed = self._mixed_state_for_measure(stmt.expr)
                if mixed is not None:
                    measure_result = self._measure_mixed(
                        mixed, sink=stmt.sink, stdout=stdout
                    )
                    self.mixed_state_measured = True
                else:
                    measure_result = self._measure(joint, stmt.expr, sink=stmt.sink, stdout=stdout)
                break
            else:
                raise KernelError(f"unsupported stmt {type(stmt)}")

        return EvalResult(
            joint=joint,
            measure=measure_result,
            rng_calls_before_measure=self._rng_calls_before_measure,
            logs=logs,
            mixed_state_measured=self.mixed_state_measured,
            execution_lane=self.execution_lane,
            measurement_kind=measurement_kind,
            deferred_pushforward=False,
            deferred_binds_applied=0,
            last_algebraic_fusion=self.last_algebraic_fusion,
            last_poly_fusion=self.last_poly_fusion,
            data_parallel_workers=self.data_parallel_workers,
            dynamic_outcomes_confirmed=self._dynamic_outcomes_confirmed,
            evolution_provenance=self.evolution_provenance,
        )

    @staticmethod
    def _main_deferred_eligible(stmts: list[Any]) -> bool:
        """ADR 0140: StateBind* + terminal Measure only (no inspect/snapshot/ops)."""
        if not stmts:
            return False
        measure_i: int | None = None
        for i, stmt in enumerate(stmts):
            if isinstance(stmt, Measure):
                if measure_i is not None:
                    return False
                measure_i = i
                continue
            if not isinstance(stmt, StateBind):
                return False
            if not Evaluator._is_deferred_state_bind(stmt):
                return False
        return measure_i is not None and measure_i == len(stmts) - 1

    @staticmethod
    def _is_deferred_state_bind(stmt: StateBind) -> bool:
        if stmt.ty is not None and stmt.ty.name != "State":
            return False
        # ADR 0180: untyped classical/Operator/object binds are not State binds.
        if stmt.ty is None and not stmt.via_state_keyword:
            return False
        # inspect / snapshot force a read boundary (ADR 0030 / 0029).
        if Evaluator._expr_has_inspect(stmt.expr):
            return False
        return True

    @staticmethod
    def _expr_has_inspect(expr: Expr) -> bool:
        if isinstance(expr, Inspect):
            return True
        if isinstance(expr, BinOp):
            return Evaluator._expr_has_inspect(expr.lhs) or Evaluator._expr_has_inspect(
                expr.rhs
            )
        if isinstance(expr, Call):
            return Evaluator._expr_has_inspect(expr.callee) or any(
                Evaluator._expr_has_inspect(a) for a in expr.args
            )
        if isinstance(expr, (WhenExpr, SuperposeExpr)):
            if Evaluator._expr_has_inspect(expr.ctrl):
                return True
            return any(Evaluator._expr_has_inspect(arm.body) for arm in expr.arms)
        if isinstance(expr, Pipe):
            return Evaluator._expr_has_inspect(expr.lhs) or Evaluator._expr_has_inspect(
                expr.rhs
            )
        if isinstance(expr, Attr):
            return Evaluator._expr_has_inspect(expr.obj)
        if isinstance(expr, (TupleExpr, ListExpr)):
            return any(Evaluator._expr_has_inspect(i) for i in expr.items)
        if isinstance(expr, BlockExpr):
            return any(
                Evaluator._expr_has_inspect(let.expr) for let in expr.lets
            ) or Evaluator._expr_has_inspect(expr.result)
        if isinstance(expr, Dirac):
            return Evaluator._expr_has_inspect(expr.arg)
        if isinstance(expr, UnitConvert):
            return Evaluator._expr_has_inspect(expr.expr)
        if isinstance(expr, Lambda):
            return Evaluator._expr_has_inspect(expr.body)
        return False

    @staticmethod
    def _expr_free_vars(expr: Expr) -> set[str]:
        names: set[str] = set()

        def walk(node: Any) -> None:
            if node is None:
                return
            if isinstance(node, Var):
                names.add(node.name)
                return
            if isinstance(node, (LitInt, LitFloat, LitBool, LitString, Coin, Vacuum, Hole)):
                return
            if isinstance(node, KetLit):
                return
            if isinstance(node, KetSumBinder):
                domain = node.domain
                walk(getattr(domain, "width", None))
                return
            if isinstance(node, NormExpr):
                walk(node.state)
                return
            if isinstance(node, SetComprehension):
                domain = node.domain
                walk(getattr(domain, "start", None))
                walk(getattr(domain, "end", None))
                walk(getattr(domain, "width", None))
                for condition in node.conditions:
                    walk(condition)
                names.discard(node.variable)
                return
            if isinstance(node, OpBinder):
                domain = node.domain
                walk(domain)
                walk(getattr(domain, "start", None))
                walk(getattr(domain, "end", None))
                walk(getattr(domain, "width", None))
                walk(node.guard)
                walk(node.body)
                names.discard(node.variable)
                return
            if isinstance(node, OpVar):
                names.add(node.name)
                return
            if isinstance(node, OpIndexed):
                walk(node.base)
                walk(node.index)
                return
            if isinstance(node, (OpBin, OpPow, OpCall)):
                if isinstance(node, OpBin):
                    walk(node.lhs)
                    walk(node.rhs)
                elif isinstance(node, OpPow):
                    walk(node.base)
                else:
                    for arg in node.args:
                        walk(arg)
                return
            if isinstance(node, OpAttr):
                walk(node.obj)
                return
            if isinstance(node, (OpLit, OpPauli, OpHop, OpNumber, OpQuadrature, OpGridQuad, OpIdentity)):
                return
            if isinstance(node, BinOp):
                walk(node.lhs)
                walk(node.rhs)
                return
            if isinstance(node, UnaryNot):
                walk(node.expr)
                return
            if isinstance(node, Call):
                walk(node.callee)
                for a in node.args:
                    walk(a)
                return
            if isinstance(node, (WhenExpr, SuperposeExpr)):
                walk(node.ctrl)
                for arm in node.arms:
                    walk(arm.body)
                return
            if isinstance(node, Pipe):
                walk(node.lhs)
                walk(node.rhs)
                return
            if isinstance(node, Lambda):
                walk(node.body)
                names.discard(node.param)
                return
            if isinstance(node, Attr):
                walk(node.obj)
                return
            if isinstance(node, Inspect):
                walk(node.expr)
                return
            if isinstance(node, UnitConvert):
                walk(node.expr)
                return
            if isinstance(node, (TupleExpr, ListExpr)):
                for item in node.items:
                    walk(item)
                return
            if isinstance(node, BlockExpr):
                for let in node.lets:
                    walk(let.expr)
                walk(node.result)
                return
            if isinstance(node, Dirac):
                walk(node.arg)
                return
            if isinstance(node, EvolveExpr):
                for t in node.seeds:
                    walk(t)
                if node.body is not None:
                    for lb in node.body.lets:
                        walk(lb.expr)
                    walk(node.body.result)
                if isinstance(node.times, Expr):
                    walk(node.times)
                if node.duration is not None:
                    walk(node.duration)
                if node.hamiltonian is not None:
                    walk(node.hamiltonian)
                return
            if isinstance(node, TensorExpr):
                walk(node.left)
                walk(node.right)
                return

        walk(expr)
        return names

    @classmethod
    def _deferred_bind_cone(
        cls,
        pending: list[StateBind],
        measure_expr: Expr,
        *,
        extra_needed: set[str] | None = None,
    ) -> set[str]:
        needed = cls._expr_free_vars(measure_expr)
        if extra_needed:
            needed |= set(extra_needed)
        changed = True
        while changed:
            changed = False
            for bind in pending:
                if needed.intersection(bind.names):
                    fv = cls._expr_free_vars(bind.expr)
                    if not fv <= needed:
                        needed |= fv
                        changed = True
        return needed

    def _apply_measure_tracing_out(self, joint: Joint, stmt: Measure) -> Joint:
        """ADR 0173: Born partial-trace leftovers before terminal measure."""
        for name in stmt.tracing_out:
            joint = joint.trace_out(name)
        return joint

    def _run_deferred_state_binds(
        self,
        joint: Joint,
        stmts: list[Any],
        *,
        logs: list[str],
        inspect_out: MeasureSinkPort | None,
        stdout: TextIO | None,
        interproc_trace: bool = False,
    ) -> tuple[Joint, MeasureResult | None, str | None, int]:
        pending = [s for s in stmts if isinstance(s, StateBind)]
        measure_stmt = stmts[-1]
        assert isinstance(measure_stmt, Measure)
        needed = self._deferred_bind_cone(
            pending,
            measure_stmt.expr,
            extra_needed=(
                set(measure_stmt.tracing_out)
                | {
                    name
                    for stmt in pending
                    if stmt.ty is not None and stmt.ty.name == "Operator"
                    for name in self._expr_free_vars(stmt.expr)
                }
            ),
        )
        applied = 0
        for i, stmt in enumerate(pending):
            if stmt.ty is not None and stmt.ty.name == "Operator":
                if len(stmt.names) != 1:
                    raise KernelError("Operator bind expects a single name")
                name = stmt.names[0]
                declared_space = operator_declared_space(stmt.ty)
                if declared_space is not None:
                    self.operator_spaces[name] = declared_space
                explicit_propagator = self._explicit_propagator(stmt.expr)
                op_val = (
                    explicit_propagator
                    if explicit_propagator is not None
                    else self._resolve_operator_expr(stmt.expr)
                )
                if (
                    isinstance(op_val, Call)
                    and isinstance(op_val.callee, Var)
                    and op_val.callee.name == "outer"
                ):
                    op_val = self._materialize_outer(joint, op_val)
                self.operators[name] = op_val
                applied += 1
                continue
            if (
                stmt.ty is not None
                and stmt.ty.name in {"Float", "Bool"}
                and len(stmt.ty.args) >= 1
            ):
                # Coefficient arrays are compile-time inputs for Operator
                # lowering and do not become Joint coordinates.
                continue
            # POVM and DensityState declarations are execution metadata for
            # the terminal measurement, not Joint coordinates.  The deferred
            # callable path must register them before resolving the measure
            # effect, including when the measured density state is returned
            # by a zero-argument function rather than named in `mixed_states`.
            if stmt.ty is not None and stmt.ty.name == "POVM":
                self._bind_povm(stmt)
                applied += 1
                continue
            if stmt.ty is not None and stmt.ty.name == "DensityState":
                self._bind_mixed_state(stmt)
                applied += 1
                continue
            if not needed.intersection(stmt.names):
                continue
            joint = self._bind_names(
                joint, stmt.names, stmt.expr, logs=logs, inspect_out=inspect_out
            )
            applied += 1
            # Keep the deferred path's classical environment in sync with
            # the legacy executor.  Binder domains and classical functions
            # resolve named Int/Float values through `self.scalars`, while
            # `_bind_names` stores the value in the Joint coordinate.
            if (
                stmt.ty is not None
                and stmt.ty.name
                not in {
                    "State",
                    "Operator",
                    "Delta",
                    "POVM",
                    "DensityState",
                    "QubitRegister",
                }
                and len(stmt.names) == 1
            ):
                self._maybe_capture_classical_scalar(joint, stmt.names[0])
            if interproc_trace and self._is_library_user_call(stmt.expr):
                later: list[Any] = [
                    s for s in pending[i + 1 :] if needed.intersection(s.names)
                ]
                later.append(measure_stmt)
                live = self._stmts_live_vars(later)
                joint = self._trace_out_dead_caller_coords(
                    joint, live, stmt.names
                )
        self._rng_calls_before_measure = self.rng_calls
        measurement_kind = self._resolve_measurement_kind(measure_stmt.povm)
        joint = self._apply_measure_tracing_out(joint, measure_stmt)
        mixed = self._mixed_state_for_measure(measure_stmt.expr)
        if mixed is not None:
            measure_result = self._measure_mixed(
                mixed,
                sink=measure_stmt.sink,
                stdout=stdout,
            )
            self.mixed_state_measured = True
        else:
            measure_result = self._measure(
                joint, measure_stmt.expr, sink=measure_stmt.sink, stdout=stdout
            )
        return joint, measure_result, measurement_kind, applied

    def _mixed_state_for_measure(self, expr: Expr) -> DensityStateValue | None:
        """Resolve a measure target to a DensityStateValue when applicable.

        LISS-0377: previously only bare ``Var`` names already present in
        ``mixed_states`` took the mixed path, so ``measure make()`` fell
        through to Joint vacuum measurement with an empty marginal.
        """
        if isinstance(expr, Var):
            return self.mixed_states.get(expr.name)
        if (
            not isinstance(expr, Call)
            or not isinstance(expr.callee, Var)
            or expr.args
        ):
            return None
        fun = self.funs.get(expr.callee.name)
        if (
            fun is None
            or fun.return_type is None
            or fun.return_type.name != "DensityState"
        ):
            return None
        domain = (
            fun.return_type.args[0].name if fun.return_type.args else "Unknown"
        )
        result_expr: Expr | None = fun.body.result
        if result_expr is None:
            for stmt in fun.body.stmts:
                if isinstance(stmt, ReturnStmt):
                    result_expr = stmt.expr
                    break
        if not isinstance(result_expr, Call):
            raise KernelError("unsupported DensityState construction")
        try:
            return density_from_call(
                result_expr,
                domain=domain,
                scalars=_float_scalars(self.scalars),
                ket_labels=self.ket_labels,
            )
        except ValueError as exc:
            raise KernelError(str(exc)) from exc

    def _resolve_measurement_kind(self, povm: Expr | None) -> str:
        if povm is None:
            return "ComputationalBasis"
        if isinstance(povm, Var) and povm.name in self.povms:
            return self.povms[povm.name][1]
        raise KernelError("INVALID_POVM_EFFECT")

    def _bind_povm(self, stmt: StateBind) -> None:
        if (
            isinstance(stmt.expr, Call)
            and _call_name(stmt.expr) == "ComputationalBasis"
        ):
            domain = stmt.ty.args[0].name if stmt.ty and stmt.ty.args else "Unknown"
            self.povms[stmt.names[0]] = (domain, "ComputationalBasis")
            return
        raise KernelError("INVALID_POVM_EFFECT")

    def _bind_mixed_state(self, stmt: StateBind) -> None:
        if len(stmt.names) != 1 or stmt.ty is None:
            raise KernelError("DensityState bind expects one name")
        domain = stmt.ty.args[0].name if stmt.ty.args else "Unknown"
        expr = stmt.expr
        if isinstance(expr, Call) and _call_name(expr) == "DensityState":
            try:
                self.mixed_states[stmt.names[0]] = density_from_call(
                    expr,
                    domain=domain,
                    scalars=_float_scalars(self.scalars),
                    ket_labels=self.ket_labels,
                )
            except ValueError as exc:
                raise KernelError(str(exc)) from exc
            return
        if isinstance(expr, Call) and _call_name(expr) == "lindblad":
            if len(expr.args) != 4 or not isinstance(expr.args[0], Var):
                raise KernelError("lindblad requires a DensityState source")
            source = self.mixed_states.get(expr.args[0].name)
            if source is None:
                raise KernelError("lindblad source must be a DensityState")
            # A declaration-only source contract may still carry unresolved
            # placeholders. Keep that path opaque; numerical lowering starts
            # only when all MVP inputs are explicit.
            if (
                isinstance(expr.args[1], Var)
                and expr.args[1].name not in self.operators
            ) or (
                isinstance(expr.args[2], Var)
            ) or (
                isinstance(expr.args[3], Var)
                and expr.args[3].name not in self.scalars
            ):
                self.mixed_states[stmt.names[0]] = DensityStateValue(
                    matrix=[row[:] for row in source.matrix],
                    domain=domain,
                    operation="lindblad",
                )
                self.execution_lane = "cpu/simulator"
                return
            n_qubits = _density_matrix_n_qubits(source.matrix)
            hamiltonian = self._resolve_lindblad_hamiltonian(expr.args[1], n_qubits)
            jumps = self._resolve_lindblad_jumps(expr.args[2], n_qubits)
            try:
                total_time = float(self._eval_value(expr.args[3], {}))
                evolved = evolve_lindblad(
                    source.matrix,
                    hamiltonian,
                    jumps,
                    total_time=total_time,
                    dt=self.SOURCE_LINDBLAD_DT,
                )
            except (KernelError, TypeError, ValueError, RuntimeError) as exc:
                raise KernelError(str(exc)) from exc
            self.mixed_states[stmt.names[0]] = DensityStateValue(
                matrix=evolved,
                domain=domain,
                operation="lindblad",
            )
            self.execution_lane = "cpu/simulator"
            return
        if isinstance(expr, Call) and _call_name(expr) == "apply":
            if len(expr.args) < 2 or not isinstance(expr.args[1], Var):
                raise KernelError("mixed apply requires a DensityState source")
            source = self.mixed_states.get(expr.args[1].name)
            if source is None:
                raise KernelError("mixed apply source must be a DensityState")
            self.mixed_states[stmt.names[0]] = source
            return
        raise KernelError("unsupported DensityState construction")

    def _resolve_lindblad_jumps(self, expr: Expr, n_qubits: int) -> list[Matrix]:
        if isinstance(expr, ListExpr):
            if expr.items:
                raise KernelError(
                    "non-empty Lindblad jumps must use JumpSet([RawMatrix(...)])"
                )
            return []
        if not isinstance(expr, Call) or _call_name(expr) != "JumpSet":
            raise KernelError("Lindblad jump input must be JumpSet or an empty list")
        if len(expr.args) != 1 or not isinstance(expr.args[0], ListExpr):
            raise KernelError("JumpSet requires a finite list")
        jumps: list[Matrix] = []
        for item in expr.args[0].items:
            if isinstance(item, Var):
                if item.name not in self.operators:
                    raise KernelError(
                        f"SYMBOLIC_JUMP_LOWERING_REQUIRED: jump `{item.name}` "
                        "must resolve to an Operator"
                    )
                try:
                    jumps.append(self._compile_lindblad_operator(item.name, n_qubits))
                except ValueError as exc:
                    raise KernelError(str(exc)) from exc
                continue
            if not isinstance(item, Call) or _call_name(item) != "RawMatrix":
                raise KernelError("JumpSet entries must be explicit RawMatrix values")
            if len(item.args) != 1:
                raise KernelError("RawMatrix requires a finite square numeric matrix")
            try:
                matrix = matrix_from_list(item.args[0])
            except ValueError as exc:
                raise KernelError(str(exc)) from exc
            jumps.append(matrix)
        return jumps

    def _resolve_lindblad_hamiltonian(self, expr: Expr, n_qubits: int) -> Matrix:
        from .unitaries import named_gate_matrix

        if isinstance(expr, Var) and expr.name in self.operators:
            try:
                return self._compile_lindblad_operator(expr.name, n_qubits)
            except ValueError as exc:
                raise KernelError(str(exc)) from exc
        if isinstance(expr, Var):
            matrix = named_gate_matrix(expr.name)
            if matrix is not None:
                return matrix
        raise KernelError("source Lindblad MVP requires a resolvable Hamiltonian")

    def _compile_lindblad_operator(self, name: str, n_qubits: int) -> Matrix:
        from .hamiltonian import compile_hamiltonian

        return compile_hamiltonian(
            self.operators[name],
            env=self.operators,
            scalars=self.scalars,
            n_qubits=n_qubits,
        )

    def _emit_measure_text(
        self,
        sink: str | None,
        text: str,
        *,
        stdout: TextIO | None,
    ) -> None:
        """Emit measure/snapshot text via MeasureSinkPort (ADR 0171)."""
        if self.measure_sink is not None:
            self.measure_sink.write(text)
            return
        port = resolve_measure_sink(sink, stdout=stdout)
        if port is None:
            return
        port.write(text)

    def _emit_sink(
        self,
        sink: str | None,
        text: str,
        *,
        stdout: TextIO | None,
    ) -> None:
        """Emit snapshot/diagnostic text; preserve write_sink newline policy."""
        if self.measure_sink is not None:
            self.measure_sink.write(text)
            return
        from ..measure_sink_port import _STDOUT_ALIASES

        if (sink is None or sink in _STDOUT_ALIASES) and text and not text.endswith("\n"):
            text = text + "\n"
        port = resolve_measure_sink(sink, stdout=stdout)
        if port is None:
            return
        port.write(text)

    def _measure_mixed(
        self,
        state: DensityStateValue,
        *,
        sink: str | None,
        stdout: TextIO | None,
    ) -> MeasureResult:
        marginal = {
            index: max(0.0, float(state.matrix[index][index].real))
            for index in range(len(state.matrix))
        }
        marginal = {key: value for key, value in marginal.items() if value > EPS}
        if not marginal:
            return MeasureResult(
                value=None, vacuum=True, marginal={}, rng_calls=self.rng_calls, sink=sink
            )
        self.rng_calls += 1
        value = sample_from_marginal(marginal, self.rng)
        text = _format_value(value)
        self._emit_measure_text(sink, text + "\n", stdout=stdout)
        return MeasureResult(
            value=value,
            vacuum=False,
            marginal=marginal,
            rng_calls=self.rng_calls,
            sink=sink,
            output=text,
        )

    def _run_foreach(self, joint: Joint, stmt: ForEachStmt) -> Joint:
        """Expand a static register loop into compiler-internal wire names."""
        collection = stmt.collection
        if isinstance(collection, Var):
            count = self.static_register_sizes.get(collection.name)
        elif (
            isinstance(collection, Call)
            and isinstance(collection.callee, Var)
            and collection.callee.name == "register"
            and len(collection.args) == 1
            and isinstance(collection.args[0], LitInt)
            and collection.args[0].value > 0
        ):
            count = collection.args[0].value
        else:
            count = None
        if count is None or count <= 0:
            raise KernelError("FOR_EACH_DYNAMIC_BOUND_ERROR: static register required")
        if count > MVP_MAX_LOGICAL_QUBITS:
            raise KernelError(
                "STATIC_HILBERT_RESOURCE_ERROR: static Hilbert expansion exceeds "
                f"the MVP budget ({MVP_MAX_LOGICAL_QUBITS})"
            )
        for index in range(count):
            wire = f"__foreach_{stmt.element}_{index}"
            joint = self._bind_names(
                joint,
                [wire],
                KetLit(label="0", span=stmt.span),
                logs=[],
                inspect_out=None,
            )
            for body_stmt in stmt.body.stmts:
                if not isinstance(body_stmt, ExprStmt) or not isinstance(body_stmt.expr, Call):
                    raise KernelError("forEach body supports Kernel operation calls only")
                call = body_stmt.expr
                if (
                    not isinstance(call.callee, Var)
                    or call.callee.name != "apply"
                    or len(call.args) != 2
                    or not isinstance(call.args[1], Var)
                    or call.args[1].name != stmt.element
                ):
                    raise KernelError("forEach body must apply an operator to its element")
                expanded = Call(
                    callee=call.callee,
                    args=[call.args[0], Var(name=wire, span=stmt.span)],
                    span=call.span,
                )
                joint = self._bind_call(joint, wire, expanded)
        return joint

    def _run_dynamic_qpu_block(
        self,
        joint: Joint,
        stmt: DynamicQpuStmt,
        *,
        logs: list[str],
        inspect_out: MeasureSinkPort | None,
    ) -> Joint:
        """LISS-0387 (ADR 0200 Decisions 1-3, 6): real dynamic qpu execution.

        Mid-circuit `Controller<T> = measure wire` performs a genuine
        Lueders projection + renormalize -- the same `project_coord`
        primitive `project(psi, k)` already uses in the Static Kernel, not a
        bookkeeping label. The matching `match` arm then runs against the
        real post-measure joint via the existing Call-statement dispatch.
        Host has already Fake-gated this run by the time this is reached
        (unchanged from LISS-0383); `physical_execution_claimed` semantics
        live entirely in the Host layer and are untouched here.

        LISS-0395: the block body is executed via `_run_dynamic_arm_body`
        (the top level is "the outermost arm body") instead of a second,
        hand-maintained copy of the same statement dispatch -- this is what
        makes a Controller-measure or a wire touched only inside a nested
        `match` arm reach the same real-collapse / block-end trace-out
        treatment as a top-level one, at any nesting depth.
        """
        controller_values: dict[str, str] = {}
        dynamically_measured: list[str] = []

        joint = self._run_dynamic_arm_body(
            joint,
            stmt.body.stmts,
            controller_values,
            dynamically_measured,
            logs=logs,
            inspect_out=inspect_out,
        )

        # LISS-0387 Decision 5: dynamically-measured wires are local to the
        # block (never referenced by the surrounding Static `main`); trace
        # them out here via the already-shipped ADR 0173 primitive instead
        # of relying on Host's LINEAR_IMPLICIT_DISCARD bypass. LISS-0395:
        # `dynamically_measured` is now populated at any nesting depth
        # (including wires only ever touched inside a match arm), since
        # `_run_dynamic_arm_body` mutates this same list by reference.
        for wire in dynamically_measured:
            joint = joint.trace_out(wire)
        return joint

    def _reset_dynamic_wire(self, joint: Joint, wire: str, span: Span) -> Joint:
        """LISS-0390: trace_out(wire) then re-prepare wire as |0>.

        Reuses the two already-shipped primitives LISS-0387 (KetLit |0>
        preparation) and ADR 0173 (Joint.trace_out) established -- no new
        Joint math. Deliberately distinct from the Static Kernel's
        same-name `state x = |0>` idiom (LISS-0114 F verification).
        """
        joint = joint.trace_out(wire)
        return self._bind_names(
            joint, [wire], KetLit(label="0", span=span), logs=[], inspect_out=None
        )

    def _run_dynamic_arm_body(
        self,
        joint: Joint,
        stmts: list[Any],
        controller_values: dict[str, str] | None = None,
        dynamically_measured: list[str] | None = None,
        *,
        logs: list[str] | None = None,
        inspect_out: MeasureSinkPort | None = None,
    ) -> Joint:
        """LISS-0395: single recursive statement dispatcher for dynamic-lane
        bodies, used both for the top-level `dynamic qpu` block (via
        `_run_dynamic_qpu_block`) and for `match` arm bodies (including
        arms nested inside arms). `controller_values` and
        `dynamically_measured` are threaded by reference so a
        Controller-measure or a reset performed at any nesting depth is
        visible to sibling/descendant statements and to the caller's
        block-end trace-out accounting, exactly as if it had happened at
        the top level.
        """
        if controller_values is None:
            controller_values = {}
        if dynamically_measured is None:
            dynamically_measured = []
        for body_stmt in stmts:
            if (
                isinstance(body_stmt, StateBind)
                and body_stmt.ty is not None
                and body_stmt.ty.name == "Controller"
                and isinstance(body_stmt.expr, MeasureExpr)
                and isinstance(body_stmt.expr.expr, Var)
                and len(body_stmt.names) == 1
            ):
                wire = body_stmt.expr.expr.name
                controller_name = body_stmt.names[0]
                outcome = self._resolve_dynamic_outcome(controller_name)
                joint = self._collapse_dynamic_wire(joint, wire, outcome)
                controller_values[controller_name] = outcome
                dynamically_measured.append(wire)
                continue
            if isinstance(body_stmt, MatchStmt):
                value = controller_values.get(body_stmt.scrutinee)
                arm = next(
                    (a for a in body_stmt.arms if a.pattern == value), None
                )
                if arm is not None:
                    joint = self._run_dynamic_arm_body(
                        joint,
                        arm.body.stmts,
                        controller_values,
                        dynamically_measured,
                        logs=logs,
                        inspect_out=inspect_out,
                    )
                continue
            if isinstance(body_stmt, ResetStmt):
                # LISS-0390 (ADR 0199 Amendment Decision 7): reuses
                # trace_out (ADR 0173) + KetLit |0> re-preparation -- no
                # new Joint primitive. Tracked for block-end disposal like
                # a measured wire, in case the wire is never touched again.
                joint = self._reset_dynamic_wire(joint, body_stmt.target, body_stmt.span)
                dynamically_measured.append(body_stmt.target)
                continue
            if isinstance(body_stmt, StateBind):
                joint = self._bind_names(
                    joint,
                    body_stmt.names,
                    body_stmt.expr,
                    logs=logs,
                    inspect_out=inspect_out,
                )
                continue
            if isinstance(body_stmt, ExprStmt) and isinstance(body_stmt.expr, Call):
                joint = self._bind_call(joint, "__dynamic_expr_stmt", body_stmt.expr)
                continue
        return joint

    def _resolve_dynamic_outcome(self, controller_name: str) -> str:
        """LISS-0387 Decision 2: supplied-outcome only (no RNG sampling yet)."""
        if self.host_input is not None:
            supplied = self.host_input.get(f"dynamic:{controller_name}")
            if supplied is not None:
                return str(supplied)
        raise KernelError(
            "DYN_SUPPLIED_OUTCOME_MISSING: no Host-supplied outcome for "
            f"controller `{controller_name}` (RNG-sampled dynamic execution "
            "is out of scope for LISS-0387)"
        )

    def _collapse_dynamic_wire(self, joint: Joint, wire: str, outcome: str) -> Joint:
        """LISS-0387 Decision 1: Lueders projection + renormalize on `wire`.

        Identical operation to the Static Kernel's `project(psi, k)` --
        reuses `Joint.project_coord`, no new Joint math.
        """
        label: Any = int(outcome) if outcome in {"0", "1"} else outcome
        projected = joint.project_coord(wire, lambda v: v == label)
        if projected.is_vacuum():
            # LISS-0389: the recorded outcome was physically unreachable.
            self._dynamic_outcomes_confirmed = False
            return Joint.empty()
        from .joint import World, _coalesce

        total = sum(abs(w.amp) ** 2 for w in projected.worlds)
        if total <= EPS:
            self._dynamic_outcomes_confirmed = False
            return Joint.empty()
        scale = 1.0 / cmath.sqrt(total)
        out = [
            World(
                assign=dict(w.assign),
                amp=w.amp * scale,
                coord_phase=dict(w.coord_phase),
            )
            for w in projected.worlds
        ]
        return Joint(worlds=_coalesce(out))

    def _require_uncompute_zero(self, joint: Joint, name: str) -> None:
        """LISS-0114 F: simulator-equivalence check for ≈ computational |0⟩."""
        from .uncompute import require_computational_basis_zero

        try:
            require_computational_basis_zero(joint, name)
        except ValueError as exc:
            raise KernelError(str(exc)) from exc

    def _verify_static_uncompute_bind(
        self, joint: Joint, name: str, expr: Expr
    ) -> None:
        if isinstance(expr, Vacuum) or (
            isinstance(expr, KetLit) and expr.label == "0"
        ):
            self._require_uncompute_zero(joint, name)

    def _bind_names(
        self,
        joint: Joint,
        names: list[str],
        expr: Expr,
        *,
        logs: list[str] | None = None,
        inspect_out: MeasureSinkPort | None = None,
    ) -> Joint:
        if isinstance(expr, EvolveExpr):
            return self._bind_evolve(joint, names, expr)
        if isinstance(expr, TensorExpr):
            return self._bind_tensor(joint, names, expr)
        if isinstance(expr, Call) and isinstance(expr.callee, Var):
            if expr.callee.name == "tensor":
                if len(expr.args) != 2:
                    raise KernelError("tensor requires exactly two arguments")
                return self._bind_tensor(
                    joint,
                    names,
                    TensorExpr(
                        left=expr.args[0], right=expr.args[1], span=expr.span
                    ),
                )
            # ADR 0123: Partial formation / completion before ordinary fn apply.
            if any(isinstance(a, Hole) for a in expr.args):
                if len(names) != 1:
                    raise KernelError("Partial bind expects a single name")
                return self._bind_call(joint, names[0], expr)
            if expr.callee.name in self.objects and isinstance(
                self.objects[expr.callee.name], PartialValue
            ):
                if len(names) != 1:
                    raise KernelError("Partial completion expects a single name")
                return self._bind_call(joint, names[0], expr)
            fun = self.funs.get(expr.callee.name)
            if fun is not None:
                # Pure classical free functions consume object/value frames,
                # not Joint coordinates.  In the callable-plan path a
                # `Float = score(report)` bind otherwise falls through to
                # `_bind_user_fun`, whose Var argument handling quite
                # correctly expects a quantum coordinate and rejects the
                # struct object.  Reuse the established classical evaluator
                # so nested field projections retain the caller frame.
                classical_heads = {
                    "Float",
                    "Int",
                    "Bool",
                    "Mass",
                    "Time",
                    "Length",
                    "Current",
                    "Temperature",
                    "Energy",
                    "Frequency",
                    "Stiffness",
                    "Momentum",
                }
                if (
                    len(names) == 1
                    and fun.return_type is not None
                    and fun.return_type.name in classical_heads
                ):
                    value, unit = self._eval_value_with_unit(expr, {})
                    self._put_unit(self.scalar_units, names[0], unit)
                    try:
                        self.scalars[names[0]] = value
                    except TypeError:
                        pass
                    return joint.bind_const(names[0], value)
                return self._bind_user_fun(
                    joint, names, expr, fun, logs=logs, inspect_out=inspect_out
                )
        if isinstance(expr, TupleExpr):
            if len(expr.items) != len(names):
                raise KernelError(
                    f"tuple arity {len(expr.items)} != bind arity {len(names)}"
                )
            # LISS-0309: multi-ket / mixed multi-bind must use per-name `_bind`
            # (KetLit is not a classical `_eval_value`). Classical closed multi-
            # bind is handled earlier via scalars; this path covers State wires.
            for name, item in zip(names, expr.items):
                joint = self._bind(
                    joint, name, item, logs=logs, inspect_out=inspect_out
                )
            return joint
        # LISS-0228: multi-wire in-place apply — `state (a, b) = apply(U, a, b)`.
        if (
            isinstance(expr, Call)
            and isinstance(expr.callee, Var)
            and expr.callee.name == "apply"
            and len(expr.args) >= 2
            and len(names) == len(expr.args) - 1
            and all(isinstance(a, Var) for a in expr.args[1:])
        ):
            return self._bind_apply_multi(joint, names, expr)
        # Multi-wire in-place cnot — `state (c, t) = cnot(c, t)` (S01 linear).
        if (
            isinstance(expr, Call)
            and isinstance(expr.callee, Var)
            and expr.callee.name == "cnot"
            and len(expr.args) == 2
            and len(names) == 2
            and all(isinstance(a, Var) for a in expr.args)
        ):
            return self._bind_cnot_multi(joint, names, expr)
        if len(names) != 1:
            raise KernelError(f"cannot bind {len(names)} names to {type(expr).__name__}")
        out = self._bind(joint, names[0], expr, logs=logs, inspect_out=inspect_out)
        self._verify_static_uncompute_bind(out, names[0], expr)
        return out

    def _bind_apply_multi(
        self, joint: Joint, names: list[str], expr: Call
    ) -> Joint:
        """apply(U, w…) rebound as ``state (n…) = apply(U, w…)`` (LISS-0228)."""
        from .unitaries import apply_unitary_on_wires

        u_expr = expr.args[0]
        wires = [a.name for a in expr.args[1:]]  # type: ignore[union-attr]
        # LISS-0112 Slice B / LISS-0239: bare Identity is a no-op on any
        # computational level (incl. Qutrit |2⟩); must run before qubit-bit gate.
        if (
            isinstance(u_expr, Var)
            and u_expr.name.upper() in {"I", "ID", "IDENTITY"}
            and len(wires) == 1
        ):
            if list(names) == wires:
                return joint
            w0 = wires[0]
            new = names[0]
            return joint.bind_pushforward(new, lambda a, w=w0: a[w])
        u_mat = self._resolve_unitary_matrix(u_expr, len(wires))
        try:
            updated = apply_unitary_on_wires(joint, wires, u_mat)
        except ValueError as e:
            raise KernelError(str(e)) from e
        if list(names) == wires:
            return updated
        # Relabel wire coordinates to bind names when they differ.
        from .joint import World, _coalesce

        out: list[World] = []
        for w in updated.worlds:
            assign = dict(w.assign)
            cp = dict(w.coord_phase)
            for old, new in zip(wires, names):
                if old == new:
                    continue
                if old in assign:
                    assign[new] = assign.pop(old)
                if old in cp:
                    cp[new] = cp.pop(old)
            out.append(World(assign=assign, amp=w.amp, coord_phase=cp))
        return Joint(worlds=_coalesce(out))

    def _bind_cnot_multi(
        self, joint: Joint, names: list[str], expr: Call
    ) -> Joint:
        """``state (c, t) = cnot(c, t)`` — keep both wires after CNOT (linear)."""
        from .joint import World, _coalesce
        from .quantum_ops import cnot_bit

        ctrl_old = expr.args[0].name  # type: ignore[union-attr]
        tgt_old = expr.args[1].name  # type: ignore[union-attr]
        ctrl_new, tgt_new = names
        out: list[World] = []
        for w in joint.worlds:
            if ctrl_old not in w.assign or tgt_old not in w.assign:
                raise KernelError(
                    f"cnot needs coordinates `{ctrl_old}` and `{tgt_old}` on the joint"
                )
            assign = {
                k: v
                for k, v in w.assign.items()
                if k not in {ctrl_old, tgt_old}
            }
            cp = {
                k: v
                for k, v in w.coord_phase.items()
                if k not in {ctrl_old, tgt_old}
            }
            ctrl_v = w.assign[ctrl_old]
            tgt_v = cnot_bit(ctrl_v, w.assign[tgt_old])
            assign[ctrl_new] = ctrl_v
            assign[tgt_new] = tgt_v
            if ctrl_old in w.coord_phase:
                cp[ctrl_new] = w.coord_phase[ctrl_old]
            if tgt_old in w.coord_phase:
                cp[tgt_new] = w.coord_phase[tgt_old]
            out.append(World(assign=assign, amp=w.amp, coord_phase=cp))
        return Joint(worlds=_coalesce(out))

    def _bind_tensor(self, joint: Joint, names: list[str], expr: TensorExpr) -> Joint:
        """Independent reduced-state tensor: (a, b) = left *|* right."""
        from .joint import World, _coalesce

        if len(names) != 2:
            raise KernelError("`*|*` / tensor bind expects two names `(a, b) = …`")

        # Both sides already on the joint → relabel product wires (preserve amps)
        if isinstance(expr.left, Var) and isinstance(expr.right, Var):
            ln, rn = expr.left.name, expr.right.name
            out: list[World] = []
            for w in joint.worlds:
                if ln not in w.assign or rn not in w.assign:
                    raise KernelError(
                        f"`*|*` needs coordinates `{ln}` and `{rn}` on the joint"
                    )
                assign = {k: v for k, v in w.assign.items() if k not in {ln, rn}}
                assign[names[0]] = w.assign[ln]
                assign[names[1]] = w.assign[rn]
                cp = {
                    k: v
                    for k, v in w.coord_phase.items()
                    if k not in {ln, rn}
                }
                if ln in w.coord_phase:
                    cp[names[0]] = w.coord_phase[ln]
                if rn in w.coord_phase:
                    cp[names[1]] = w.coord_phase[rn]
                out.append(World(assign=assign, amp=w.amp, coord_phase=cp))
            return Joint(worlds=_coalesce(out))

        def _amps_indep(side: Expr) -> list[tuple[Any, complex]]:
            jl = self._bind(Joint.unit(), "_T", side)
            return [(w.assign["_T"], w.amp) for w in jl.worlds]

        left = _amps_indep(expr.left)
        right = _amps_indep(expr.right)
        if not left or not right:
            return Joint.empty()
        out = [
            World(assign={names[0]: vl, names[1]: vr}, amp=al * ar)
            for vl, al in left
            for vr, ar in right
        ]
        return Joint(worlds=_coalesce(out))

    def _eval_times(self, times: Expr | int) -> int:
        """ADR 0060: resolve evolve `times` to a non-negative int (Float truncates)."""
        if isinstance(times, int):
            n = times
        else:
            raw = self._eval_value(times, {})
            try:
                n = int(float(raw))
            except (TypeError, ValueError) as e:
                raise KernelError(
                    f"evolve times must evaluate to a number, got {raw!r}"
                ) from e
        if n < 0:
            raise KernelError(f"evolve times must be non-negative, got {n}")
        return n

    def _bind_evolve(self, joint: Joint, names: list[str], expr: EvolveExpr) -> Joint:
        if expr.explicit_transform:
            return self._bind_explicit_evolve(joint, names, expr)
        if len(expr.seeds) != len(names):
            raise KernelError(
                f"evolve seeds {len(expr.seeds)} != bind names {len(names)}"
            )

        # Hamiltonian path: evolve psi under H for t  (ADR 0038 / 0041)
        if expr.hamiltonian is not None:
            return self._bind_evolve_hamiltonian(joint, names, expr)

        pre_live = self._joint_coord_names(joint)

        # Initialize working coordinates from seeds (correlated copy / eval).
        init: dict[str, Callable[[dict[str, Any]], Any]] = {}
        for name, seed in zip(names, expr.seeds):
            if isinstance(seed, Var):
                sn = seed.name
                init[name] = lambda a, sn=sn: a[sn]
            else:
                init[name] = lambda a, s=seed: self._eval_value(s, a)
        joint = joint.bind_multi(init)

        if expr.body is None:
            raise KernelError("block evolve requires a `{ … }` body")

        n_times = self._eval_times(expr.times)
        for _step in range(n_times):
            for let in expr.body.lets:
                ln = let.name
                le = let.expr
                # Gate / walk Call must use Joint transformers, not scalar eval
                if isinstance(le, Call):
                    joint = self._bind(joint, ln, le)
                else:
                    joint = joint.bind_pushforward(
                        ln, lambda a, e=le: self._eval_value(e, a)
                    )
            res = expr.body.result
            if isinstance(res, Call) and isinstance(res.callee, Var):
                fun = self.funs.get(res.callee.name)
                if fun is not None:
                    joint = self._bind_user_fun(joint, names, res, fun)
                    continue
            if isinstance(res, TupleExpr):
                if len(res.items) != len(names):
                    raise KernelError("evolve result tuple arity mismatch")
                updates = {
                    name: (lambda a, e=item: self._eval_value(e, a))
                    for name, item in zip(names, res.items)
                }
                joint = joint.bind_multi(updates)
            else:
                if len(names) != 1:
                    raise KernelError("evolve scalar result requires a single bind name")
                if isinstance(res, Call):
                    joint = self._bind(joint, names[0], res)
                else:
                    joint = joint.bind_pushforward(
                        names[0], lambda a, e=res: self._eval_value(e, a)
                    )
        # ADR 0142: drop evolve-local let axes (and other non-live coords).
        return self._trace_out_dead_fn_locals(joint, pre_live, names)

    def _bind_explicit_evolve(
        self, joint: Joint, names: list[str], expr: EvolveExpr
    ) -> Joint:
        """Realize the Phase 2 `Operator * State` application.

        The explicit source form is intentionally narrow in this phase.  A
        propagator must have been declared from the canonical exponential;
        arbitrary operator/state products fail closed until their target
        realization is specified.
        """
        if not names or expr.body is None:
            raise KernelDiagnosticError(
                "EVOLUTION_RUNTIME_UNSUPPORTED",
                "explicit Evolve currently requires one State result and one block result",
                line=expr.span.line,
                col=expr.span.col,
            )
        result = expr.body.result
        if not (isinstance(result, BinOp) and result.op == "*"):
            raise KernelDiagnosticError(
                "EVOLUTION_RUNTIME_UNSUPPORTED",
                "explicit Evolve runtime requires `propagator * state`",
                line=result.span.line,
                col=result.span.col,
            )
        propagator = (
            self.operators.get(result.lhs.name)
            if isinstance(result.lhs, Var)
            else self._explicit_propagator(result.lhs)
        )
        if not isinstance(propagator, ExplicitPropagator):
            raise KernelDiagnosticError(
                "EVOLUTION_RUNTIME_UNSUPPORTED",
                "explicit Operator * State runtime requires an `exp(-i * H * t / hbar)` propagator",
                line=result.span.line,
                col=result.span.col,
            )
        seed_expr = result.rhs
        if isinstance(seed_expr, TupleExpr):
            seeds = list(seed_expr.items)
        else:
            seeds = [seed_expr]
        if len(seeds) != len(names):
            raise KernelDiagnosticError(
                "EVOLUTION_RUNTIME_UNSUPPORTED",
                "explicit Evolve tuple arity must match the State bind",
                line=result.span.line,
                col=result.span.col,
            )
        normalized_seeds: list[Expr] = []
        for seed, name in zip(seeds, names):
            if not isinstance(seed, Var):
                raise KernelDiagnosticError(
                    "EVOLUTION_RUNTIME_UNSUPPORTED",
                    "explicit Evolve currently requires named State operands",
                    line=result.span.line,
                    col=result.span.col,
                )
            if seed.name != name:
                joint = joint.rename_coord(seed.name, name)
            normalized_seeds.append(Var(name=name, span=seed.span))
        lowered = EvolveExpr(
            seeds=normalized_seeds,
            times=1,
            body=None,
            span=expr.span,
            duration=propagator.duration,
            hamiltonian=propagator.hamiltonian,
        )
        max_steps = self._eval_max_steps(expr.max_steps) if expr.until_predicate else 1
        previous = joint
        for iteration in range(1, max_steps + 1):
            joint = self._bind_evolve_hamiltonian(joint, names, lowered)
            if expr.until_predicate is None:
                break
            if self._eval_until_predicate(
                joint, names, expr.until_predicate, previous=previous,
                allow_single_alias=True,
            ):
                self.evolution_provenance = {
                    "source_transform": "Operator * State",
                    "predicate": "converged",
                    "metric": "full_state_l2_difference",
                    "numeric_type": "Float64",
                    "tolerance": 1e-9,
                    "iteration_count": iteration,
                    "max_steps": max_steps,
                    "stop_reason": "predicate",
                    "realization": "simulator_exact_step",
                    "predicate_effect": "non_collapsing",
                }
                return joint
            previous = joint
        if expr.until_predicate is not None:
            provenance = {
                "source_transform": "Operator * State",
                "predicate": "converged",
                "metric": "full_state_l2_difference",
                "numeric_type": "Float64",
                "tolerance": 1e-9,
                "iteration_count": max_steps,
                "max_steps": max_steps,
                "stop_reason": "max_exhausted",
                "realization": "simulator_exact_step",
                "predicate_effect": "non_collapsing",
            }
            self.evolution_provenance = provenance
            raise KernelDiagnosticError(
                "EVOLVE_UNTIL_MAX_STEPS_ERROR",
                "evolve until reached max steps without predicate success",
                line=expr.span.line,
                col=expr.span.col,
                provenance=provenance,
            )
        return joint

    @staticmethod
    def _explicit_propagator(expr: Expr) -> ExplicitPropagator | None:
        """Recognize only the canonical written propagator expression."""
        if not (
            isinstance(expr, Call)
            and isinstance(expr.callee, Var)
            and expr.callee.name == "exp"
            and len(expr.args) == 1
        ):
            return None
        exponent = expr.args[0]
        if not (
            isinstance(exponent, BinOp)
            and exponent.op == "/"
            and isinstance(exponent.rhs, Var)
            and exponent.rhs.name == "hbar"
            and isinstance(exponent.lhs, BinOp)
            and exponent.lhs.op == "*"
            and isinstance(exponent.lhs.lhs, BinOp)
            and exponent.lhs.lhs.op == "*"
        ):
            return None
        signed_generator = exponent.lhs.lhs.lhs
        hamiltonian = exponent.lhs.lhs.rhs
        duration = exponent.lhs.rhs
        if not (
            isinstance(signed_generator, BinOp)
            and signed_generator.op == "-"
            and isinstance(signed_generator.rhs, Var)
            and signed_generator.rhs.name == "i"
            and isinstance(signed_generator.lhs, (LitInt, LitFloat))
            and signed_generator.lhs.value == 0
        ):
            return None
        return ExplicitPropagator(hamiltonian=hamiltonian, duration=duration)

    def _eval_max_steps(self, max_steps: Expr | None) -> int:
        if not isinstance(max_steps, LitInt) or max_steps.value <= 0:
            raise KernelError("evolve until requires a positive compile-time `max` bound")
        return max_steps.value

    def _eval_until_predicate(
        self, joint: Joint, names: list[str], predicate: Expr,
        *, previous: Joint | None = None, allow_single_alias: bool = False,
    ) -> bool:
        """Pure Kernel predicate: no RNG, measure, or outer mutation (ADR 0079)."""
        if isinstance(predicate, LitBool):
            return predicate.value
        if isinstance(predicate, Call) and isinstance(predicate.callee, Var):
            if predicate.callee.name == "converged":
                if len(predicate.args) != 1 or not isinstance(predicate.args[0], Var):
                    raise KernelError("converged requires one state variable")
                coord = predicate.args[0].name
                if coord not in names:
                    if not allow_single_alias and coord not in joint.variables():
                        raise KernelError(
                            f"converged predicate may reference evolve seeds only, got `{coord}`"
                        )
                if previous is None:
                    return len(joint.amplitude_marginal(coord)) == 1
                return self._joint_l2_distance(previous, joint) <= 1e-9
        raise KernelError(
            "evolve until predicates support `converged(state)` or literal booleans only"
        )

    @staticmethod
    def _joint_l2_distance(left: Joint, right: Joint) -> float:
        def amplitudes(joint: Joint) -> dict[str, complex]:
            result: dict[str, complex] = {}
            for world in joint.worlds:
                key = repr(sorted(world.assign.items(), key=lambda item: item[0]))
                result[key] = result.get(key, 0j) + world.amp
            return result

        lhs = amplitudes(left)
        rhs = amplitudes(right)
        keys = set(lhs) | set(rhs)
        return sum(abs(lhs.get(key, 0j) - rhs.get(key, 0j)) ** 2 for key in keys) ** 0.5

    def _bind_evolve_hamiltonian(
        self, joint: Joint, names: list[str], expr: EvolveExpr
    ) -> Joint:
        if len(names) != len(expr.seeds):
            raise KernelError("hamiltonian evolve seed/bind arity mismatch")
        if expr.hamiltonian is None or expr.duration is None:
            raise KernelError("hamiltonian evolve requires `under H for t`")

        # Resolve seed coords into `names` working wires
        init: dict[str, Callable[[dict[str, Any]], Any]] = {}
        for name, seed in zip(names, expr.seeds):
            if isinstance(seed, Var):
                sn = seed.name
                init[name] = lambda a, sn=sn: a[sn]
            else:
                init[name] = lambda a, s=seed: self._eval_value(s, a)
        joint = joint.bind_multi(init)

        if expr.until_predicate is None:
            return self._hamiltonian_evolve_one_step(joint, names, expr)

        max_n = self._eval_max_steps(expr.max_steps)
        for _ in range(max_n):
            joint = self._hamiltonian_evolve_one_step(joint, names, expr)
            if self._eval_until_predicate(joint, names, expr.until_predicate):
                return joint
        raise KernelDiagnosticError(
            "EVOLVE_UNTIL_MAX_STEPS_ERROR",
            "evolve until reached max steps without predicate success",
            line=expr.span.line,
            col=expr.span.col,
        )

    def _hamiltonian_evolve_one_step(
        self, joint: Joint, names: list[str], expr: EvolveExpr
    ) -> Joint:
        from .hamiltonian import compile_hamiltonian, hop_basis_dim, op_n_qubits
        from .joint import World, _coalesce
        from .matrix import apply_mat, expm_ih
        from .quantum_ops import apply_u2, pauli_u
        from ..ast_nodes import (
            OpBin,
            OpGridQuad,
            OpHop,
            OpLit,
            OpNumber,
            OpPauli,
            OpPow,
            OpQuadrature,
            OpVar,
        )
        from ..dimensions import UNIT_TABLE

        # ADR 0195: evolve's duration must resolve to a real Time unit --
        # a bare dimensionless duration can no longer be silently treated
        # as "already in seconds" under the old hbar=1 convention.
        # LISS-0357: resolve via the already-general _eval_value_with_unit
        # (Var, struct-field Attr via ADR 0174 field_units, and
        # literal-suffix Attr) instead of a bare-Var-only check, so
        # `evolve ... for config.duration` and `evolve ... for 0.25.fs`
        # are recognized the same as a pre-bound Time variable.
        t_raw_val, duration_unit = self._eval_value_with_unit(expr.duration, {})
        if UNIT_TABLE.get(duration_unit, (None, None))[0] != "Time":
            raise KernelDiagnosticError(
                "EVOLVE_UNRESOLVED_UNIT_ERROR",
                "evolve duration must resolve to a real Time unit (e.g. "
                "a Float scalar declared with a `s`/`ps`/`ns`/`fs` suffix) "
                "-- a bare dimensionless duration is not accepted (ADR 0195)",
                line=expr.span.line,
                col=expr.span.col,
            )

        t_raw = float(t_raw_val)
        # ADR 0195: bare unit suffixes stay in their declared unit unless
        # explicitly `to`-converted (dimensions.py convention) -- so a
        # duration declared as `X.fs` must still be canonicalized to real
        # seconds here before use, regardless of whether the source also
        # wrote an explicit `to s`.
        from ..dimensions import to_canonical_magnitude

        t, _canon_duration_unit = to_canonical_magnitude(t_raw, duration_unit)
        hop = expr.hamiltonian
        assert hop is not None

        # Legacy single-name Pauli string: evolve psi under X for t
        if isinstance(hop, Var) and hop.name.upper() in {"I", "X", "Y", "Z"} and len(names) == 1:
            # LISS-0112 Slice B: Identity is a no-op on any computational level
            # (matches qubit `pauli_u(I)` = I; enables D=3 |2⟩ support).
            if hop.name.upper() in {"I", "ID", "IDENTITY"}:
                return joint
            try:
                u = pauli_u(hop.name, t)
            except ValueError as e:
                raise KernelError(str(e)) from e
            src = names[0]
            amps = joint.amplitude_marginal(src)
            if any(v not in (0, 1) for v in amps):
                raise KernelError(
                    f"hamiltonian `{hop.name}` expects qubit support {{0,1}}, got {sorted(amps)}"
                )
            # Preserve sibling / classical coords (LISS-0243): group by non-src
            # assigns and apply the 2×2 unitary within each slice — same strategy
            # as the multi-qubit Pauli path below. Do not rebuild a single-wire Joint.
            from collections import defaultdict

            groups: dict[tuple, list[World]] = defaultdict(list)
            for w in joint.worlds:
                if src not in w.assign:
                    continue
                if w.assign[src] not in (0, 1):
                    raise KernelError(
                        f"hamiltonian `{hop.name}` expects qubit support {{0,1}}, "
                        f"got {w.assign[src]!r}"
                    )
                key = tuple(sorted((k, v) for k, v in w.assign.items() if k != src))
                groups[key].append(w)

            out: list[World] = []
            for key, ws in groups.items():
                a0 = a1 = 0j
                phase0: dict[str, complex] = {}
                phase1: dict[str, complex] = {}
                for w in ws:
                    if w.assign[src] == 0:
                        a0 += w.amp
                        phase0 = dict(w.coord_phase)
                    else:
                        a1 += w.amp
                        phase1 = dict(w.coord_phase)
                b0, b1 = apply_u2(a0, a1, u)
                base = dict(key)
                if abs(b0) ** 2 > EPS:
                    out.append(
                        World(assign={**base, src: 0}, amp=b0, coord_phase=phase0)
                    )
                if abs(b1) ** 2 > EPS:
                    out.append(
                        World(assign={**base, src: 1}, amp=b1, coord_phase=phase1)
                    )
            return Joint(worlds=_coalesce(out))

        # Operator expression or bound Operator name
        if isinstance(hop, Var):
            if hop.name not in self.operators:
                # bare Pauli already handled; unknown
                raise KernelError(f"unknown Operator / Hamiltonian `{hop.name}`")
            op_ast = self.operators[hop.name]
        elif isinstance(
            hop,
            (
                OpPauli,
                OpNumber,
                OpQuadrature,
                OpGridQuad,
                OpHop,
                OpLit,
                OpBin,
                OpPow,
                OpVar,
                OpAttr,
                OpIndexed,
                OpBinder,
                OpIdentity,
                OpCall,
            ),
        ):
            op_ast = hop
        else:
            raise KernelError("hamiltonian must be Operator name or Pauli literal")

        try:
            op_ast = materialize_op_attrs(
                op_ast, self.objects, operators=self.operators
            )
        except OpAttrElaborationError as exc:
            raise KernelError(str(exc)) from exc

        declared_space = (
            self.operator_spaces.get(hop.name)
            if isinstance(hop, Var)
            else None
        )
        if isinstance(op_ast, GridHamiltonianRef):
            gh = self.grid_hamiltonians[op_ast.alias]
            return self._evolve_precomputed_grid(joint, names, gh, t)
        try:
            nq = (
                declared_space
                if declared_space is not None
                else op_n_qubits(op_ast, self.operators, self.scalars)
            )
        except ValueError as e:
            raise KernelError(str(e)) from e

        if nq == 0:
            # Fock / site-basis: single coordinate, levels 0..dim-1
            if len(names) != 1:
                raise KernelError("Fock Hamiltonian evolve requires a single bind name")
            src = names[0]
            amps = joint.amplitude_marginal(src)
            keys = sorted(amps.keys())
            if not keys or any(not isinstance(k, int) or k < 0 for k in keys):
                raise KernelError("Fock evolve expects non-negative Int levels")
            dim = max(keys) + 1
            dim = max(dim, hop_basis_dim(op_ast, self.operators, self.scalars), 2)
            try:
                hmat = compile_hamiltonian(
                    op_ast,
                    env=self.operators,
                    scalars=self.scalars,
                    n_qubits=0,
                    fock_dim=dim,
                )
                u = expm_ih(hmat, t)
            except ValueError as e:
                raise KernelError(str(e)) from e
            vec = [amps.get(i, 0j) for i in range(dim)]
            outv = apply_mat(u, vec)
            out_w = [
                World(assign={src: i}, amp=outv[i])
                for i in range(dim)
                if abs(outv[i]) ** 2 > EPS
            ]
            return Joint(worlds=_coalesce(out_w))

        if nq < 0:
            # Position grid: Float abscissae on a single wire
            if len(names) != 1:
                raise KernelError("grid Hamiltonian evolve requires a single bind name")
            src = names[0]
            amps = joint.amplitude_marginal(src)
            keys = sorted(amps.keys(), key=lambda x: float(x))
            if not keys or any(not isinstance(k, (int, float)) for k in keys):
                raise KernelError("grid evolve expects Float (or Int) abscissae")
            xs = [float(k) for k in keys]
            try:
                hmat = compile_hamiltonian(
                    op_ast,
                    env=self.operators,
                    scalars=self.scalars,
                    n_qubits=-1,
                    grid_xs=xs,
                )
                u = expm_ih(hmat, t)
            except ValueError as e:
                raise KernelError(str(e)) from e
            vec = [amps[k] for k in keys]
            outv = apply_mat(u, vec)
            out_w = [
                World(assign={src: keys[i]}, amp=outv[i])
                for i in range(len(keys))
                if abs(outv[i]) ** 2 > EPS
            ]
            return Joint(worlds=_coalesce(out_w))

        # ADR 0205 / LISS-0404: a single tuple-valued coordinate (e.g. from
        # prepare_selection) stands in for nq separate qubit wires -- same
        # Hamiltonian, same compile_sparse_pauli/expm_ih_apply primitives,
        # verified by direct execution to give physically identical
        # results to the nq-separate-names path below (ADR 0205 Context).
        if len(names) == 1:
            src = names[0]
            sample = next(
                (w.assign.get(src) for w in joint.worlds if src in w.assign), None
            )
            if isinstance(sample, tuple):
                if len(sample) != nq:
                    raise KernelError(
                        f"Operator needs {nq} qubit positions, tuple coordinate "
                        f"`{src}` has {len(sample)}"
                    )
                from .sparse_pauli import compile_sparse_pauli

                try:
                    terms = compile_sparse_pauli(
                        op_ast,
                        env=self.operators,
                        scalars=self.scalars,
                        n_qubits=nq,
                    )
                except ValueError as e:
                    raise KernelError(str(e)) from e
                return self._hamiltonian_evolve_tuple_coordinate(joint, src, nq, terms, t)

        # Multi-qubit Pauli H on names[0..nq) — sparse Pauli-sum + Taylor e^{-iHt}
        if len(names) < nq:
            raise KernelError(
                f"Operator needs {nq} qubit wires, bind has {len(names)}"
            )
        wires = names[:nq]
        from .sparse_pauli import compile_sparse_pauli, expm_ih_apply

        try:
            terms = compile_sparse_pauli(
                op_ast,
                env=self.operators,
                scalars=self.scalars,
                n_qubits=nq,
            )
        except ValueError as e:
            raise KernelError(str(e)) from e

        dim = 2**nq
        # Build amplitude vector over computational basis; other coords kept per world
        # Strategy: group worlds by non-wire assigns; within each group apply U on wire bits
        from collections import defaultdict

        groups: dict[tuple, list[World]] = defaultdict(list)
        for w in joint.worlds:
            key = tuple(sorted((k, v) for k, v in w.assign.items() if k not in wires))
            groups[key].append(w)

        out_worlds: list[World] = []
        for key, ws in groups.items():
            vec = [0j] * dim
            phases = {}
            for w in ws:
                bits = []
                ok = True
                for name in wires:
                    if name not in w.assign or w.assign[name] not in (0, 1):
                        ok = False
                        break
                    bits.append(int(w.assign[name]))
                if not ok:
                    raise KernelError(
                        f"hamiltonian evolve expects qubit bits on {wires}"
                    )
                idx = 0
                for b in bits:
                    idx = (idx << 1) | b
                vec[idx] += w.amp
                phases[idx] = dict(w.coord_phase)
            try:
                outv = expm_ih_apply(terms, t, vec)
            except ValueError as e:
                raise KernelError(str(e)) from e
            base_assign = dict(key)
            for idx, amp in enumerate(outv):
                if abs(amp) ** 2 <= EPS:
                    continue
                assign = dict(base_assign)
                # unpack bits MSB = wires[0]
                x = idx
                bit_list = []
                for _ in range(nq):
                    bit_list.append(x & 1)
                    x >>= 1
                bit_list.reverse()
                for name, bit in zip(wires, bit_list):
                    assign[name] = bit
                out_worlds.append(
                    World(
                        assign=assign,
                        amp=amp,
                        coord_phase=phases.get(idx, {}),
                    )
                )
        return Joint(worlds=_coalesce(out_worlds))

    def _hamiltonian_evolve_tuple_coordinate(
        self,
        joint: Joint,
        src: str,
        nq: int,
        terms: Any,
        t: float,
    ) -> Joint:
        """ADR 0205 / LISS-0404: same Pauli-sum evolution as the
        nq-separate-names path above, reading/writing one tuple-valued
        coordinate's `nq` positions instead of `nq` separate coordinate
        names. Verified by direct execution to give physically identical
        results to that path (ADR 0205 Context point 3).
        """
        from collections import defaultdict

        from .joint import World, _coalesce
        from .sparse_pauli import expm_ih_apply

        dim = 2**nq
        groups: dict[tuple, list[World]] = defaultdict(list)
        for w in joint.worlds:
            key = tuple(sorted((k, v) for k, v in w.assign.items() if k != src))
            groups[key].append(w)

        out_worlds: list[World] = []
        for key, ws in groups.items():
            vec = [0j] * dim
            phases: dict[int, dict[str, complex]] = {}
            for w in ws:
                pattern = w.assign[src]
                idx = 0
                for b in pattern:
                    idx = (idx << 1) | int(b)
                vec[idx] += w.amp
                phases[idx] = dict(w.coord_phase)
            outv = expm_ih_apply(terms, t, vec)
            base_assign = dict(key)
            for idx, amp in enumerate(outv):
                if abs(amp) ** 2 <= EPS:
                    continue
                x = idx
                bits = []
                for _ in range(nq):
                    bits.append(x & 1)
                    x >>= 1
                bits.reverse()
                assign = dict(base_assign)
                assign[src] = tuple(bits)
                out_worlds.append(
                    World(assign=assign, amp=amp, coord_phase=phases.get(idx, {}))
                )
        return Joint(worlds=_coalesce(out_worlds))

    def _evolve_precomputed_grid(
        self,
        joint: Joint,
        names: list[str],
        grid: GridHamiltonian,
        t: float,
    ) -> Joint:
        from .joint import World, _coalesce
        from .matrix import apply_mat, expm_ih

        if len(names) != 1:
            raise KernelError("grid Hamiltonian evolve requires a single bind name")
        src = names[0]
        amps = joint.amplitude_marginal(src)
        keys = sorted(amps.keys(), key=lambda x: float(x))
        if not keys or any(not isinstance(k, (int, float)) for k in keys):
            raise KernelError("grid evolve expects Float (or Int) abscissae")
        xs = list(grid.xs)
        if len(keys) != len(xs) or any(abs(float(k) - x) > 1e-9 for k, x in zip(keys, xs)):
            raise KernelError(
                "grid state abscissae must match the lowered discretization grid"
            )
        hmat = [list(row) for row in grid.matrix]
        u = expm_ih(hmat, t)
        vec = [amps[k] for k in keys]
        outv = apply_mat(u, vec)
        out_w = [
            World(assign={src: keys[i]}, amp=outv[i])
            for i in range(len(keys))
            if abs(outv[i]) ** 2 > EPS
        ]
        return Joint(worlds=_coalesce(out_w))

    def _operator_name(self, expr: Expr) -> str:
        if isinstance(expr, Var):
            return expr.name
        raise KernelError("hamiltonian / observable must be a named operator (X,Y,Z,…)")

    def _resolve_unitary_matrix(self, u_expr: Expr, n_wires: int) -> list[list[complex]]:
        """Resolve Operator / Hadamard / Pauli / S|T / rx|ry|rz → dense unitary."""
        from .hamiltonian import compile_hamiltonian, op_n_qubits
        from .unitaries import named_gate_matrix, rotation_gate_matrix
        from ..ast_nodes import Call, Var

        if isinstance(u_expr, Call) and isinstance(u_expr.callee, Var):
            op = u_expr.callee.name.lower()
            if op in {"rx", "ry", "rz"}:
                if len(u_expr.args) != 1:
                    raise KernelError(f"{op} requires (theta)")
                if n_wires != 1:
                    raise KernelError(f"{op} is 1-qubit; pass one target wire")
                theta = float(self._eval_value(u_expr.args[0], {}))
                return rotation_gate_matrix(op[1], theta)
            qft_mat = self._qft_family_matrix(u_expr, n_wires)
            if qft_mat is not None:
                return qft_mat

        if not isinstance(u_expr, Var):
            raise KernelError(
                "unitary must be an Operator / gate name / rx|ry|rz(theta)"
            )
        uname = u_expr.name
        if uname in self.operators:
            op_ast = self.operators[uname]
            from .qft_dense import DenseMatrixOp

            if isinstance(op_ast, DenseMatrixOp):
                if op_ast.n_qubits != n_wires:
                    raise KernelError(
                        f"Operator `{uname}` needs {op_ast.n_qubits} wires, "
                        f"got {n_wires}"
                    )
                return op_ast.matrix
            if isinstance(op_ast, Call):
                qft_mat = self._qft_family_matrix(op_ast, n_wires)
                if qft_mat is not None:
                    return qft_mat
            try:
                nq = op_n_qubits(op_ast, self.operators, self.scalars)
                if nq == 0:
                    raise KernelError("unitary apply does not support Fock N operators")
                if nq != n_wires:
                    raise KernelError(
                        f"Operator `{uname}` needs {nq} wires, got {n_wires}"
                    )
                return compile_hamiltonian(
                    op_ast,
                    env=self.operators,
                    scalars=self.scalars,
                    n_qubits=n_wires,
                )
            except ValueError as e:
                raise KernelError(str(e)) from e
        u_mat = named_gate_matrix(uname)
        if u_mat is None:
            raise KernelError(
                f"unknown unitary `{uname}` "
                "(Operator name, H/S/T, Pauli X|Y|Z|I, or rx|ry|rz(theta))"
            )
        if n_wires != 1:
            raise KernelError(f"gate `{uname}` is 1-qubit; pass one target wire")
        return u_mat

    def _qft_family_matrix(
        self, call: Call, n_wires: int
    ) -> list[list[complex]] | None:
        """Dense exact QFT family for Joint apply (LISS-0228)."""
        from .qft_dense import cqft_matrix, iqft_matrix, qft_matrix
        from ..ast_nodes import Var

        if not isinstance(call.callee, Var):
            return None
        name = call.callee.name
        if name not in {"qft", "iqft", "cqft", "ciqft"}:
            return None
        if name in {"qft", "iqft"}:
            if len(call.args) != 1 or not isinstance(call.args[0], Var):
                raise KernelError("qft/iqft requires a QubitRegister argument")
            n = self.static_register_sizes.get(call.args[0].name)
            if n is None:
                raise KernelError(
                    f"qft/iqft register `{call.args[0].name}` has no static size"
                )
            if n_wires != n:
                raise KernelError(
                    f"Operator `{name}` needs {n} wires, got {n_wires}"
                )
            return iqft_matrix(n) if name == "iqft" else qft_matrix(n)
        # cqft / ciqft
        if len(call.args) != 2 or not all(isinstance(a, Var) for a in call.args):
            raise KernelError(
                "cqft/ciqft requires QubitRegister control and target"
            )
        ctrl_n = self.static_register_sizes.get(call.args[0].name)  # type: ignore[union-attr]
        tgt_n = self.static_register_sizes.get(call.args[1].name)  # type: ignore[union-attr]
        if ctrl_n != 1 or tgt_n is None:
            raise KernelError(
                "cqft/ciqft requires QubitRegister<1> control and QubitRegister<N> target"
            )
        need = 1 + tgt_n
        if n_wires != need:
            raise KernelError(
                f"Operator `{name}` needs {need} wires, got {n_wires}"
            )
        return cqft_matrix(tgt_n, inverse=(name == "ciqft"))

    def _bind_apply(self, joint: Joint, name: str, expr: Call) -> Joint:
        """apply(U, w0[, w1, …]) — apply unitary matrix (not e^{-iHt})."""
        from .unitaries import apply_unitary_on_wires

        if len(expr.args) < 2:
            raise KernelError("apply requires (U, wire[, wire…])")
        u_expr = expr.args[0]
        wire_args = expr.args[1:]
        if not all(isinstance(a, Var) for a in wire_args):
            raise KernelError("apply wires must be state variables")
        wires = [a.name for a in wire_args]  # type: ignore[union-attr]
        # LISS-0112 Slice B: bare Identity is a no-op (preserves D=3 levels).
        if (
            isinstance(u_expr, Var)
            and u_expr.name.upper() in {"I", "ID", "IDENTITY"}
            and len(wires) == 1
        ):
            if name in wires:
                return joint
            w0 = wires[0]
            return joint.bind_pushforward(name, lambda a, w=w0: a[w])
        u_mat = self._resolve_unitary_matrix(u_expr, len(wires))
        try:
            updated = apply_unitary_on_wires(joint, wires, u_mat)
        except ValueError as e:
            raise KernelError(str(e)) from e

        if name in wires:
            return updated
        w0 = wires[0]
        return updated.bind_pushforward(name, lambda a, w=w0: a[w])

    def _is_unitary_name(self, name: str) -> bool:
        from .unitaries import named_gate_matrix

        return name in self.operators or named_gate_matrix(name) is not None

    def _split_capply_args(
        self, args: list
    ) -> tuple[list[str], list[int], Expr, list[str]]:
        """Parse capply(c0[, !c1…], U, t0[, …]) — polarity 1=filled, 0=open (`!`)."""
        from ..ast_nodes import UnaryNot

        u_idx = None
        for i, a in enumerate(args):
            if isinstance(a, Var) and self._is_unitary_name(a.name):
                u_idx = i
                break
        if u_idx is None:
            raise KernelError(
                "capply requires a unitary name (Operator / Hadamard / Pauli) "
                "between controls and targets"
            )
        if u_idx < 1:
            raise KernelError("capply requires at least one control before U")
        if u_idx >= len(args) - 1:
            raise KernelError("capply requires at least one target after U")
        ctrl_args = args[:u_idx]
        u_expr = args[u_idx]
        tgt_args = args[u_idx + 1 :]

        ctrls: list[str] = []
        poles: list[int] = []
        for a in ctrl_args:
            if isinstance(a, Var):
                ctrls.append(a.name)
                poles.append(1)
            elif isinstance(a, UnaryNot) and isinstance(a.expr, Var):
                ctrls.append(a.expr.name)
                poles.append(0)
            else:
                raise KernelError(
                    "capply controls must be state vars or open-polarity `!var`"
                )
        if not all(isinstance(a, Var) for a in tgt_args):
            raise KernelError("capply targets must be state variables")
        tgts = [a.name for a in tgt_args]  # type: ignore[union-attr]
        if len(set(ctrls + tgts)) != len(ctrls) + len(tgts):
            raise KernelError("capply wires must be distinct")
        return ctrls, poles, u_expr, tgts

    def _bind_capply(
        self,
        joint: Joint,
        name: str,
        expr: Call,
        *,
        force_all_open: bool = False,
        op_label: str = "capply",
    ) -> Joint:
        """capply / ocapply — filled, open, or mixed polarities (ADR 0048)."""
        from .unitaries import apply_unitary_on_wires, multi_controlled_unitary

        if len(expr.args) < 3:
            raise KernelError(f"{op_label} requires (ctrl[, …], U, tgt[, …])")
        ctrls, poles, u_expr, tgts = self._split_capply_args(list(expr.args))
        if force_all_open:
            poles = [0] * len(ctrls)
        u_mat = self._resolve_unitary_matrix(u_expr, len(tgts))
        mask = 0
        for p in poles:
            mask = (mask << 1) | p
        cu = multi_controlled_unitary(
            u_mat, n_controls=len(ctrls), active_mask=mask
        )
        wires = [*ctrls, *tgts]
        try:
            updated = apply_unitary_on_wires(joint, wires, cu)
        except ValueError as e:
            raise KernelError(str(e)) from e
        if name in wires:
            return updated
        t0 = tgts[0]
        return updated.bind_pushforward(name, lambda a, w=t0: a[w])

    def _bind_ket(self, joint: Joint, name: str, expr: KetLit) -> Joint:
        from .joint import World, _coalesce
        from .quantum_ops import ket_support

        try:
            pairs = ket_support(expr.label)
        except ValueError as e:
            raise KernelError(str(e)) from e
        if joint.is_vacuum():
            return Joint.empty()
        out: list[World] = []
        for w in joint.worlds:
            for val, amp in pairs:
                na = w.amp * amp
                if abs(na) ** 2 > EPS:
                    out.append(
                        World(
                            assign={**w.assign, name: val},
                            amp=na,
                            coord_phase=dict(w.coord_phase),
                        )
                    )
        return Joint(worlds=_coalesce(out))

    def _bind(
        self,
        joint: Joint,
        name: str,
        expr: Expr,
        *,
        logs: list[str] | None = None,
        inspect_out: MeasureSinkPort | None = None,
    ) -> Joint:
        if isinstance(expr, Inspect):
            # identity bind of inner; side-effect host log
            marg = self._expr_marginal(joint, expr.expr)
            text = format_marginal_table(marg, label=expr.label)
            if inspect_out is not None:
                inspect_out.write(text)
            if logs is not None:
                logs.append(f"inspect:{expr.label or ''}:{marg}")
            return self._bind(joint, name, expr.expr, logs=logs, inspect_out=inspect_out)
        if isinstance(expr, Coin):
            return joint.bind_split(name, {0: 0.5, 1: 0.5})
        if isinstance(expr, Vacuum):
            return Joint.empty()
        if isinstance(expr, KetLit):
            return self._bind_ket(joint, name, expr)
        if isinstance(expr, KetSumBinder):
            return self._bind_ket_sum_binder(joint, name, expr)
        if isinstance(expr, NormExpr):
            # LISS-0426: `Float n = ||state_expr||` as a top-level bind
            # (as opposed to the `<state> / ||<state>||` division case,
            # handled separately below since that needs the numerator's
            # own bind too).
            norm = self._compute_norm(joint, expr.state)
            return joint.bind_const(name, norm)
        if isinstance(expr, SetComprehension):
            # LISS-0429: `Set F = { x In D : cond1, cond2, ... }` -- a
            # pure classical computation (the comprehension's own bound
            # variable ranges over `D`, never a per-World assign value),
            # so it needs no Joint access beyond the uniform `bind_const`
            # wrapper every World shares.
            elements = self._eval_set_comprehension(expr, {})
            return joint.bind_const(name, elements)
        if isinstance(expr, OpBinder):
            # LISS-0424: an OpBinder reaching general `_bind` (as opposed
            # to the separate `Operator H = ...` statement-level dispatch,
            # which never calls `_bind` at all) means the surrounding
            # declared type is non-Operator -- a classical numeric
            # Sigma/Pi, e.g. `Int total = Sigma (i In 0..n-1) { x[i] }`.
            return joint.bind_pushforward(
                name, lambda a: self._eval_classical_op_binder(expr, a)
            )
        if isinstance(expr, Dirac):
            if self._is_closed(expr.arg):
                return joint.bind_const(name, self._eval_value(expr.arg, {}))
            return joint.bind_pushforward(name, lambda a: self._eval_value(expr.arg, a))
        if isinstance(expr, (LitInt, LitFloat, LitBool, LitString)):
            return joint.bind_const(name, self._lit(expr))
        if isinstance(expr, Var):
            return joint.bind_pushforward(
                name,
                lambda a: a[resolve_scientific_binding(expr.name, a)],
            )
        if isinstance(expr, BinOp) and expr.op == "*":
            # LISS-0420: `classical_scalar * <State-producing expr>` (e.g.
            # `(1.0/sqrt(2.0^n)) * Sigma (x In {0,1}^n) { |x> }`) -- scale
            # the sub-expression's own amplitudes by the classical scalar,
            # rather than treating the whole BinOp as a pure classical
            # pushforward (which cannot evaluate a State-producing node at
            # all, e.g. KetLit/KetSumBinder). General, not special-cased to
            # just KetSumBinder: any State-producing node type recognized
            # here on exactly one side triggers this path.
            lhs_state = self._is_state_producing_bind_expr(expr.lhs)
            rhs_state = self._is_state_producing_bind_expr(expr.rhs)
            if lhs_state != rhs_state:
                state_expr = expr.lhs if lhs_state else expr.rhs
                scalar_expr = expr.rhs if lhs_state else expr.lhs
                return self._bind_scaled_state(joint, name, state_expr, scalar_expr)
        if isinstance(expr, BinOp) and expr.op == "/" and isinstance(expr.rhs, NormExpr):
            # LISS-0426: `<state-expr> / ||<state-expr>||` -- the literal
            # transcription of X/||X||. Binds the numerator's own
            # sub-expression (whatever shape `_bind` already knows how to
            # handle, e.g. a `project(...)` Call), computes the norm's
            # inner expression as its own independent bind (matching the
            # equation's own literal repetition of the numerator inside
            # the norm bars), and divides every amplitude by that norm.
            return self._bind_state_divided_by_norm(joint, name, expr.lhs, expr.rhs)
        if isinstance(expr, BinOp):
            return joint.bind_pushforward(name, lambda a: self._eval_value(expr, a))
        if isinstance(expr, Attr):
            return joint.bind_pushforward(name, lambda a: self._eval_value(expr, a))
        if isinstance(expr, UnitConvert):
            return joint.bind_pushforward(name, lambda a: self._eval_value(expr, a))
        if isinstance(expr, WhenExpr):
            return self._bind_when(joint, name, expr)
        if isinstance(expr, SuperposeExpr):
            # LISS-0320: superpose has a real grammar/AST/type boundary, but
            # coherent amplitude/phase execution is a separate, later slice.
            # Fail closed with one explicit diagnostic rather than crash with
            # an unhandled-node error or silently run mix/Mixture semantics.
            raise KernelDiagnosticError(
                "COHERENT_EXECUTION_UNSUPPORTED",
                "`superpose` type-checks but coherent amplitude/phase "
                "execution is not yet implemented in the Static Kernel",
                line=expr.span.line,
                col=expr.span.col,
            )
        if isinstance(expr, Call):
            return self._bind_call(joint, name, expr)
        if isinstance(expr, Pipe):
            fused = self._try_bind_fused_unary_pipe(
                joint, name, expr, logs=logs, inspect_out=inspect_out
            )
            if fused is not None:
                return fused
            if isinstance(expr.rhs, Call):
                return self._bind_call(joint, name, self._piped_call(expr))
            if isinstance(expr.rhs, Var):
                # ADR 0152: tuple |> multi-hole Partial → fill all remaining holes.
                if isinstance(expr.lhs, TupleExpr):
                    partial = self.objects.get(expr.rhs.name)
                    if isinstance(partial, PartialValue):
                        need = sum(1 for s in partial.slots if s is None)
                        if need == len(expr.lhs.items):
                            synthetic = Call(
                                callee=expr.rhs,
                                args=list(expr.lhs.items),
                                span=expr.span,
                            )
                            return self._bind_call(joint, name, synthetic)
                synthetic = Call(
                    callee=expr.rhs, args=[expr.lhs], span=expr.span
                )
                return self._bind_call(joint, name, synthetic)
            raise KernelError(
                "PIPE_CALLABLE_ERROR: pipeline right-hand side must be a function call "
                "or unary fn name"
            )
        if isinstance(expr, EvolveExpr):
            return self._bind_evolve(joint, [name], expr)
        if isinstance(expr, BlockExpr):
            return self._bind_block_expr(joint, name, expr)
        if isinstance(expr, TensorExpr):
            raise KernelError("tensor product requires tuple bind `(a, b) = left *|* right`")
        raise KernelError(f"cannot bind expr {type(expr).__name__}")

    def _bind_block_expr(self, joint: Joint, name: str, expr: BlockExpr) -> Joint:
        """ADR 0153: evaluate bare `{ let …; result }` then Trace-Out dead lets."""
        pre_live = self._joint_coord_names(joint)
        for let in expr.lets:
            ln = let.name
            le = let.expr
            if isinstance(le, Call):
                joint = self._bind(joint, ln, le)
            else:
                joint = joint.bind_pushforward(
                    ln, lambda a, e=le: self._eval_value(e, a)
                )
        res = expr.result
        if isinstance(res, Call):
            joint = self._bind(joint, name, res)
        else:
            joint = joint.bind_pushforward(
                name, lambda a, e=res: self._eval_value(e, a)
            )
        return self._trace_out_dead_fn_locals(joint, pre_live, [name])

    def _try_bind_fused_unary_pipe(
        self,
        joint: Joint,
        name: str,
        expr: Pipe,
        *,
        logs: list[str] | None = None,
        inspect_out: MeasureSinkPort | None = None,
    ) -> Joint | None:
        """ADR 0137 / 0141 / 0143 / 0152: fuse pure pipe chains into one Joint pass."""
        base, stages = self._flatten_pipe(expr)
        # ADR 0152: peel tuple+multi-hole Call into a fully applied Call base so
        # Fusion never binds a TupleExpr wire.
        if (
            stages
            and isinstance(base, TupleExpr)
            and isinstance(stages[0], Call)
        ):
            peeled = self._piped_call(
                Pipe(lhs=base, rhs=stages[0], span=expr.span)
            )
            base = peeled
            stages = stages[1:]
        if len(stages) < 2:
            return None
        resolved: list[tuple[FunDecl, list[Expr | None]]] = []
        for stage in stages:
            item = self._resolve_fuse_stage(stage)
            if item is None:
                return None
            resolved.append(item)
        # Materialize base once into the destination name, then fold stages.
        joint = self._bind(joint, name, base, logs=logs, inspect_out=inspect_out)
        # ADR 0141 / 0157: algebraic collapse — affine or poly≤N unary returns.
        if all(
            len(slots) == 1 and slots[0] is None for _fun, slots in resolved
        ):
            funs = [fun for fun, _slots in resolved]
            returns = [self._fuse_simple_return(fun) for fun in funs]
            if all(r is not None for r in returns):
                rets = [r for r in returns if r is not None]
                composed_poly = self._compose_poly_pipe(funs, rets)
                if composed_poly is not None:
                    coeffs = composed_poly
                    if len(coeffs) <= 2 or (
                        len(coeffs) == 3 and abs(coeffs[2]) < 1e-15
                    ):
                        # Preserve affine evidence shape for ADR 0141 tests.
                        scale = coeffs[1] if len(coeffs) > 1 else 0.0
                        bias = coeffs[0] if coeffs else 0.0
                        self.last_algebraic_fusion = (scale, bias)
                        self.last_poly_fusion = None
                    else:
                        self.last_algebraic_fusion = None
                        self.last_poly_fusion = tuple(coeffs)
                    joint = joint.bind_pushforward(
                        name,
                        lambda a, c=coeffs, src=name: Evaluator._eval_poly(
                            c, a[src]
                        ),
                    )
                    return joint
        self.last_algebraic_fusion = None
        self.last_poly_fusion = None
        for fun, slots in resolved:
            ret = self._fuse_simple_return(fun)
            assert ret is not None
            joint = joint.bind_pushforward(
                name,
                lambda a, f=fun, sl=slots, e=ret, src=name: self._eval_fused_stage(
                    a, f, sl, e, src
                ),
            )
        return joint

    def _resolve_fuse_stage(
        self, stage: Expr
    ) -> tuple[FunDecl, list[Expr | None]] | None:
        """ADR 0143: bare unary fn, one-hole Call, or one-hole PartialValue."""
        if isinstance(stage, Var):
            fun = self.funs.get(stage.name)
            if (
                fun is not None
                and len(fun.params) == 1
                and not fun.effects
                and self._fuse_simple_return(fun) is not None
            ):
                return fun, [None]
            partial = self.objects.get(stage.name)
            if isinstance(partial, PartialValue):
                fun = self.funs.get(partial.fun_name)
                if (
                    fun is None
                    or fun.effects
                    or len(fun.params) != len(partial.slots)
                    or self._fuse_simple_return(fun) is None
                ):
                    return None
                if sum(1 for s in partial.slots if s is None) != 1:
                    return None
                return fun, list(partial.slots)
            return None
        if isinstance(stage, Call):
            if not isinstance(stage.callee, Var):
                return None
            if sum(1 for a in stage.args if isinstance(a, Hole)) != 1:
                return None
            fun = self.funs.get(stage.callee.name)
            if (
                fun is None
                or fun.effects
                or len(fun.params) != len(stage.args)
                or self._fuse_simple_return(fun) is None
            ):
                return None
            slots: list[Expr | None] = [
                None if isinstance(a, Hole) else a for a in stage.args
            ]
            return fun, slots
        return None

    def _eval_fused_stage(
        self,
        assign: dict[str, Any],
        fun: FunDecl,
        slots: list[Expr | None],
        ret: Expr,
        src: str,
    ) -> Any:
        env = dict(assign)
        for param, slot in zip(fun.params, slots):
            if slot is None:
                env[param.name] = assign[src]
            else:
                env[param.name] = self._eval_value(slot, assign)
        return self._eval_value(ret, env)

    def _compose_affine_pipe(
        self, funs: list[FunDecl], returns: list[Expr]
    ) -> tuple[float, float] | None:
        """Compose affine maps (ADR 0141); thin wrapper over poly compose."""
        poly = self._compose_poly_pipe(funs, returns)
        if poly is None or len(poly) > 2:
            if poly is not None and len(poly) == 3 and abs(poly[2]) < 1e-15:
                return (poly[1], poly[0])
            return None
        if len(poly) == 1:
            return (0.0, poly[0])
        return (poly[1], poly[0])

    def _compose_poly_pipe(
        self, funs: list[FunDecl], returns: list[Expr]
    ) -> list[float] | None:
        """Compose unary returns as polynomials (ADR 0157); coeffs low→high."""
        coeffs = [0.0, 1.0]  # identity
        for fun, ret in zip(funs, returns):
            parsed = self._parse_poly(ret, fun.params[0].name)
            if parsed is None:
                return None
            coeffs = self._compose_poly(parsed, coeffs)
            if len(coeffs) > 8:
                return None
        return coeffs

    @staticmethod
    def _eval_poly(coeffs: list[float], x: Any) -> Any:
        """Horner evaluation of coeffs[0] + coeffs[1]·x + …"""
        acc: Any = 0.0
        for c in reversed(coeffs):
            acc = acc * x + c
        return acc

    @staticmethod
    def _compose_poly(outer: list[float], inner: list[float]) -> list[float]:
        """Return coeffs of outer(inner(x))."""
        # outer = Σ o_k y^k ; y = inner(x)
        result = [0.0]
        power = [1.0]  # y^0
        for o in outer:
            # result += o * power
            for i, p in enumerate(power):
                if i >= len(result):
                    result.extend([0.0] * (i + 1 - len(result)))
                result[i] += o * p
            # power *= inner
            power = Evaluator._mul_poly(power, inner)
        while len(result) > 1 and abs(result[-1]) < 1e-15:
            result.pop()
        return result

    def _run_unit_body(
        self, unit: CompilationUnit, *, stdout: TextIO | None = None
    ) -> EvalResult:
        """Compatibility name for internal tests; canonical paths do not call it."""

        return self._run_legacy_ast_body(unit, stdout=stdout)

    @staticmethod
    def _mul_poly(a: list[float], b: list[float]) -> list[float]:
        out = [0.0] * (len(a) + len(b) - 1)
        for i, x in enumerate(a):
            for j, y in enumerate(b):
                out[i + j] += x * y
        return out

    @staticmethod
    def _add_poly(a: list[float], b: list[float], sign: float = 1.0) -> list[float]:
        n = max(len(a), len(b))
        out = [0.0] * n
        for i in range(n):
            out[i] = (a[i] if i < len(a) else 0.0) + sign * (
                b[i] if i < len(b) else 0.0
            )
        while len(out) > 1 and abs(out[-1]) < 1e-15:
            out.pop()
        return out

    @classmethod
    def _parse_poly(cls, expr: Expr, param: str) -> list[float] | None:
        """Parse polynomial in `param` over +,-,* and numeric literals (ADR 0157)."""
        if isinstance(expr, Var):
            if expr.name == param:
                return [0.0, 1.0]
            return None
        if isinstance(expr, LitInt):
            return [float(expr.value)]
        if isinstance(expr, LitFloat):
            return [float(expr.value)]
        if isinstance(expr, BinOp):
            left = cls._parse_poly(expr.lhs, param)
            right = cls._parse_poly(expr.rhs, param)
            if left is None or right is None:
                return None
            if expr.op == "+":
                return cls._add_poly(left, right, 1.0)
            if expr.op == "-":
                return cls._add_poly(left, right, -1.0)
            if expr.op == "*":
                return cls._mul_poly(left, right)
            return None
        return None

    @classmethod
    def _parse_affine(cls, expr: Expr, param: str) -> tuple[float, float] | None:
        """Parse affine map; delegates to poly parse (degree ≤ 1)."""
        poly = cls._parse_poly(expr, param)
        if poly is None or len(poly) > 2:
            return None
        if len(poly) == 1:
            return (0.0, poly[0])
        return (poly[1], poly[0])

    @staticmethod
    def _flatten_pipe(expr: Pipe) -> tuple[Expr, list[Expr]]:
        """Return (base, [stage1, stage2, …]) for a left-associative pipe chain."""
        stages: list[Expr] = []
        cur: Expr = expr
        while isinstance(cur, Pipe):
            stages.append(cur.rhs)
            cur = cur.lhs
        stages.reverse()
        return cur, stages

    @staticmethod
    def _fuse_simple_return(fun: FunDecl) -> Expr | None:
        """Eligible bodies: no mid StateBind; explicit return / block result only."""
        for stmt in fun.body.stmts:
            if isinstance(stmt, ReturnStmt):
                return stmt.expr
            if isinstance(stmt, (Measure, Snapshot, StateBind, ForEachStmt)):
                return None
            if isinstance(stmt, ExprStmt):
                return None
        return fun.body.result

    @staticmethod
    def _piped_call(expr: Pipe) -> Call:
        rhs = expr.rhs
        if not isinstance(rhs, Call):
            raise KernelError(
                "PIPE_CALLABLE_ERROR: pipeline right-hand side must be a function call"
            )
        # ADR 0152: Tuple LHS + N holes → fill all holes left-to-right.
        hole_idxs = [i for i, a in enumerate(rhs.args) if isinstance(a, Hole)]
        if (
            hole_idxs
            and isinstance(expr.lhs, TupleExpr)
            and len(expr.lhs.items) == len(hole_idxs)
        ):
            it = iter(expr.lhs.items)
            args = [next(it) if isinstance(a, Hole) else a for a in rhs.args]
            return Call(callee=rhs.callee, args=args, span=rhs.span)
        # ADR 0133: Call with `_` holes → fill leftmost hole; else prepend.
        if any(isinstance(a, Hole) for a in rhs.args):
            args: list[Expr] = []
            filled = False
            for a in rhs.args:
                if not filled and isinstance(a, Hole):
                    args.append(expr.lhs)
                    filled = True
                else:
                    args.append(a)
            return Call(callee=rhs.callee, args=args, span=rhs.span)
        return Call(callee=rhs.callee, args=[expr.lhs, *rhs.args], span=rhs.span)

    def _bind_when(self, joint: Joint, name: str, expr: WhenExpr) -> Joint:
        if joint.is_vacuum():
            return Joint.empty()
        out_worlds = []
        from .joint import World, _coalesce

        for w in joint.worlds:
            for ctrl, cp in self._ctrl_masses(expr.ctrl, w.assign).items():
                if cp <= EPS:
                    continue
                arm_body = None
                for arm in expr.arms:
                    if arm.is_else:
                        continue
                    if _pat_match(arm.pat, ctrl):
                        arm_body = arm.body
                        break
                if arm_body is None:
                    for arm in expr.arms:
                        if arm.is_else:
                            arm_body = arm.body
                            break
                if arm_body is None:
                    continue
                amp = w.amp * cmath.sqrt(cp)
                if isinstance(arm_body, Coin):
                    for val, p in ((0, 0.5), (1, 0.5)):
                        out_worlds.append(
                            World(
                                assign={**w.assign, name: val},
                                amp=amp * cmath.sqrt(p),
                                coord_phase=dict(w.coord_phase),
                            )
                        )
                elif isinstance(arm_body, KetLit):
                    # LISS-0138: prepare branching with ket arms (Never Leave
                    # the State — mixture of computational / ± supports).
                    from .quantum_ops import ket_support

                    try:
                        pairs = ket_support(arm_body.label)
                    except ValueError as e:
                        raise KernelError(str(e)) from e
                    for val, kamp in pairs:
                        na = amp * kamp
                        if abs(na) ** 2 > EPS:
                            out_worlds.append(
                                World(
                                    assign={**w.assign, name: val},
                                    amp=na,
                                    coord_phase=dict(w.coord_phase),
                                )
                            )
                else:
                    val = self._eval_value(arm_body, w.assign)
                    out_worlds.append(
                        World(
                            assign={**w.assign, name: val},
                            amp=amp,
                            coord_phase=dict(w.coord_phase),
                        )
                    )
        if not out_worlds:
            return Joint.empty()
        return Joint(worlds=_coalesce(out_worlds))

    def _ctrl_masses(self, ctrl: Expr, assign: dict[str, Any]) -> dict[Any, float]:
        if isinstance(ctrl, Coin):
            return {0: 0.5, 1: 0.5}
        if isinstance(ctrl, Var):
            if ctrl.name in assign:
                return {assign[ctrl.name]: 1.0}
            # LISS-0225: classical enum / object binds live in self.objects.
            if ctrl.name in self.objects:
                return {self.objects[ctrl.name]: 1.0}
            if ctrl.name in self.scalars:
                return {self.scalars[ctrl.name]: 1.0}
            raise KernelError(
                f"when control `{ctrl.name}` is not bound in this world"
            )
        if isinstance(ctrl, (LitInt, LitFloat, LitBool)):
            return {self._lit(ctrl): 1.0}
        v = self._eval_value(ctrl, assign)
        return {v: 1.0}

    def _expr_qualname(self, expr: Expr) -> str | None:
        """`Topology.ChainLattice` path from Var/Attr chain."""
        if isinstance(expr, Var):
            return expr.name
        if isinstance(expr, Attr):
            base = self._expr_qualname(expr.obj)
            if base is None:
                return None
            return f"{base}.{expr.name}"
        return None

    def _construct_instance(self, class_name: str, expr: Expr) -> ClassInstance:
        cls = self.classes.get(class_name)
        if cls is None:
            raise KernelError(f"unknown class `{class_name}`")
        if not isinstance(expr, Call):
            raise KernelError(
                f"class `{class_name}` instance requires `{cls.qualified_name}(…)`"
            )
        q = self._expr_qualname(expr.callee)
        if q is not None and q not in self.classes:
            raise KernelError(f"unknown constructor `{q}()`")

        init = next((m for m in cls.methods if m.name == "init"), None)
        if expr.args and init is None:
            raise KernelError(
                f"`{cls.qualified_name}(…)` has no `fn init`; "
                f"use defaults or declare `fn init(...)`"
            )
        if init is not None and len(expr.args) != len(init.params):
            raise KernelError(
                f"`{cls.qualified_name}(…)` / `init` expects {len(init.params)} args, "
                f"got {len(expr.args)}"
            )

        fields: dict[str, Any] = {}
        mutable: set[str] = set()
        for fbind in cls.fields:
            if len(fbind.names) != 1:
                raise KernelError("class field must be a single name")
            fields[fbind.names[0]] = self._eval_value(fbind.expr, {})
        for mem in cls.members:
            if mem.default is not None:
                fields[mem.name] = self._eval_value(mem.default, {})
            if mem.mutable:
                mutable.add(mem.name)

        inst = ClassInstance(
            class_name=cls.qualified_name, fields=fields, mutable=mutable
        )
        if init is not None:
            self._run_init(inst, init, list(expr.args))
        else:
            # No init: every member must already have a default
            for mem in cls.members:
                if mem.name not in inst.fields:
                    raise KernelError(
                        f"class `{cls.qualified_name}` member `{mem.name}` needs a "
                        f"default or `fn init`"
                    )
        for mem in cls.members:
            if mem.name not in inst.fields:
                raise KernelError(
                    f"class `{cls.qualified_name}` field `{mem.name}` was not "
                        f"initialized by `fn init`"
                )
        return inst

    def _run_init(
        self, receiver: ClassInstance, init: FunDecl, args: list[Expr]
    ) -> None:
        """Execute `fn init(...)` — may assign `val` fields; no return bind required."""
        prev_this = self._this
        prev_init = self._in_init
        prev_frame = self._frame_units
        self._this = receiver
        self._in_init = True
        self._frame_units = {}
        local: dict[str, Any] = dict(receiver.fields)
        try:
            for param, arg in zip(init.params, args):
                if isinstance(arg, Var) and arg.name in self.objects:
                    obj = self.objects[arg.name]
                    local[param.name] = (
                        obj.copy() if isinstance(obj, StructValue) else obj
                    )
                else:
                    v, unit = self._eval_value_with_unit(arg, {})
                    local[param.name] = (
                        v.copy() if isinstance(v, StructValue) else v
                    )
                    if unit is not None:
                        self._frame_units[param.name] = unit
            for stmt in init.body.stmts:
                if isinstance(stmt, (Measure, Snapshot)):
                    raise KernelError("`measure`/`snapshot` forbidden inside `init`")
                if isinstance(stmt, ReturnStmt):
                    raise KernelError("`init` cannot return a value")
                if isinstance(stmt, AssignStmt):
                    self._exec_assign(stmt, local)
                    local.update(receiver.fields)
                    continue
                if isinstance(stmt, StateBind):
                    if len(stmt.names) != 1:
                        raise KernelError("`init` binds must be single-name")
                    val = self._eval_value(stmt.expr, local)
                    local[stmt.names[0]] = val
                else:
                    raise KernelError(
                        f"unsupported stmt in `init`: {type(stmt).__name__}"
                    )
        finally:
            self._this = prev_this
            self._in_init = prev_init
            self._frame_units = prev_frame

    def _construct_struct(
        self, struct_name: str, expr: Expr, assign: dict[str, Any] | None = None
    ) -> StructValue:
        st = self.structs.get(struct_name)
        if st is None:
            raise KernelError(f"unknown struct `{struct_name}`")
        if not isinstance(expr, Call):
            raise KernelError(
                f"struct `{struct_name}` requires `{st.qualified_name}(…)`"
            )
        q = self._expr_qualname(expr.callee)
        if q is not None and q not in self.structs:
            raise KernelError(f"unknown struct constructor `{q}()`")
        # Positional args, named kwargs (ADR 0181), or all-defaults.
        fields: dict[str, Any] = {}
        field_units: dict[str, str] = {}
        kwargs = getattr(expr, "kwargs", None) or []
        if kwargs and expr.args:
            raise KernelError(
                f"`{st.qualified_name}`: cannot mix positional and named fields"
            )
        if kwargs:
            by_name = {k: v for k, v in kwargs}
            for mem in st.fields:
                if mem.name not in by_name:
                    if mem.default is None:
                        raise KernelError(
                            f"struct `{st.qualified_name}` missing field `{mem.name}`"
                        )
                    val, unit = self._eval_value_with_unit(mem.default, {})
                else:
                    val, unit = self._eval_struct_arg(by_name[mem.name], assign)
                fields[mem.name] = val
                self._put_unit(field_units, mem.name, unit)
            extra = set(by_name) - {m.name for m in st.fields}
            if extra:
                raise KernelError(
                    f"struct `{st.qualified_name}` unknown fields: "
                    f"{', '.join(sorted(extra))}"
                )
        elif not expr.args:
            for mem in st.fields:
                if mem.default is None:
                    raise KernelError(
                        f"struct `{st.qualified_name}` field `{mem.name}` "
                        f"requires a constructor argument"
                    )
                val, unit = self._eval_value_with_unit(mem.default, {})
                fields[mem.name] = val
                self._put_unit(field_units, mem.name, unit)
        else:
            if len(expr.args) != len(st.fields):
                raise KernelError(
                    f"`{st.qualified_name}(…)` expects {len(st.fields)} args, "
                    f"got {len(expr.args)}"
                )
            for mem, arg in zip(st.fields, expr.args):
                # ADR 0181 / LISS-0277: resolve object locals (nested packs).
                val, unit = self._eval_struct_arg(arg, assign)
                fields[mem.name] = val
                self._put_unit(field_units, mem.name, unit)
        return StructValue(
            struct_name=st.qualified_name, fields=fields, field_units=field_units
        )

    def _eval_struct_arg(
        self, arg: Expr, assign: dict[str, Any] | None = None
    ) -> tuple[Any, str | None]:
        """Evaluate a struct field argument, including nested object Vars.

        ``assign`` is the enclosing free-fn's local frame (LISS-0338 /
        LISS-0353), so a struct constructed inside a free function's own
        `return Simple(a, b)` can resolve `a`/`b` as parameters, not just
        globally-registered `self.objects` names.
        """
        if isinstance(arg, Var) and assign is not None and arg.name in assign:
            val = assign[arg.name]
            if isinstance(val, StructValue):
                return val.copy(), None
            return val, None
        if isinstance(arg, Var) and arg.name in self.objects:
            obj = self.objects[arg.name]
            if isinstance(obj, StructValue):
                return obj.copy(), None
            return obj, None
        return self._eval_value_with_unit(arg, assign or {})

    def _looks_like_operator_rhs(self, expr: Expr) -> bool:
        """ADR 0180: heuristic for untyped Operator algebra binds."""
        from ..ast_nodes import OpAttr, OpCall, OpIndexed, OpPauli

        if isinstance(
            expr, (OpVar, OpBin, OpLit, OpBinder, OpIndexed, OpCall, OpAttr, OpPauli)
        ):
            return True
        if isinstance(expr, BinOp) and expr.op in {"+", "-", "*"}:
            return self._looks_like_operator_rhs(expr.lhs) or self._looks_like_operator_rhs(
                expr.rhs
            )
        if isinstance(expr, Var) and expr.name in {"X", "Y", "Z", "I", "H"}:
            return True
        if isinstance(expr, Call) and isinstance(expr.callee, Var):
            if expr.callee.name in self.funs:
                return False
        return False

    def _resolve_operator_expr(
        self,
        expr: Any,
        *,
        objects: Mapping[str, Any] | None = None,
        extra_arrays: Mapping[str, Any] | None = None,
    ) -> Any:
        """Resolve an explicit Operator value/factory without leaking locals.

        `objects` (LISS-0410): the struct/class-instance context `OpAttr`
        resolution should use. Defaults to `self.objects` (module scope);
        `_resolve_operator_factory_call` passes its own param-name-rekeyed
        `attr_objects` here for a factory function's own local `Operator`
        binds, so `c.defect` resolves against the callee's parameter `c`,
        not a same-named (or absent) module-level object.
        `extra_arrays` (LISS-0434): a factory's own param-name-rekeyed
        `Float[N]…` arrays -- needed here (not only in the caller's later
        `_materialize_op` pass) once a scalar-parameterized binder domain
        (e.g. `Sigma (i In 0..n-1)` where `n` is this call's own scalar
        parameter) makes this same call eagerly lower the binder's body
        too, instead of leaving it for the deferred pass.
        """
        if isinstance(expr, OpVar) and expr.name in self.grid_hamiltonians:
            return GridHamiltonianRef(expr.name)
        if isinstance(expr, Var) and expr.name in self.grid_hamiltonians:
            return GridHamiltonianRef(expr.name)
        if isinstance(expr, OpVar) and expr.name in self.operators:
            return self.operators[expr.name]
        if isinstance(expr, Var) and expr.name in self.operators:
            return self.operators[expr.name]
        if isinstance(expr, Call) and isinstance(expr.callee, Var):
            fun = self.funs.get(expr.callee.name)
            if fun is not None:
                return self._resolve_operator_factory_call(expr, fun)
        # LISS-0139: Operator H = recv.method(…)
        if isinstance(expr, Call) and isinstance(expr.callee, Attr):
            return self._resolve_operator_method_call(expr)
        return self._lower_operator_value(
            expr, objects=objects, extra_arrays=extra_arrays
        )

    def _operator_array_context(self) -> dict[str, Any]:
        """Merged Float[N]… coefficient arrays (literal + Host-resolved,
        ADR 0119/LISS-0406) visible at `main` level, for binder lowering
        anywhere an Operator AST needs it (LISS-0407)."""
        from ..finite_binder import _collect_float_arrays

        unit = getattr(self, "_unit", None)
        if unit is None:
            return {}
        arrays = dict(_collect_float_arrays(unit))
        arrays.update(getattr(self, "_resolved_host_arrays", None) or {})
        return arrays

    def _op_expr_arg_to_source_expr(self, arg: Any, call_name: str) -> Any:
        """Convert an OpExpr Call argument (OpVar/OpLit) into the generic
        Expr shape `_resolve_operator_factory_call` already understands,
        so a nested Operator-returning call found anywhere inside a
        larger Operator expression (LISS-0407) can reuse that existing,
        tested arg-binding logic unchanged."""
        if isinstance(arg, OpVar):
            return Var(name=arg.name, span=arg.span)
        if isinstance(arg, OpLit):
            return LitFloat(value=arg.value, span=arg.span)
        raise KernelError(
            f"unsupported argument shape `{type(arg).__name__}` in "
            f"nested Operator call `{call_name}`"
        )

    def _resolve_op_call(self, call: "OpCall") -> Any:
        """Inline a call to a known Operator-returning function found
        anywhere inside an Operator expression tree, not only when it is
        the entire right-hand side (LISS-0407, closes the LISS-0402
        "Operator-Call-inline" gap: `scale * f(weights)` previously
        raised `cannot compile sparse Pauli for OpCall`).

        A call to anything else (e.g. binder-internal `next`/`wrap`
        helpers, LISS-0373) is left untouched -- those are resolved by a
        separate, unrelated mechanism inside binder lowering."""
        fun = self.funs.get(call.name)
        if fun is None or fun.return_type is None or fun.return_type.name != "Operator":
            return call
        call_args = [
            self._op_expr_arg_to_source_expr(a, call.name) for a in call.args
        ]
        synthetic = Call(
            callee=Var(name=call.name, span=call.span),
            args=call_args,
            span=call.span,
        )
        return self._resolve_operator_factory_call(synthetic, fun)

    def _resolve_operator_tree(
        self,
        expr: Any,
        *,
        arrays: Mapping[str, Any],
        objects: Mapping[str, Any] | None = None,
    ) -> Any:
        """Single recursive resolution pass over an Operator AST
        (LISS-0407 / ADR 0206, completed LISS-0410): resolves `OpAttr`
        struct-field coefficients, inlines Operator-returning function
        calls found anywhere in the tree, then lowers any remaining
        finite binder against the merged array context. Preserves
        object identity when a subtree needs no change.

        LISS-0410: `OpAttr` used to be resolved by a separate, bolted-on
        call (`materialize_op_attrs`) reachable only from `evolve`'s own
        call site and the factory-call path -- `apply`/`capply`
        (`_resolve_unitary_matrix`) read `self.operators[name]` directly
        with no resolution step at all, so a struct-field coefficient
        that already worked for `evolve` still failed for `apply`/
        `capply`. Folding `OpAttr` in here makes every `Operator`
        StateBind fully resolved by the time it's stored, so any later
        consumer that just reads `self.operators[name]` sees a clean
        tree for free."""
        from ..finite_binder import _contains_binder, _lower_operator_expr
        from .op_attr_elaboration import OpAttrElaborationError, _op_attr_float

        resolved_objects = self.objects if objects is None else objects

        if isinstance(expr, OpAttr):
            try:
                value = _op_attr_float(expr, resolved_objects)
            except OpAttrElaborationError as exc:
                raise KernelError(str(exc)) from exc
            return OpLit(value=float(value), span=expr.span)
        if isinstance(expr, OpCall):
            resolved = self._resolve_op_call(expr)
            if resolved is expr:
                return expr
            return self._resolve_operator_tree(resolved, arrays=arrays, objects=objects)
        if isinstance(expr, OpBin):
            new_lhs = self._resolve_operator_tree(expr.lhs, arrays=arrays, objects=objects)
            new_rhs = self._resolve_operator_tree(expr.rhs, arrays=arrays, objects=objects)
            if new_lhs is expr.lhs and new_rhs is expr.rhs:
                return expr
            return OpBin(op=expr.op, lhs=new_lhs, rhs=new_rhs, span=expr.span)
        if isinstance(expr, OpPow):
            new_base = self._resolve_operator_tree(expr.base, arrays=arrays, objects=objects)
            if new_base is expr.base:
                return expr
            return OpPow(base=new_base, exp=expr.exp, span=expr.span)
        if isinstance(expr, OpBinder):
            # LISS-0430: `Sigma (x In F) { |x><x| }` -- F is a named `Set`
            # variable, not an Index/{0,1}^n domain, so the static
            # `_lower_operator_expr` pass (bounded-integer-range only)
            # cannot resolve it and already skips it (ValueError, caught
            # upstream in `lower_finite_binder_operators`). Resolved here
            # instead, where F's already-computed value is reachable.
            if expr.kind == "Sigma" and isinstance(expr.domain, OpVar):
                looked_up = self._lookup_set_comprehension_value(expr.domain.name)
                if looked_up is not None:
                    set_value, domain_width = looked_up
                    return self._build_projector_sum_operator(
                        set_value, expr.variable, expr.body, domain_width
                    )
            unit = getattr(self, "_unit", None)
            if unit is None:
                return expr
            try:
                if not _contains_binder(expr):
                    return expr
            except TypeError:
                return expr
            try:
                return _lower_operator_expr(expr, unit, arrays=arrays)
            except (IndexError, ValueError) as exc:
                raise KernelError(f"cannot lower Operator binder: {exc}") from exc
        return expr

    def _lookup_set_comprehension_value(
        self, name: str
    ) -> tuple[tuple[Any, ...], int] | None:
        """LISS-0430: find `name`'s defining `Set name = { ... }` statement
        in `main()` and re-evaluate its comprehension directly. Set
        comprehensions are pure/deterministic (LISS-0429's own bound
        variable never touches per-World data), so re-evaluating here --
        rather than threading the live `Joint` through the whole Operator-
        resolution call chain just to read one already-computed,
        world-independent value back out of it -- gives the identical
        answer with far less invasive plumbing. Also returns the domain's
        own `n` (needed to materialize the empty-`F` identity below, since
        an empty `elements` tuple carries no pattern to infer it from)."""
        from ..ast_nodes import SetPowerDomain

        unit = getattr(self, "_unit", None)
        if unit is None or unit.main is None:
            return None
        for stmt in unit.main.body.stmts:
            if (
                isinstance(stmt, StateBind)
                and stmt.names == [name]
                and stmt.ty is not None
                and stmt.ty.name == "Set"
                and isinstance(stmt.expr, SetComprehension)
            ):
                elements = self._eval_set_comprehension(stmt.expr, {})
                domain = stmt.expr.domain
                width = (
                    int(self._eval_value(domain.width, {}))
                    if isinstance(domain, SetPowerDomain)
                    else 0
                )
                return elements, width
        return None

    def _build_projector_sum_operator(
        self,
        elements: tuple[Any, ...],
        bound_variable: str,
        body: Any,
        domain_width: int,
    ) -> Any:
        """$P_F=\\sum_{x\\in F}\\lvert x\\rangle\\langle x\\rvert$ (LISS-0430)
        -- `body` must be exactly `|<bound_variable>><<bound_variable>|`
        (parser-verified shape, matching `KetSumBinder`'s own body
        restriction), desugared by `_ket_or_outer`/ADR 0169 to
        `projector(Var(bound_variable))`. For each concrete `x` in
        `elements`, lowers $\\lvert x\\rangle\\langle x\\rvert$ via the
        standard Pauli-Z identity
        $\\bigotimes_i\\frac{I+(-1)^{x_i}Z_i}{2}$ as a literal `OpBin`
        product tree -- deliberately NOT manually expanded into a flat
        Pauli-string sum; `hamiltonian.py`'s existing matrix compiler
        already reduces arbitrary `OpBin(+)/OpBin(*)/OpPauli` trees to a
        matrix (proven by the already-shipped `objective_hamiltonian`'s
        own `Z[i] * Z[j]` coupling term), so the tensor-product structure
        is left for that existing, tested path to resolve, not
        reimplemented here."""
        if not (
            isinstance(body, Call)
            and isinstance(body.callee, Var)
            and body.callee.name == "projector"
            and len(body.args) == 1
            and isinstance(body.args[0], Var)
            and body.args[0].name == bound_variable
        ):
            raise KernelError(
                "Sigma (x In F) { ... } over a Set domain requires the "
                "body to be exactly `|x><x|` (the bound variable's own "
                "projector)"
            )
        if not elements:
            return OpIdentity(
                kind="Sigma", acting_space=domain_width, span=body.span
            )
        terms: list[Any] = []
        for pattern in elements:
            n = len(pattern)
            factors = []
            for i in range(n):
                sign = -1.0 if pattern[i] else 1.0
                z_term: Any = OpPauli(kind="Z", site=i, span=body.span)
                if sign < 0:
                    z_term = OpBin(
                        op="*", lhs=OpLit(value=-1.0, span=body.span),
                        rhs=z_term, span=body.span,
                    )
                factor = OpBin(
                    op="*",
                    lhs=OpLit(value=0.5, span=body.span),
                    rhs=OpBin(
                        op="+",
                        lhs=OpPauli(kind="I", site=i, span=body.span),
                        rhs=z_term,
                        span=body.span,
                    ),
                    span=body.span,
                )
                factors.append(factor)
            product = factors[0]
            for factor in factors[1:]:
                product = OpBin(op="*", lhs=product, rhs=factor, span=body.span)
            terms.append(product)
        result = terms[0]
        for term in terms[1:]:
            result = OpBin(op="+", lhs=result, rhs=term, span=body.span)
        return result

    def _lower_operator_value(
        self,
        expr: Any,
        *,
        extra_arrays: Mapping[str, Any] | None = None,
        objects: Mapping[str, Any] | None = None,
    ) -> Any:
        """Resolve an Operator AST's remaining non-literal nodes (struct
        fields, nested Operator-returning calls, finite binders) via
        `_resolve_operator_tree` (LISS-0407/LISS-0410 unifies what used
        to be several separate, bolted-on passes into one recursive
        resolver)."""
        if expr is None or isinstance(expr, (GridHamiltonianRef, str)):
            return expr
        arrays = self._operator_array_context()
        if extra_arrays:
            arrays.update(extra_arrays)
        return self._resolve_operator_tree(expr, arrays=arrays, objects=objects)

    def _resolve_operator_factory_call(self, expr: Call, fun: FunDecl) -> Any:
        """Evaluate a `fn … -> Operator` Call into a materialized OpExpr.

        LISS-0297: object (struct/class) params bind under **parameter** names so
        ``return coeffs.congestion * Z[0]`` elaborates even when the caller
        passed a differently named outer object (``drive_h(k)``).
        """
        local_scalars: dict[str, float] = {}
        local_ops: dict[str, Any] = {}
        # Param-name → ClassInstance | StructValue for OpAttr elaboration.
        local_objects: dict[str, Any] = {}
        # Param-name → Float[N]… array (LISS-0407): closes the gap where a
        # Float[N] array threaded as a function parameter and indexed
        # inside that function's own `sum` binder body never reached the
        # binder-lowering pass (`cannot compile sparse Pauli for OpBinder`).
        local_arrays: dict[str, Any] = {}
        caller_arrays = self._operator_array_context()
        if len(expr.args) != len(fun.params):
            raise KernelError(
                f"`{fun.name}` expects {len(fun.params)} args, "
                f"got {len(expr.args)}"
            )
        for param, arg in zip(fun.params, expr.args):
            if param.ty is not None and param.ty.name == "Operator":
                continue
            if (
                param.ty is not None
                and param.ty.name == "Float"
                and len(param.ty.args) >= 1
                and isinstance(arg, Var)
                and arg.name in caller_arrays
            ):
                local_arrays[param.name] = caller_arrays[arg.name]
                continue
            # Object params (struct/class) — map under the parameter name.
            if isinstance(arg, Var) and arg.name in self.objects:
                local_objects[param.name] = self.objects[arg.name]
                continue
            try:
                local_scalars[param.name] = float(self._eval_value(arg, {}))
            except (KernelError, TypeError, ValueError):
                if isinstance(arg, Var) and arg.name in self.scalars:
                    local_scalars[param.name] = float(self.scalars[arg.name])
        # Attr / classical eval frame: free-fn locals prefer param-bound objects.
        local_assign: dict[str, Any] = dict(local_objects)
        local_assign.update(local_scalars)
        attr_objects: dict[str, Any] = dict(self.objects)
        attr_objects.update(local_objects)

        def _fold_scalars_and_attrs(raw: Any) -> Any:
            folded = materialize_op_scalar_vars(
                raw,
                local_scalars,
                local_operators=local_ops,
            )
            try:
                folded = materialize_op_attrs(
                    folded, attr_objects, operators=self.operators
                )
            except OpAttrElaborationError as exc:
                raise KernelError(str(exc)) from exc
            return folded

        def _materialize_op(raw: Any) -> Any:
            folded = _fold_scalars_and_attrs(raw)
            return self._lower_operator_value(folded, extra_arrays=local_arrays)

        for stmt in fun.body.stmts:
            if not isinstance(stmt, StateBind) or stmt.ty is None:
                continue
            if stmt.ty.name == "Operator" and len(stmt.names) == 1:
                # LISS-0410: resolve against this call's own param-name
                # object scope (attr_objects), not module-level
                # self.objects -- a factory-local `Operator H = c.field *
                # ...` must see the callee's own parameter `c`.
                # LISS-0434: fold this call's own scalar params/struct
                # attrs (e.g. a width `n` used as a Sigma binder's own
                # `0..n-1` range bound, or `w.activity` as a per-term
                # coefficient inside the binder body, not just as an
                # already-built Operator's outer scale) BEFORE resolving
                # -- `_resolve_operator_expr` eagerly lowers the whole
                # binder (domain and body) in one static pass, which fails
                # closed on an unresolved name/OpAttr rather than
                # deferring; substituting first, the same way `body`/
                # `guard` are already substituted by `_map_op_tree`, avoids
                # that instead of only folding the (already-crashed)
                # result afterward.
                pre_folded = _fold_scalars_and_attrs(stmt.expr)
                raw = self._resolve_operator_expr(
                    pre_folded, objects=attr_objects, extra_arrays=local_arrays
                )
                local_ops[stmt.names[0]] = _materialize_op(raw)
                continue
            if (
                stmt.ty.name
                not in {
                    "State",
                    "Operator",
                    "Delta",
                    "POVM",
                    "DensityState",
                    "QubitRegister",
                }
                and stmt.ty.name not in self.classes
                and stmt.ty.name not in self.structs
                and stmt.ty.name not in self.enums
                and len(stmt.names) == 1
            ):
                # Closed globals, or Attr on a free-fn object param (local_objects).
                expr_closed = self._is_closed(stmt.expr)
                if (
                    not expr_closed
                    and isinstance(stmt.expr, Attr)
                    and isinstance(stmt.expr.obj, Var)
                    and stmt.expr.obj.name in local_objects
                ):
                    expr_closed = True
                if not expr_closed:
                    continue
                try:
                    local_scalars[stmt.names[0]] = float(
                        self._eval_value(stmt.expr, local_assign)
                    )
                    local_assign[stmt.names[0]] = local_scalars[stmt.names[0]]
                except (KernelError, TypeError, ValueError):
                    pass
        result = next(
            (stmt.expr for stmt in fun.body.stmts if isinstance(stmt, ReturnStmt)),
            fun.body.result,
        )
        if isinstance(result, (Var, OpVar)) and result.name in local_ops:
            return self._lower_operator_value(local_ops[result.name])
        if result is not None and not isinstance(result, (Var, OpVar)):
            return _materialize_op(result)
        return expr

    def _resolve_operator_method_call(self, expr: Call) -> Any:
        """Evaluate `recv.method(…)` returning Operator (LISS-0139)."""
        callee = expr.callee
        if not isinstance(callee, Attr):
            return expr
        recv_expr = callee.obj
        method_name = callee.name
        inst = self._resolve_receiver_instance(recv_expr)
        if inst is None:
            raise KernelError(
                f"Operator method call requires a bound receiver "
                f"(got `{type(recv_expr).__name__}`)"
            )
        if not isinstance(inst, ClassInstance):
            raise KernelError(
                f"Operator method `{method_name}` requires a class instance"
            )
        cls = self.classes.get(inst.class_name) or self.classes.get(
            inst.class_name.split(".")[-1]
        )
        if cls is None:
            raise KernelError(f"unknown class `{inst.class_name}`")
        method = next((m for m in cls.methods if m.name == method_name), None)
        if method is None:
            raise KernelError(
                f"class `{inst.class_name}` has no method `{method_name}`"
            )
        if method.return_type is None or method.return_type.name != "Operator":
            raise KernelError(
                f"method `{method_name}` must return Operator for "
                f"`Operator … = recv.{method_name}(…)`"
            )
        # Evaluate method body with `this` = receiver; reuse factory scalar fold.
        prev_this = self._this
        self._this = inst
        try:
            local_scalars: dict[str, float] = {}
            local_ops: dict[str, Any] = {}
            # Seed scalars from instance fields (this.J → Float J pattern).
            for fname, fval in inst.fields.items():
                try:
                    local_scalars[fname] = float(fval)
                except (TypeError, ValueError):
                    pass
            if len(expr.args) != len(method.params):
                raise KernelError(
                    f"`{method_name}` expects {len(method.params)} args, "
                    f"got {len(expr.args)}"
                )
            for param, arg in zip(method.params, expr.args):
                if param.ty is not None and param.ty.name == "Operator":
                    continue
                try:
                    local_scalars[param.name] = float(self._eval_value(arg, {}))
                except (KernelError, TypeError, ValueError):
                    if isinstance(arg, Var) and arg.name in self.scalars:
                        local_scalars[param.name] = float(self.scalars[arg.name])
            for stmt in method.body.stmts:
                if isinstance(stmt, ReturnStmt):
                    continue
                if isinstance(stmt, AssignStmt):
                    self._exec_assign(stmt)
                    local_scalars.update(
                        {
                            k: float(v)
                            for k, v in inst.fields.items()
                            if _is_numeric(v)
                        }
                    )
                    continue
                if not isinstance(stmt, StateBind) or stmt.ty is None:
                    continue
                if stmt.ty.name == "Operator" and len(stmt.names) == 1:
                    raw = stmt.expr
                    # Resolve this.field / local Float into OpLit via scalars.
                    local_ops[stmt.names[0]] = self._lower_operator_value(
                        materialize_op_scalar_vars(
                            raw,
                            {**local_scalars, **{
                                k: float(v)
                                for k, v in inst.fields.items()
                                if _is_numeric(v)
                            }},
                            local_operators=local_ops,
                        )
                    )
                    continue
                if stmt.ty.name == "Float" and len(stmt.names) == 1:
                    try:
                        local_scalars[stmt.names[0]] = float(
                            self._eval_value(stmt.expr, {})
                        )
                    except (KernelError, TypeError, ValueError):
                        pass
            result = next(
                (
                    stmt.expr
                    for stmt in method.body.stmts
                    if isinstance(stmt, ReturnStmt)
                ),
                method.body.result,
            )
            field_scalars = {
                k: float(v) for k, v in inst.fields.items() if _is_numeric(v)
            }
            merged = {**field_scalars, **local_scalars}
            if isinstance(result, (Var, OpVar)) and result.name in local_ops:
                return self._lower_operator_value(
                    materialize_op_scalar_vars(
                        local_ops[result.name], merged, local_operators=local_ops
                    )
                )
            if result is not None and not isinstance(result, (Var, OpVar)):
                return self._lower_operator_value(
                    materialize_op_scalar_vars(
                        result, merged, local_operators=local_ops
                    )
                )
            raise KernelError(
                f"method `{method_name}` did not return an Operator"
            )
        finally:
            self._this = prev_this

    def _bind_second_quantized(self, name: str, family: str, expr: Any) -> None:
        """Bind a typed second-quantized local (LISS-0032, ADR 0093).

        `FermionOperator`/`BosonOperator`/`SpinOperator` locals are kept
        symbolic (no classical value, no numeric mapping yet). A
        `QubitOperator` bind whose expr is `map(op, JordanWigner)` resolves
        the referenced `FermionOperator` through the Jordan-Wigner mapping
        into an ordinary Pauli OpExpr, stored in `self.operators` exactly
        like a hand-written `Operator` bind so `evolve`/`apply` need no
        special-casing downstream.
        """
        if family == "QubitOperator":
            try:
                mapped_expr = resolve_mapping_expr(
                    expr, self.second_quantized_operators, self.scalars, self.objects
                )
            except SecondQuantizationMappingError as exc:
                raise KernelError(f"{exc.code}: {exc.message}") from exc
            if mapped_expr is not None:
                self.operators[name] = mapped_expr
                return
        self.second_quantized_operators[name] = expr

    def _exec_assign(self, stmt: AssignStmt, local: dict[str, Any] | None = None) -> None:
        target = stmt.target
        if not isinstance(target, Attr):
            raise KernelError("assignment target must be `obj.field` or `this.field`")
        env = local if local is not None else {}
        val, unit = self._eval_value_with_unit(stmt.value, env)
        # this.field =
        if isinstance(target.obj, Var) and target.obj.name == "this":
            if self._this is None:
                raise KernelError("`this` is only valid inside a class method")
            if target.name not in self._this.mutable and not self._in_init:
                raise KernelError(
                    f"IMMUTABLE_ASSIGNMENT_ERROR: field `{target.name}` is not "
                    f"`var` (cannot assign through `this`)"
                )
            self._this.fields[target.name] = val
            self._put_unit(self._this.field_units, target.name, unit)
            return
        # obj.field =
        if isinstance(target.obj, Var) and target.obj.name in self.objects:
            obj = self.objects[target.obj.name]
            if isinstance(obj, StructValue):
                raise KernelError(
                    f"IMMUTABLE_ASSIGNMENT_ERROR: struct `{obj.struct_name}` "
                    f"fields are immutable"
                )
            if isinstance(obj, ClassInstance):
                if target.name not in obj.mutable:
                    raise KernelError(
                        f"IMMUTABLE_ASSIGNMENT_ERROR: field `{target.name}` is not "
                        f"`var`"
                    )
                obj.fields[target.name] = val
                self._put_unit(obj.field_units, target.name, unit)
                return
        raise KernelError("assignment target is not a mutable object field")

    def _bind_method(
        self,
        joint: Joint,
        name: str,
        receiver: ClassInstance,
        method: FunDecl,
        args: list[Expr],
        *,
        logs: list[str] | None = None,
        inspect_out: MeasureSinkPort | None = None,
    ) -> Joint:
        """Run a measure-free method and bind its result.

        New signatures return the explicit terminal `return` expression.
        """
        if method.name == "init":
            raise KernelError("`init` is a constructor; call `ClassName(…)` instead")
        if len(args) != len(method.params):
            raise KernelError(
                f"`{method.name}` expects {len(method.params)} args, got {len(args)}"
            )
        prev_this = self._this
        prev_frame = self._frame_units
        self._this = receiver
        self._frame_units = {}
        # Local classical env for params + this fields
        local: dict[str, Any] = dict(receiver.fields)
        for param, arg in zip(method.params, args):
            if isinstance(arg, Var) and arg.name in self.objects:
                obj = self.objects[arg.name]
                # struct: copy-on-pass; class: reference
                if isinstance(obj, StructValue):
                    local[param.name] = obj.copy()
                else:
                    local[param.name] = obj
            else:
                v, unit = self._eval_value_with_unit(arg, {})
                if isinstance(v, StructValue):
                    local[param.name] = v.copy()
                else:
                    local[param.name] = v
                if unit is not None:
                    self._frame_units[param.name] = unit

        last_val: Any = None
        last_unit: str | None = None
        result_joint: Joint | None = None
        try:
            for stmt in method.body.stmts:
                if isinstance(stmt, Measure):
                    raise KernelError(
                        f"`measure` forbidden inside method `{method.name}`"
                    )
                if isinstance(stmt, Snapshot):
                    raise KernelError(
                        f"`snapshot` forbidden inside method `{method.name}`"
                    )
                if isinstance(stmt, ReturnStmt):
                    continue
                if isinstance(stmt, AssignStmt):
                    self._exec_assign(stmt, local)
                    # Reflect this.fields into local for subsequent reads of bare names
                    local.update(receiver.fields)
                    continue
                if isinstance(stmt, StateBind):
                    if stmt.ty is not None and stmt.ty.name == "Operator":
                        if len(stmt.names) != 1:
                            raise KernelError("Operator bind expects a single name")
                        # LISS-0413: resolve the same way the top-level
                        # Operator StateBind dispatch does -- unlike this
                        # method's own Operator-typed *parameters|struct
                        # fields the runtime evaluator already resolves,
                        # a *local* Operator bind here previously stored
                        # its raw AST, so a struct-field coefficient
                        # (`weights.a * X`) failed with `cannot compile
                        # operator node OpAttr`.
                        self.operators[stmt.names[0]] = self._resolve_operator_expr(
                            stmt.expr
                        )
                        continue
                    # Evaluate RHS with this/local; bind into local (classical methods)
                    if len(stmt.names) != 1:
                        raise KernelError(
                            f"method `{method.name}` binds must be single-name"
                        )
                    # Prefer classical eval of method bodies (physics helpers)
                    try:
                        val, unit = self._eval_value_with_unit(stmt.expr, local)
                        local[stmt.names[0]] = val
                        last_val = val
                        last_unit = unit
                        self._put_unit(self._frame_units, stmt.names[0], unit)
                        if (
                            stmt.ty is not None
                            and stmt.ty.name not in {"State", "Operator", "Delta"}
                        ):
                            try:
                                if isinstance(val, Fraction):
                                    self.scalars[stmt.names[0]] = val
                                else:
                                    self.scalars[stmt.names[0]] = float(val)
                                self._put_unit(
                                    self.scalar_units, stmt.names[0], unit
                                )
                            except (TypeError, ValueError):
                                pass
                    except KernelError:
                        # Quantum bind path (rare in methods)
                        joint = self._bind_names(
                            joint,
                            stmt.names,
                            stmt.expr,
                            logs=logs,
                            inspect_out=inspect_out,
                        )
                        last_val = None
                        last_unit = None
                else:
                    raise KernelError(
                        f"unsupported stmt in method `{method.name}`: "
                        f"{type(stmt).__name__}"
                    )
            if method.body.result is not None:
                try:
                    # Methods such as `advance()` return a classical field
                    # projection after updating the receiver.  Resolve that
                    # expression in the method-local environment first;
                    # quantum expressions still use the Joint binder.
                    value, unit = self._eval_value_with_unit(
                        method.body.result, local
                    )
                    last_unit = unit
                    result_joint = joint.bind_const(name, value)
                    try:
                        if isinstance(value, Fraction):
                            self.scalars[name] = value
                        else:
                            self.scalars[name] = float(value)
                        self._put_unit(self.scalar_units, name, unit)
                    except (TypeError, ValueError):
                        pass
                except KernelError:
                    result_joint = self._bind(
                        joint,
                        name,
                        method.body.result,
                        logs=logs,
                        inspect_out=inspect_out,
                    )
        finally:
            self._this = prev_this
            self._frame_units = prev_frame

        if result_joint is not None:
            return result_joint

        if method.body.result is None:
            raise KernelError(
                f"method `{method.name}` has no explicit return"
            )
        if last_val is None:
            return self._bind(
                joint,
                name,
                method.body.result,
                logs=logs,
                inspect_out=inspect_out,
            )
        if last_unit is not None:
            self.scalar_units[name] = last_unit
        return joint.bind_const(name, last_val)

    def _eval_classical_call(
        self, expr: Call, assign: dict[str, Any] | None = None
    ) -> Any:
        """Evaluate a pure classical Call as a classical value (ADR 0179).

        Allows ``c.get() * 0.4`` / ``twice(1.5) + 0.5`` without temps.
        State/Joint-forming Calls remain rejected.

        ``assign`` is the parent classical frame (free-fn locals). Nested free-fn
        calls such as ``queue_pressure`` → ``recovery_priority(q.a)`` resolve
        object args from that frame (LISS-0294).
        """
        classical_heads = {
            "Float",
            "Int",
            "Bool",
            "Mass",
            "Time",
            "Length",
            "Current",
            "Temperature",
            "Energy",
            "Frequency",
            "Stiffness",
            "Momentum",
        }
        if isinstance(expr.callee, Var):
            # LISS-0338's deferred gap: sin/cos/exp/sqrt/abs/log/tan
            # (stdlib.math_ops.MATH_OPS) previously only had a State-
            # pushforward execution path (via joint.map_coord); a classical-
            # scalar call like `abs(x)` had no evaluator support at all.
            if math_ops.known_math_op(expr.callee.name):
                if len(expr.args) != 1:
                    raise KernelError(
                        f"`{expr.callee.name}` expects exactly 1 argument, "
                        f"got {len(expr.args)}"
                    )
                arg_val = self._eval_value(expr.args[0], assign or {})
                return math_ops.apply_math(expr.callee.name, arg_val)
            fun = self.funs.get(expr.callee.name)
            if fun is None:
                raise KernelError(
                    "call cannot be classical value in Phase 2.2 value context"
                )
            # LISS-0338's deferred gap: a free fn returning a struct type is
            # also a pure classical value, not just the fixed scalar/
            # dimensioned classical_heads set.
            if fun.return_type is None or (
                fun.return_type.name not in classical_heads
                and fun.return_type.name not in self.structs
            ):
                raise KernelError(
                    "call cannot be classical value in Phase 2.2 value context: "
                    f"`{fun.name}` is not a pure classical-returning fn"
                )
            return self._eval_classical_user_fun(fun, expr, assign)
        if isinstance(expr.callee, Attr):
            return self._eval_classical_method_call(expr, classical_heads)
        raise KernelError("call cannot be classical value in Phase 2.2 value context")

    def _eval_classical_method_call(
        self, expr: Call, classical_heads: set[str]
    ) -> Any:
        """Evaluate ``recv.method(…)`` returning a classical head (ADR 0179)."""
        callee = expr.callee
        if not isinstance(callee, Attr):
            raise KernelError("call cannot be classical value in Phase 2.2 value context")
        method_name = callee.name
        recv_expr = callee.obj
        inst = self._resolve_receiver_instance(recv_expr)
        if inst is None:
            raise KernelError(
                f"classical method call requires a bound receiver "
                f"(got `{type(recv_expr).__name__}`)"
            )
        if not isinstance(inst, ClassInstance):
            raise KernelError(
                f"classical method `{method_name}` requires a class instance"
            )
        cls = self.classes.get(inst.class_name) or self.classes.get(
            inst.class_name.split(".")[-1]
        )
        if cls is None:
            raise KernelError(f"unknown class `{inst.class_name}`")
        method = next((m for m in cls.methods if m.name == method_name), None)
        if method is None:
            raise KernelError(
                f"class `{inst.class_name}` has no method `{method_name}`"
            )
        if method.return_type is None or method.return_type.name not in classical_heads:
            raise KernelError(
                "call cannot be classical value in Phase 2.2 value context: "
                f"`{method_name}` is not a pure classical-returning method"
            )
        if len(expr.args) != len(method.params):
            raise KernelError(
                f"`{method_name}` expects {len(method.params)} args, "
                f"got {len(expr.args)}"
            )
        prev_this = self._this
        self._this = inst
        try:
            local: dict[str, Any] = dict(inst.fields)
            for param, arg in zip(method.params, expr.args):
                if isinstance(arg, Var) and arg.name in self.objects:
                    local[param.name] = self.objects[arg.name]
                elif isinstance(arg, Var) and arg.name in self.scalars:
                    local[param.name] = self.scalars[arg.name]
                else:
                    local[param.name] = self._eval_value(arg, {})
            for stmt in method.body.stmts:
                if isinstance(stmt, AssignStmt):
                    self._exec_assign(stmt, local)
                    local.update(inst.fields)
            result = next(
                (
                    stmt.expr
                    for stmt in method.body.stmts
                    if isinstance(stmt, ReturnStmt)
                ),
                method.body.result,
            )
            if result is None:
                raise KernelError(f"method `{method_name}` has no return")
            return self._eval_value(result, local)
        finally:
            self._this = prev_this

    def _eval_classical_user_fun(
        self,
        fun: FunDecl,
        expr: Call,
        assign: dict[str, Any] | None = None,
    ) -> Any:
        """Evaluate a classical-returning library fn (LISS-0231); value only."""
        val, _unit = self._eval_classical_user_fun_value(fun, expr, assign)
        return val

    def _eval_classical_user_fun_value(
        self,
        fun: FunDecl,
        expr: Call,
        assign: dict[str, Any] | None = None,
    ) -> tuple[Any, str | None]:
        """Classical free-fn with object/scalar args (LISS-0231 / LISS-0292).

        Supports Type-First object parameters without Joint coordinates, and
        multi-statement bodies with intermediate classical binds.

        Nested free-fn calls receive the caller frame via ``assign`` so params
        and field projections (``q.a``, ``board.coastal``) resolve without
        leaking to outer ``self.objects`` names (LISS-0294).
        """
        if len(expr.args) != len(fun.params):
            raise KernelError(
                f"`{fun.name}` expects {len(fun.params)} args, got {len(expr.args)}"
            )
        parent = assign if assign is not None else {}
        local: dict[str, Any] = {}
        local_units: dict[str, str] = {}
        prev_this = self._this
        prev_frame = self._frame_units
        prev_call_units = getattr(self, "_call_local_units", None)
        self._frame_units = {}
        self._call_local_units = local_units
        try:
            for param, arg in zip(fun.params, expr.args):
                if isinstance(arg, Var) and arg.name in parent:
                    local[param.name] = parent[arg.name]
                    if prev_call_units is not None and arg.name in prev_call_units:
                        local_units[param.name] = prev_call_units[arg.name]
                    elif arg.name in self.scalar_units:
                        local_units[param.name] = self.scalar_units[arg.name]
                elif isinstance(arg, Var) and arg.name in self.objects:
                    local[param.name] = self.objects[arg.name]
                elif isinstance(arg, Var) and arg.name in self.scalars:
                    local[param.name] = self.scalars[arg.name]
                    if arg.name in self.scalar_units:
                        local_units[param.name] = self.scalar_units[arg.name]
                else:
                    # Attr / nested expr: evaluate in parent frame so free-fn
                    # locals shadow outer objects of the same name.
                    v, u = self._eval_value_with_unit(arg, parent)
                    local[param.name] = v
                    if u is not None:
                        local_units[param.name] = u
            # Interface / method-style: first object arg as `this` when useful.
            for _pname, pval in local.items():
                if isinstance(pval, ClassInstance):
                    self._this = pval
                    break
            # Execute intermediate classical binds (Length road = q.road_km to m).
            for stmt in fun.body.stmts:
                if isinstance(stmt, ReturnStmt):
                    continue
                if isinstance(stmt, AssignStmt):
                    self._exec_assign(stmt, local)
                    continue
                if isinstance(stmt, StateBind) and len(stmt.names) == 1:
                    v, u = self._eval_value_with_unit(stmt.expr, local)
                    local[stmt.names[0]] = v
                    if u is not None:
                        local_units[stmt.names[0]] = u
                        self._frame_units[stmt.names[0]] = u
                    continue
                if isinstance(stmt, (Measure, Snapshot)):
                    raise KernelError(
                        f"`measure`/`snapshot` forbidden inside classical fn `{fun.name}`"
                    )
            result = next(
                (
                    stmt.expr
                    for stmt in fun.body.stmts
                    if isinstance(stmt, ReturnStmt)
                ),
                fun.body.result,
            )
            if result is None:
                raise KernelError(f"`{fun.name}` has no return")
            # `unit.readiness()` — Attr Call on interface-typed local.
            if isinstance(result, Call) and isinstance(result.callee, Attr):
                recv = result.callee.obj
                if isinstance(recv, Var) and recv.name in local:
                    self._this = local[recv.name]
                    method_name = result.callee.name
                    inst = local[recv.name]
                    if not isinstance(inst, ClassInstance):
                        raise KernelError(
                            f"`{fun.name}` receiver is not a class instance"
                        )
                    cls = self.classes.get(inst.class_name) or self.classes.get(
                        inst.class_name.split(".")[-1]
                    )
                    if cls is None:
                        raise KernelError(f"unknown class `{inst.class_name}`")
                    method = next(
                        (m for m in cls.methods if m.name == method_name), None
                    )
                    if method is None:
                        raise KernelError(
                            f"class `{inst.class_name}` has no method `{method_name}`"
                        )
                    ret = next(
                        (
                            s.expr
                            for s in method.body.stmts
                            if isinstance(s, ReturnStmt)
                        ),
                        method.body.result,
                    )
                    if ret is None:
                        raise KernelError(f"method `{method_name}` has no return")
                    return self._eval_value(ret, dict(inst.fields)), None
            return self._eval_value_with_unit(result, local)
        finally:
            self._this = prev_this
            self._frame_units = prev_frame
            if prev_call_units is None:
                if hasattr(self, "_call_local_units"):
                    del self._call_local_units
            else:
                self._call_local_units = prev_call_units

    def _bind_user_fun(
        self,
        joint: Joint,
        names: list[str],
        expr: Call,
        fun: FunDecl,
        *,
        logs: list[str] | None = None,
        inspect_out: MeasureSinkPort | None = None,
    ) -> Joint:
        """Execute a measure-free library `fn` and bind results to `names`."""
        if len(expr.args) != len(fun.params):
            raise KernelError(
                f"`{fun.name}` expects {len(fun.params)} args, got {len(expr.args)}"
            )
        pre_live = self._joint_coord_names(joint)
        saved_operators = dict(self.operators)
        # Bind arguments onto parameter coordinates
        for param, arg in zip(fun.params, expr.args):
            if param.ty is not None and param.ty.name == "Operator":
                self.operators[param.name] = self._resolve_operator_expr(arg)
                continue
            if isinstance(arg, Var) and arg.name == param.name:
                continue
            if isinstance(arg, Var):
                src = arg.name
                try:
                    joint = joint.bind_pushforward(
                        param.name, lambda a, s=src: a[s]
                    )
                except KeyError as exc:
                    raise KernelError(
                        f"RUNTIME_ERROR: unbound coordinate `{src}` while "
                        f"binding parameter `{param.name}` of `{fun.name}`"
                    ) from exc
            else:
                # ADR 0130: KetLit / Dirac / nested State-forming exprs.
                joint = self._bind(
                    joint,
                    param.name,
                    arg,
                    logs=logs,
                    inspect_out=inspect_out,
                )

        for stmt in fun.body.stmts:
            if isinstance(stmt, Measure):
                raise KernelError(
                f"`measure` is forbidden inside library fn `{fun.name}` "
                    "(measure-free module boundary)"
                )
            if isinstance(stmt, Snapshot):
                raise KernelError(
                    f"`snapshot` is forbidden inside library fn `{fun.name}`"
                )
            if isinstance(stmt, ReturnStmt):
                continue
            if isinstance(stmt, StateBind):
                if stmt.ty is not None and stmt.ty.name == "Operator":
                    if len(stmt.names) != 1:
                        raise KernelError("Operator bind expects a single name")
                    # LISS-0413: same fix as _bind_method -- a local
                    # Operator bind inside a library fn previously stored
                    # its raw AST unresolved (unlike this same function's
                    # own Operator-typed *parameter* binding a few lines
                    # above, which already resolves).
                    self.operators[stmt.names[0]] = self._resolve_operator_expr(
                        stmt.expr
                    )
                    continue
                joint = self._bind_names(
                    joint,
                    stmt.names,
                    stmt.expr,
                    logs=logs,
                    inspect_out=inspect_out,
                )
            else:
                raise KernelError(
                    f"unsupported stmt in fn `{fun.name}`: {type(stmt).__name__}"
                )

        if fun.body.result is not None:
            if len(names) == 0:
                # A result with no destination is still evaluated for its
                # state-preserving transform, but has no visible coordinate.
                result_joint = self._trace_out_dead_fn_locals(joint, pre_live, names)
                self.operators = saved_operators
                return result_joint
            # Operator-returning functions bind their result in the operator
            # environment, not as a Joint coordinate.  A library function
            # commonly ends with `return local_operator`; routing that
            # OpVar through the ordinary value binder loses the callee-local
            # operator and raises `cannot bind expr OpVar` at the caller.
            if (
                len(names) == 1
                and fun.return_type is not None
                and fun.return_type.name == "Operator"
                and isinstance(fun.body.result, (Var, OpVar))
                and fun.body.result.name in self.operators
            ):
                self.operators[names[0]] = self.operators[fun.body.result.name]
                self.operators = {
                    **saved_operators,
                    names[0]: self.operators[names[0]],
                }
                return joint
            result_joint = self._bind_names(
                joint,
                names,
                fun.body.result,
                logs=logs,
                inspect_out=inspect_out,
            )
            if "Uncompute" in fun.effects:
                for n in names:
                    self._require_uncompute_zero(result_joint, n)
            result_joint = self._trace_out_dead_fn_locals(result_joint, pre_live, names)
            self.operators = saved_operators
            return result_joint

        # Legacy state-transformer path: project parameter coordinates into
        # the caller's bind names when no explicit result expression exists.
        if len(names) == 0:
            result_joint = self._trace_out_dead_fn_locals(joint, pre_live, names)
            self.operators = saved_operators
            return result_joint
        if len(names) == len(fun.params):
            updates = {
                n: (lambda a, p=p.name: a[p])
                for n, p in zip(names, fun.params)
            }
            result_joint = joint.bind_multi(updates)
            result_joint = self._trace_out_dead_fn_locals(result_joint, pre_live, names)
            self.operators = saved_operators
            return result_joint
        if len(names) == 1 and len(fun.params) == 1:
            p = fun.params[0].name
            result_joint = joint.bind_pushforward(names[0], lambda a, pn=p: a[pn])
            result_joint = self._trace_out_dead_fn_locals(result_joint, pre_live, names)
            self.operators = saved_operators
            return result_joint
        raise KernelError(
            f"`{fun.name}` result arity {len(fun.params)} != bind arity {len(names)}"
        )

    @staticmethod
    def _joint_coord_names(joint: Joint) -> set[str]:
        names: set[str] = set()
        for w in joint.worlds:
            names.update(w.assign)
        return names

    def _trace_out_dead_fn_locals(
        self, joint: Joint, pre_live: set[str], result_names: list[str]
    ) -> Joint:
        """ADR 0138: drop fn-local axes not live before the Call and not results."""
        keep = pre_live | set(result_names)
        for coord in sorted(self._joint_coord_names(joint) - keep):
            joint = joint.trace_out(coord)
        return joint

    def _is_library_user_call(self, expr: Expr) -> bool:
        """True when `expr` is a Call to a known measure-free library `fn`.

        LISS-0201: Partial formation (`f(…, _)`) is not an executed Call — it
        only captures arguments. Interprocedural Trace-Out must not drop those
        closed-over caller coordinates.
        """
        if not isinstance(expr, Call):
            return False
        if not isinstance(expr.callee, Var):
            return False
        if any(isinstance(a, Hole) for a in expr.args):
            return False
        return expr.callee.name in self.funs

    @classmethod
    def _main_interproc_trace_eligible(cls, stmts: list[Any]) -> bool:
        """ADR 0158: skip mains with inspect / snapshot (same family as ADR 0140)."""
        for stmt in stmts:
            if isinstance(stmt, Snapshot):
                return False
            if isinstance(stmt, StateBind) and cls._expr_has_inspect(stmt.expr):
                return False
            if isinstance(stmt, Measure) and cls._expr_has_inspect(stmt.expr):
                return False
            if isinstance(stmt, ExprStmt) and cls._expr_has_inspect(stmt.expr):
                return False
        return True

    @classmethod
    def _stmts_live_vars(cls, stmts: list[Any]) -> set[str]:
        """Free-var union of subsequent main stmts (thin live-out, ADR 0158)."""
        live: set[str] = set()
        for stmt in stmts:
            if isinstance(stmt, StateBind):
                live |= cls._expr_free_vars(stmt.expr)
            elif isinstance(stmt, Measure):
                live |= cls._expr_free_vars(stmt.expr)
                live |= set(stmt.tracing_out)
            elif isinstance(stmt, Snapshot):
                live |= cls._expr_free_vars(stmt.expr)
            elif isinstance(stmt, ExprStmt):
                live |= cls._expr_free_vars(stmt.expr)
        return live

    def _trace_out_dead_caller_coords(
        self,
        joint: Joint,
        live_out: set[str],
        result_names: list[str],
    ) -> Joint:
        """ADR 0158: drop caller axes absent from post-Call free-var live-out."""
        keep = live_out | set(result_names)
        for coord in sorted(self._joint_coord_names(joint) - keep):
            joint = joint.trace_out(coord)
        return joint

    @staticmethod
    def _fill_partial(
        partial: PartialValue, fill_args: list[Expr]
    ) -> Call | PartialValue:
        """Fill holes left-to-right; exact fill → Call, partial fill → PartialValue."""
        need = sum(1 for s in partial.slots if s is None)
        if not fill_args or len(fill_args) > need:
            raise KernelError(
                f"Partial `{partial.fun_name}` expects 1..{need} remaining args, "
                f"got {len(fill_args)}"
            )
        new_slots: list[Expr | None] = []
        fi = 0
        for slot in partial.slots:
            if slot is None:
                if fi < len(fill_args):
                    new_slots.append(fill_args[fi])
                    fi += 1
                else:
                    new_slots.append(None)
            else:
                new_slots.append(slot)
        remaining = sum(1 for s in new_slots if s is None)
        if remaining == 0:
            assert all(s is not None for s in new_slots)
            filled = [s for s in new_slots if s is not None]
            sp = fill_args[0].span
            return Call(
                callee=Var(name=partial.fun_name, span=sp), args=filled, span=sp
            )
        # ADR 0131: stepwise Partial.
        return PartialValue(fun_name=partial.fun_name, slots=new_slots)

    def _bind_call(self, joint: Joint, name: str, expr: Call) -> Joint:
        callee = expr.callee

        # Class / struct construction reached via a free-function's own
        # `return Simple(args)` (or any other non-top-level classical
        # binding site) -- mirrors the top-level statement dispatch in
        # _run_unit_body and the classical-expression dispatch in
        # _eval_value, neither of which this function-body binding path
        # otherwise shares.
        if isinstance(callee, Var):
            q = self._expr_qualname(callee) or callee.name
            if q in self.classes:
                self.objects[name] = self._construct_instance(q, expr)
                return joint
            if q in self.structs:
                self.objects[name] = self._construct_struct(q, expr)
                return joint

        # ADR 0123: form Partial when any `_` hole is present.
        if any(isinstance(a, Hole) for a in expr.args):
            fun_name: str | None = None
            if isinstance(callee, Var):
                fun_name = callee.name
            else:
                q = self._expr_qualname(callee)
                if q is not None:
                    fun_name = q
            if fun_name is None or fun_name not in self.funs:
                raise KernelError("Partial requires a known function callee")
            slots: list[Expr | None] = [
                None if isinstance(a, Hole) else a for a in expr.args
            ]
            self.objects[name] = PartialValue(fun_name=fun_name, slots=slots)
            return joint

        # ADR 0123: Call on a bound Partial fills remaining holes.
        if isinstance(callee, Var) and callee.name in self.objects:
            partial = self.objects[callee.name]
            if isinstance(partial, PartialValue):
                filled = self._fill_partial(partial, list(expr.args))
                if isinstance(filled, PartialValue):
                    self.objects[name] = filled
                    return joint
                return self._bind_call(joint, name, filled)

        # ADR 0056: instance.method(args)
        if isinstance(callee, Attr):
            recv_expr = callee.obj
            method_name = callee.name
            q = self._expr_qualname(callee)
            if q is not None and q in self.funs:
                return self._bind_user_fun(joint, [name], expr, self.funs[q])
            # Namespace-qualified struct constructors are represented as an
            # Attr (`D.Item(...)`), but are constructors rather than method
            # calls.  Resolve them before receiver/method dispatch so the
            # callable-plan path matches the value-evaluator path.
            if q is not None and q in self.structs:
                self.objects[name] = self._construct_struct(q, expr)
                return joint
            if q is not None and q in self.classes:
                raise KernelError(
                    f"construct `{q}()` via Type-First "
                    f"`{q} obj = {q}()`, not as a State expression"
                )
            inst = self._resolve_receiver_instance(recv_expr)
            if isinstance(inst, ClassInstance):
                cls = self.classes.get(inst.class_name) or self.classes.get(
                    inst.class_name.split(".")[-1]
                )
                if cls is None:
                    raise KernelError(f"unknown class `{inst.class_name}`")
                method = next(
                    (m for m in cls.methods if m.name == method_name), None
                )
                if method is None:
                    raise KernelError(
                        f"class `{inst.class_name}` has no method `{method_name}`"
                    )
                return self._bind_method(
                    joint, name, inst, method, list(expr.args)
                )
            if isinstance(inst, StructValue):
                raise KernelError(
                    f"struct `{inst.struct_name}` has no methods "
                    f"(use class for methods)"
                )
            # Fall through to Math.* / map / etc.

        # User-module fn (ADR 0054)
        if isinstance(callee, Var) and callee.name in self.funs:
            return self._bind_user_fun(joint, [name], expr, self.funs[callee.name])

        # Math.sin(x) / Math.cos(x) / …
        if isinstance(callee, Attr):
            if isinstance(callee.obj, Var) and callee.obj.name == "Complex":
                if callee.name == "cis":
                    if len(expr.args) != 1:
                        raise KernelError("Complex.cis requires (theta)")
                    theta = float(self._eval_value(expr.args[0], {}))
                    from .joint import World

                    return Joint(
                        worlds=[World(assign={name: 0}, amp=cmath.exp(1j * theta))]
                    )
                raise KernelError(f"unknown Complex.{callee.name}")
            if isinstance(callee.obj, Var) and callee.obj.name == "Math":
                if not math_ops.known_math_op(callee.name):
                    raise KernelError(f"unknown Math.{callee.name}")
                if len(expr.args) != 1 or not isinstance(expr.args[0], Var):
                    raise KernelError(f"Math.{callee.name} expects one State variable")
                src = expr.args[0].name
                op = callee.name
                return joint.map_coord(src, name, lambda v: math_ops.apply_math(op, v))
            # extension: x.sin() → Math.sin(x)
            if isinstance(callee.obj, Var) and math_ops.known_math_op(callee.name):
                src = callee.obj.name
                op = callee.name
                return joint.map_coord(src, name, lambda v: math_ops.apply_math(op, v))
            # x.map(fn) — project is not a method (Hilbert project(state, k) only)
            if isinstance(callee.obj, Var) and callee.name == "map":
                src_expr = callee.obj
                if len(expr.args) < 1:
                    raise KernelError("map requires a lambda")
                f = self._as_unary_fn(expr.args[0])
                return joint.map_coord(src_expr.name, name, f)
            if isinstance(callee.obj, Var) and callee.name == "project":
                raise KernelError(
                    "use project(state, k) for Hilbert |k⟩⟨k|; "
                    "method form state.project(pred) is removed"
                )
            raise KernelError(f"unsupported method {callee.name}")

        if isinstance(callee, Var):
            op = callee.name
        elif isinstance(callee, Coin):
            return joint.bind_split(name, {0: 0.5, 1: 0.5})
        else:
            raise KernelError(f"unsupported callee {type(callee)}")

        if op == "map":
            if len(expr.args) < 2:
                raise KernelError("map requires (src, fn)")
            src_expr, fn = expr.args[0], expr.args[1]
            if not isinstance(src_expr, Var):
                raise KernelError("map src must be a variable")
            f = self._as_unary_fn(fn)
            return joint.map_coord(src_expr.name, name, f)

        if op == "project":
            # Hilbert projector P̂ = |k⟩⟨k| on a wire (Lüders), then renorm.
            # Predicate filters are forbidden (classical programming smell).
            if len(expr.args) < 2:
                raise KernelError(
                    "project requires (state, basisLabel) — Hilbert |k⟩⟨k|, "
                    "not a predicate lambda"
                )
            src_expr, target = expr.args[0], expr.args[1]
            if not isinstance(src_expr, Var):
                raise KernelError("project src must be a state variable")
            if isinstance(target, Lambda):
                raise KernelError(
                    "PREDICATE_PROJECTOR_ERROR: `project` is the Hilbert "
                    "projector |k⟩⟨k|, not a classical filter. "
                    "Write project(psi, 0) or project(psi, |0>)."
                )
            if isinstance(target, Var) and target.name in self.operators:
                # LISS-0431: `project psi onto P_F` -- a general (possibly
                # multi-term) Operator, e.g. LISS-0430's literal
                # $P_F=\sum_{x\in F}\lvert x\rangle\langle x\rvert$. Diagonal
                # projectors only for now (the confirmed target design
                # never needs anything else); scales each World's
                # amplitude by sqrt of the projector's diagonal entry at
                # that World's own coordinate value, matching
                # `bind_split`'s own probability->amplitude convention.
                projected = self._project_onto_operator(
                    joint, src_expr.name, target.name
                )
            else:
                if isinstance(target, KetLit):
                    bits = target.label
                    if bits in {"0", "1"}:
                        label: Any = int(bits)
                    elif set(bits) <= {"0", "1"} and bits != "":
                        label = int(bits, 2)
                    else:
                        raise KernelError(
                            f"project onto |{bits}⟩: MVP supports "
                            "computational |0⟩/|1⟩ (and bitstrings) only"
                        )
                else:
                    label = self._eval_value(target, {})
                projected = joint.project_coord(src_expr.name, lambda v, lab=label: v == lab)
            if projected.is_vacuum():
                return Joint.empty()
            # LISS-0431: `project` no longer renormalizes -- the result is
            # the literal, generally-unnormalized $P\lvert\psi\rangle$;
            # explicit renormalization is written at the call site via
            # `/ ||...||` (LISS-0426), matching the equation's own
            # separate $/\lVert\cdot\rVert$ factor instead of folding it
            # silently into every `project`.
            return projected.bind_pushforward(name, lambda a: a[src_expr.name])

        if op == "interfer":
            if not expr.args:
                return Joint.empty()
            from .joint import World, _coalesce

            # Sum complex amplitudes per result value (path interference).
            from collections import defaultdict

            amps: dict[Any, complex] = defaultdict(complex)
            for arg in expr.args:
                if isinstance(arg, Var):
                    for val, c in joint.amplitude_marginal(arg.name).items():
                        amps[val] += c
                elif isinstance(arg, (LitInt, LitFloat, LitBool)):
                    amps[self._lit(arg)] += complex(1.0, 0.0)
                else:
                    for w in joint.worlds:
                        val = self._eval_value(arg, w.assign)
                        amps[val] += w.amp
            # Drop cancelled bins; renormalize Born measure (SV-07 mixture).
            alive = {v: c for v, c in amps.items() if abs(c) ** 2 > EPS}
            if not alive:
                return Joint.empty()
            total = sum(abs(c) ** 2 for c in alive.values())
            scale = 1.0 / cmath.sqrt(total)
            out = [
                World(assign={name: val}, amp=c * scale) for val, c in alive.items()
            ]
            return Joint(worlds=_coalesce(out))

        if op == "phase":
            # phase(src, theta) or phase(src, theta, only_value)
            # ADR 0060: θ / only resolve against scalars ∪ objects ∪ assign
            if len(expr.args) < 2 or not isinstance(expr.args[0], Var):
                raise KernelError("phase requires (src, theta[, only])")
            src = expr.args[0].name
            theta = float(self._eval_value(expr.args[1], {}))
            only = None
            if len(expr.args) >= 3:
                only = self._eval_value(expr.args[2], {})
            return joint.phase_copy(src, name, theta, only=only)

        if op in {"grover_diffuse", "diffuse"}:
            # grover_diffuse(src) — Grover inversion about mean
            if len(expr.args) != 1 or not isinstance(expr.args[0], Var):
                raise KernelError("grover_diffuse requires (src)")
            return joint.diffuse_copy(expr.args[0].name, name)

        if op == "cis":
            # cis(theta): unit |0⟩ with amplitude e^{iθ}
            if len(expr.args) != 1:
                raise KernelError("cis requires (theta)")
            theta = float(self._eval_value(expr.args[0], {}))
            from .joint import World

            return Joint(worlds=[World(assign={name: 0}, amp=cmath.exp(1j * theta))])

        if op == "cnot":
            # cnot(ctrl, tgt) — unitary |c,t⟩↦|c,t⊕c⟩; bind result as new tgt wire
            if len(expr.args) != 2:
                raise KernelError("cnot requires (ctrl, tgt)")
            if not isinstance(expr.args[0], Var) or not isinstance(expr.args[1], Var):
                raise KernelError("cnot args must be state variables")
            from .quantum_ops import cnot_bit

            ctrl_n = expr.args[0].name
            tgt_n = expr.args[1].name
            return joint.bind_pushforward(
                name, lambda a: cnot_bit(a[ctrl_n], a[tgt_n])
            )

        if op == "apply":
            # apply(U, w0[, w1, …]) — unitary on wires (H⊗I…); U = Operator | Hadamard | Pauli
            return self._bind_apply(joint, name, expr)

        if op in {"capply", "controlled"}:
            # capply(ctrl[, …], U, tgt[, …]) — Cⁿ(U) on |1…1⟩
            return self._bind_capply(joint, name, expr, op_label=op)

        if op == "ocapply":
            # ocapply(ctrl[, …], U, tgt[, …]) — all open (|0⟩) controls
            return self._bind_capply(
                joint, name, expr, force_all_open=True, op_label="ocapply"
            )

        if op == "toffoli":
            # toffoli(c0, c1, tgt) — sugar for capply(c0, c1, X, tgt)
            if len(expr.args) != 3:
                raise KernelError("toffoli requires (ctrl0, ctrl1, tgt)")
            if not all(isinstance(a, Var) for a in expr.args):
                raise KernelError("toffoli args must be state variables")
            sp = expr.span
            synthetic = Call(
                callee=Var(name="capply", span=sp),
                args=[
                    expr.args[0],
                    expr.args[1],
                    Var(name="X", span=sp),
                    expr.args[2],
                ],
                span=sp,
            )
            return self._bind_capply(joint, name, synthetic)

        if op == "hadamard":
            # hadamard(w) — sugar for apply(Hadamard, w)
            if len(expr.args) != 1 or not isinstance(expr.args[0], Var):
                raise KernelError("hadamard requires (wire)")
            from .unitaries import apply_unitary_on_wires, hadamard

            wire = expr.args[0].name
            try:
                updated = apply_unitary_on_wires(joint, [wire], hadamard())
            except ValueError as e:
                raise KernelError(str(e)) from e
            if name == wire:
                return updated
            return updated.bind_pushforward(name, lambda a, w=wire: a[w])

        if op in {"walk_shift", "shift"}:
            # walk_shift(coin, pos) — DTQW conditional translation
            if len(expr.args) != 2:
                raise KernelError("walk_shift requires (coin, pos)")
            if not isinstance(expr.args[0], Var) or not isinstance(expr.args[1], Var):
                raise KernelError("walk_shift args must be state variables")
            from .unitaries import shift_position

            coin_n = expr.args[0].name
            pos_n = expr.args[1].name
            return joint.bind_pushforward(
                name, lambda a: shift_position(a[coin_n], a[pos_n])
            )

        if op == "tensor":
            raise KernelError("use `(a, b) = left *|* right`")

        if op == "trace_out":
            # trace_out(coord) — partial trace / discard subsystem coordinate
            if len(expr.args) != 1 or not isinstance(expr.args[0], Var):
                raise KernelError("trace_out requires (coordVar)")
            coord = expr.args[0].name
            trimmed = joint.trace_out(coord)
            # Placeholder classical bind; remaining coordinates stay measurable
            return trimmed.bind_const(name, 0)

        if op == "expect":
            # expect(O, psi) — single-qubit ⟨P⟩
            # expect(ZZ, a, b) — two-qubit ⟨Z⊗Z⟩ (Bell correlation; no collapse)
            from .quantum_ops import expect_pauli, expect_zz

            if len(expr.args) == 2 and isinstance(expr.args[1], Var):
                op_name = self._operator_name(expr.args[0])
                if op_name.upper() == "ZZ":
                    raise KernelError("expect(ZZ, …) requires two qubit variables")
                src = expr.args[1].name
                amps = joint.amplitude_marginal(src)
                a0 = amps.get(0, 0j)
                a1 = amps.get(1, 0j)
                try:
                    val = expect_pauli(op_name, a0, a1)
                except ValueError as e:
                    raise KernelError(str(e)) from e
                # Non-destructive: bind scalar onto existing joint worlds
                return joint.bind_const(name, float(val))
            if (
                len(expr.args) == 3
                and isinstance(expr.args[1], Var)
                and isinstance(expr.args[2], Var)
            ):
                op_name = self._operator_name(expr.args[0])
                if op_name.upper() != "ZZ":
                    raise KernelError(
                        f"two-qubit expect supports ZZ only, got `{op_name}`"
                    )
                try:
                    val = expect_zz(
                        joint.worlds, expr.args[1].name, expr.args[2].name
                    )
                except ValueError as e:
                    raise KernelError(str(e)) from e
                return joint.bind_const(name, float(val))
            raise KernelError(
                "expect requires (operator, stateVar) or (ZZ, qubitA, qubitB)"
            )

        if op == "occupation":
            # occupation(psi, k) — Born weight |⟨k|ψ⟩|² on Int site / Fock label
            if len(expr.args) != 2 or not isinstance(expr.args[0], Var):
                raise KernelError("occupation requires (stateVar, siteIndex)")
            src = expr.args[0].name
            k = self._eval_value(expr.args[1], {})
            if not isinstance(k, int):
                try:
                    k = int(k)
                except (TypeError, ValueError) as e:
                    raise KernelError("occupation site index must be Int") from e
            amps = joint.amplitude_marginal(src)
            val = float(abs(amps.get(k, 0j)) ** 2)
            return joint.bind_const(name, val)

        if op == "Coin":
            return joint.bind_split(name, {0: 0.5, 1: 0.5})
        if op == "Vacuum":
            # vacuum() = |0⟩ (Fock / computational ground), NOT empty support
            return joint.bind_pushforward(name, lambda a: 0)
        if op == "empty":
            # empty support (destructive interference / null joint)
            return Joint.empty()
        if op == "Dirac":
            if not expr.args:
                raise KernelError("dirac requires an argument (point mass δ_c)")
            return joint.bind_pushforward(name, lambda a: self._eval_value(expr.args[0], a))
        if op == "finiteize":
            # ADR 0185 Lane A: finiteize(lo, hi, n_bins, n_samples[, seed])
            # Host equal-width histogram of uniform continuous draws on [lo, hi).
            # Result is ordinary finite State (no mid-program Continuous type).
            # ADR 0204 / LISS-0401: a Continuous first argument dispatches to
            # the second overload instead -- discriminated by the first
            # arg's bound value, not by arity (both forms take 4-5 args).
            if (
                expr.args
                and isinstance(expr.args[0], Var)
                and isinstance(self.objects.get(expr.args[0].name), ContinuousFieldValue)
            ):
                return self._bind_finiteize_continuous(joint, name, expr)
            return self._bind_finiteize(joint, name, expr)
        if op == "field_from_host":
            # ADR 0204 / LISS-0399: Continuous injection -- never touches the
            # Joint; the Kernel only ever holds an opaque handle.
            return self._bind_field_from_host(joint, name, expr)
        if op == "weight":
            # ADR 0204 / LISS-0400: pointwise composition -- Kernel-side
            # bookkeeping only, no math evaluated here.
            return self._bind_continuous_compose(joint, name, expr, op_name="weight", arity=(2, 3))
        if op == "mask":
            return self._bind_continuous_compose(joint, name, expr, op_name="mask", arity=(2, 2))
        if op == "prepare_selection":
            # LISS-0324: prepare_selection(n) -- equal superposition over all
            # 2**n n-candidate selection patterns. Candidate identity never
            # crosses into the Kernel; only the finite width does.
            return self._bind_prepare_selection(joint, name, expr)

        if op == "wavepacket":
            # wavepacket(xmin, xmax, n, x0, sigma) — Gaussian on a uniform grid
            if len(expr.args) != 5:
                raise KernelError(
                    "wavepacket requires (xmin, xmax, n, x0, sigma)"
                )
            xmin = float(self._eval_value(expr.args[0], {}))
            xmax = float(self._eval_value(expr.args[1], {}))
            n_raw = self._eval_value(expr.args[2], {})
            if type(n_raw) is not int:
                raise KernelError("wavepacket n must be Int")
            n = n_raw
            x0 = float(self._eval_value(expr.args[3], {}))
            sigma = float(self._eval_value(expr.args[4], {}))
            if n < 2:
                raise KernelError("wavepacket needs n >= 2")
            if sigma <= 0:
                raise KernelError("wavepacket sigma must be positive")
            if xmax <= xmin:
                raise KernelError("wavepacket requires xmax > xmin")
            dx = (xmax - xmin) / float(n)
            xs = [xmin + i * dx for i in range(n)]
            # ψ ∝ exp(-(x-x0)²/(4σ²)) so |ψ|² has std σ
            import math as _math

            raw = [
                _math.exp(-((x - x0) ** 2) / (4.0 * sigma * sigma)) for x in xs
            ]
            norm2 = sum(a * a for a in raw)
            if norm2 <= EPS:
                raise KernelError("wavepacket amplitudes vanished")
            dist = {xs[i]: (raw[i] * raw[i]) / norm2 for i in range(n)}
            return joint.bind_split(name, dist)
        if math_ops.known_math_op(op):
            if len(expr.args) != 1 or not isinstance(expr.args[0], Var):
                raise KernelError(f"{op} expects one State variable")
            src = expr.args[0].name
            return joint.map_coord(src, name, lambda v: math_ops.apply_math(op, v))

        if op == "inner":
            return self._bind_inner(joint, name, expr)
        if op == "outer":
            raise KernelError(
                "outer must be bound as `Operator … = outer(…)`, not a State Call"
            )

        raise KernelError(f"unknown function `{op}`")

    def _bind_ket_sum_binder(self, joint: Joint, name: str, expr: KetSumBinder) -> Joint:
        """`Sigma (x In {0,1}^n) { |x> }` (LISS-0420, literal semantics per
        LISS-0422) -- the literal, unnormalized sum $\\sum_{x} |x\\rangle$:
        each basis ket gets amplitude 1, exactly matching the bare
        blackboard `Sigma` symbol. Normalization is never implicit -- the
        caller must apply an explicit coefficient (e.g.
        `(1.0/sqrt(2.0^n)) * Sigma (...) { |x> }`) to obtain a normalized
        State, the same way the blackboard equation carries its own
        separate `1/sqrt(2^n)` prefactor. Deliberately NOT the same
        construction as `_bind_prepare_selection` (which stays equal-
        weight/normalized as its own, unrelated native primitive) --
        `bind_split` takes a probability `p` and computes `amp =
        parent_amp * sqrt(p)`, so `p = 1.0` per branch yields amplitude 1,
        i.e. literal unnormalized addition."""
        width_raw = self._eval_value(expr.domain.width, {})
        try:
            n = int(width_raw)
        except (TypeError, ValueError) as e:
            raise KernelError("Sigma ket-sum domain width must be Int") from e
        if n < 1:
            raise KernelError("Sigma ket-sum domain width must be >= 1")

        import itertools

        labels = tuple(expr.domain.labels)
        patterns = list(itertools.product(labels, repeat=n))
        return joint.bind_split(name, {pattern: 1.0 for pattern in patterns})

    def _eval_classical_op_binder(self, expr: "OpBinder", assign: dict[str, Any]) -> Any:
        """LISS-0424/0427: classical numeric `Sigma`/`Pi` and the Bool-
        valued `ForAll` -- alongside the existing Operator-typed
        (`OpBinder` reached via the separate `Operator H = ...` statement
        dispatch) and State-typed (`KetSumBinder`) forms. Folds the body
        with `+` (Sigma), `*` (Pi), or logical AND with early exit
        (ForAll) over a bare-range `IndexDomain` (LISS-0423), evaluating
        the body/guard as plain classical expressions -- reuses the
        Operator-DSL's existing `OpIndexed`/`OpBin`/`OpVar`/`OpLit`
        grammar (already proven for classical array-indexed coefficients
        like `activity_w[i] * Z[i]`) rather than requiring new general-
        expression array-index syntax. Handles multi-binding
        (`Sigma (i In D1, j In D2) where ... {...}`) by recursing into a
        nested `OpBinder` body, matching how the parser itself nests
        multi-binding binders (`parser.py::_op_binder`)."""
        from ..ast_nodes import IndexDomain, RevDomain

        domain = expr.domain
        descending = False
        while isinstance(domain, RevDomain):
            descending = not descending
            domain = domain.inner
        if not isinstance(domain, IndexDomain):
            raise KernelError(
                "classical Sigma/Pi/ForAll requires a bare-range binder "
                "domain (e.g. `0..n-1`), not an Operator/State-shaped domain"
            )
        start = int(self._eval_op_expr_classical(domain.start, assign))
        end = int(self._eval_op_expr_classical(domain.end, assign))
        indices = list(range(start, end + 1)) if end >= start else []
        if descending:
            indices.reverse()
        if expr.kind == "Sigma":
            acc: Any = 0
        elif expr.kind == "Pi":
            acc = 1
        elif expr.kind == "ForAll":
            acc = True
        else:  # Min
            # LISS-0428: min over an empty guarded domain is +infinity --
            # the standard identity element for min-as-a-fold (matching
            # sum's 0 / product's 1), and it reproduces the original
            # `_bind_feasible_predicate`/`host/scoring.py::is_feasible`
            # Python behavior exactly: "if pairs and min(...) < threshold"
            # skips the diversity check entirely (vacuously satisfied)
            # when no pair is selected -- `+inf >= theta` is always True,
            # the same vacuous pass.
            acc = float("inf")
        for i in indices:
            local = dict(assign)
            local[expr.variable] = i
            if expr.guard is not None and not bool(
                self._eval_op_expr_classical(expr.guard, local)
            ):
                continue
            if isinstance(expr.body, OpBinder):
                term = self._eval_classical_op_binder(expr.body, local)
            else:
                term = self._eval_op_expr_classical(expr.body, local)
            if expr.kind == "Sigma":
                acc = acc + term
            elif expr.kind == "Pi":
                acc = acc * term
            elif expr.kind == "ForAll":
                acc = acc and bool(term)
                if not acc:  # short-circuit on the first False
                    break
            else:  # Min
                acc = term if term < acc else acc
        return acc

    def _eval_op_expr_classical(self, expr: Any, assign: dict[str, Any]) -> Any:
        """Evaluate an Operator-DSL `OpExpr` node as a plain classical
        value (LISS-0424) -- rejects genuine Operator/Pauli atoms with a
        clear error, since those belong in an Operator-typed Sigma/Pi."""
        if isinstance(expr, OpBinder):
            # LISS-0429: a nested Sigma/Pi/ForAll/Min used as part of a
            # larger classical expression, e.g. `Sigma (...) {...} == 3`
            # as one condition inside a Set comprehension's list.
            return self._eval_classical_op_binder(expr, assign)
        if isinstance(expr, OpLit):
            return expr.value
        if isinstance(expr, OpVar):
            if expr.name in assign:
                return assign[expr.name]
            if expr.name in self.scalars:
                return self.scalars[expr.name]
            # LISS-0432: a Host-bound `Float[N]…`/`Bool[N]…` coefficient
            # array (e.g. `C`/`D` in the confirmed S02 step 2 design) used
            # inside a classical Sigma/ForAll/Min/Set-comprehension body --
            # the same array store `activity_w`/`selectivity_w` already use
            # inside an `Operator = Sigma(...) {...}` body, just made
            # visible from the classical evaluation path too.
            array_context = self._operator_array_context()
            if expr.name in array_context:
                return array_context[expr.name]
            raise KernelError(
                f"classical Sigma/Pi: unbound name `{expr.name}`"
            )
        if isinstance(expr, OpIndexed):
            base = self._eval_op_expr_classical(expr.base, assign)
            index = int(self._eval_op_expr_classical(expr.index, assign))
            try:
                return base[index]
            except (TypeError, IndexError, KeyError) as e:
                raise KernelError(
                    f"classical Sigma/Pi: index {index} out of range"
                ) from e
        if isinstance(expr, OpPow):
            base = self._eval_op_expr_classical(expr.base, assign)
            return base ** expr.exp
        if isinstance(expr, OpBin):
            if expr.op in ("&&", "||"):
                lhs = bool(self._eval_op_expr_classical(expr.lhs, assign))
                rhs = bool(self._eval_op_expr_classical(expr.rhs, assign))
                return (lhs and rhs) if expr.op == "&&" else (lhs or rhs)
            if expr.op == "Implies":
                lhs = bool(self._eval_op_expr_classical(expr.lhs, assign))
                rhs = bool(self._eval_op_expr_classical(expr.rhs, assign))
                return (not lhs) or rhs
            lhs = self._eval_op_expr_classical(expr.lhs, assign)
            rhs = self._eval_op_expr_classical(expr.rhs, assign)
            ops: dict[str, Any] = {
                "+": lambda a, b: a + b,
                "-": lambda a, b: a - b,
                "*": lambda a, b: a * b,
                "<": lambda a, b: a < b,
                "<=": lambda a, b: a <= b,
                ">": lambda a, b: a > b,
                ">=": lambda a, b: a >= b,
                "==": lambda a, b: a == b,
                "!=": lambda a, b: a != b,
            }
            if expr.op not in ops:
                raise KernelError(
                    f"classical Sigma/Pi: unsupported operator `{expr.op}`"
                )
            return ops[expr.op](lhs, rhs)
        raise KernelError(
            f"classical Sigma/Pi body contains a non-classical term "
            f"({type(expr).__name__}) -- Operator/Pauli atoms belong in "
            "an Operator-typed Sigma/Pi, not a classical one"
        )

    def _is_state_producing_bind_expr(self, expr: Expr) -> bool:
        """LISS-0420 (coefficient semantics corrected by LISS-0422): does
        this expression need the amplitude-scaling bind path, as opposed
        to `_eval_value` (pure classical)? Deliberately narrow --
        `KetLit`/`KetSumBinder` only, not a general classifier over every
        State-producing node type. A broader first attempt (also matching
        `Coin`/`Vacuum`/`WhenExpr`/`SuperposeExpr`/`TensorExpr`) was found,
        during LISS-0420's own Green phase, to reopen a boundary LISS-0273
        deliberately closed: `Float bad = Coin() * 0.5` must still fail (a
        State-forming call is not a valid classical operand), and
        previously did so precisely because `_eval_value` could not
        evaluate `Coin()` at all -- silently "fixing" that crash for every
        State-producing type removed a real safety net the declared-type
        check doesn't independently replace at this layer. `KetLit`/
        `KetSumBinder` are safe to include because nothing pre-existing
        relied on either crashing here. Since LISS-0422, `KetSumBinder` is
        itself unnormalized, so this scaling path is how a caller supplies
        the required normalization coefficient, not an optional/redundant
        one."""
        if isinstance(expr, KetLit):
            return True
        return isinstance(expr, KetSumBinder)

    def _bind_scaled_state(
        self, joint: Joint, name: str, state_expr: Expr, scalar_expr: Expr
    ) -> Joint:
        """Bind `state_expr` (any node `_bind` handles) then scale every
        resulting world's amplitude by the classical `scalar_expr` value --
        the general mechanism behind `classical_scalar * <State-producing
        expr>` (LISS-0420)."""
        from .joint import World, _coalesce

        scale = self._eval_value(scalar_expr, {})
        temp = f"__scale_tmp_{id(state_expr)}"
        sub = self._bind(joint, temp, state_expr)
        out: list[World] = []
        for w in sub.worlds:
            assign = {k: v for k, v in w.assign.items() if k != temp}
            assign[name] = w.assign[temp]
            out.append(
                World(assign=assign, amp=w.amp * scale, coord_phase=dict(w.coord_phase))
            )
        return Joint(worlds=_coalesce(out))

    def _bind_state_divided_by_norm(
        self, joint: Joint, name: str, state_expr: Expr, norm_expr: NormExpr
    ) -> Joint:
        """`<state_expr> / ||<state_expr's own repetition>||` (LISS-0426) --
        the literal transcription of
        $P_F\\lvert\\psi_0\\rangle/\\lVert P_F\\lvert\\psi_0\\rangle\\rVert$.
        Binds the numerator independently from the norm's own inner
        expression (two separate `_bind` calls, matching the equation's
        own literal repetition rather than trying to cleverly reuse one
        computation), then scales every numerator world's amplitude by
        `1/norm`. `project`'s own renormalization was removed in LISS-0431
        specifically so this division is what performs it -- doing it here
        too would double-normalize."""
        from .joint import World, _coalesce

        temp = f"__div_tmp_{id(state_expr)}"
        sub = self._bind(joint, temp, state_expr)
        norm = self._compute_norm(joint, norm_expr.state)

        out: list[World] = []
        for w in sub.worlds:
            assign = {k: v for k, v in w.assign.items() if k != temp}
            assign[name] = w.assign[temp]
            out.append(
                World(assign=assign, amp=w.amp / norm, coord_phase=dict(w.coord_phase))
            )
        return Joint(worlds=_coalesce(out))

    def _compute_norm(self, joint: Joint, state_expr: Expr) -> float:
        """$\\lVert\\text{state\\_expr}\\rVert = \\sqrt{\\sum_x\\lvert c_x\\rvert^2}$
        (LISS-0426) -- binds `state_expr` as its own independent
        sub-computation and sums squared amplitudes across every
        resulting world."""
        temp = f"__norm_tmp_{id(state_expr)}"
        sub = self._bind(joint, temp, state_expr)
        total = sum(abs(w.amp) ** 2 for w in sub.worlds)
        if total <= EPS:
            raise KernelError("||...|| of a zero-norm (vacuum) state")
        return total**0.5

    def _project_onto_operator(
        self, joint: Joint, coord_name: str, operator_name: str
    ) -> Joint:
        """`project psi onto P` where `P` is a general (multi-term)
        Operator (LISS-0431) -- compiles `P`'s already-resolved OpExpr
        (`self.operators[operator_name]`, e.g. LISS-0430's Pauli-Z-
        decomposed $P_F$) to a matrix and scales each World's amplitude
        by the square root of `P`'s diagonal entry at that World's own
        `coord_name` value (big-endian tuple-to-index, matching
        `hamiltonian.py`'s own convention -- confirmed by direct
        execution, not assumed). Diagonal-only: the confirmed target
        design (a projector built from `Sigma (x In F) { |x><x| }`) is
        always diagonal in the computational basis by construction; a
        genuinely non-diagonal Operator target is out of scope and
        rejected with a clear error rather than silently mishandled."""
        from .hamiltonian import compile_hamiltonian
        from .joint import World, _coalesce

        op_ast = self.operators.get(operator_name)
        if op_ast is None:
            raise KernelError(f"project onto `{operator_name}`: unknown Operator")
        sample = next(
            (
                world.assign.get(coord_name)
                for world in joint.worlds
                if isinstance(world.assign.get(coord_name), tuple)
            ),
            None,
        )
        if sample is None:
            raise KernelError(
                "project onto a general Operator requires a tuple-valued "
                "coordinate"
            )
        n = len(sample)
        cache_key = (operator_name, n)
        matrix = self._compiled_operator_cache.get(cache_key)
        if matrix is None:
            matrix = compile_hamiltonian(op_ast, env={}, n_qubits=n)
            self._compiled_operator_cache[cache_key] = matrix
        dim = len(matrix)
        for i in range(dim):
            for j in range(dim):
                if i != j and abs(matrix[i][j]) > EPS:
                    raise KernelError(
                        "project onto a general Operator currently supports "
                        "diagonal projectors only (e.g. Sigma (x In F) "
                        "{ |x><x| }); the given Operator has a non-zero "
                        "off-diagonal entry"
                    )

        def _index(pattern: tuple[int, ...]) -> int:
            idx = 0
            for bit in pattern:
                idx = idx * 2 + int(bit)
            return idx

        out: list[World] = []
        for w in joint.worlds:
            value = w.assign.get(coord_name)
            if not isinstance(value, tuple):
                continue
            diag = matrix[_index(value)][_index(value)].real
            if diag <= EPS:
                continue
            new_amp = w.amp * cmath.sqrt(diag)
            if abs(new_amp) ** 2 <= EPS:
                continue
            out.append(
                World(assign=dict(w.assign), amp=new_amp, coord_phase=dict(w.coord_phase))
            )
        if not out:
            return Joint.empty()
        return Joint(worlds=_coalesce(out))

    def _eval_set_comprehension(
        self, expr: "SetComprehension", assign: dict[str, Any]
    ) -> tuple[Any, ...]:
        """`{ x In D : cond1, cond2, ... }` (LISS-0429) -- enumerates `D`
        (currently only `{0,1}^n`, matching the confirmed target design;
        a bare-range `D` is deliberately out of scope for this Issue),
        keeping only elements where every comma-separated condition
        (implicit conjunction) holds. Reuses `_eval_op_expr_classical`
        for conditions, the same leaf evaluator LISS-0424's classical
        Sigma/Pi/ForAll/Min already use."""
        from ..ast_nodes import SetPowerDomain

        domain = expr.domain
        if not isinstance(domain, SetPowerDomain):
            raise KernelError(
                "Set comprehension domain must be `{0,1}^n` (or a similar "
                "set-power literal) -- a bare-range domain is not yet "
                "supported"
            )
        width_raw = self._eval_value(domain.width, assign)
        n = int(width_raw)
        labels = tuple(domain.labels)

        import itertools

        matches: list[Any] = []
        for element in itertools.product(labels, repeat=n):
            local = dict(assign)
            local[expr.variable] = element
            if all(
                bool(self._eval_op_expr_classical(cond, local))
                for cond in expr.conditions
            ):
                matches.append(element)
        return tuple(matches)

    def _bind_prepare_selection(self, joint: Joint, name: str, expr: Call) -> Joint:
        """prepare_selection(n: Int) -- equal superposition over all 2**n
        n-candidate selection patterns (each an n-tuple of 0/1 flags),
        mechanically identical to `n` independent unconstrained qubits
        (LISS-0324)."""
        if len(expr.args) != 1:
            raise KernelError("prepare_selection requires (n)")
        n_raw = self._eval_value(expr.args[0], {})
        if type(n_raw) is not int:
            raise KernelError("prepare_selection n must be Int")
        n = n_raw
        if n < 1:
            raise KernelError("prepare_selection requires n >= 1")

        import itertools

        patterns = list(itertools.product((0, 1), repeat=n))
        weight = 1.0 / len(patterns)
        return joint.bind_split(name, {pattern: weight for pattern in patterns})

    def _bind_finiteize(self, joint: Joint, name: str, expr: Call) -> Joint:
        """finiteize(lo, hi, n_bins, n_samples[, seed]) — ADR 0185 Lane A.

        Host equal-width histogram (ADR 0163/0164) of uniform continuous draws
        on half-open ``[lo, hi)``. Binds a finite State coordinate ``name``.
        """
        from ..host_monte_carlo import (
            APPROX_EQUAL_WIDTH,
            EqualWidthHistogramMonteCarlo,
            HostRngAdapter,
            MonteCarloInjectError,
            MonteCarloSpec,
        )

        if len(expr.args) not in (4, 5):
            raise KernelError(
                "finiteize requires (lo, hi, n_bins, n_samples[, seed])"
            )
        lo = float(self._eval_value(expr.args[0], {}))
        hi = float(self._eval_value(expr.args[1], {}))
        n_bins_raw = self._eval_value(expr.args[2], {})
        n_samples_raw = self._eval_value(expr.args[3], {})
        if type(n_bins_raw) is not int or type(n_samples_raw) is not int:
            raise KernelError("finiteize n_bins and n_samples must be Int")
        n_bins = n_bins_raw
        n_samples = n_samples_raw
        seed: int | None = self.seed
        if len(expr.args) == 5:
            seed_raw = self._eval_value(expr.args[4], {})
            if type(seed_raw) is not int:
                raise KernelError("finiteize seed must be Int")
            seed = seed_raw
        if hi <= lo:
            raise KernelError("finiteize requires hi > lo")
        if n_bins < 1 or n_samples < 1:
            raise KernelError(
                "finiteize requires n_bins >= 1 and n_samples >= 1"
            )

        width = hi - lo

        def continuous_draw(rng: Any, _lo: float = lo, _w: float = width) -> float:
            return _lo + _w * float(rng.random())

        spec = MonteCarloSpec(
            domain_label=name,
            interval=(lo, hi),
            n_bins=n_bins,
            n_samples=n_samples,
            approximation=APPROX_EQUAL_WIDTH,
            coordinate=name,
            provenance={"surface": "finiteize", "draw": "uniform_interval"},
            seed=seed,
        )
        try:
            inject = EqualWidthHistogramMonteCarlo().sample_to_finite(
                spec,
                HostRngAdapter(seed=seed),
                continuous_draw=continuous_draw,
            )
        except MonteCarloInjectError as exc:
            raise KernelError(f"{exc.code}: {exc}") from exc

        # Stash provenance for Host/debug (not a State carrier).
        self.objects[f"__finiteize_prov_{name}"] = dict(inject.provenance)
        dist = {label: float(mass) for label, mass in inject.atoms}
        return joint.bind_split(name, dist)

    def _bind_finiteize_continuous(self, joint: Joint, name: str, expr: Call) -> Joint:
        """finiteize(continuous, lo, hi, n_bins[, seed]) — ADR 0204 / LISS-0401.

        Delegates the actual discretization to `ContinuousFieldPort.discretize`
        -- the Kernel never evaluates the composed handle tree itself, only
        assembles provenance (ADR 0074 `discretization` block +
        `continuous_pipeline`) from it.
        """
        if len(expr.args) not in (4, 5):
            raise KernelError(
                "finiteize(Continuous, lo, hi, n_bins[, seed]) requires 4-5 arguments"
            )
        continuous_value = self.objects[expr.args[0].name]  # type: ignore[union-attr]
        lo = float(self._eval_value(expr.args[1], {}))
        hi = float(self._eval_value(expr.args[2], {}))
        n_bins_raw = self._eval_value(expr.args[3], {})
        if type(n_bins_raw) is not int:
            raise KernelError("finiteize n_bins must be Int")
        n_bins = n_bins_raw
        seed: int | None = self.seed
        if len(expr.args) == 5:
            seed_raw = self._eval_value(expr.args[4], {})
            if type(seed_raw) is not int:
                raise KernelError("finiteize seed must be Int")
            seed = seed_raw
        if hi <= lo:
            raise KernelError("finiteize requires hi > lo")
        if n_bins < 1:
            raise KernelError("finiteize requires n_bins >= 1")
        if self.continuous_field is None:
            raise KernelError(
                "CONTINUOUS_FIELD_PORT_MISSING: no ContinuousFieldPort configured"
            )

        dist = self.continuous_field.discretize(
            continuous_value, lo=lo, hi=hi, n_bins=n_bins, seed=seed
        )
        self.objects[f"__finiteize_prov_{name}"] = {
            "surface": "finiteize",
            "source": "continuous",
            "interval": [lo, hi],
            "n_bins": n_bins,
            "discretization": {
                "domain": name,
                "basis": "EqualWidthHistogram",
                "resolution": n_bins,
            },
            "continuous_pipeline": continuous_pipeline_ops(continuous_value),
            "finite_approximation": True,
            "note": "finite histogram approximation of a Continuous value; not the continuous field",
        }
        return joint.bind_split(name, {label: float(mass) for label, mass in dist.items()})

    def _bind_field_from_host(self, joint: Joint, name: str, expr: Call) -> Joint:
        """field_from_host(source, domain) — ADR 0204 / LISS-0399.

        Routes through the injected `ContinuousFieldPort`; the Kernel never
        evaluates the underlying continuous function. Binds an opaque
        `ContinuousFieldValue` handle in `self.objects` -- the Joint is
        never touched (Continuous values are never Joint-compatible).
        """
        if len(expr.args) != 2:
            raise KernelError("field_from_host requires (source, domain)")
        source = self._eval_value(expr.args[0], {})
        domain = self._eval_value(expr.args[1], {})
        if not isinstance(source, str) or not isinstance(domain, str):
            raise KernelError("field_from_host requires string (source, domain)")
        if self.continuous_field is None:
            raise KernelError(
                "CONTINUOUS_FIELD_PORT_MISSING: no ContinuousFieldPort configured"
            )
        host_ref = self.continuous_field.field(source, domain)
        self.objects[name] = ContinuousFieldValue(op="field_from_host", host_ref=host_ref)
        return joint

    def _bind_continuous_compose(
        self,
        joint: Joint,
        name: str,
        expr: Call,
        *,
        op_name: str,
        arity: tuple[int, int],
    ) -> Joint:
        """weight/mask — ADR 0204 / LISS-0400.

        Composes a new opaque `ContinuousFieldValue` referencing its input
        handles; no pointwise math runs here (deferred to `finiteize`,
        LISS-0401). Never touches the Joint.
        """
        lo, hi = arity
        if not (lo <= len(expr.args) <= hi):
            raise KernelError(
                f"{op_name} requires {lo}-{hi} Continuous arguments"
                if lo != hi
                else f"{op_name} requires {lo} Continuous arguments"
            )
        inputs: list[ContinuousFieldValue] = []
        for arg in expr.args:
            if not isinstance(arg, Var):
                raise KernelError(f"{op_name} arguments must be Continuous-bound names")
            value = self.objects.get(arg.name)
            if not isinstance(value, ContinuousFieldValue):
                raise KernelError(
                    f"{op_name} argument `{arg.name}` is not a Continuous value"
                )
            inputs.append(value)
        self.objects[name] = ContinuousFieldValue(op=op_name, inputs=tuple(inputs))
        return joint

    def _bind_inner(self, joint: Joint, name: str, expr: Call) -> Joint:
        """inner(phi, psi) → Classical Float on ``name`` (LISS-0229)."""
        from .joint import World, _coalesce

        if len(expr.args) != 2 or not all(isinstance(a, Var) for a in expr.args):
            raise KernelError("inner requires two state variables")
        left = resolve_scientific_binding(
            expr.args[0].name, joint.worlds[0].assign if joint.worlds else {}
        )  # type: ignore[union-attr]
        right = resolve_scientific_binding(
            expr.args[1].name, joint.worlds[0].assign if joint.worlds else {}
        )  # type: ignore[union-attr]
        amps_l = joint.amplitude_marginal(left)
        amps_r = joint.amplitude_marginal(right)
        keys = set(amps_l) | set(amps_r)
        overlap = sum(
            (amps_l.get(k, 0j).conjugate() * amps_r.get(k, 0j)) for k in keys
        )
        value = float(overlap.real) if abs(overlap.imag) < 1e-10 else float(abs(overlap))
        return Joint(worlds=_coalesce([World(assign={name: value}, amp=1 + 0j)]))

    def _materialize_outer(self, joint: Joint, expr: Call) -> Any:
        """outer(psi, phi) → dense |ψ⟩⟨φ| Operator (LISS-0229, 1-qubit MVP)."""
        from .qft_dense import DenseMatrixOp

        if len(expr.args) != 2 or not all(isinstance(a, Var) for a in expr.args):
            raise KernelError("outer requires two state variables")
        psi = expr.args[0].name  # type: ignore[union-attr]
        phi = expr.args[1].name  # type: ignore[union-attr]
        amps_psi = joint.amplitude_marginal(psi)
        amps_phi = joint.amplitude_marginal(phi)
        # Single-qubit computational support {0,1}.
        labels = sorted(set(amps_psi) | set(amps_phi) | {0, 1})
        if any(lab not in (0, 1) for lab in labels):
            raise KernelError("outer MVP requires qubit computational labels {0,1}")
        # |ψ⟩⟨φ| with rows/cols ordered 0,1
        mat = [
            [
                amps_psi.get(i, 0j) * amps_phi.get(j, 0j).conjugate()
                for j in (0, 1)
            ]
            for i in (0, 1)
        ]
        return DenseMatrixOp(matrix=mat, n_qubits=1)

    def _as_unary_fn(self, fn: Expr) -> Callable[[Any], Any]:
        if isinstance(fn, Lambda):
            param = fn.param

            def f(v: Any) -> Any:
                return self._eval_value(fn.body, {param: v})

            return f
        raise KernelError("map/project fn must be a lambda (x -> expr)")

    def _as_pred_fn(self, fn: Expr) -> Callable[[Any], bool]:
        f = self._as_unary_fn(fn)

        def p(v: Any) -> bool:
            r = f(v)
            return bool(r)

        return p

    def _maybe_capture_classical_scalar(self, joint: Joint, name: str) -> None:
        """Promote a deterministic classical Joint coordinate into scalars.

        Used when Type-First `Float x = …` was bound via a method Call (not
        `_is_closed`), so `evolve … for x` and Operator OpVars can resolve it
        (LISS-0137).
        """
        if name in self.scalars:
            return
        try:
            marg = joint.marginal(name)
        except Exception:
            return
        if len(marg) != 1:
            return
        raw = next(iter(marg))
        try:
            if isinstance(raw, Fraction):
                self.scalars[name] = raw
            else:
                self.scalars[name] = float(raw)
        except (TypeError, ValueError):
            pass

    def _is_closed(self, expr: Expr) -> bool:
        if isinstance(expr, (LitInt, LitFloat, LitBool, LitString)):
            return True
        if isinstance(expr, Var):
            # Prelude / already-bound classical scalars (ADR 0062)
            return expr.name in self.scalars
        if isinstance(expr, Attr):
            if (
                isinstance(expr.obj, Var)
                and expr.obj.name == "Math"
                and expr.name in {"pi", "sqrt2", "inv_sqrt2"}
            ):
                return True
            # Struct / class field projections are classical once the object exists
            # (LISS-0137: Float J = c.J → Operator coeffs).
            if isinstance(expr.obj, Var) and expr.obj.name in self.objects:
                return True
            # Unit-suffixed literals are closed classical magnitudes.
            if isinstance(expr.obj, (LitInt, LitFloat)):
                from ..dimensions import UNIT_TABLE

                return expr.name in UNIT_TABLE
            return False
        if isinstance(expr, UnitConvert):
            return self._is_closed(expr.expr)
        if isinstance(expr, BinOp):
            return self._is_closed(expr.lhs) and self._is_closed(expr.rhs)
        return False

    def _lit(self, expr: Expr) -> Any:
        if isinstance(expr, LitInt):
            return expr.value
        if isinstance(expr, LitFloat):
            return expr.value
        if isinstance(expr, LitBool):
            return expr.value
        if isinstance(expr, LitString):
            return expr.value
        raise KernelError("not a literal")

    def _eval_unit_convert(self, expr: UnitConvert, assign: dict[str, Any]) -> float:
        """ADR 0124/0132/0134/0154/0155: scale or affine unit conversion."""
        from ..dimensions import UNIT_AFFINE_TO_CANONICAL, UNIT_SCALE_TO_CANONICAL

        raw, source = self._eval_value_with_unit(expr.expr, assign)
        raw = float(raw)
        if source is None:
            if isinstance(expr.expr, Attr) and expr.expr.name in (
                set(UNIT_SCALE_TO_CANONICAL) | set(UNIT_AFFINE_TO_CANONICAL)
            ):
                source = expr.expr.name
            else:
                raise KernelError("unit conversion requires a known source unit suffix")
        target = expr.target_unit
        if source in UNIT_SCALE_TO_CANONICAL and target in UNIT_SCALE_TO_CANONICAL:
            src_canon, src_factor = UNIT_SCALE_TO_CANONICAL[source]
            tgt_canon, tgt_factor = UNIT_SCALE_TO_CANONICAL[target]
            if src_canon != tgt_canon:
                raise KernelError(
                    f"cannot convert `{source}` to `{target}` "
                    f"(canonical {src_canon} vs {tgt_canon})"
                )
            return raw * (src_factor / tgt_factor)
        if source in UNIT_AFFINE_TO_CANONICAL and target in UNIT_AFFINE_TO_CANONICAL:
            src_canon, src_scale, src_off = UNIT_AFFINE_TO_CANONICAL[source]
            tgt_canon, tgt_scale, tgt_off = UNIT_AFFINE_TO_CANONICAL[target]
            if src_canon != tgt_canon:
                raise KernelError(
                    f"cannot convert `{source}` to `{target}` "
                    f"(affine canonical {src_canon} vs {tgt_canon})"
                )
            canon = raw * src_scale + src_off
            return (canon - tgt_off) / tgt_scale
        raise KernelError(
            f"unit `{source}` → `{target}` is not in the scale or affine set"
        )

    def _eval_value_with_unit(
        self, expr: Expr, assign: dict[str, Any]
    ) -> tuple[Any, str | None]:
        """Evaluate expression and optional unit suffix (ADR 0155 / 0174)."""
        from ..dimensions import UNIT_TABLE, to_canonical_magnitude, unit_canonical

        if isinstance(expr, Attr):
            if isinstance(expr.obj, (LitInt, LitFloat)) and expr.name in UNIT_TABLE:
                return float(expr.obj.value), expr.name
            # ADR 0174 / LISS-0292: field units from objects or free-fn locals.
            field_unit = self._attr_field_unit(expr, assign)
            if field_unit is not None or self._attr_is_object_field(expr, assign):
                return self._eval_value(expr, assign), field_unit
        if isinstance(expr, UnitConvert):
            return self._eval_unit_convert(expr, assign), expr.target_unit
        if isinstance(expr, Var):
            name = resolve_scientific_binding(expr.name, assign)
            if name in assign:
                unit = self.scalar_units.get(name)
                if unit is None:
                    unit = self._frame_units.get(name)
                # Locals may also carry unit in assign_units (free-fn frame).
                if unit is None and hasattr(self, "_call_local_units"):
                    unit = self._call_local_units.get(name)
                return assign[name], unit
            if expr.name in self.scalars:
                return self.scalars[expr.name], self.scalar_units.get(expr.name)
        if isinstance(expr, BinOp) and expr.op in {"+", "-"}:
            from ..dimensions import from_canonical_magnitude

            l, lu = self._eval_value_with_unit(expr.lhs, assign)
            r, ru = self._eval_value_with_unit(expr.rhs, assign)
            if lu is not None and ru is not None and lu != ru:
                lc = unit_canonical(lu)
                rc = unit_canonical(ru)
                if lc is not None and lc == rc:
                    # ADR 0155: compute in canonical; ADR 0186: restore LHS unit.
                    l_c, _ = to_canonical_magnitude(float(l), lu)
                    r_c, _ = to_canonical_magnitude(float(r), ru)
                    canon_out = _apply_op(expr.op, l_c, r_c)
                    try:
                        restored = from_canonical_magnitude(float(canon_out), lu)
                    except KeyError as e:
                        raise KernelError(
                            f"cannot restore display unit `{lu}` after promote"
                        ) from e
                    return restored, lu
            out_unit = lu if lu == ru else (lu or ru)
            if lu and ru and lu != ru:
                out_unit = None
            return _apply_op(expr.op, l, r), out_unit
        return self._eval_value(expr, assign), None

    @staticmethod
    def _put_unit(store: dict[str, str], name: str, unit: str | None) -> None:
        """Record or clear a unit suffix on a field/frame/scalar store."""
        if unit is not None:
            store[name] = unit
        else:
            store.pop(name, None)

    def _attr_host(
        self, expr: Attr, assign: dict[str, Any] | None = None
    ) -> ClassInstance | StructValue | None:
        """Resolve the class/struct instance hosting an Attr field read."""
        if isinstance(expr.obj, Var) and expr.obj.name == "this":
            return self._this
        if isinstance(expr.obj, Var) and assign and expr.obj.name in assign:
            inst = assign[expr.obj.name]
            if isinstance(inst, (ClassInstance, StructValue)):
                return inst
        if isinstance(expr.obj, Var) and expr.obj.name in self.objects:
            inst = self.objects[expr.obj.name]
            if isinstance(inst, (ClassInstance, StructValue)):
                return inst
        return None

    def _resolve_receiver_instance(
        self, recv_expr: Expr, assign: dict[str, Any] | None = None
    ) -> ClassInstance | StructValue | None:
        """Resolve a method-call receiver (`recv.method(...)`) to its
        instance (LISS-0358). The bare-Var-in-self.objects fast path is
        preserved exactly; any other expression shape (nested Attr, Call,
        ...) resolves through the general evaluator, so `outer.inner.m()`
        works the same as `Inner tmp = outer.inner; tmp.m()`. Returns None
        (never raises) for a non-instance receiver -- callers rely on this
        to fall through to their existing Math.*/map/project dispatch.
        """
        if isinstance(recv_expr, Var) and recv_expr.name in self.objects:
            return self.objects[recv_expr.name]
        if isinstance(recv_expr, Var):
            return None
        try:
            candidate = self._eval_value(recv_expr, assign or {})
        except KernelError:
            return None
        if isinstance(candidate, (ClassInstance, StructValue)):
            return candidate
        return None

    def _attr_is_object_field(
        self, expr: Attr, assign: dict[str, Any] | None = None
    ) -> bool:
        host = self._attr_host(expr, assign)
        return host is not None and expr.name in host.fields

    def _attr_field_unit(
        self, expr: Attr, assign: dict[str, Any] | None = None
    ) -> str | None:
        host = self._attr_host(expr, assign)
        if host is None:
            return None
        return host.field_units.get(expr.name)

    def _eval_value(self, expr: Expr, assign: dict[str, Any]) -> Any:
        if isinstance(expr, LitInt):
            return expr.value
        if isinstance(expr, LitFloat):
            return expr.value
        if isinstance(expr, LitBool):
            return expr.value
        if isinstance(expr, LitString):
            return expr.value
        if isinstance(expr, Var):
            name = resolve_scientific_binding(expr.name, assign)
            if name in assign:
                return assign[name]
            # ADR 0060: classical Type-First scalars (Float cfg = …)
            if expr.name in self.scalars:
                return self.scalars[expr.name]
            raise KernelError(f"unbound variable `{expr.name}`")
        if isinstance(expr, Coin):
            # classical eval of coin is forbidden mid-value; sample (counts as rng — avoid)
            raise KernelError("coin() cannot be evaluated as a classical value; bind via state")
        if isinstance(expr, Vacuum):
            raise KernelError("vacuum() is not a classical value")
        if isinstance(expr, Dirac):
            return self._eval_value(expr.arg, assign)
        if isinstance(expr, BinOp):
            if expr.op in {"+", "-"}:
                value, _unit = self._eval_value_with_unit(expr, assign)
                return value
            l = self._eval_value(expr.lhs, assign)
            r = self._eval_value(expr.rhs, assign)
            return _apply_op(expr.op, l, r)
        if isinstance(expr, UnitConvert):
            return self._eval_unit_convert(expr, assign)
        if isinstance(expr, Attr):
            # Unit suffix is compile-time only: 1.0.kg → 1.0 at runtime
            from ..dimensions import UNIT_TABLE

            if isinstance(expr.obj, (LitInt, LitFloat)) and expr.name in UNIT_TABLE:
                return float(expr.obj.value)
            # ADR 0062: Math.<const> ≡ prelude classical constants
            if (
                isinstance(expr.obj, Var)
                and expr.obj.name == "Math"
                and expr.name in {"pi", "sqrt2", "inv_sqrt2"}
            ):
                from ..stdlib.prelude import PRELUDE_CONSTANTS

                return PRELUDE_CONSTANTS[expr.name]
            # Enum.Variant (incl. Namespace.Enum.Variant)
            eq = self._expr_qualname(expr.obj)
            if eq is not None and eq in self.enums:
                ed = self.enums[eq]
                if expr.name not in ed.variants:
                    raise KernelError(
                        f"enum `{ed.qualified_name}` has no variant `{expr.name}`"
                    )
                return EnumValue(enum_name=ed.qualified_name, variant=expr.name)
            # ADR 0056: this.field
            if isinstance(expr.obj, Var) and expr.obj.name == "this":
                if self._this is None:
                    raise KernelError("`this` is only valid inside a class method")
                if expr.name not in self._this.fields:
                    raise KernelError(
                        f"class `{self._this.class_name}` has no field `{expr.name}`"
                    )
                return self._this.fields[expr.name]
            # Free-fn / method locals shadow outer objects of the same name
            # (e.g. param `board: ShelterBoard` vs outer CommandBoard board).
            if isinstance(expr.obj, Var) and expr.obj.name in assign:
                inst = assign[expr.obj.name]
                if isinstance(inst, (ClassInstance, StructValue)):
                    fields = inst.fields
                    cname = (
                        inst.class_name
                        if isinstance(inst, ClassInstance)
                        else inst.struct_name
                    )
                    if expr.name not in fields:
                        raise KernelError(f"`{cname}` has no field `{expr.name}`")
                    return fields[expr.name]
                if isinstance(inst, EnumValue):
                    raise KernelError("enum values have no fields")
            # instance.field (classical object field read — global objects)
            if isinstance(expr.obj, Var) and expr.obj.name in self.objects:
                inst = self.objects[expr.obj.name]
                if isinstance(inst, (ClassInstance, StructValue)):
                    fields = inst.fields
                    cname = (
                        inst.class_name
                        if isinstance(inst, ClassInstance)
                        else inst.struct_name
                    )
                    if expr.name not in fields:
                        raise KernelError(f"`{cname}` has no field `{expr.name}`")
                    return fields[expr.name]
                if isinstance(inst, EnumValue):
                    raise KernelError("enum values have no fields")
            obj = self._eval_value(expr.obj, assign)
            if isinstance(obj, (ClassInstance, StructValue)):
                fields = obj.fields
                cname = (
                    obj.class_name if isinstance(obj, ClassInstance) else obj.struct_name
                )
                if expr.name not in fields:
                    raise KernelError(f"`{cname}` has no field `{expr.name}`")
                return fields[expr.name]
            if isinstance(obj, EnumValue):
                raise KernelError("enum values have no fields")
            raise KernelError(f"cannot evaluate attribute `.{expr.name}` on {obj!r}")
        if isinstance(expr, WhenExpr):
            ctrl = self._eval_value(expr.ctrl, assign)
            for arm in expr.arms:
                if not arm.is_else and arm.pat == ctrl:
                    return self._eval_value(arm.body, assign)
            for arm in expr.arms:
                if arm.is_else:
                    return self._eval_value(arm.body, assign)
            raise KernelError("mix: no matching arm")
        if isinstance(expr, Call):
            q = self._expr_qualname(expr.callee)
            if q is not None and q in self.structs:
                return self._construct_struct(q, expr, assign)
            if q is not None and q in self.classes:
                return self._construct_instance(q, expr)
            # ADR 0179 / LISS-0273: pure classical Calls as classical operands.
            # Thread assign so nested free-fn object args see the caller frame.
            return self._eval_classical_call(expr, assign)
        if isinstance(expr, OpBinder):
            # LISS-0424: classical numeric Sigma/Pi as a sub-expression
            # (e.g. `Sigma (i In 0..n-1) { x[i] } == 3`), not just a bare
            # top-level bind -- reuses the same fold `_bind`'s OpBinder
            # case uses.
            return self._eval_classical_op_binder(expr, assign)
        raise KernelError(f"cannot evaluate {type(expr).__name__} as value")

    def _expr_marginal(self, joint: Joint, expr: Expr) -> dict[Any, float]:
        if isinstance(expr, Var):
            return joint.marginal(expr.name)
        # general: pushforward values across worlds
        from collections import defaultdict

        acc: dict[Any, float] = defaultdict(float)
        if joint.is_vacuum():
            return {}
        for w in joint.worlds:
            try:
                v = self._eval_value(expr, w.assign)
            except KernelError:
                continue
            acc[v] += abs(w.amp) ** 2
        return {k: v for k, v in acc.items() if v > EPS}

    def _measure(
        self,
        joint: Joint,
        expr: Expr,
        *,
        sink: str | None,
        stdout: TextIO | None,
    ) -> MeasureResult:
        marginal = self._expr_marginal(joint, expr)
        if not marginal:
            text = ""  # vacuum: no sample
            # Preserve prior behavior: attempt an empty write on the stdout path.
            if sink is None or sink in {"stdout", "Stdout", "STDOUT"}:
                self._emit_measure_text(sink, text, stdout=stdout)
            return MeasureResult(
                value=None,
                vacuum=True,
                marginal={},
                rng_calls=self.rng_calls,
                sink=sink,
                output=text,
            )

        self.rng_calls += 1  # terminal measure draws once
        value = sample_from_marginal(marginal, self.rng)
        text = "" if value is None else _format_value(value)
        payload = (text + "\n") if text else ""
        if sink is None or sink in {"stdout", "Stdout", "STDOUT"}:
            if text:
                self._emit_measure_text(sink, payload, stdout=stdout)
        else:
            self._emit_measure_text(sink, payload, stdout=None)
        return MeasureResult(
            value=value,
            vacuum=False,
            marginal=marginal,
            rng_calls=self.rng_calls,
            sink=sink,
            output=text,
        )


def _is_numeric(value: Any) -> bool:
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False


def _apply_op(op: str, l: Any, r: Any) -> Any:
    if op == "+":
        return l + r
    if op == "-":
        return l - r
    if op == "*":
        return l * r
    if op == "/":
        if r == 0 or r == 0.0:
            # failure as value tag (ADR 0025) — classical context in joint atom
            return ("Err", "DivByZero")
        # ADR 0160: exact rational on int/Fraction operands; float otherwise.
        if isinstance(l, bool) or isinstance(r, bool):
            return l / r
        if isinstance(l, Fraction) or isinstance(r, Fraction):
            return Fraction(l) / Fraction(r)
        if isinstance(l, int) and isinstance(r, int):
            return Fraction(l, r)
        return l / r
    if op == "^":
        return l**r
    if op == "==":
        return l == r
    if op == "!=":
        return l != r
    if op == "<":
        return l < r
    if op == "<=":
        return l <= r
    if op == ">":
        return l > r
    if op == ">=":
        return l >= r
    if op == "&&":
        # ADR 0196: total pushforward -- l/r are already fully evaluated by
        # the caller before this function runs (no lazy sub-expressions
        # reach here), so this is a plain truth-table combination of two
        # known values, not classical short-circuit control flow.
        return bool(l) and bool(r)
    if op == "||":
        return bool(l) or bool(r)
    if op == "Implies":
        # LISS-0425: A => B, i.e. !A || B.
        return (not bool(l)) or bool(r)
    raise KernelError(f"unknown op {op}")


def _format_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _call_name(expr: Call) -> str | None:
    return expr.callee.name if isinstance(expr.callee, Var) else None


def _float_scalars(scalars: dict[str, float | Fraction]) -> dict[str, float]:
    """Project evaluator scalars to float for mixed-state constructors."""
    out: dict[str, float] = {}
    for name, value in scalars.items():
        try:
            out[name] = float(value)
        except (TypeError, ValueError):
            continue
    return out


def _density_matrix_n_qubits(matrix: Matrix) -> int:
    """Qubit count implied by a density matrix's own dimension (LISS-0011):
    the DensityState type parameter, e.g. `Qubit`, is a domain label only
    and never encodes a qubit count -- the constructed matrix is the only
    source of truth."""
    return max(len(matrix), 2).bit_length() - 1


def _pat_match(pat: Any, ctrl: Any) -> bool:
    if pat == ctrl:
        return True
    if isinstance(pat, (int, float)) and isinstance(ctrl, (int, float)):
        return float(pat) == float(ctrl)
    # LISS-0225: when arms use bare variant idents (`Open`); controls are EnumValue.
    if isinstance(ctrl, EnumValue):
        if isinstance(pat, str) and pat == ctrl.variant:
            return True
        if isinstance(pat, Var) and pat.name == ctrl.variant:
            return True
    return False
