"""Kernel evaluator — AST → Joint transformers + terminal measure."""

from __future__ import annotations

import cmath
import math
import random
from dataclasses import dataclass, field, replace
from fractions import Fraction
from typing import TYPE_CHECKING, Any, Callable, Mapping, MutableMapping, TextIO

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
    # Public compatibility re-exports retained after evaluator extraction.
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
from .evaluation.calls import bind_call
from .evaluation.compatibility import (
    install_classical_compatibility as _install_classical_compatibility,
    install_classical_call_compatibility as _install_classical_call_compatibility,
    install_call_compatibility as _install_call_compatibility,
    install_continuous_compatibility as _install_continuous_compatibility,
    install_evolution_compatibility as _install_evolution_compatibility,
    install_execution_compatibility as _install_execution_compatibility,
    install_binding_compatibility as _install_binding_compatibility,
    install_constructor_compatibility as _install_constructor_compatibility,
    install_assignment_compatibility as _install_assignment_compatibility,
    install_pipe_compatibility as _install_pipe_compatibility,
    install_state_ops_compatibility as _install_state_ops_compatibility,
    install_frame_compatibility as _install_frame_compatibility,
    install_operator_compatibility as _install_operator_compatibility,
    install_value_compatibility as _install_value_compatibility,
)
from .evaluation.evolution import (
    ExplicitPropagator,
    execute_evolution,
)
from .evaluation.errors import KernelDiagnosticError, KernelError
from .evaluation.operators import resolve_operator
from .evaluation.orchestration import (
    execute_binder_plan,
    execute_callable_plan,
    execute_control_mixture_plan,
    execute_dynamic_lane_plan,
    execute_evolution_plan,
    execute_pure_transformation_plan,
)
from .evaluation import dynamic_lane as _dynamic_lane_evaluation
from .evaluation import observation as _observation_evaluation
from .evaluation.values import evaluate_value
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
    authority_evidence: "CanonicalExecutionEvidence | None" = None


@dataclass(frozen=True, slots=True)
class CanonicalExecutionEvidence:
    """Immutable, non-authoritative observation of compile-owned execution input."""

    semantic_ir: "ScientificSemanticIR"
    execution_authority: str
    source_id: str
    source_fingerprint: str


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


class Evaluator:
    """Discrete PMF Kernel (stance a). Pure stmts are Joint → Joint."""

    SOURCE_LINDBLAD_DT = 0.01

    # Private compatibility attributes retained for earlier plan-family
    # characterization tests. Dispatch itself is owned by orchestration.py.
    _execute_pure_transformation_plan = execute_pure_transformation_plan
    _execute_control_mixture_plan = execute_control_mixture_plan
    _execute_evolution_plan = execute_evolution_plan
    _execute_binder_plan = execute_binder_plan
    _execute_callable_plan = execute_callable_plan
    _execute_dynamic_lane_plan = execute_dynamic_lane_plan

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
        self._canonical_semantic_ir: ScientificSemanticIR | None = None

    @property
    def semantic_ir(self) -> ScientificSemanticIR | None:
        """Read-only compatibility observation; never an authority setter."""

        return self._canonical_semantic_ir

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

        # Do not leave a previous successful authority visible after a rejected
        # invocation; the observation always describes the current request.
        self._canonical_semantic_ir = None
        _validate_canonical_semantic_ir(semantic_ir)
        self._canonical_semantic_ir = semantic_ir
        from .evaluation.orchestration import execute_canonical_unit

        result = execute_canonical_unit(self, unit, semantic_ir, stdout=stdout)
        from ..scientific_semantic_ir import semantic_fingerprint

        result.execution_authority = "scientific_semantic_ir"
        result.source_id = semantic_ir.source_id
        result.authority_evidence = CanonicalExecutionEvidence(
            semantic_ir=semantic_ir,
            execution_authority="scientific_semantic_ir",
            source_id=semantic_ir.source_id,
            source_fingerprint=semantic_fingerprint(semantic_ir),
        )
        return result

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

    @staticmethod
    def _is_deferred_callable_eligible(unit: CompilationUnit) -> bool:
        """Keep callable deferral inside the currently closed scope boundary.

        A library function may refer to a module-level struct while building a
        local Operator (for example ``weights.a * X``).  The eager path owns
        that caller frame today; deferring it would resolve the attribute with
        no object frame and fail closed.  Route this narrow shape through the
        established executor until callable global-object capture is modeled.
        """
        class_names = {
            declaration.qualified_name
            for declaration in unit.decls
            if isinstance(declaration, ClassDecl)
        }
        class_short_names = {name.rsplit(".", 1)[-1] for name in class_names}
        if unit.main is None:
            return False
        for declaration in unit.decls:
            if not isinstance(declaration, FunDecl) or declaration.name == "main":
                continue
            if any(
                statement.ty is not None
                and statement.ty.name == "Operator"
                and Evaluator._operator_expr_contains_attr(statement.expr)
                for statement in declaration.body.stmts
                if isinstance(statement, StateBind)
            ):
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
    def _operator_expr_contains_attr(expr: Any) -> bool:
        if isinstance(expr, OpAttr):
            return True
        if isinstance(expr, OpBin):
            return Evaluator._operator_expr_contains_attr(expr.lhs) or Evaluator._operator_expr_contains_attr(expr.rhs)
        if isinstance(expr, OpPow):
            return Evaluator._operator_expr_contains_attr(expr.base)
        if isinstance(expr, OpBinder):
            return (
                Evaluator._operator_expr_contains_attr(expr.domain)
                or Evaluator._operator_expr_contains_attr(expr.guard)
                or Evaluator._operator_expr_contains_attr(expr.body)
            )
        if isinstance(expr, OpIndexed):
            return Evaluator._operator_expr_contains_attr(expr.base) or Evaluator._operator_expr_contains_attr(expr.index)
        if isinstance(expr, OpCall):
            return any(Evaluator._operator_expr_contains_attr(arg) for arg in expr.args)
        return False

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
                joint = bind_call(self, joint, wire, expanded)
        return joint






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
            raw = evaluate_value(self, times, {})
            try:
                n = int(float(raw))
            except (TypeError, ValueError) as e:
                raise KernelError(
                    f"evolve times must evaluate to a number, got {raw!r}"
                ) from e
        if n < 0:
            raise KernelError(f"evolve times must be non-negative, got {n}")
        return n

    def _unitary_operator_definition(self, name: str) -> Any | None:
        """Return one operator definition for extracted gate services."""
        return self.operators.get(name)

    def _unitary_operator_environment(self) -> Mapping[str, Any]:
        """Expose the live operator environment without transferring ownership."""
        return self.operators

    def _scalar_environment(self) -> Mapping[str, Any]:
        """Expose scalar lookup values to extracted gate services."""
        return self.scalars

    def _unit_for(self, name: str) -> str | None:
        """Resolve a live scalar/frame/call-local unit without copying state."""
        unit = self.scalar_units.get(name)
        if unit is None:
            unit = self._frame_units.get(name)
        if unit is None and hasattr(self, "_call_local_units"):
            unit = self._call_local_units.get(name)
        return unit

    def _scalar_unit(self, name: str) -> str | None:
        return self.scalar_units.get(name)

    def _make_enum_value(self, enum_name: str, variant: str) -> EnumValue:
        return EnumValue(enum_name=enum_name, variant=variant)

    def _evaluate_classical_call(self, expr: Any, assign: dict[str, Any]) -> Any:
        return self._eval_classical_call(expr, assign)

    def _evaluate_classical_op_binder(self, expr: Any, assign: dict[str, Any]) -> Any:
        return self._eval_classical_op_binder(expr, assign)

    def _static_register_size(self, name: str) -> int | None:
        """Return a declared register size for QFT-family validation."""
        return self.static_register_sizes.get(name)

    def _operator_environment(self) -> Mapping[str, Any]:
        return self.operators

    def _grid_hamiltonian_environment(self) -> Mapping[str, Any]:
        return self.grid_hamiltonians

    def _function_environment(self) -> Mapping[str, Any]:
        return self.funs

    def _object_environment(self) -> Mapping[str, Any]:
        return self.objects

    def _class_environment(self) -> Mapping[str, Any]:
        return self.classes

    def _struct_environment(self) -> Mapping[str, Any]:
        return self.structs

    def _enum_environment(self) -> Mapping[str, Any]:
        return self.enums

    def _second_quantized_environment(self) -> Mapping[str, Any]:
        return self.second_quantized_operators

    def _evaluate_value_with_unit(self, expr: Any, assign: dict[str, Any]) -> Any:
        return self._eval_value_with_unit(expr, assign)

    def _evaluate_unit_convert(self, expr: Any, assign: dict[str, Any]) -> Any:
        return self._eval_unit_convert(expr, assign)

    @staticmethod
    def _put_unit(store: dict[str, str], name: str, unit: str | None) -> None:
        if unit is not None:
            store[name] = unit
        else:
            store.pop(name, None)

    def _evaluate_set_comprehension(self, expr: Any, assign: dict[str, Any]) -> Any:
        return self._eval_set_comprehension(expr, assign)

    def _current_receiver(self) -> Any:
        return self._this

    def _set_current_receiver(self, value: Any) -> None:
        self._this = value

    def _make_partial_value(
        self, fun_name: str, slots: list[Expr | None]
    ) -> PartialValue:
        return PartialValue(fun_name=fun_name, slots=slots)

    def _compilation_unit(self) -> Any:
        return getattr(self, "_unit", None)

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
                    val = evaluate_value(self, arm_body, w.assign)
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
        v = evaluate_value(self, ctrl, assign)
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

    def _frame_environment(self) -> Mapping[str, Any]:
        """Expose frame state through a narrow callback, without copying it."""
        return {"receiver": self._this, "units": self._frame_units}

    def _make_class_instance(
        self, class_name: str, fields: dict[str, Any], mutable: set[str]
    ) -> ClassInstance:
        return ClassInstance(class_name=class_name, fields=fields, mutable=mutable)

    def _make_struct_value(
        self, struct_name: str, fields: dict[str, Any], field_units: dict[str, str]
    ) -> StructValue:
        return StructValue(
            struct_name=struct_name, fields=fields, field_units=field_units
        )

    @staticmethod
    def _copy_runtime_value(value: Any) -> Any:
        return value.copy() if isinstance(value, StructValue) else value

    def _set_initializing(self, value: bool) -> None:
        self._in_init = value

    def _is_initializing(self) -> bool:
        return self._in_init

    def _set_frame_units(self, value: dict[str, str]) -> None:
        self._frame_units = value

    def _call_local_units_environment(self) -> MutableMapping[str, str] | None:
        """Expose the active call-local unit frame without copying it."""
        return getattr(self, "_call_local_units", None)

    def _set_call_local_units_environment(
        self, value: MutableMapping[str, str] | None
    ) -> None:
        """Replace or clear the active call-local unit frame."""
        if value is None:
            if hasattr(self, "_call_local_units"):
                del self._call_local_units
            return
        self._call_local_units = value

    def _scalar_units_environment(self) -> MutableMapping[str, str]:
        return self.scalar_units

    def _restore_frame(
        self, receiver: Any, frame_units: dict[str, str]
    ) -> None:
        """Restore frame state for extracted invocation services."""
        self._this = receiver
        self._frame_units = frame_units

    def _evaluate_nested_value(self, expr: Any, assign: dict[str, Any]) -> Any:
        """Evaluate a nested value through the existing value entrypoint."""
        return evaluate_value(self, expr, assign)

    def _value_environment(self) -> Mapping[str, Any]:
        """Expose evaluator-owned object bindings to value services."""
        return self.objects

    def _continuous_field_port(self) -> ContinuousFieldPort | None:
        """Expose the injected continuous-field port without copying it."""
        return self.continuous_field

    def _runtime_seed(self) -> int | None:
        """Expose the evaluator seed to deterministic continuous services."""
        return self.seed

    def _store_runtime_object(self, name: str, value: Any) -> None:
        """Store an opaque runtime value in the evaluator-owned object map."""
        self.objects[name] = value

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

    def _set_fusion_evidence(
        self,
        algebraic: tuple[float, float] | None,
        polynomial: tuple[float, ...] | None,
    ) -> None:
        self.last_algebraic_fusion = algebraic
        self.last_poly_fusion = polynomial

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
        width_raw = evaluate_value(self, domain.width, assign)
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

    def _as_unary_fn(self, fn: Expr) -> Callable[[Any], Any]:
        if isinstance(fn, Lambda):
            param = fn.param

            def f(v: Any) -> Any:
                return evaluate_value(self, fn.body, {param: v})

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

# Compatibility aliases preserve existing consumers while each domain-family
# body is migrated in its own bounded slice. Assignment avoids duplicate
# method definitions in the public facade.
Evaluator._resolve_operator_expr = resolve_operator
_install_evolution_compatibility(Evaluator)
_install_binding_compatibility(Evaluator)
_install_execution_compatibility(Evaluator)
_install_call_compatibility(Evaluator)
_install_operator_compatibility(Evaluator)
_install_frame_compatibility(Evaluator)
_install_classical_compatibility(Evaluator)
_install_classical_call_compatibility(Evaluator)
_install_value_compatibility(Evaluator)
_install_continuous_compatibility(Evaluator)
_install_constructor_compatibility(Evaluator)
_install_assignment_compatibility(Evaluator)
_install_pipe_compatibility(Evaluator)
_install_state_ops_compatibility(Evaluator)


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


# LISS-0561 compatibility wiring: extracted lanes operate on the existing
# Evaluator instance, which remains the sole owner of mutable runtime state.
Evaluator._kernel_error = KernelError
Evaluator._eval_result_type = EvalResult
Evaluator._measure_result_type = MeasureResult
Evaluator._enum_value_type = EnumValue
Evaluator._format_value = staticmethod(_format_value)
Evaluator._call_name = staticmethod(_call_name)
Evaluator._float_scalars = staticmethod(_float_scalars)
Evaluator._density_matrix_n_qubits = staticmethod(_density_matrix_n_qubits)
Evaluator._resolve_scientific_binding = staticmethod(resolve_scientific_binding)

Evaluator._execute_deferred_state_measure_plan = (
    _observation_evaluation.execute_deferred_state_measure_plan
)
Evaluator._prepare_first_family_context = _observation_evaluation._prepare_first_family_context
Evaluator._main_deferred_eligible = staticmethod(
    _observation_evaluation._main_deferred_eligible
)
Evaluator._is_deferred_state_bind = staticmethod(
    _observation_evaluation._is_deferred_state_bind
)
Evaluator._expr_has_inspect = staticmethod(_observation_evaluation._expr_has_inspect)
Evaluator._expr_free_vars = staticmethod(_observation_evaluation._expr_free_vars)
Evaluator._deferred_bind_cone = staticmethod(_observation_evaluation._deferred_bind_cone)
Evaluator._apply_measure_tracing_out = _observation_evaluation._apply_measure_tracing_out
Evaluator._run_deferred_state_binds = _observation_evaluation._run_deferred_state_binds
Evaluator._mixed_state_for_measure = _observation_evaluation._mixed_state_for_measure
Evaluator._resolve_measurement_kind = _observation_evaluation._resolve_measurement_kind
Evaluator._bind_povm = _observation_evaluation._bind_povm
Evaluator._bind_mixed_state = _observation_evaluation._bind_mixed_state
Evaluator._resolve_lindblad_jumps = _observation_evaluation._resolve_lindblad_jumps
Evaluator._resolve_lindblad_hamiltonian = _observation_evaluation._resolve_lindblad_hamiltonian
Evaluator._compile_lindblad_operator = _observation_evaluation._compile_lindblad_operator
Evaluator._emit_measure_text = _observation_evaluation._emit_measure_text
Evaluator._emit_sink = _observation_evaluation._emit_sink
Evaluator._measure_mixed = _observation_evaluation._measure_mixed
Evaluator._expr_marginal = _observation_evaluation._expr_marginal
Evaluator._measure = _observation_evaluation._measure

Evaluator._run_dynamic_qpu_block = _dynamic_lane_evaluation._run_dynamic_qpu_block
Evaluator._reset_dynamic_wire = _dynamic_lane_evaluation._reset_dynamic_wire
Evaluator._run_dynamic_arm_body = _dynamic_lane_evaluation._run_dynamic_arm_body
Evaluator._resolve_dynamic_outcome = _dynamic_lane_evaluation._resolve_dynamic_outcome
Evaluator._collapse_dynamic_wire = _dynamic_lane_evaluation._collapse_dynamic_wire
