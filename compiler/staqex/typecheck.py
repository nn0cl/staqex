"""Type checker — Lit-Lift, Type-First decls, dimensional analysis."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .ast_nodes import (
    AssignStmt,
    Attr,
    BinOp,
    BlockExpr,
    Call,
    ClassDecl,
    Coin,
    DiscretizationBridgeDecl,
    CompilationUnit,
    Dirac,
    DynamicQpuStmt,
    EnumDecl,
    EvolveExpr,
    Expr,
    ExprStmt,
    ForEachStmt,
    FunDecl,
    Hole,
    ImplDecl,
    InterfaceDecl,
    IndexDomain,
    Inspect,
    BraLit,
    KetLit,
    Lambda,
    ListExpr,
    LitBool,
    LitFloat,
    LitInt,
    LitString,
    MeasureExpr,
    Measure,
    OpBinder,
    OpCall,
    OpIndexed,
    OpLit,
    OpExpr,
    OpBin,
    OpVar,
    Pipe,
    ReturnStmt,
    RevDomain,
    Snapshot,
    StateBind,
    StructDecl,
    ScientificScopeDecl,
    TensorExpr,
    TupleExpr,
    TypeRef,
    UnaryNot,
    UnitConvert,
    Vacuum,
    Var,
    WhenExpr,
    SuperposeExpr,
)
from .dimensions import (
    DIMLESS,
    ELABORATION_COEFFICIENT_HEADS,
    QUANTITY_CANONICAL_UNIT,
    TYPE_DIMS,
    UNIT_SCALE_TO_CANONICAL,
    UNIT_AFFINE_TO_CANONICAL,
    UNIT_TABLE,
    Dim,
    dim_of_type_name,
    format_dim_mismatch,
    product_payload,
    split_product_payload,
)
from .static_hilbert import MVP_MAX_LOGICAL_QUBITS
from .kernel_literals import (
    RELATIONAL,
    SECOND_QUANTIZED_FAMILIES,
)


@dataclass(frozen=True, slots=True)
class Ty:
    """Runtime/static type: State wrapper, Classical scalar, Operator, + physical dimension."""

    kind: str  # State | Classical | Operator | POVM | Register | Param | Unit
    payload: str  # Int, Float, Length, Mass, …
    dim: Dim = DIMLESS
    unit: str | None = None  # ADR 0154: known unit suffix when tracked

    def __str__(self) -> str:
        if self.kind == "Classical":
            base = f"Classical<{self.payload}>"
        elif self.kind == "Operator":
            base = f"Operator<{self.payload}>"
        elif self.kind == "Unit":
            return "Unit"
        elif self.kind == "Register":
            base = f"QubitRegister<{self.payload}>"
        elif self.kind == "Param":
            base = f"Param<{self.payload}>"
        elif self.kind == "POVM":
            base = f"POVM<{self.payload}>"
        elif self.kind in {"Meta", "Execution", "Discrete"}:
            return self.payload
        elif self.kind == "DiagnosticView":
            base = f"DiagnosticView<{self.payload}>"
        elif self.dim.is_dimensionless():
            base = f"State<{self.payload}>"
        else:
            base = f"State<{self.payload}>{self.dim}"
        if self.unit:
            return f"{base}@{self.unit}"
        return base


ARITH = {"+", "-", "*", "/"}
TRIG_AND_TRANS = frozenset({"sin", "cos", "tan", "exp", "log", "cis"})


@dataclass
class TypedExpr:
    expr: Expr
    ty: Ty


_PAULI_ATOM_NAMES = frozenset({"I", "X", "Y", "Z", "H", "S", "T"})


class TypeChecker:
    _EFFECTS = frozenset({"Measure", "Snapshot", "Inspect", "Host", "Uncompute"})

    def __init__(self) -> None:
        self.env: dict[str, Ty] = {}
        self.diagnostics: list[dict] = []
        self.typed: dict[int, Ty] = {}  # id(expr) → ty
        self.class_meta: dict[str, ClassDecl] = {}
        self.struct_meta: dict[str, StructDecl] = {}
        # short + qualified enum name → variant list (LISS-0304 exhaustive when)
        self.enum_variants: dict[str, list[str]] = {}
        self.fun_returns: dict[str, tuple[FunDecl, Ty]] = {}
        self._in_class: str | None = None  # qualified/simple name while checking methods
        self.semantic_values: dict[str, int] = {}
        self.fun_effects: dict[str, frozenset[str]] = {}
        self._current_effects: frozenset[str] = frozenset()
        self.interface_names: set[str] = set()
        self.system_registers: dict[str, tuple[tuple[str, int], ...]] = {}
        self._active_register_set: str | None = None
        self.has_entry_main: bool = False
        self.float_arrays: dict[str, tuple[int, ...]] = {}  # name → shape (LISS-0143/0144)
        self._binder_depth: int = 0
        # name → value for classical scalar binds resolvable at typecheck time
        # (LISS-0371); mirrors the runtime `scalars` dict trotter.py builds,
        # but populated statically so checks like `_check_suzuki_policy` can
        # accept a named constant, not just a bare literal.
        self.static_scalars: dict[str, float] = {}

    _SEMANTIC_CARRIERS = {
        "Dimension",
        "Index",
        "Basis",
        "Bit",
        "EnergyLevel",
        "SpinProjection",
        "ShotCount",
        "IterationCount",
        "Count",
        "Nat",
    }
    _SECOND_QUANTIZED_FAMILIES = SECOND_QUANTIZED_FAMILIES

    def check_unit(self, unit: CompilationUnit) -> list[dict]:
        if unit.main is None:
            return self.diagnostics

        self.has_entry_main = True

        # ADR 0062: prelude classical constants (pi, …)
        from .stdlib.prelude import PRELUDE_CONSTANTS

        for name in PRELUDE_CONSTANTS:
            self.env[name] = Ty("Classical", "Float", DIMLESS)
            self.static_scalars[name] = float(PRELUDE_CONSTANTS[name])

        for declaration in unit.decls:
            if isinstance(declaration, DiscretizationBridgeDecl):
                self.env[declaration.alias] = Ty("Operator", "Grid", DIMLESS)

        enum_names: set[str] = set()
        struct_names: set[str] = set()
        self.interface_names = set()
        self.system_registers = {
            declaration.name: declaration.registers
            for declaration in unit.decls
            if isinstance(declaration, ScientificScopeDecl)
            and declaration.kind == "system"
        }
        class_meta: dict[str, ClassDecl] = {}
        struct_meta: dict[str, StructDecl] = {}
        for d in unit.decls:
            if isinstance(d, EnumDecl):
                enum_names.add(d.qualified_name)
                enum_names.add(d.name)
                self.enum_variants[d.qualified_name] = list(d.variants)
                self.enum_variants[d.name] = list(d.variants)
            elif isinstance(d, StructDecl):
                struct_names.add(d.qualified_name)
                struct_names.add(d.name)
                struct_meta[d.qualified_name] = d
                struct_meta[d.name] = d
            elif isinstance(d, ClassDecl):
                class_meta[d.qualified_name] = d
                class_meta[d.name] = d
                self._in_class = d.qualified_name
                for m in d.methods:
                    self._check_method_assigns(m, d)
                self._in_class = None
            elif isinstance(d, InterfaceDecl):
                self.interface_names.add(d.name)
        self.class_meta = class_meta
        self.struct_meta = struct_meta

        # Register explicit function/method results before checking main so
        # calls can acquire their declared State/domain type.
        self.fun_returns = {}
        self.fun_effects = {}
        impl_pairs: set[tuple[str, str]] = set()
        for d in unit.decls:
            if isinstance(d, FunDecl) and d.return_type is not None:
                ty = self._ty_from_ref(d.return_type)
                self.fun_returns[d.name] = (d, ty)
                self.fun_returns[d.qualified_name] = (d, ty)
                effects = frozenset(d.effects)
                unknown = effects - self._EFFECTS
                if unknown:
                    self.diagnostics.append(
                        {
                            "code": "EFFECT_DECLARATION_ERROR",
                            "line": d.span.line,
                            "col": d.span.col,
                            "message": f"unknown function effect(s): {', '.join(sorted(unknown))}",
                        }
                    )
                self.fun_effects[d.name] = effects
                self.fun_effects[d.qualified_name] = effects
                if "Measure" in effects and ty.kind == "State":
                    self.diagnostics.append(
                        {
                            "code": "EFFECT_MEASURE_RETURN_ERROR",
                            "line": d.span.line,
                            "col": d.span.col,
                            "message": "a `Measure` function cannot return State<T>",
                        }
                    )
            if isinstance(d, ClassDecl):
                for method in d.methods:
                    if method.return_type is not None:
                        ty = self._ty_from_ref(method.return_type)
                        self.fun_returns[f"{d.name}.{method.name}"] = (method, ty)
                        self.fun_returns[
                            f"{d.qualified_name}.{method.name}"
                        ] = (method, ty)
            if isinstance(d, ImplDecl):
                self._check_impl_contract(d, impl_pairs)

        # Explicitly typed declarations are checked in their own parameter /
        # receiver environment. Legacy untyped functions keep their existing
        # compatibility behavior until the migration policy is accepted.
        base_env = dict(self.env)
        for d in unit.decls:
            if isinstance(d, FunDecl) and d.return_type is not None:
                self._check_function_body(d, base_env)
            elif isinstance(d, ClassDecl):
                for method in d.methods:
                    if method.return_type is not None or method.name == "init":
                        self._check_function_body(method, base_env, d)

        self._current_effects = frozenset(self._EFFECTS)
        for p in unit.main.params:
            if p.ty is not None:
                self.env[p.name] = self._ty_from_ref(p.ty)
            else:
                self.env[p.name] = Ty("State", "Any", DIMLESS)

        for stmt in unit.main.body.stmts:
            if isinstance(stmt, DynamicQpuStmt):
                self.diagnostics.extend(
                    [
                        {
                            "code": "DYNAMIC_CAPABILITY_REQUIRED_ERROR",
                            "line": stmt.span.line,
                            "col": stmt.span.col,
                            "message": "dynamic QPU execution requires an explicit target capability profile",
                        },
                        {
                            "code": "DYNAMIC_UNSUPPORTED_FEATURE_ERROR",
                            "line": stmt.span.line,
                            "col": stmt.span.col,
                            "message": "dynamic QPU lane is not implemented by the current Kernel",
                        },
                    ]
                )
                continue
            if isinstance(stmt, ForEachStmt):
                self._check_foreach_stmt(stmt)
                continue
            if isinstance(stmt, ExprStmt):
                self._infer(stmt.expr)
                continue
            if isinstance(stmt, AssignStmt):
                self._check_assign_stmt(stmt, class_meta)
                continue
            if isinstance(stmt, StateBind):
                # LISS-0074 Slice A: validate qutrit/qudit type-level shapes early.
                if stmt.ty is not None:
                    self._validate_local_dimension_surface(
                        stmt.ty, stmt.span.line, stmt.span.col
                    )
                # ADR 0180 / LISS-0290: omitted-type desugar (Decision §3 fill).
                if self._try_desugar_omitted_bind(stmt):
                    continue
                # Operator H = … — not a State coordinate (ADR 0041)
                if stmt.ty is not None and stmt.ty.name == "Operator":
                    declared_operator = self._ty_from_ref(stmt.ty)
                    self._check_silent_qubit_operator_coercion(
                        stmt.ty, stmt.span.line, stmt.span.col
                    )
                    if isinstance(stmt.expr, Call):
                        if self._is_qft_call(stmt.expr):
                            self._check_qft_call(
                                stmt.expr, stmt.span.line, stmt.span.col
                            )
                        inferred_operator = self._check_algebra_call(stmt.expr)
                        if inferred_operator.kind != "Operator":
                            inferred_operator = self._infer(stmt.expr)
                        if not stmt.ty.args and inferred_operator.kind == "Operator":
                            declared_operator = inferred_operator
                        if (
                            stmt.ty.args
                            and inferred_operator.kind == "Operator"
                            and declared_operator.payload != inferred_operator.payload
                        ):
                            self.diagnostics.append(
                                {
                                    "code": (
                                        "ACTING_SPACE_MISMATCH"
                                        if declared_operator.payload.startswith("RegisterSet<")
                                        or inferred_operator.payload.startswith("RegisterSet<")
                                        else "OPERATOR_DOMAIN_ERROR"
                                    ),
                                    "line": stmt.span.line,
                                    "col": stmt.span.col,
                                    "message": (
                                        f"operator domain `{inferred_operator.payload}` "
                                        f"does not match `{declared_operator.payload}`"
                                    ),
                                }
                            )
                    else:
                        previous_register_set = self._active_register_set
                        self._active_register_set = self._register_set_name(
                            declared_operator.payload
                        )
                        try:
                            self._check_operator_expr(stmt.expr)
                        finally:
                            self._active_register_set = previous_register_set
                    for n in stmt.names:
                        self.env[n] = declared_operator
                    continue
                # LISS-0143 / LISS-0144: Float[N]… classical coefficient tensor
                if (
                    stmt.ty is not None
                    and stmt.ty.name == "Float"
                    and len(stmt.ty.args) >= 1
                ):
                    self._check_float_array_bind(stmt)
                    continue
                # Enum / struct / class object binds
                if stmt.ty is not None:
                    tname = stmt.ty.name
                    if tname in self._SECOND_QUANTIZED_FAMILIES:
                        family = (
                            f"{tname}<{stmt.ty.args[0].name}>"
                            if stmt.ty.args
                            else tname
                        )
                        self._check_second_quantized_expr(stmt.expr, tname)
                        for n in stmt.names:
                            self.env[n] = Ty("Operator", family, DIMLESS)
                        continue
                    if tname == "Host":
                        # ADR 0189: tomography is a Host/protocol operation.
                        # Inspect it before the generic Host-in-Kernel guard so
                        # it cannot fall through as an implicit State call.
                        if (
                            isinstance(stmt.expr, Call)
                            and _call_op_name(stmt.expr) == "tomography"
                        ):
                            self._infer(stmt.expr)
                        self.diagnostics.append(
                            {
                                "code": "HOST_TYPE_IN_KERNEL_ERROR",
                                "line": stmt.span.line,
                                "col": stmt.span.col,
                                "message": "`Host<T>` belongs to the Host API, not QPU Kernel logic",
                            }
                        )
                        for n in stmt.names:
                            self.env[n] = Ty("Host", "Host", DIMLESS)
                        continue
                    if tname == "QubitRegister":
                        if not self._is_static_shape_ref(stmt.ty):
                            self.diagnostics.append(
                                {
                                    "code": "STATIC_REGISTER_TYPE_ERROR",
                                    "line": stmt.span.line,
                                    "col": stmt.span.col,
                                    "message": "`QubitRegister<N>` requires a positive integer type-level shape",
                                }
                            )
                        for n in stmt.names:
                            self.env[n] = Ty("Register", "Qubit", DIMLESS)
                            if stmt.ty.args:
                                try:
                                    self.semantic_values[n] = int(stmt.ty.args[0].name)
                                except ValueError:
                                    pass
                        continue
                    if tname == "QutritRegister":
                        # Shape already validated by `_validate_local_dimension_surface`.
                        for n in stmt.names:
                            self.env[n] = Ty("Register", "Qutrit", DIMLESS)
                            if stmt.ty.args:
                                try:
                                    self.semantic_values[n] = int(stmt.ty.args[0].name)
                                except ValueError:
                                    pass
                        continue
                    if tname == "QuditRegister":
                        for n in stmt.names:
                            dim = "Qudit"
                            if len(stmt.ty.args) >= 1:
                                dim = f"Qudit<{stmt.ty.args[0].name}>"
                            self.env[n] = Ty("Register", dim, DIMLESS)
                            if len(stmt.ty.args) >= 2:
                                try:
                                    self.semantic_values[n] = int(stmt.ty.args[1].name)
                                except ValueError:
                                    pass
                        continue
                    if tname == "Param":
                        carrier = stmt.ty.args[0].name if stmt.ty.args else "Any"
                        if carrier not in {"Angle", "Float", "Int"}:
                            self.diagnostics.append(
                                {
                                    "code": "PARAMETER_TYPE_ERROR",
                                    "line": stmt.span.line,
                                    "col": stmt.span.col,
                                    "message": "`Param<T>` requires a supported parameter carrier",
                                }
                            )
                        for n in stmt.names:
                            self.env[n] = Ty("Param", carrier, DIMLESS)
                        continue
                    if tname in self._SEMANTIC_CARRIERS and tname not in enum_names:
                        declared = self._ty_from_ref(stmt.ty)
                        inferred = self._infer(stmt.expr)
                        self._check_semantic_assignment(
                            declared, inferred, stmt.expr, stmt.span.line, stmt.span.col
                        )
                        if isinstance(stmt.expr, LitInt):
                            self.semantic_values[stmt.names[0]] = stmt.expr.value
                        for n in stmt.names:
                            self.env[n] = declared
                        continue
                    if tname in enum_names:
                        if not self._expr_is_enum_variant(stmt.expr, tname, enum_names):
                            # Integer / float literals are never enum tags
                            if isinstance(stmt.expr, (LitInt, LitFloat, LitBool, LitString)):
                                self.diagnostics.append(
                                    {
                                        "code": "ENUM_TYPE_MISMATCH",
                                        "line": stmt.span.line,
                                        "col": stmt.span.col,
                                        "message": (
                                            f"cannot assign literal to enum `{tname}`; "
                                            f"use `{tname}.Variant`"
                                        ),
                                    }
                                )
                        for n in stmt.names:
                            self.env[n] = Ty("Enum", tname, DIMLESS)
                        continue
                    if tname in struct_names or tname in class_meta:
                        for n in stmt.names:
                            kind = "Struct" if tname in struct_names else "Object"
                            self.env[n] = Ty(kind, tname, DIMLESS)
                        continue
                    if tname == "Controller":
                        # ADR 0197 / LISS-0382: Controller bind from `measure`
                        # is mid-circuit only inside `dynamic qpu`. Outside the
                        # lane, MeasureExpr must emit EARLY_COLLAPSE_ERROR via
                        # `_infer`. Do not take the capitalized-Object shortcut.
                        self._infer(stmt.expr)
                        carrier = (
                            stmt.ty.args[0].name if stmt.ty.args else "Bit"
                        )
                        for n in stmt.names:
                            self.env[n] = Ty("Controller", carrier, DIMLESS)
                        continue
                    if tname in self.interface_names:
                        self._infer(stmt.expr)
                        for n in stmt.names:
                            self.env[n] = Ty("Object", tname, DIMLESS)
                        continue
                    is_quantity = tname in TYPE_DIMS or tname in {
                        "State",
                        "Operator",
                        "Delta",
                        "Tuple",
                    }
                    if not is_quantity and (
                        "." in tname or (tname[:1].isupper() and "(" not in tname)
                    ):
                        for n in stmt.names:
                            self.env[n] = Ty("Object", tname, DIMLESS)
                        continue
                # Evolve working coords shadow seeds (names ← seed types) for body check.
                if isinstance(stmt.expr, EvolveExpr):
                    seed_tys = []
                    for name, seed in zip(stmt.names, stmt.expr.seeds):
                        st = self._infer(seed)
                        self.env[name] = st
                        seed_tys.append(st)
                    inferred = self._infer(stmt.expr)
                    # Pairwise dim match for tuple evolve results
                    if (
                        isinstance(stmt.expr.body, type(None)) is False
                        and stmt.expr.body is not None
                        and isinstance(stmt.expr.body.result, TupleExpr)
                        and len(stmt.names) == len(stmt.expr.body.result.items)
                    ):
                        for i, (name, item) in enumerate(
                            zip(stmt.names, stmt.expr.body.result.items)
                        ):
                            item_ty = self.typed.get(id(item)) or self._infer(item)
                            if i < len(seed_tys):
                                seed_ty = seed_tys[i]
                                if not seed_ty.dim.matches(item_ty.dim):
                                    self._dim_error(
                                        stmt.span.line,
                                        stmt.span.col,
                                        seed_ty.dim,
                                        item_ty.dim,
                                        "evolve-result",
                                    )
                                self.env[name] = Ty(
                                    "State", item_ty.payload, item_ty.dim
                                )
                                self._assert_is_state(
                                    self.env[name], stmt.span.line, stmt.span.col, name
                                )
                        continue
                    if stmt.ty is not None:
                        declared = self._ty_from_ref(stmt.ty)
                        self._check_assign(
                            declared, inferred, stmt.span.line, stmt.span.col
                        )
                        ty = declared
                    else:
                        ty = inferred
                    for n in stmt.names:
                        self.env[n] = ty
                        self._assert_is_state(ty, stmt.span.line, stmt.span.col, n)
                    continue
                # Product / tensor bind: (a, b) = left *|* right  or typed State<(A,B)> (a,b)=…
                if len(stmt.names) > 1 and self._bind_product_components(stmt):
                    continue
                inferred = self._infer(stmt.expr)
                if stmt.ty is not None:
                    # ADR 0115: only `state name: T = …` (not Type-First) requires State.
                    if stmt.via_state_keyword and stmt.ty.name != "State":
                        self.diagnostics.append(
                            {
                                "code": "STATE_ANNOTATION_TYPE_ERROR",
                                "line": stmt.span.line,
                                "col": stmt.span.col,
                                "message": (
                                    "`state name: …` annotations require a `State<…>` "
                                    f"carrier, got `{stmt.ty.name}`"
                                ),
                            }
                        )
                        for n in stmt.names:
                            self.env[n] = inferred
                            self._assert_is_state(
                                inferred, stmt.span.line, stmt.span.col, n
                            )
                        continue
                    declared = self._ty_from_ref(stmt.ty)
                    if (
                        declared.kind == "Operator"
                        and isinstance(stmt.expr, Call)
                        and self._is_qft_call(stmt.expr)
                    ):
                        self._check_qft_call(stmt.expr, stmt.span.line, stmt.span.col)
                    # Single name must not declare a product carrier (needs tuple bind)
                    if (
                        split_product_payload(declared.payload) is not None
                        and len(stmt.names) == 1
                    ):
                        self.diagnostics.append(
                            {
                                "code": "PRODUCT_BIND_ERROR",
                                "line": stmt.span.line,
                                "col": stmt.span.col,
                                "message": (
                                    f"product type {declared} requires tuple bind "
                                    f"`State<(…)> (a, b) = …`, not a single name"
                                ),
                            }
                        )
                    self._check_ket_bra_local_dimension(
                        stmt.ty, stmt.expr, stmt.span.line, stmt.span.col
                    )
                    self._check_assign(declared, inferred, stmt.span.line, stmt.span.col)
                    # LISS-0203: a basis-label ket/bra literal is local-dimension
                    # polymorphic — `|0>` is the zeroth basis state of whatever
                    # space the declaration names, so it infers `Qubit` but is
                    # legal in `State<Qutrit>` / `State<Qudit<D>>`. The label is
                    # already validated against D by
                    # `_check_ket_bra_local_dimension` just above; comparing
                    # payload names as well rejects what that check accepted.
                    # Non-literal values (e.g. `coin()`) still go through the
                    # payload check, so no silent qubit embedding is introduced.
                    if not isinstance(stmt.expr, (KetLit, BraLit)):
                        self._check_payload_assign(
                            declared, inferred, stmt.span.line, stmt.span.col
                        )
                    # ADR 0154: preserve known unit suffix through Type-First binds.
                    if inferred.unit is not None:
                        ty = Ty(
                            declared.kind,
                            declared.payload,
                            declared.dim,
                            unit=inferred.unit,
                        )
                    else:
                        ty = declared
                else:
                    ty = inferred
                    # ADR 0180 / LISS-0290: desugar omitted ty from unique elaboration.
                    if stmt.ty is None and not stmt.via_state_keyword:
                        filled = self._type_ref_from_ty(ty)
                        if filled is not None:
                            self._fill_bind_ty(stmt, filled)
                for n in stmt.names:
                    self.env[n] = ty
                    if ty.kind == "Classical" and len(stmt.names) == 1:
                        static_val = self._static_scalar_value(stmt.expr)
                        if static_val is not None:
                            self.static_scalars[n] = static_val
                    # ADR 0180: inferred classical/Operator/object binds are not State.
                    # `state` keyword and State-kind still require NLTS discipline.
                    if stmt.via_state_keyword or ty.kind == "State":
                        self._assert_is_state(ty, stmt.span.line, stmt.span.col, n)
            elif isinstance(stmt, (Measure, Snapshot)):
                ty = self._infer(stmt.expr)
                self._assert_is_state(
                    ty, stmt.span.line, stmt.span.col, "measure/snapshot"
                )
                self._check_unsupported_qudit_runtime_ty(
                    ty, stmt.span.line, stmt.span.col, allow_mvp_d3=True
                )
        return self.diagnostics

    @staticmethod
    def _is_static_shape_ref(ref: TypeRef) -> bool:
        """Recognize the Phase 2 type-level positive integer shape."""
        if ref.name != "QubitRegister" or len(ref.args) != 1:
            return False
        try:
            return int(ref.args[0].name) > 0
        except ValueError:
            return False

    def _local_dimension_type_error(self, line: int, col: int, message: str) -> None:
        self.diagnostics.append(
            {
                "code": "LOCAL_DIMENSION_TYPE_ERROR",
                "line": line,
                "col": col,
                "message": message,
            }
        )

    def _unsupported_local_dimension_error(
        self, line: int, col: int, message: str
    ) -> None:
        self.diagnostics.append(
            {
                "code": "UNSUPPORTED_LOCAL_DIMENSION",
                "line": line,
                "col": col,
                "message": message,
            }
        )

    @staticmethod
    def _ty_is_mvp_d3_state(ty: Ty) -> bool:
        """LISS-0112 Slice A: single-site D=3 carriers eligible for measure SV."""
        if ty.kind != "State":
            return False
        payload = ty.payload
        return payload == "Qutrit" or payload == "Qudit<3>"

    @staticmethod
    def _expr_is_identity_atom(expr: Expr) -> bool:
        """Bare Identity atom for Slice B MVP (apply(I) / evolve under I)."""
        return isinstance(expr, Var) and expr.name.upper() in {"I", "ID", "IDENTITY"}

    @staticmethod
    def _ty_is_deferred_qudit_state(ty: Ty) -> bool:
        """Single-site qudit State still blocked from Kernel SV (except MVP D=3)."""
        if ty.kind != "State":
            return False
        payload = ty.payload
        if payload == "Qutrit" or payload == "Qudit<3>":
            return False
        return payload == "Qudit" or payload.startswith("Qudit")

    @staticmethod
    def _ty_is_deferred_qudit_operator(ty: Ty) -> bool:
        if ty.kind != "Operator":
            return False
        payload = ty.payload
        return payload.startswith("LocalRegister<") or payload.startswith("LocalSite<")

    def _check_unsupported_qudit_runtime_ty(
        self, ty: Ty, line: int, col: int, *, allow_mvp_d3: bool = False
    ) -> None:
        """Fail closed on qudit SV entry points (LISS-0074 D / LISS-0112 A–B)."""
        if allow_mvp_d3 and self._ty_is_mvp_d3_state(ty):
            return
        if not (
            self._ty_is_deferred_qudit_state(ty)
            or self._ty_is_deferred_qudit_operator(ty)
            or (not allow_mvp_d3 and self._ty_is_mvp_d3_state(ty))
        ):
            return
        self._unsupported_local_dimension_error(
            line,
            col,
            (
                "qudit / qutrit carriers are not supported by the shipping "
                "Kernel runtime (deferred; no silent qubit embedding)"
            ),
        )

    @staticmethod
    def _positive_type_level_int(ref: TypeRef) -> int | None:
        try:
            value = int(ref.name)
        except ValueError:
            return None
        return value if value > 0 else None

    def _validate_local_dimension_surface(
        self, ref: TypeRef, line: int, col: int
    ) -> None:
        """LISS-0074 Slice A: nominal qutrit/qudit shapes (not Int aliases)."""
        name = ref.name
        if name == "Qudit":
            if len(ref.args) != 1:
                self._local_dimension_type_error(
                    line,
                    col,
                    "`Qudit<D>` requires exactly one positive integer type-level dimension",
                )
                return
            if self._positive_type_level_int(ref.args[0]) is None:
                self._local_dimension_type_error(
                    line,
                    col,
                    "`Qudit<D>` requires a positive integer type-level dimension `D`",
                )
            return
        if name == "Qutrit":
            if ref.args:
                self._local_dimension_type_error(
                    line,
                    col,
                    "`Qutrit` takes no type arguments (use `Qudit<D>` for D ≠ 3)",
                )
            return
        if name == "QutritRegister":
            if len(ref.args) != 1 or self._positive_type_level_int(ref.args[0]) is None:
                self._local_dimension_type_error(
                    line,
                    col,
                    "`QutritRegister<N>` requires a positive integer type-level shape",
                )
            return
        if name == "QuditRegister":
            if len(ref.args) != 2:
                self._local_dimension_type_error(
                    line,
                    col,
                    "`QuditRegister<D, N>` requires type-level dimension `D` and length `N`",
                )
                return
            if self._positive_type_level_int(ref.args[0]) is None:
                self._local_dimension_type_error(
                    line,
                    col,
                    "`QuditRegister<D, N>` requires a positive integer local dimension `D`",
                )
            if self._positive_type_level_int(ref.args[1]) is None:
                self._local_dimension_type_error(
                    line,
                    col,
                    "`QuditRegister<D, N>` requires a positive integer type-level length `N`",
                )
            return
        if name == "State":
            for arg in ref.args:
                self._validate_local_dimension_surface(arg, line, col)
            return
        if name == "Operator":
            for arg in ref.args:
                self._validate_local_dimension_surface(arg, line, col)
            return
        # Product carriers such as `(Qubit, Qutrit)` are represented as a
        # TypeRef whose name encodes the product; walk nested args if present.
        for arg in ref.args:
            self._validate_local_dimension_surface(arg, line, col)

    def _local_dim_of_state_carrier(self, ref: TypeRef) -> int | None:
        """Return D for `State<Qubit|Qutrit|Qudit<D>>`, else None."""
        if ref.name != "State" or not ref.args:
            return None
        inner = ref.args[0]
        if inner.name == "Qubit" and not inner.args:
            return 2
        if inner.name == "Qutrit" and not inner.args:
            return 3
        if inner.name == "Qudit" and len(inner.args) == 1:
            return self._positive_type_level_int(inner.args[0])
        return None

    def _check_ket_bra_local_dimension(
        self, ty_ref: TypeRef, expr: Expr, line: int, col: int
    ) -> None:
        """LISS-0074 Slice B: numeric ket/bra labels must satisfy 0 ≤ k < D."""
        if not isinstance(expr, (KetLit, BraLit)):
            return
        dim = self._local_dim_of_state_carrier(ty_ref)
        if dim is None:
            return
        try:
            label_index = int(expr.label)
        except ValueError:
            # Named non-numeric labels are out of Slice B.
            return
        if 0 <= label_index < dim:
            return
        kind = "ket" if isinstance(expr, KetLit) else "bra"
        self._local_dimension_type_error(
            line,
            col,
            (
                f"{kind} label `{expr.label}` is outside local dimension {dim} "
                f"(require 0 ≤ k < {dim})"
            ),
        )

    def _check_foreach_stmt(self, stmt: ForEachStmt) -> None:
        """Check static bounds and an opaque element-handle body."""
        collection = stmt.collection
        collection_ty = self._infer(collection)
        if (
            isinstance(collection, Call)
            and isinstance(collection.callee, Var)
            and collection.callee.name == "register"
        ):
            self.diagnostics.append(
                {
                    "code": "STATIC_HILBERT_SURFACE_ERROR",
                    "line": stmt.span.line,
                    "col": stmt.span.col,
                    "message": (
                        "the historical `register(N)` spelling is not a "
                        "compatibility alias; use `QubitRegister<N>`"
                    ),
                }
            )
        if (
            isinstance(collection, Var)
            and collection_ty.kind == "Register"
            and collection.name in self.semantic_values
            and self.semantic_values[collection.name] > 1024
        ):
            self.diagnostics.append(
                {
                    "code": "STATIC_HILBERT_RESOURCE_ERROR",
                    "line": stmt.span.line,
                    "col": stmt.span.col,
                    "message": (
                        "static Hilbert expansion exceeds the MVP logical "
                        "qubit resource budget (1024)"
                    ),
                }
            )
        parameter_bound = collection_ty.kind == "Param"
        if isinstance(collection, Call) and collection.args:
            parameter_bound = parameter_bound or any(
                isinstance(arg, Var)
                and self.env.get(arg.name, Ty("State", "Any")).kind == "Param"
                for arg in collection.args
            )
        if parameter_bound:
            self.diagnostics.append(
                {
                    "code": "PARAMETER_CONTROL_ERROR",
                    "line": stmt.span.line,
                    "col": stmt.span.col,
                    "message": "symbolic parameters cannot control register shape or `forEach`",
                }
            )
        valid_static_register = (
            (isinstance(collection, Var) and collection_ty.kind == "Register")
            or (
                isinstance(collection, Call)
                and isinstance(collection.callee, Var)
                and collection.callee.name == "register"
                and len(collection.args) == 1
                and isinstance(collection.args[0], LitInt)
                and collection.args[0].value > 0
            )
        )
        if not valid_static_register:
            self.diagnostics.append(
                {
                    "code": "FOR_EACH_DYNAMIC_BOUND_ERROR",
                    "line": stmt.span.line,
                    "col": stmt.span.col,
                    "message": "`forEach` requires a statically known finite register",
                }
            )
        previous_env = self.env
        self.env = dict(previous_env)
        self.env[stmt.element] = Ty("Wire", "Qubit", DIMLESS)
        for body_stmt in stmt.body.stmts:
            if isinstance(body_stmt, ExprStmt):
                self._infer(body_stmt.expr)
            elif isinstance(body_stmt, StateBind):
                inferred = self._infer(body_stmt.expr)
                if body_stmt.ty is not None:
                    declared = self._ty_from_ref(body_stmt.ty)
                    self._check_assign(
                        declared,
                        inferred,
                        body_stmt.span.line,
                        body_stmt.span.col,
                    )
                for name in body_stmt.names:
                    self.env[name] = inferred
            elif isinstance(body_stmt, (Measure, Snapshot)):
                self.diagnostics.append(
                    {
                        "code": "FOR_EACH_MEASURE_ERROR",
                        "line": body_stmt.span.line,
                        "col": body_stmt.span.col,
                        "message": "`forEach` bodies cannot observe or snapshot",
                    }
                )
            elif isinstance(body_stmt, ForEachStmt):
                self._check_foreach_stmt(body_stmt)
        self.env = previous_env

    @staticmethod
    def _register_set_name(payload: str) -> str | None:
        """Extract a composite system name without accepting implicit shapes."""
        prefix = "RegisterSet<"
        if payload.startswith(prefix) and payload.endswith(">"):
            return payload[len(prefix) : -1]
        return None

    @staticmethod
    def _is_qft_call(expr: Call) -> bool:
        return isinstance(expr.callee, Var) and expr.callee.name in {
            "qft",
            "iqft",
            "cqft",
            "ciqft",
        }

    def _check_qft_call(self, expr: Call, line: int, col: int) -> None:
        from .static_hilbert import MVP_MAX_LOGICAL_QUBITS

        name = expr.callee.name if isinstance(expr.callee, Var) else "qft"
        if name in {"cqft", "ciqft"}:
            valid = (
                len(expr.args) == 2
                and isinstance(expr.args[0], Var)
                and isinstance(expr.args[1], Var)
                and self.env.get(expr.args[0].name, Ty("Unknown", "Unknown")).kind
                == "Register"
                and self.env.get(expr.args[1].name, Ty("Unknown", "Unknown")).kind
                == "Register"
                and self.semantic_values.get(expr.args[0].name, 0) == 1
            )
            if not valid:
                self.diagnostics.append(
                    {
                        "code": "QFT_REGISTER_TYPE_ERROR",
                        "line": line,
                        "col": col,
                        "message": (
                            "cqft/ciqft requires QubitRegister<1> control and "
                            "QubitRegister<N> target"
                        ),
                    }
                )
                return
            ctrl_size = self.semantic_values.get(expr.args[0].name, 0)
            reg_size = self.semantic_values.get(expr.args[1].name, 0)
            if ctrl_size + reg_size > MVP_MAX_LOGICAL_QUBITS:
                self.diagnostics.append(
                    {
                        "code": "QFT_RESOURCE_ERROR",
                        "line": line,
                        "col": col,
                        "message": (
                            "cqft/ciqft qubit count exceeds the MVP resource budget "
                            f"({MVP_MAX_LOGICAL_QUBITS})"
                        ),
                    }
                )
            return

        valid = (
            len(expr.args) == 1
            and isinstance(expr.args[0], Var)
            and self.env.get(expr.args[0].name, Ty("Unknown", "Unknown")).kind
            == "Register"
        )
        if not valid:
            self.diagnostics.append(
                {
                    "code": "QFT_REGISTER_TYPE_ERROR",
                    "line": line,
                    "col": col,
                    "message": "qft/iqft requires a statically typed QubitRegister<N>",
                }
            )
            return
        register_name = expr.args[0].name
        if self.semantic_values.get(register_name, 0) > MVP_MAX_LOGICAL_QUBITS:
            self.diagnostics.append(
                {
                    "code": "QFT_RESOURCE_ERROR",
                    "line": line,
                    "col": col,
                    "message": (
                        "qft/iqft register shape exceeds the MVP resource budget "
                        f"({MVP_MAX_LOGICAL_QUBITS})"
                    ),
                }
            )

    def _bind_product_components(self, stmt: StateBind) -> bool:
        """Split product/tensor into per-coordinate types. Returns True if handled."""
        names = stmt.names
        expr = stmt.expr
        declared_parts: list[str] | None = None
        if stmt.ty is not None:
            declared = self._ty_from_ref(stmt.ty)
            declared_parts = split_product_payload(declared.payload)
            if declared_parts is None:
                # Non-product annotation on multi-name → fall through (evolve already handled)
                return False
            if len(declared_parts) != len(names):
                self.diagnostics.append(
                    {
                        "code": "PRODUCT_ARITY_ERROR",
                        "line": stmt.span.line,
                        "col": stmt.span.col,
                        "message": (
                            f"product type has {len(declared_parts)} components, "
                            f"bind has {len(names)} names"
                        ),
                    }
                )
                return True

        if isinstance(expr, TensorExpr):
            left_ty = self._infer(expr.left)
            right_ty = self._infer(expr.right)
            if len(names) != 2:
                self.diagnostics.append(
                    {
                        "code": "PRODUCT_ARITY_ERROR",
                        "line": stmt.span.line,
                        "col": stmt.span.col,
                        "message": "`*|*` bind expects exactly two names `(a, b)`",
                    }
                )
                return True
            components = [
                Ty("State", left_ty.payload, left_ty.dim),
                Ty("State", right_ty.payload, right_ty.dim),
            ]
            product = Ty(
                "State",
                product_payload([c.payload for c in components]),
                DIMLESS,
            )
            self.typed[id(expr)] = product
            if declared_parts is not None:
                for name, part, comp in zip(names, declared_parts, components):
                    want = Ty("State", part, comp.dim)
                    self._check_payload_assign(want, comp, stmt.span.line, stmt.span.col)
                    self.env[name] = want
                    self._assert_is_state(want, stmt.span.line, stmt.span.col, name)
            else:
                for name, comp in zip(names, components):
                    self.env[name] = comp
                    self._assert_is_state(comp, stmt.span.line, stmt.span.col, name)
            return True

        # Multi-name with product annotation but non-tensor RHS (e.g. evolve seeds)
        if declared_parts is not None:
            inferred = self._infer(expr)
            inf_parts = split_product_payload(inferred.payload)
            for i, name in enumerate(names):
                payload = declared_parts[i]
                if inf_parts is not None and i < len(inf_parts):
                    got = Ty("State", inf_parts[i], DIMLESS)
                    want = Ty("State", payload, DIMLESS)
                    self._check_payload_assign(want, got, stmt.span.line, stmt.span.col)
                self.env[name] = Ty("State", payload, DIMLESS)
                self._assert_is_state(self.env[name], stmt.span.line, stmt.span.col, name)
            return True

        return False

    def _check_assign(self, declared: Ty, inferred: Ty, line: int, col: int) -> None:
        # LISS-0133: unit literals infer as State<Qty>; Type-First classical
        # quantity heads accept matching dims without becoming linear.
        if (
            declared.kind == "Classical"
            and inferred.kind == "State"
            and declared.dim.matches(inferred.dim)
        ):
            return
        # Dimensionless numeric may not silently become a dimensioned quantity.
        if declared.dim.is_dimensionless() and inferred.dim.is_dimensionless():
            return
        if declared.dim.matches(inferred.dim):
            return
        # Allow Any/Float dimensionless only when declared is also dimensionless
        if inferred.payload == "Any" and inferred.dim.is_dimensionless():
            return
        self.diagnostics.append(
            {
                "code": "DIMENSION_MISMATCH_ERROR",
                "line": line,
                "col": col,
                "message": (
                    f"cannot assign {inferred} to declared {declared}: "
                    + format_dim_mismatch(declared.dim, inferred.dim, "=")
                ),
            }
        )

    def _check_payload_assign(self, declared: Ty, inferred: Ty, line: int, col: int) -> None:
        if (
            declared.kind == "Classical"
            and inferred.kind == "State"
            and declared.dim.matches(inferred.dim)
        ):
            return
        if inferred.payload in {"Any", declared.payload}:
            return
        if declared.payload in {"Any", "Int"} and inferred.payload in {
            "Int",
            "Qubit",
            "Coin",
            "Position",
            "Any",
        }:
            # Discrete carriers are Int-compatible at MVP
            return
        if inferred.payload in {"Int", "Qubit", "Coin"} and declared.payload in {
            "Qubit",
            "Coin",
            "Int",
        }:
            return
        if inferred.payload in {"Int", "Position"} and declared.payload in {
            "Position",
            "Int",
        }:
            return
        # Classical Delta<Time> vs State Time: same physical dim, different labels
        if declared.kind == "Classical" and inferred.kind == "State":
            if declared.dim.matches(inferred.dim):
                return
        self.diagnostics.append(
            {
                "code": "PRODUCT_TYPE_MISMATCH",
                "line": line,
                "col": col,
                "message": f"cannot assign {inferred} to declared {declared}",
            }
        )

    def _looks_like_operator_ast(self, expr: Expr) -> bool:
        """ADR 0180: untyped bind RHS that should elaborate as Operator."""
        if isinstance(expr, (OpVar, OpBin, OpLit, OpBinder, OpCall, OpIndexed)):
            return True
        if isinstance(expr, BinOp) and expr.op in {"+", "-", "*"}:
            return self._looks_like_operator_ast(expr.lhs) or self._looks_like_operator_ast(
                expr.rhs
            )
        if isinstance(expr, Var) and expr.name in {"X", "Y", "Z", "I", "H"}:
            return True
        return False

    def _try_desugar_omitted_bind(self, stmt: StateBind) -> bool:
        """Fill omitted `ty` + env for unique ADR 0180 elaborations.

        Returns True when the bind was fully handled (caller should `continue`).
        """
        if stmt.ty is not None or stmt.via_state_keyword:
            return False
        if self._looks_like_operator_ast(stmt.expr):
            self._check_operator_expr(stmt.expr)
            self._commit_omitted_bind(
                stmt, TypeRef(name="Operator"), Ty("Operator", "Operator", DIMLESS)
            )
            return True
        if len(stmt.names) == 1 and self._is_classical_coefficient_expr(stmt.expr):
            head = "Int" if isinstance(stmt.expr, LitInt) else "Float"
            self._commit_omitted_bind(
                stmt, TypeRef(name=head), Ty("Classical", head, DIMLESS)
            )
            return True
        if (
            len(stmt.names) == 1
            and isinstance(stmt.expr, Call)
            and isinstance(stmt.expr.callee, Var)
            and stmt.expr.callee.name in self.fun_returns
        ):
            _fun, result_ty = self.fun_returns[stmt.expr.callee.name]
            if result_ty.kind == "Classical" and result_ty.payload == "Float":
                self._infer(stmt.expr)
                self._commit_omitted_bind(stmt, TypeRef(name="Float"), result_ty)
                return True
        if len(stmt.names) == 1 and isinstance(stmt.expr, Call):
            ctor = self._ctor_type_name(stmt.expr)
            if ctor is not None and ctor in self.struct_meta:
                st = self.struct_meta[ctor]
                self._commit_omitted_bind(
                    stmt,
                    TypeRef(name=st.qualified_name),
                    Ty("Struct", st.qualified_name, DIMLESS),
                )
                return True
            if ctor is not None and ctor in self.class_meta:
                cls = self.class_meta[ctor]
                self._commit_omitted_bind(
                    stmt,
                    TypeRef(name=cls.qualified_name),
                    Ty("Object", cls.qualified_name, DIMLESS),
                )
                return True
        return False

    def _commit_omitted_bind(
        self, stmt: StateBind, type_ref: TypeRef, env_ty: Ty
    ) -> None:
        """Write desugared TypeRef onto the AST and bind names in env."""
        self._fill_bind_ty(stmt, type_ref)
        for n in stmt.names:
            self.env[n] = env_ty

    @staticmethod
    def _fill_bind_ty(stmt: StateBind, ty: TypeRef) -> None:
        """ADR 0180 Decision §3: write omitted type onto the AST bind."""
        stmt.ty = ty

    @staticmethod
    def _type_ref_from_ty(ty: Ty) -> TypeRef | None:
        """Map a unique elaboration Ty back to a surface TypeRef for desugar."""
        if ty.kind == "Operator":
            return TypeRef(name="Operator")
        if ty.kind == "Classical":
            return TypeRef(name=ty.payload)
        if ty.kind in {"Struct", "Object", "Enum"}:
            return TypeRef(name=ty.payload)
        return None

    def _ctor_type_name(self, expr: Call) -> str | None:
        """Resolve `Name(…)` / `A.B { … }` constructor head to a type path."""
        if isinstance(expr.callee, Var):
            return expr.callee.name
        if isinstance(expr.callee, Attr):
            parts: list[str] = []
            cur: Expr = expr.callee
            while isinstance(cur, Attr):
                parts.append(cur.name)
                cur = cur.obj
            if isinstance(cur, Var):
                parts.append(cur.name)
                return ".".join(reversed(parts))
        return None

    def _is_classical_coefficient_expr(self, expr: Expr) -> bool:
        """Pure classical numeric tree for ADR 0180 coefficient inference."""
        if isinstance(expr, (LitInt, LitFloat)):
            return True
        if isinstance(expr, Var):
            ty = self.env.get(expr.name)
            return ty is not None and ty.kind == "Classical"
        if isinstance(expr, Attr):
            # `seg.length` after a Struct bind — classical field projection.
            field_ty = self._infer_attr(expr)
            return field_ty.kind == "Classical"
        if isinstance(expr, BinOp) and expr.op in {"+", "-", "*", "/"}:
            return self._is_classical_coefficient_expr(
                expr.lhs
            ) and self._is_classical_coefficient_expr(expr.rhs)
        if isinstance(expr, UnitConvert):
            return self._is_classical_coefficient_expr(expr.expr)
        return False

    def _check_operator_expr(self, expr: OpExpr) -> None:
        """Check a symbolic operator tree without expanding or executing it."""
        if isinstance(expr, OpBinder):
            domain_ty: Ty | None = None
            if isinstance(expr.domain, (IndexDomain, RevDomain)):
                self._check_index_domain_expr(expr.domain)
                domain_ty = Ty("Meta", "Index", DIMLESS)
            elif isinstance(expr.domain, TypeRef):
                if expr.domain.name == "Basis":
                    if not self._valid_basis_domain(expr.domain):
                        self.diagnostics.append(
                            {
                                "code": "BINDER_DOMAIN_ERROR",
                                "line": expr.span.line,
                                "col": expr.span.col,
                                "message": (
                                    "`Basis<N>` binder domain requires a static "
                                    "non-negative integer size"
                                ),
                            }
                        )
                    else:
                        size = int(expr.domain.args[0].name)
                        if size == 0:
                            self.diagnostics.append(
                                {
                                    "code": "EMPTY_BINDER_DOMAIN_WARNING",
                                    "line": expr.span.line,
                                    "col": expr.span.col,
                                    "message": (
                                        "Basis binder domain is empty; "
                                        "using the fold identity"
                                    ),
                                }
                            )
                        end = size - 1
                        capacity = max(
                            (
                                value
                                for name, value in self.semantic_values.items()
                                if self.env.get(name) is not None
                                and self.env[name].kind == "Register"
                            ),
                            default=None,
                        )
                        if capacity is not None and size > 0 and end >= capacity:
                            self.diagnostics.append(
                                {
                                    "code": "BINDER_DOMAIN_ERROR",
                                    "line": expr.span.line,
                                    "col": expr.span.col,
                                    "message": (
                                        "Basis binder domain exceeds the static "
                                        "register shape"
                                    ),
                                }
                            )
                elif expr.domain.name != "Index":
                    self.diagnostics.append(
                        {
                            "code": "BINDER_DOMAIN_ERROR",
                            "line": expr.span.line,
                            "col": expr.span.col,
                            "message": (
                                f"binder domain `{expr.domain.name}` is not a finite "
                                "`Index` or `Basis` range; other carriers remain deferred"
                            ),
                        }
                    )
                elif not self._valid_index_domain(expr.domain):
                    self.diagnostics.append(
                        {
                            "code": "BINDER_DOMAIN_ERROR",
                            "line": expr.span.line,
                            "col": expr.span.col,
                            "message": "`Index<N>` or inclusive `Index<start..end>` requires static bounds",
                        }
                    )
                elif expr.domain.is_inclusive_range:
                    start = int(expr.domain.args[0].name)
                    end = int(expr.domain.args[1].name)
                    if end < start:
                        self.diagnostics.append(
                            {
                                "code": "EMPTY_BINDER_DOMAIN_WARNING",
                                "line": expr.span.line,
                                "col": expr.span.col,
                                "message": "inclusive binder range is empty; using the fold identity",
                            }
                        )
                    capacity = max(
                        (
                            value
                            for name, value in self.semantic_values.items()
                            if self.env.get(name) is not None
                            and self.env[name].kind == "Register"
                        ),
                        default=None,
                    )
                    if capacity is not None and end >= capacity:
                        self.diagnostics.append(
                            {
                                "code": "BINDER_DOMAIN_ERROR",
                                "line": expr.span.line,
                                "col": expr.span.col,
                                "message": "inclusive binder range exceeds the static register shape",
                            }
                        )
                domain_ty = self._ty_from_ref(expr.domain)
            else:
                domain_ty = self.env.get(expr.domain.name)
                if domain_ty is None:
                    self.diagnostics.append(
                        {
                            "code": "BINDER_DOMAIN_ERROR",
                            "line": expr.domain.span.line,
                            "col": expr.domain.span.col,
                            "message": f"unknown finite binder domain `{expr.domain.name}`",
                        }
                    )
                elif domain_ty.kind == "Execution":
                    self.diagnostics.append(
                        {
                            "code": "PHASE_TYPE_VISIBILITY_ERROR",
                            "line": expr.domain.span.line,
                            "col": expr.domain.span.col,
                            "message": f"execution carrier `{domain_ty}` cannot be a theory domain",
                        }
                    )
                elif domain_ty.kind not in {"Meta", "Discrete"}:
                    self.diagnostics.append(
                        {
                            "code": "BINDER_DOMAIN_ERROR",
                            "line": expr.domain.span.line,
                            "col": expr.domain.span.col,
                            "message": f"`{expr.domain.name}` is not a finite semantic domain",
                        }
                    )
                if self.semantic_values.get(expr.domain.name, 0) > 1_000_000:
                    self.diagnostics.append(
                        {
                            "code": "BINDER_RESOURCE_ERROR",
                            "line": expr.domain.span.line,
                            "col": expr.domain.span.col,
                            "message": "finite binder expansion exceeds the Kernel resource budget",
                        }
                    )
            previous = self.env.get(expr.variable)
            if (
                isinstance(expr.domain, TypeRef)
                and expr.domain.name == "Basis"
                and self._valid_basis_domain(expr.domain)
            ):
                self.env[expr.variable] = self._ty_from_ref(expr.domain)
            else:
                self.env[expr.variable] = Ty("Meta", "Index", DIMLESS)
            self._binder_depth += 1
            try:
                self._check_operator_expr(expr.body)
                self._require_full_rank_coeff(expr.body)
            finally:
                self._binder_depth -= 1
            if previous is None:
                self.env.pop(expr.variable, None)
            else:
                self.env[expr.variable] = previous
            return

        if isinstance(expr, OpBin):
            self._check_operator_expr(expr.lhs)
            self._check_operator_expr(expr.rhs)
            if self._binder_depth > 0:
                self._require_full_rank_coeff(expr.lhs)
                self._require_full_rank_coeff(expr.rhs)
            return
        if isinstance(expr, OpIndexed):
            self._check_operator_expr(expr.base)
            self._check_operator_expr(expr.index)
            if (
                self._binder_depth > 0
                and isinstance(expr.base, OpVar)
                and expr.base.name not in {"create", "annihilate"}
                and expr.base.name not in self.float_arrays
            ):
                self.diagnostics.append(
                    {
                        "code": "BINDER_LOWERING_UNSUPPORTED",
                        "line": expr.base.span.line,
                        "col": expr.base.span.col,
                        "message": (
                            f"indexed coefficient `{expr.base.name}[…]` requires a "
                            "`Float[N]…` binding (or a second-quantized atom)"
                        ),
                    }
                )
            if isinstance(expr.index, OpVar):
                index_ty = self.env.get(expr.index.name)
                if index_ty is not None and index_ty.kind == "Execution":
                    self.diagnostics.append(
                        {
                            "code": "PHASE_TYPE_VISIBILITY_ERROR",
                            "line": expr.index.span.line,
                            "col": expr.index.span.col,
                            "message": "execution carrier cannot index a theory operator",
                        }
                    )
            if (
                self._active_register_set is not None
                and isinstance(expr.index, OpLit)
                and len(self.system_registers.get(self._active_register_set, ())) > 1
            ):
                # LISS-0133: `data[0]` building blocks are register-qualified;
                # only bare operator sites like `Z[0]` are ambiguous.
                registers = dict(
                    self.system_registers.get(self._active_register_set, ())
                )
                base_is_register = (
                    isinstance(expr.base, OpVar) and expr.base.name in registers
                )
                if not base_is_register:
                    self.diagnostics.append(
                        {
                            "code": "MULTI_REGISTER_INDEX_AMBIGUOUS",
                            "line": expr.index.span.line,
                            "col": expr.index.span.col,
                            "message": "multi-register operators require a register-qualified site",
                        }
                    )
            if isinstance(expr.index, OpIndexed) and isinstance(expr.index.base, OpVar):
                register_name = expr.index.base.name
                registers = dict(self.system_registers.get(self._active_register_set or "", ()))
                if self._active_register_set is not None and register_name not in registers:
                    self.diagnostics.append(
                        {
                            "code": "UNKNOWN_REGISTER_ID",
                            "line": expr.index.span.line,
                            "col": expr.index.span.col,
                            "message": f"unknown register `{register_name}` in acting space",
                        }
                    )
            return
        if isinstance(expr, OpCall):
            if expr.name in {"I", "X", "Y", "Z"}:
                self.diagnostics.append(
                    {
                        "code": "RETIRED_OPERATOR_INDEX_SYNTAX",
                        "line": expr.span.line,
                        "col": expr.span.col,
                        "message": (
                            f"`{expr.name}(…)` is retired operator-index syntax; "
                            f"write `{expr.name}[…]`"
                        ),
                    }
                )
            if expr.name in {"measure", "log", "write", "send"}:
                self.diagnostics.append(
                    {
                        "code": "MATHEMATICAL_BINDER_EFFECT_ERROR",
                        "line": expr.span.line,
                        "col": expr.span.col,
                        "message": f"`{expr.name}` is not allowed in a mathematical binder",
                    }
                )
            for arg in expr.args:
                self._check_operator_expr(arg)
            return

    @staticmethod
    def _valid_index_domain(ref: TypeRef) -> bool:
        if ref.name != "Index":
            return True
        if len(ref.args) == 1:
            try:
                return int(ref.args[0].name) > 0
            except ValueError:
                return False
        if len(ref.args) == 2:
            try:
                return int(ref.args[0].name) >= 0 and int(ref.args[1].name) >= 0
            except ValueError:
                return False
        return False

    @staticmethod
    def _valid_basis_domain(ref: TypeRef) -> bool:
        """ADR 0118: `Basis<N>` with static non-negative integer N."""
        if ref.name != "Basis" or len(ref.args) != 1:
            return False
        try:
            return int(ref.args[0].name) >= 0
        except ValueError:
            return False

    def _check_index_endpoint_expr(self, expr: OpExpr) -> None:
        """ADR 0117: static additive endpoints only."""
        if isinstance(expr, OpLit):
            return
        if isinstance(expr, OpVar):
            ty = self.env.get(expr.name)
            if ty is not None and ty.kind == "Register":
                return
            if ty is not None and ty.kind == "Meta" and ty.payload == "Index":
                return
            if expr.name in self.semantic_values and (
                self.env.get(expr.name) is not None
                and self.env[expr.name].kind == "Register"
            ):
                return
            # Outer binder variables are Meta Index in env while checking body,
            # but domain of an inner binder is checked while outer var is already
            # in env. Unknown names fail at lowering; warn only if clearly wrong.
            if ty is None:
                return
            if ty.kind not in {"Meta", "Register", "Classical"}:
                self.diagnostics.append(
                    {
                        "code": "BINDER_DOMAIN_ERROR",
                        "line": expr.span.line,
                        "col": expr.span.col,
                        "message": (
                            f"`{expr.name}` cannot be used as a static Index endpoint"
                        ),
                    }
                )
            return
        if isinstance(expr, OpBin) and expr.op in {"+", "-"}:
            self._check_index_endpoint_expr(expr.lhs)
            self._check_index_endpoint_expr(expr.rhs)
            return
        self.diagnostics.append(
            {
                "code": "BINDER_DOMAIN_ERROR",
                "line": expr.span.line,
                "col": expr.span.col,
                "message": "Index endpoints must be static additive expressions",
            }
        )

    def _check_index_domain_expr(self, domain: IndexDomain | RevDomain) -> None:
        while isinstance(domain, RevDomain):
            domain = domain.inner  # type: ignore[assignment]
        if isinstance(domain, IndexDomain):
            self._check_index_endpoint_expr(domain.start)
            self._check_index_endpoint_expr(domain.end)
            # Literal-only empty-range warning (ADR 0096 D9)
            if isinstance(domain.start, OpLit) and isinstance(domain.end, OpLit):
                start = int(domain.start.value)
                end = int(domain.end.value)
                if end < start:
                    self.diagnostics.append(
                        {
                            "code": "EMPTY_BINDER_DOMAIN_WARNING",
                            "line": domain.span.line,
                            "col": domain.span.col,
                            "message": (
                                "inclusive binder range is empty; using the fold identity"
                            ),
                        }
                    )
                capacity = max(
                    (
                        value
                        for name, value in self.semantic_values.items()
                        if self.env.get(name) is not None
                        and self.env[name].kind == "Register"
                    ),
                    default=None,
                )
                if capacity is not None and end >= capacity:
                    self.diagnostics.append(
                        {
                            "code": "BINDER_DOMAIN_ERROR",
                            "line": domain.span.line,
                            "col": domain.span.col,
                            "message": (
                                "inclusive binder range exceeds the static register shape"
                            ),
                        }
                    )
            return
        if isinstance(domain, TypeRef):
            ok_index = domain.name == "Index" and self._valid_index_domain(domain)
            ok_basis = domain.name == "Basis" and self._valid_basis_domain(domain)
            if not ok_index and not ok_basis:
                self.diagnostics.append(
                    {
                        "code": "BINDER_DOMAIN_ERROR",
                        "line": 0,
                        "col": 0,
                        "message": "rev() requires a finite Index or Basis domain",
                    }
                )
            return
        self.diagnostics.append(
            {
                "code": "BINDER_DOMAIN_ERROR",
                "line": 0,
                "col": 0,
                "message": "rev() requires a finite Index domain",
            }
        )

    def _check_float_array_bind(self, stmt: StateBind) -> None:
        """LISS-0143/0144: validate `Float[N]… name = […]` and register shape."""
        assert stmt.ty is not None
        shape: list[int] = []
        for arg in stmt.ty.args:
            try:
                dim = int(arg.name)
            except ValueError:
                self.diagnostics.append(
                    {
                        "code": "TYPE_MISMATCH",
                        "line": stmt.span.line,
                        "col": stmt.span.col,
                        "message": "`Float[N]…` requires positive integer lengths",
                    }
                )
                return
            if dim <= 0:
                self.diagnostics.append(
                    {
                        "code": "TYPE_MISMATCH",
                        "line": stmt.span.line,
                        "col": stmt.span.col,
                        "message": "`Float[N]…` lengths must be positive",
                    }
                )
                return
            shape.append(dim)
        shape_t = tuple(shape)
        product = 1
        for dim in shape_t:
            product *= dim
            if product > 1_000_000:
                self.diagnostics.append(
                    {
                        "code": "BINDER_RESOURCE_ERROR",
                        "line": stmt.span.line,
                        "col": stmt.span.col,
                        "message": (
                            "`Float[N]…` element count exceeds the Kernel resource budget"
                        ),
                    }
                )
                return
        if isinstance(stmt.expr, ListExpr):
            err = self._validate_float_tensor_literal(stmt.expr, shape_t, depth=0)
            if err is not None:
                self.diagnostics.append(err)
                return
        elif isinstance(stmt.expr, OpIndexed):
            if not self._check_float_partial_bind(stmt, shape_t):
                return
        elif self._is_host_coefficient_call(stmt.expr):
            pass  # shape-only placeholder; values arrive via Host overlay
        else:
            self.diagnostics.append(
                {
                    "code": "TYPE_MISMATCH",
                    "line": stmt.span.line,
                    "col": stmt.span.col,
                    "message": (
                        "`Float[N]…` requires a nested list literal `[…]`, a "
                        "static partial index, or `host(\"…\")`"
                    ),
                }
            )
            return
        label = "".join(f"[{d}]" for d in shape_t)
        for n in stmt.names:
            self.env[n] = Ty("Classical", f"Float{label}", DIMLESS)
            self.float_arrays[n] = shape_t

    @staticmethod
    def _is_host_coefficient_call(expr: Any) -> bool:
        return (
            isinstance(expr, Call)
            and isinstance(expr.callee, Var)
            and expr.callee.name == "host"
            and len(expr.args) == 1
            and isinstance(expr.args[0], LitString)
            and bool(expr.args[0].value.strip())
        )

    def _check_float_partial_bind(
        self, stmt: StateBind, declared_shape: tuple[int, ...]
    ) -> bool:
        """ADR 0118: `Float[M…] row = h[i]` with static literal indices."""
        assert isinstance(stmt.expr, OpIndexed)
        root, indices = self._peel_indexed(stmt.expr)
        if not isinstance(root, OpVar) or root.name not in self.float_arrays:
            self.diagnostics.append(
                {
                    "code": "TYPE_MISMATCH",
                    "line": stmt.span.line,
                    "col": stmt.span.col,
                    "message": (
                        "partial Float index requires a known `Float[…]` tensor root"
                    ),
                }
            )
            return False
        parent_shape = self.float_arrays[root.name]
        if not (0 < len(indices) < len(parent_shape)):
            self.diagnostics.append(
                {
                    "code": "TYPE_MISMATCH",
                    "line": stmt.span.line,
                    "col": stmt.span.col,
                    "message": (
                        "partial Float index must apply a proper prefix of axes "
                        f"(rank {len(parent_shape)})"
                    ),
                }
            )
            return False
        remaining = parent_shape[len(indices) :]
        if remaining != declared_shape:
            self.diagnostics.append(
                {
                    "code": "TYPE_MISMATCH",
                    "line": stmt.span.line,
                    "col": stmt.span.col,
                    "message": (
                        "partial Float bind shape does not match the remaining axes "
                        f"(expected {list(remaining)}, declared {list(declared_shape)})"
                    ),
                }
            )
            return False
        for axis, index_expr in enumerate(indices):
            if not isinstance(index_expr, OpLit):
                self.diagnostics.append(
                    {
                        "code": "TYPE_MISMATCH",
                        "line": stmt.span.line,
                        "col": stmt.span.col,
                        "message": (
                            "classical partial Float indices must be static "
                            "integer literals"
                        ),
                    }
                )
                return False
            try:
                index = int(index_expr.value)
            except (TypeError, ValueError):
                self.diagnostics.append(
                    {
                        "code": "TYPE_MISMATCH",
                        "line": index_expr.span.line,
                        "col": index_expr.span.col,
                        "message": "Float index must be an integer literal",
                    }
                )
                return False
            if index < 0 or index >= parent_shape[axis]:
                self.diagnostics.append(
                    {
                        "code": "BINDER_INDEX_OUT_OF_BOUNDS",
                        "line": index_expr.span.line,
                        "col": index_expr.span.col,
                        "message": (
                            f"Float index {index} is out of bounds for axis "
                            f"{axis} of length {parent_shape[axis]}"
                        ),
                    }
                )
                return False
        return True

    def _validate_float_tensor_literal(
        self, expr: Any, shape: tuple[int, ...], *, depth: int
    ) -> dict | None:
        """Recursively check nested ListExpr against remaining shape axes."""
        if depth >= len(shape):
            if not isinstance(expr, (LitInt, LitFloat)):
                return {
                    "code": "TYPE_MISMATCH",
                    "line": getattr(expr, "span", None).line
                    if getattr(expr, "span", None)
                    else 0,
                    "col": getattr(expr, "span", None).col
                    if getattr(expr, "span", None)
                    else 0,
                    "message": "`Float[N]…` leaf elements must be numeric literals",
                }
            return None
        if not isinstance(expr, ListExpr):
            return {
                "code": "TYPE_MISMATCH",
                "line": getattr(expr, "span", None).line
                if getattr(expr, "span", None)
                else 0,
                "col": getattr(expr, "span", None).col
                if getattr(expr, "span", None)
                else 0,
                "message": (
                    f"`Float[…]` axis {depth} requires a list of length {shape[depth]}"
                ),
            }
        if len(expr.items) != shape[depth]:
            return {
                "code": "TYPE_MISMATCH",
                "line": expr.span.line,
                "col": expr.span.col,
                "message": (
                    f"`Float[…]` axis {depth} has length {len(expr.items)}; "
                    f"expected {shape[depth]}"
                ),
            }
        for item in expr.items:
            err = self._validate_float_tensor_literal(item, shape, depth=depth + 1)
            if err is not None:
                return err
        return None

    @staticmethod
    def _peel_indexed(expr: OpExpr) -> tuple[OpExpr, list[OpExpr]]:
        indices: list[OpExpr] = []
        cur: OpExpr = expr
        while isinstance(cur, OpIndexed):
            indices.append(cur.index)
            cur = cur.base
        indices.reverse()
        return cur, indices

    def _require_full_rank_coeff(self, expr: OpExpr) -> None:
        """Reject partial `h[p]` when `h` is an ND Float tensor (LISS-0144)."""
        if isinstance(expr, OpBin):
            self._require_full_rank_coeff(expr.lhs)
            self._require_full_rank_coeff(expr.rhs)
            return
        if not isinstance(expr, OpIndexed):
            return
        root, indices = self._peel_indexed(expr)
        if not isinstance(root, OpVar) or root.name not in self.float_arrays:
            return
        shape = self.float_arrays[root.name]
        if len(indices) != len(shape):
            self.diagnostics.append(
                {
                    "code": "BINDER_LOWERING_UNSUPPORTED",
                    "line": expr.span.line,
                    "col": expr.span.col,
                    "message": (
                        f"indexed coefficient `{root.name}` requires {len(shape)} "
                        f"indices, got {len(indices)}"
                    ),
                }
            )

    def _operator_value_kind(self, expr: Expr) -> str:
        if isinstance(expr, Var) and expr.name.upper() in {"I", "X", "Y", "Z", "H", "S", "T"}:
            return "Operator"
        if isinstance(expr, Call) and _call_op_name(expr) in {
            "adjoint",
            "outer",
            "projector",
            "commutator",
            "anticommutator",
        }:
            return "Operator"
        return self._infer(expr).kind

    def _operator_domain(self, expr: Expr) -> str | None:
        if isinstance(expr, Var) and expr.name.upper() in {"I", "X", "Y", "Z", "H", "S", "T"}:
            return "Qubit"
        if isinstance(expr, Var):
            ty = self.env.get(expr.name)
            return ty.payload if ty is not None and ty.kind == "Operator" else None
        if isinstance(expr, Call):
            name = _call_op_name(expr)
            if name in {"adjoint", "commutator", "anticommutator"} and expr.args:
                return self._operator_domain(expr.args[0])
            if name in {"outer", "projector"} and expr.args:
                return self._infer(expr.args[0]).payload
        return None

    def _check_algebra_call(self, expr: Call) -> Ty:
        """Validate the first typed operator-algebra forms."""
        name = _call_op_name(expr)
        if name not in {
            "adjoint",
            "inner",
            "outer",
            "projector",
            "commutator",
            "anticommutator",
        }:
            self._infer(expr)
            return Ty("State", "Any", DIMLESS)
        args = [self._infer(arg) for arg in expr.args]
        kinds = [self._operator_value_kind(arg) for arg in expr.args]
        if name == "adjoint" and (len(args) != 1 or kinds[0] != "Operator"):
            self._operator_algebra_error(expr, "adjoint requires one Operator")
        elif name in {"commutator", "anticommutator"} and (
            len(args) != 2 or any(kind != "Operator" for kind in kinds)
        ):
            self._operator_algebra_error(
                expr, f"{name} requires two compatible Operators"
            )
        elif name in {"commutator", "anticommutator"} and (
            self._operator_domain(expr.args[0])
            and self._operator_domain(expr.args[1])
            and self._operator_domain(expr.args[0])
            != self._operator_domain(expr.args[1])
        ):
            self.diagnostics.append(
                {
                    "code": "OPERATOR_DOMAIN_ERROR",
                    "line": expr.span.line,
                    "col": expr.span.col,
                    "message": f"{name} operands require the same Hilbert-space domain",
                }
            )
        elif name in {"inner", "outer"} and (
            len(args) != 2 or any(arg.kind != "State" for arg in args)
        ):
            self._operator_algebra_error(
                expr, f"{name} requires two State values with one Hilbert carrier"
            )
        elif name == "inner" and len(expr.args) == 2:
            self._check_matrix_element_middle(expr)
        elif name == "projector" and (len(args) != 1 or args[0].kind != "State"):
            self._operator_algebra_error(expr, "projector requires one State value")
        if name == "adjoint":
            return Ty("Operator", self._operator_domain(expr.args[0]) or "Algebra", DIMLESS)
        if name in {"commutator", "anticommutator"}:
            return Ty("Operator", self._operator_domain(expr.args[0]) or "Algebra", DIMLESS)
        if name in {"outer", "projector"}:
            return Ty("Operator", args[0].payload if args else "Algebra", DIMLESS)
        if name == "inner":
            return Ty("Classical", "Float", DIMLESS)
        return Ty("State", "Any", DIMLESS)

    def _operator_algebra_error(self, expr: Call, message: str) -> None:
        self.diagnostics.append(
            {
                "code": "OPERATOR_ALGEBRA_TYPE_ERROR",
                "line": expr.span.line,
                "col": expr.span.col,
                "message": message,
            }
        )

    def _check_matrix_element_middle(self, expr: Call) -> None:
        """`⟨φ|A|ψ⟩` → `inner(φ, A(ψ))`: middle callee must be Operator-shaped."""
        applied = expr.args[1]
        if not isinstance(applied, Call) or len(applied.args) != 1:
            return
        callee = applied.callee
        ty: Ty | None
        if isinstance(callee, Var):
            if callee.name in _PAULI_ATOM_NAMES:
                return
            ty = self.env.get(callee.name)
        elif isinstance(callee, Attr) and isinstance(callee.obj, Var):
            # LISS-0374: a class-method middle (`b.getPsi`) must be
            # checked the same way a plain-name middle already is --
            # resolve the method's declared return type through the
            # same fun_returns table method-call inference already uses
            # elsewhere, instead of silently skipping any non-Var callee.
            receiver_ty = self.env.get(callee.obj.name)
            ty = None
            if receiver_ty is not None and receiver_ty.kind in {"Object", "Struct"}:
                entry = self.fun_returns.get(f"{receiver_ty.payload}.{callee.name}")
                if entry is not None:
                    ty = entry[1]
        else:
            return
        if ty is not None and ty.kind != "Operator":
            self._operator_algebra_error(
                expr,
                "matrix element middle requires an Operator (not a State or other value)",
            )

    def _check_second_quantized_expr(self, expr: Expr, expected_family: str) -> None:
        if isinstance(expr, OpIndexed):
            self._check_operator_expr(expr)
            return
        if isinstance(expr, OpBin):
            self._check_second_quantized_expr(expr.lhs, expected_family)
            self._check_second_quantized_expr(expr.rhs, expected_family)
            return
        if isinstance(expr, Call):
            name = _call_op_name(expr)
            if name in {"create", "annihilate", "spin_raise", "spin_lower"}:
                for arg in expr.args:
                    self._infer(arg)
                return
            if name == "map":
                if len(expr.args) != 2:
                    self.diagnostics.append(
                        {
                            "code": "FERMION_MAPPING_REQUIRED_ERROR",
                            "line": expr.span.line,
                            "col": expr.span.col,
                            "message": "mapping requires an operator and an explicit mapping name",
                        }
                    )
                else:
                    op_arg, mapping_arg = expr.args
                    op_ty = (
                        self.env.get(op_arg.name)
                        if isinstance(op_arg, Var)
                        else None
                    )
                    source_family = (
                        op_ty.payload.split("<", 1)[0]
                        if op_ty is not None and op_ty.kind == "Operator"
                        else None
                    )
                    mapping_name = (
                        mapping_arg.name if isinstance(mapping_arg, Var) else None
                    )
                    if source_family != "FermionOperator" or mapping_name != "JordanWigner":
                        self.diagnostics.append(
                            {
                                "code": "SECOND_QUANTIZATION_MAPPING_UNSUPPORTED",
                                "line": expr.span.line,
                                "col": expr.span.col,
                                "message": (
                                    f"mapping `{mapping_name}` from `{source_family}` is not "
                                    "supported; only JordanWigner from FermionOperator is "
                                    "implemented (LISS-0032)"
                                ),
                            }
                        )
                for arg in expr.args:
                    self._infer(arg)
                return
            self._infer(expr)
            return
        if isinstance(expr, BinOp):
            self._check_second_quantized_expr(expr.lhs, expected_family)
            self._check_second_quantized_expr(expr.rhs, expected_family)
            self._infer(expr)
            return
        self._infer(expr)

    def type_of(self, expr: Expr) -> Ty | None:
        return self.typed.get(id(expr))

    def _operator_domain_payload(self, domain: TypeRef) -> str:
        """Canonical Operator domain payload (LISS-0074 Slice C).

        `QutritRegister<N>` and `QuditRegister<3,N>` share
        `LocalRegister<3,N>` so acting-space checks treat them as
        dimensionally equivalent while remaining nominal at the source.
        """
        if domain.name == "RegisterSet":
            return "RegisterSet<{}>".format(
                domain.args[0].name if domain.args else "Any"
            )
        if domain.name == "QutritRegister":
            shape = domain.args[0].name if len(domain.args) == 1 else "?"
            return f"LocalRegister<3,{shape}>"
        if domain.name == "QuditRegister" and len(domain.args) == 2:
            return f"LocalRegister<{domain.args[0].name},{domain.args[1].name}>"
        if domain.name == "Qutrit" and not domain.args:
            return "LocalSite<3>"
        if domain.name == "Qudit" and len(domain.args) == 1:
            return f"LocalSite<{domain.args[0].name}>"
        return domain.name

    def _env_has_register_payload(self, predicate) -> bool:
        return any(
            ty.kind == "Register" and predicate(ty.payload)
            for ty in self.env.values()
        )

    def _check_silent_qubit_operator_coercion(
        self, ty_ref: TypeRef, line: int, col: int
    ) -> None:
        """Reject Operator<QubitRegister<…>> in a qudit-only register context."""
        if not ty_ref.args or ty_ref.args[0].name != "QubitRegister":
            return
        has_qudit = self._env_has_register_payload(
            lambda payload: payload == "Qutrit" or payload.startswith("Qudit")
        )
        has_qubit = self._env_has_register_payload(lambda payload: payload == "Qubit")
        if not has_qudit or has_qubit:
            return
        self.diagnostics.append(
            {
                "code": "OPERATOR_DOMAIN_ERROR",
                "line": line,
                "col": col,
                "message": (
                    "cannot use `Operator<QubitRegister<…>>` in a qudit-only "
                    "register context (no silent qubit coercion)"
                ),
            }
        )

    def _ty_from_ref(self, ref: TypeRef) -> Ty:
        if ref.name == "Unit":
            return Ty("Unit", "Unit", DIMLESS)
        if ref.name == "Operator":
            if not ref.args:
                return Ty("Operator", "Hamiltonian", DIMLESS)
            return Ty(
                "Operator", self._operator_domain_payload(ref.args[0]), DIMLESS
            )
        if ref.name == "POVM":
            payload = ref.args[0].name if ref.args else "Any"
            return Ty("POVM", payload, DIMLESS)
        if ref.name == "State":
            if not ref.args:
                return Ty("State", "Any", DIMLESS)
            inner = ref.args[0]
            payload, dim = self._payload_dim_from_ref(inner)
            return Ty("State", payload, dim)
        if ref.name == "Delta":
            # ADR 0114 / LISS-0133: Type-First ``Delta<Q>`` is a classical
            # quantity increment (e.g. evolve-for step), not a linear State.
            if not ref.args:
                return Ty("Classical", "Delta", DIMLESS)
            payload, dim = self._payload_dim_from_ref(ref.args[0])
            return Ty("Classical", f"Delta<{payload}>", dim)
        if ref.name in self._SEMANTIC_CARRIERS:
            return self._semantic_ty_from_ref(ref)
        # ADR 0114: Type-First elaboration coefficients are Classical, not
        # linear State carriers (Float J = 1.0 used in Operator trees).
        if ref.name in ELABORATION_COEFFICIENT_HEADS:
            payload, dim = self._payload_dim_from_ref(ref)
            return Ty("Classical", payload, dim)
        # Enum type heads (including field types like `OpsPhase`).
        if ref.name in self.enum_variants or ref.name.split(".")[-1] in self.enum_variants:
            key = ref.name if ref.name in self.enum_variants else ref.name.split(".")[-1]
            return Ty("Enum", key, DIMLESS)
        payload, dim = self._payload_dim_from_ref(ref)
        return Ty("State", payload, dim)

    def _check_when_enum_exhaustive(self, expr: WhenExpr, ctrl_ty: Ty) -> None:
        """Hard-fail incomplete closed-enum `mix` without `else` (LISS-0304)."""
        if any(arm.is_else for arm in expr.arms):
            return
        enum_key: str | None = None
        if ctrl_ty.kind == "Enum":
            enum_key = ctrl_ty.payload
        elif ctrl_ty.payload in self.enum_variants:
            enum_key = ctrl_ty.payload
        elif ctrl_ty.payload.split(".")[-1] in self.enum_variants:
            enum_key = ctrl_ty.payload.split(".")[-1]
        if enum_key is None:
            return
        variants = self.enum_variants.get(enum_key) or self.enum_variants.get(
            enum_key.split(".")[-1]
        )
        if not variants:
            return
        covered = {
            arm.pat
            for arm in expr.arms
            if not arm.is_else and isinstance(arm.pat, str)
        }
        missing = [v for v in variants if v not in covered]
        if not missing:
            return
        self.diagnostics.append(
            {
                "code": "WHEN_NONEXHAUSTIVE",
                "line": expr.span.line,
                "col": expr.span.col,
                "message": (
                    f"`mix` on enum `{enum_key}` is missing variant(s) "
                    f"{', '.join(missing)}; cover every variant or add `else`"
                ),
            }
        )

    def _semantic_ty_from_ref(self, ref: TypeRef) -> Ty:
        """Build a meaning-bearing discrete type without lowering it to Int."""
        argument = ""
        if ref.args:
            argument = "<" + ",".join(arg.name for arg in ref.args) + ">"
        name = f"{ref.name}{argument}"
        if ref.name in {"ShotCount", "IterationCount", "Count"}:
            kind = "Execution"
        elif ref.name in {"Basis", "Bit", "EnergyLevel", "SpinProjection"}:
            kind = "Discrete"
        else:
            kind = "Meta"
        return Ty(kind, name, DIMLESS)

    def _check_semantic_assignment(
        self, declared: Ty, inferred: Ty, expr: Expr, line: int, col: int
    ) -> None:
        """Check explicit carrier boundaries before any indexed syntax exists."""
        if declared.kind == "Meta" and declared.payload.startswith("Dimension"):
            if isinstance(expr, LitInt) and expr.value > 0:
                return
            if isinstance(expr, LitInt) and expr.value <= 0:
                self.diagnostics.append(
                    {
                        "code": "BINDER_DOMAIN_ERROR",
                        "line": line,
                        "col": col,
                        "message": "finite `Dimension` values must be positive",
                    }
                )
                return
        if declared.kind == "Execution" and declared.payload.startswith(
            ("ShotCount", "IterationCount", "Count")
        ):
            if isinstance(expr, LitInt) and expr.value >= 0:
                return
        if inferred.kind == declared.kind and (
            inferred.payload == declared.payload
            or inferred.payload.split("<", 1)[0] == declared.payload.split("<", 1)[0]
        ):
            return
        if inferred.kind == "Execution" and declared.kind != "Execution":
            self.diagnostics.append(
                {
                    "code": "PHASE_TYPE_VISIBILITY_ERROR",
                    "line": line,
                    "col": col,
                    "message": (
                        f"execution carrier `{inferred}` is not visible in theory type "
                        f"`{declared}`"
                    ),
                }
            )
            return
        self.diagnostics.append(
            {
                "code": "SEMANTIC_CARRIER_MISMATCH_ERROR",
                "line": line,
                "col": col,
                "message": f"cannot assign semantic carrier {inferred} to {declared}",
            }
        )

    def _payload_dim_from_ref(self, ref: TypeRef) -> tuple[str, Dim]:
        if ref.name == "Tuple":
            parts: list[str] = []
            for a in ref.args:
                p, _d = self._payload_dim_from_ref(a)
                parts.append(p)
            return product_payload(parts), DIMLESS
        if ref.name == "Delta" and ref.args:
            inner_p, inner_d = self._payload_dim_from_ref(ref.args[0])
            return f"Delta<{inner_p}>", inner_d
        if ref.name == "Qudit" and len(ref.args) == 1:
            # Preserve type-level D so LISS-0112 can lift D=3 only.
            return f"Qudit<{ref.args[0].name}>", DIMLESS
        if ref.name in TYPE_DIMS:
            return ref.name, TYPE_DIMS[ref.name]
        return ref.name, dim_of_type_name(ref.name)

    def _assert_is_state(self, ty: Ty, line: int, col: int, what: str) -> None:
        if ty.kind not in {
            "State",
            "Classical",
            "Operator",
            "Object",
            "Enum",
            "Struct",
            "Partial",
            "DiagnosticView",
        }:
            self.diagnostics.append(
                {
                    "code": "TYPE_NOT_STATE",
                    "line": line,
                    "col": col,
                    "message": f"{what} has non-State type {ty}",
                }
            )

    def _expr_is_enum_variant(
        self, expr: Expr, enum_name: str, enum_names: set[str]
    ) -> bool:
        if not isinstance(expr, Attr):
            return False
        q = None
        if isinstance(expr.obj, Var):
            q = expr.obj.name
        elif isinstance(expr.obj, Attr):
            # Namespace.Enum.Variant — obj is Namespace.Enum
            parts: list[str] = []
            cur: Expr = expr.obj
            while isinstance(cur, Attr):
                parts.append(cur.name)
                cur = cur.obj
            if isinstance(cur, Var):
                parts.append(cur.name)
                q = ".".join(reversed(parts))
        return q is not None and q in enum_names

    def _check_assign_stmt(
        self, stmt: AssignStmt, class_meta: dict[str, ClassDecl]
    ) -> None:
        target = stmt.target
        if not isinstance(target, Attr):
            return
        # struct field write is always illegal; var class field OK
        if isinstance(target.obj, Var):
            recv_ty = self.env.get(target.obj.name)
            if recv_ty is not None and recv_ty.kind == "Struct":
                self.diagnostics.append(
                    {
                        "code": "IMMUTABLE_ASSIGNMENT_ERROR",
                        "line": stmt.span.line,
                        "col": stmt.span.col,
                        "message": (
                            f"struct `{recv_ty.payload}` fields are immutable"
                        ),
                    }
                )
                return
            if recv_ty is not None and recv_ty.kind == "Object":
                cls = class_meta.get(recv_ty.payload)
                if cls is not None:
                    mem = next(
                        (m for m in cls.members if m.name == target.name), None
                    )
                    if mem is not None and not mem.mutable:
                        self.diagnostics.append(
                            {
                                "code": "IMMUTABLE_ASSIGNMENT_ERROR",
                                "line": stmt.span.line,
                                "col": stmt.span.col,
                                "message": (
                                    f"field `{target.name}` is `val` (immutable)"
                                ),
                            }
                        )

    def _check_method_assigns(self, method, cls: ClassDecl) -> None:
        # `fun init` may assign `val` fields once (constructor initialization).
        if method.name == "init":
            return
        mutable = {m.name for m in cls.members if m.mutable}
        for stmt in method.body.stmts:
            if not isinstance(stmt, AssignStmt):
                continue
            t = stmt.target
            if not isinstance(t, Attr):
                continue
            if isinstance(t.obj, Var) and t.obj.name == "this":
                if t.name not in mutable:
                    self.diagnostics.append(
                        {
                            "code": "IMMUTABLE_ASSIGNMENT_ERROR",
                            "line": stmt.span.line,
                            "col": stmt.span.col,
                            "message": (
                                f"field `{t.name}` is not `var` "
                                f"(cannot assign through `this`)"
                            ),
                        }
                    )

    def _check_function_body(
        self,
        fun: FunDecl,
        base_env: dict[str, Ty],
        cls: ClassDecl | None = None,
    ) -> None:
        """Check explicit function results without changing main's environment."""
        previous_env = self.env
        previous_class = self._in_class
        previous_effects = self._current_effects
        previous_static_scalars = self.static_scalars
        self.env = dict(base_env)
        self.static_scalars = dict(previous_static_scalars)
        self._in_class = cls.qualified_name if cls is not None else None
        self._current_effects = self._effect_context(fun)
        for param in fun.params:
            self.env[param.name] = (
                self._ty_from_ref(param.ty)
                if param.ty is not None
                else Ty("State", "Any", DIMLESS)
            )
        if cls is not None:
            self.env["this"] = Ty("Object", cls.qualified_name, DIMLESS)

        for stmt in fun.body.stmts:
            if isinstance(stmt, (Measure, Snapshot)):
                self.diagnostics.append(
                    {
                        "code": "MEASURE_IN_FUNCTION_ERROR"
                        if isinstance(stmt, Measure)
                        else "SNAPSHOT_IN_FUNCTION_ERROR",
                        "line": stmt.span.line,
                        "col": stmt.span.col,
                        "message": f"`{type(stmt).__name__}` is forbidden inside `{fun.name}`",
                    }
                )
            elif isinstance(stmt, AssignStmt):
                if fun.name != "init":
                    self._check_assign_stmt(stmt, self.class_meta)
            elif isinstance(stmt, StateBind):
                if stmt.ty is not None and stmt.ty.name == "Operator":
                    # Operator locals must remain visible to later return
                    # expressions so their declared type can be checked.
                    for name in stmt.names:
                        self.env[name] = self._ty_from_ref(stmt.ty)
                    continue
                inferred = self._infer(stmt.expr)
                ty = inferred
                if stmt.ty is not None:
                    ty = self._ty_from_ref(stmt.ty)
                    self._check_assign(ty, inferred, stmt.span.line, stmt.span.col)
                for name in stmt.names:
                    self.env[name] = ty
                    if ty.kind == "Classical" and len(stmt.names) == 1:
                        static_val = self._static_scalar_value(stmt.expr)
                        if static_val is not None:
                            self.static_scalars[name] = static_val

        return_stmt = next(
            (stmt for stmt in fun.body.stmts if isinstance(stmt, ReturnStmt)),
            None,
        )
        if fun.name == "init":
            if return_stmt is not None:
                self.diagnostics.append(
                    {
                        "code": "INIT_RETURN_ERROR",
                        "line": return_stmt.span.line,
                        "col": return_stmt.span.col,
                        "message": "`init` cannot return a value",
                    }
                )
        elif return_stmt is None:
            self.diagnostics.append(
                {
                    "code": "MISSING_RETURN_STATEMENT",
                    "line": fun.span.line,
                    "col": fun.span.col,
                    "message": f"`{fun.name}` must end with an explicit `return`",
                }
            )
        elif return_stmt is not None:
            inferred = self._infer(return_stmt.expr)
            declared = self._ty_from_ref(fun.return_type)  # type: ignore[arg-type]
            # LISS-0133: numeric literals infer as State<Float>; Classical return
            # heads (ADR 0114 elaboration coefficients) accept them.
            if (
                declared.kind == "Classical"
                and inferred.kind == "State"
                and inferred.payload in {"Float", "Int", "Any", declared.payload}
                and declared.dim.matches(inferred.dim)
            ):
                inferred = declared
            if inferred.kind != declared.kind and inferred.payload != "Any":
                self.diagnostics.append(
                    {
                        "code": "RETURN_TYPE_MISMATCH",
                        "line": return_stmt.span.line,
                        "col": return_stmt.span.col,
                        "message": f"`{fun.name}` returns {inferred}, declared {declared}",
                    }
                )
            if (
                inferred.payload != "Any"
                and declared.payload != "Any"
                and inferred.payload != declared.payload
            ):
                decl_parts = split_product_payload(declared.payload)
                inf_parts = split_product_payload(inferred.payload)
                compatible = False
                if (
                    decl_parts is not None
                    and inf_parts is not None
                    and len(decl_parts) == len(inf_parts)
                ):
                    compatible = all(
                        d == i or d == "Any" or i == "Any"
                        for d, i in zip(decl_parts, inf_parts)
                    )
                if not compatible:
                    self.diagnostics.append(
                        {
                            "code": "RETURN_TYPE_MISMATCH",
                            "line": return_stmt.span.line,
                            "col": return_stmt.span.col,
                            "message": f"`{fun.name}` returns {inferred}, declared {declared}",
                        }
                    )
            if not declared.dim.matches(inferred.dim):
                self._dim_error(
                    return_stmt.span.line,
                    return_stmt.span.col,
                    declared.dim,
                    inferred.dim,
                    "return",
                )

        self.env = previous_env
        self._in_class = previous_class
        self._current_effects = previous_effects
        self.static_scalars = previous_static_scalars

    def _effect_context(self, fun: FunDecl) -> frozenset[str]:
        """Return the capabilities available while checking one function."""
        if fun.name == "main":
            return self._EFFECTS
        return frozenset(fun.effects)

    def _check_impl_contract(
        self, impl: ImplDecl, impl_pairs: set[tuple[str, str]]
    ) -> None:
        """Check linked-program coherence and impl-local visibility rules."""
        pair = (impl.interface.name, impl.target.name)
        if pair in impl_pairs:
            self.diagnostics.append(
                {
                    "code": "IMPL_COHERENCE_ERROR",
                    "line": impl.span.line,
                    "col": impl.span.col,
                    "message": (
                        f"duplicate implementation for `{pair[0]}` "
                        f"and `{pair[1]}`"
                    ),
                }
            )
        impl_pairs.add(pair)
        for method in impl.methods:
            if method.visibility == "public":
                self.diagnostics.append(
                    {
                        "code": "IMPL_VISIBILITY_ERROR",
                        "line": method.span.line,
                        "col": method.span.col,
                        "message": "`pub` is not allowed inside an impl block",
                    }
                )

    def check_access_bounds(
        self,
        *,
        visibility: str,
        name: str,
        decl_package: list[str] | None,
        use_package: list[str] | None,
        span_line: int,
        span_col: int,
        same_class: bool = False,
        is_subclass: bool = False,
        same_module: bool = True,
        same_file: bool = False,
    ) -> None:
        """ADR 0058 — static access control (`pub` / module / `_`)."""
        from .access import access_violation

        viol = access_violation(
            visibility=visibility,
            name=name,
            decl_package=decl_package,
            use_package=use_package,
            span_line=span_line,
            span_col=span_col,
            same_class=same_class,
            is_subclass=is_subclass,
            same_module=same_module,
            package_exported=True,
            same_file=same_file,
        )
        if viol is not None:
            self.diagnostics.append(viol)

    def _member_visibility(self, cls: ClassDecl | None, member: str) -> str:
        from .access import effective_member_visibility

        if cls is None:
            return effective_member_visibility(member, "module")
        for f in cls.members or []:
            if f.name == member:
                return effective_member_visibility(member, f.visibility)
        for m in cls.methods or []:
            if m.name == member:
                return effective_member_visibility(member, m.visibility)
        return effective_member_visibility(member, "module")

    def _check_external_member_access(
        self, recv_ty: Ty, member: str, span_line: int, span_col: int
    ) -> None:
        """Reject `_` / private members unless inside the defining class."""
        from .access import is_underscore_private

        cls = self.class_meta.get(recv_ty.payload)
        if cls is None and recv_ty.kind not in {"Object", "Struct"}:
            return
        same_class = False
        if self._in_class is not None and cls is not None:
            same_class = self._in_class in {cls.name, cls.qualified_name}
        if same_class:
            return
        vis = self._member_visibility(cls, member)
        if vis == "private" or is_underscore_private(member):
            self.diagnostics.append(
                {
                    "code": "PRIVATE_ACCESS_VIOLATION_ERROR",
                    "line": span_line,
                    "col": span_col,
                    "message": (
                        f"cannot access private member `{member}` outside its class"
                    ),
                }
            )

    def _dim_error(self, line: int, col: int, left: Dim, right: Dim, op: str) -> None:
        self.diagnostics.append(
            {
                "code": "DIMENSION_MISMATCH_ERROR",
                "line": line,
                "col": col,
                "message": format_dim_mismatch(left, right, op),
            }
        )

    def _infer(self, expr: Expr) -> Ty:
        ty = self._infer_inner(expr)
        self.typed[id(expr)] = ty
        return ty

    def _infer_inner(self, expr: Expr) -> Ty:
        if isinstance(expr, LitInt):
            return Ty("State", "Int", DIMLESS)
        if isinstance(expr, LitFloat):
            return Ty("State", "Float", DIMLESS)
        if isinstance(expr, LitBool):
            return Ty("State", "Bool", DIMLESS)
        if isinstance(expr, LitString):
            return Ty("State", "String", DIMLESS)
        if isinstance(expr, Coin):
            return Ty("State", "Coin", DIMLESS)
        if isinstance(expr, Vacuum):
            return Ty("State", "Any", DIMLESS)
        if isinstance(expr, Dirac):
            inner = self._infer(expr.arg)
            return Ty("State", inner.payload, inner.dim)
        if isinstance(expr, (KetLit, BraLit)):
            # Alone bra shares the ket carrier in Slice A; juxtaposition /
            # adjoint lowering is deferred to later LISS-0073 slices.
            return Ty("State", "Qubit", DIMLESS)
        if isinstance(expr, Var):
            return self.env.get(expr.name, Ty("State", "Any", DIMLESS))
        if isinstance(expr, MeasureExpr):
            self.diagnostics.append(
                {
                    "code": "EARLY_COLLAPSE_ERROR",
                    "line": expr.span.line,
                    "col": expr.span.col,
                    "message": "`measure` is terminal and cannot appear as an expression",
                }
            )
            return self._infer(expr.expr)
        if isinstance(expr, BinOp):
            return self._infer_binop(expr)
        if isinstance(expr, WhenExpr):
            ctrl_ty = self._infer(expr.ctrl)
            if ctrl_ty.kind == "Classical":
                self.diagnostics.append(
                    {
                        "code": "COEFFICIENT_IN_QUANTUM_POSITION",
                        "line": expr.span.line,
                        "col": expr.span.col,
                        "message": (
                            "`mix` control must be a quantum/probabilistic state, "
                            "not an elaboration coefficient (classical Type-First "
                            "quantity). Keep couplings in Operator formulas; put "
                            "classical iteration in Host/Outer (ADR 0114)."
                        ),
                    }
                )
            # LISS-0304: closed enum `mix` without `else` must list every variant
            # (incomplete arms currently sample vacuum — fail closed).
            self._check_when_enum_exhaustive(expr, ctrl_ty)
            payloads: list[str] = []
            dims: list[Dim] = []
            for arm in expr.arms:
                t = self._infer(arm.body)
                payloads.append(t.payload)
                dims.append(t.dim)
            payload = payloads[0] if payloads else "Any"
            dim = dims[0] if dims else DIMLESS
            for i in range(1, len(payloads)):
                payload = _promote(payload, payloads[i])
                if not dim.matches(dims[i]) and not (
                    dim.is_dimensionless() and dims[i].is_dimensionless()
                ):
                    # when arms must share dimension
                    self._dim_error(
                        expr.span.line, expr.span.col, dim, dims[i], "when-arm"
                    )
            return Ty("State", payload, dim)
        if isinstance(expr, SuperposeExpr):
            # LISS-0320: distinct coherent lane. Arm-type unification mirrors
            # `WhenExpr`'s State<T> rule; exhaustiveness/coefficient-control
            # checks are deliberately not replicated here — they govern
            # `mix`'s vacuum-sampling execution policy, which does not apply
            # since `superpose` execution is a separate, later slice (it
            # always fails closed at evaluation for now).
            self._infer(expr.ctrl)
            payloads = []
            dims = []
            for arm in expr.arms:
                t = self._infer(arm.body)
                payloads.append(t.payload)
                dims.append(t.dim)
            payload = payloads[0] if payloads else "Any"
            dim = dims[0] if dims else DIMLESS
            for i in range(1, len(payloads)):
                payload = _promote(payload, payloads[i])
                if not dim.matches(dims[i]) and not (
                    dim.is_dimensionless() and dims[i].is_dimensionless()
                ):
                    self._dim_error(
                        expr.span.line, expr.span.col, dim, dims[i], "superpose-arm"
                    )
            return Ty("State", payload, dim)
        if isinstance(expr, Call):
            return self._infer_call(expr)
        if isinstance(expr, Pipe):
            return self._infer_pipe(expr)
        if isinstance(expr, Lambda):
            self._infer(expr.body)
            return Ty("State", "Any", DIMLESS)
        if isinstance(expr, Attr):
            return self._infer_attr(expr)
        if isinstance(expr, UnitConvert):
            return self._infer_unit_convert(expr)
        if isinstance(expr, Hole):
            self.diagnostics.append(
                {
                    "code": "PARSE_ERROR",
                    "line": expr.span.line,
                    "col": expr.span.col,
                    "message": "`_` hole is only valid inside a call argument list",
                }
            )
            return Ty("State", "Any", DIMLESS)
        if isinstance(expr, Inspect):
            self._infer(expr.expr)
            # ADR 0189: inspection is a non-destructive diagnostic view, not
            # a State value that can cross the terminal measurement boundary.
            return Ty("DiagnosticView", "Any", DIMLESS)
        if isinstance(expr, TupleExpr):
            for it in expr.items:
                self._infer(it)
            return Ty("State", "Any", DIMLESS)
        if isinstance(expr, BlockExpr):
            # ADR 0153: type lets in a nested env, then the result.
            saved = dict(self.env)
            for let in expr.lets:
                self.env[let.name] = self._infer(let.expr)
            result_ty = self._infer(expr.result)
            self.env = saved
            return result_ty
        if isinstance(expr, ListExpr):
            for item in expr.items:
                self._infer(item)
            return Ty("State", "Any", DIMLESS)
        if isinstance(expr, EvolveExpr):
            return self._infer_evolve(expr)
        if isinstance(expr, TensorExpr):
            left = self._infer(expr.left)
            right = self._infer(expr.right)
            return Ty(
                "State",
                product_payload([left.payload, right.payload]),
                DIMLESS,
            )
        if isinstance(expr, UnaryNot):
            # Open-control marker; carrier follows inner wire
            return self._infer(expr.expr)
        return Ty("State", "Any", DIMLESS)

    def _infer_pipe(self, expr: Pipe) -> Ty:
        """Type-check one left-to-right pipeline application."""
        lhs_ty = self._infer(expr.lhs)
        rhs = expr.rhs
        if isinstance(rhs, MeasureExpr):
            self.diagnostics.append(
                {
                    "code": "PIPE_EFFECT_ERROR",
                    "line": rhs.span.line,
                    "col": rhs.span.col,
                    "message": "a pipeline stage cannot perform terminal `measure`",
                }
            )
            self._infer(rhs)
            return lhs_ty
        if isinstance(rhs, Var):
            rhs_ty = self.env.get(rhs.name)
            if rhs_ty is not None and rhs_ty.kind == "Operator":
                self.diagnostics.append(
                    {
                        "code": "PIPE_CALLABLE_ERROR",
                        "line": rhs.span.line,
                        "col": rhs.span.col,
                        "message": f"operator `{rhs.name}` is not a callable pipeline stage",
                    }
                )
                return lhs_ty
            if rhs_ty is not None and rhs_ty.kind == "Partial":
                # ADR 0123 / 0149: Partial as pipe stage — fill hole(s) left-to-right.
                if "#" not in rhs_ty.payload:
                    self.diagnostics.append(
                        {
                            "code": "FUNCTION_ARITY_ERROR",
                            "line": rhs.span.line,
                            "col": rhs.span.col,
                            "message": "pipeline Partial payload is malformed",
                        }
                    )
                    return lhs_ty
                fun_name, holes_s = rhs_ty.payload.rsplit("#", 1)
                try:
                    need = int(holes_s)
                except ValueError:
                    need = -1
                if need < 1:
                    self.diagnostics.append(
                        {
                            "code": "FUNCTION_ARITY_ERROR",
                            "line": rhs.span.line,
                            "col": rhs.span.col,
                            "message": (
                                "pipeline bare Partial requires at least one remaining hole"
                            ),
                        }
                    )
                    return lhs_ty
                # ADR 0152: tuple LHS fills N holes when arities match.
                if isinstance(expr.lhs, TupleExpr):
                    n = len(expr.lhs.items)
                    if n != need:
                        self.diagnostics.append(
                            {
                                "code": "FUNCTION_ARITY_ERROR",
                                "line": rhs.span.line,
                                "col": rhs.span.col,
                                "message": (
                                    f"pipeline tuple arity {n} does not match "
                                    f"Partial remaining holes {need}"
                                ),
                            }
                        )
                        return lhs_ty
                    # Infer item types for side effects; result is completed fn.
                    for it in expr.lhs.items:
                        self._infer(it)
                    return Ty("State", "Any", DIMLESS)
                if need == 1:
                    return Ty("State", lhs_ty.payload, lhs_ty.dim)
                # ADR 0149: multi-hole → smaller Partial after one pipe fill.
                return Ty("Partial", f"{fun_name}#{need - 1}", DIMLESS)
            # ADR 0122: bare unary `fn` stage — `lhs |> f` ≡ `f(lhs)`.
            synthetic = Call(callee=rhs, args=[expr.lhs], span=expr.span)
            if self._call_effects(synthetic):
                self.diagnostics.append(
                    {
                        "code": "PIPE_EFFECT_ERROR",
                        "line": rhs.span.line,
                        "col": rhs.span.col,
                        "message": "effectful functions cannot be pipeline stages",
                    }
                )
            return self._infer_call(synthetic)
        if isinstance(rhs, Call):
            if self._call_effects(rhs):
                self.diagnostics.append(
                    {
                        "code": "PIPE_EFFECT_ERROR",
                        "line": rhs.span.line,
                        "col": rhs.span.col,
                        "message": "effectful functions cannot be pipeline stages",
                    }
                )
            return self._infer_call(self._piped_call(expr.lhs, rhs))
        self._pipe_error(
            rhs, "pipeline right-hand side must be a function call or unary fn name"
        )
        return lhs_ty

    @staticmethod
    def _piped_call(lhs: Expr, call: Call) -> Call:
        # ADR 0152: Tuple LHS + N holes → fill all holes left-to-right.
        hole_idxs = [i for i, a in enumerate(call.args) if isinstance(a, Hole)]
        if (
            hole_idxs
            and isinstance(lhs, TupleExpr)
            and len(lhs.items) == len(hole_idxs)
        ):
            it = iter(lhs.items)
            args = [next(it) if isinstance(a, Hole) else a for a in call.args]
            return Call(callee=call.callee, args=args, span=call.span)
        # ADR 0133: Call with `_` holes → fill leftmost hole; else prepend.
        if any(isinstance(a, Hole) for a in call.args):
            args: list[Expr] = []
            filled = False
            for a in call.args:
                if not filled and isinstance(a, Hole):
                    args.append(lhs)
                    filled = True
                else:
                    args.append(a)
            return Call(callee=call.callee, args=args, span=call.span)
        return Call(callee=call.callee, args=[lhs, *call.args], span=call.span)

    def _pipe_error(self, expr: Expr, message: str) -> None:
        self.diagnostics.append(
            {
                "code": "PIPE_CALLABLE_ERROR",
                "line": expr.span.line,
                "col": expr.span.col,
                "message": message,
            }
        )

    def _call_effects(self, expr: Call) -> frozenset[str]:
        if isinstance(expr.callee, Var):
            if expr.callee.name == "inspect":
                return frozenset({"Inspect"})
            return self.fun_effects.get(expr.callee.name, frozenset())
        return frozenset()

    def _check_call_effects(self, expr: Call) -> None:
        required = self._call_effects(expr)
        missing = required - self._current_effects
        if not missing:
            return
        self.diagnostics.append(
            {
                "code": "EFFECT_VIOLATION_ERROR",
                "line": expr.span.line,
                "col": expr.span.col,
                "message": (
                    "function call requires effect(s): "
                    + ", ".join(sorted(missing))
                ),
            }
        )

    def _infer_attr(self, expr: Attr) -> Ty:
        # ADR 0062: Math.pi / Math.sqrt2 / Math.inv_sqrt2 ≡ prelude classicals
        if (
            isinstance(expr.obj, Var)
            and expr.obj.name == "Math"
            and expr.name in {"pi", "sqrt2", "inv_sqrt2"}
        ):
            return Ty("Classical", "Float", DIMLESS)
        obj_ty = self._infer(expr.obj)
        # Unit suffix: 0.05.s / 1.0.kg
        if isinstance(expr.obj, (LitInt, LitFloat)) and expr.name in UNIT_TABLE:
            payload, dim = UNIT_TABLE[expr.name]
            return Ty("State", payload, dim, unit=expr.name)
        # `this.field` inside methods is same-class
        if isinstance(expr.obj, Var) and expr.obj.name == "this":
            if self._in_class is not None:
                cls = self.class_meta.get(self._in_class)
                vis = self._member_visibility(cls, expr.name)
                _ = vis  # allowed
                if cls is not None:
                    field = next(
                        (f for f in cls.members if f.name == expr.name), None
                    )
                    if field is not None:
                        return self._ty_from_ref(field.ty)
                    state_field = next(
                        (f for f in cls.fields if f.name == expr.name), None
                    )
                    if state_field is not None and state_field.ty is not None:
                        return self._ty_from_ref(state_field.ty)
            return Ty("State", obj_ty.payload, obj_ty.dim)
        self._check_external_member_access(
            obj_ty, expr.name, expr.span.line, expr.span.col
        )
        cls = self.class_meta.get(obj_ty.payload)
        if cls is not None:
            field = next((f for f in cls.members if f.name == expr.name), None)
            if field is not None:
                return self._ty_from_ref(field.ty)
            state_field = next((f for f in cls.fields if f.name == expr.name), None)
            if state_field is not None and state_field.ty is not None:
                return self._ty_from_ref(state_field.ty)
        # ADR 0174: struct field Type-First heads (Mass, Length, …).
        st = self.struct_meta.get(obj_ty.payload)
        if st is not None:
            field = next((f for f in st.fields if f.name == expr.name), None)
            if field is not None:
                return self._ty_from_ref(field.ty)
        return Ty("State", obj_ty.payload, obj_ty.dim)

    def _infer_unit_convert(self, expr: UnitConvert) -> Ty:
        """ADR 0124/0132/0134: `expr to unit` — scale or affine, same Dim."""
        inner = self._infer(expr.expr)
        target = expr.target_unit
        if target not in UNIT_TABLE:
            self.diagnostics.append(
                {
                    "code": "TYPE_MISMATCH",
                    "line": expr.span.line,
                    "col": expr.span.col,
                    "message": f"unknown target unit `{target}` for scale conversion",
                }
            )
            return inner
        target_payload, target_dim = UNIT_TABLE[target]
        if not inner.dim.matches(target_dim):
            self.diagnostics.append(
                {
                    "code": "DIMENSION_MISMATCH_ERROR",
                    "line": expr.span.line,
                    "col": expr.span.col,
                    "message": format_dim_mismatch(inner.dim, target_dim, "to"),
                }
            )
            return inner
        source_unit = None
        if isinstance(expr.expr, Attr) and expr.expr.name in UNIT_TABLE:
            source_unit = expr.expr.name
        elif inner.unit is not None:
            # ADR 0154: unit tracked through Type-First / prior `to`.
            source_unit = inner.unit
        if source_unit is None:
            # ADR 0174: dimful Classical field Attr without literal suffix —
            # allow `to` using the quantity head's canonical unit; runtime
            # still converts from the stored field unit.
            if inner.kind == "Classical" and inner.payload in QUANTITY_CANONICAL_UNIT:
                source_unit = QUANTITY_CANONICAL_UNIT[inner.payload]
        if source_unit is None:
            self.diagnostics.append(
                {
                    "code": "TYPE_MISMATCH",
                    "line": expr.span.line,
                    "col": expr.span.col,
                    "message": "unit conversion requires a known source unit suffix",
                }
            )
            return inner
        if (
            source_unit in UNIT_SCALE_TO_CANONICAL
            and target in UNIT_SCALE_TO_CANONICAL
        ):
            src_canon, src_factor = UNIT_SCALE_TO_CANONICAL[source_unit]
            tgt_canon, tgt_factor = UNIT_SCALE_TO_CANONICAL[target]
            if src_canon != tgt_canon:
                self.diagnostics.append(
                    {
                        "code": "TYPE_MISMATCH",
                        "line": expr.span.line,
                        "col": expr.span.col,
                        "message": (
                            f"cannot convert `{source_unit}` to `{target}` "
                            f"(canonical {src_canon} vs {tgt_canon})"
                        ),
                    }
                )
                return inner
            _ = src_factor / tgt_factor
            return Ty(inner.kind, target_payload, target_dim, unit=target)
        if (
            source_unit in UNIT_AFFINE_TO_CANONICAL
            and target in UNIT_AFFINE_TO_CANONICAL
        ):
            src_canon, src_scale, src_off = UNIT_AFFINE_TO_CANONICAL[source_unit]
            tgt_canon, tgt_scale, tgt_off = UNIT_AFFINE_TO_CANONICAL[target]
            if src_canon != tgt_canon:
                self.diagnostics.append(
                    {
                        "code": "TYPE_MISMATCH",
                        "line": expr.span.line,
                        "col": expr.span.col,
                        "message": (
                            f"cannot convert `{source_unit}` to `{target}` "
                            f"(affine canonical {src_canon} vs {tgt_canon})"
                        ),
                    }
                )
                return inner
            _ = (src_scale, src_off, tgt_scale, tgt_off)
            return Ty(inner.kind, target_payload, target_dim, unit=target)
        self.diagnostics.append(
            {
                "code": "TYPE_MISMATCH",
                "line": expr.span.line,
                "col": expr.span.col,
                "message": (
                    "SI conversion requires a known scale or affine pair "
                    f"(got source={source_unit!r} → {target})"
                ),
            }
        )
        return inner

    def _infer_binop(self, expr: BinOp) -> Ty:
        if expr.op in {"*", "/"} and (
            isinstance(expr.lhs, TensorExpr) or isinstance(expr.rhs, TensorExpr)
        ):
            tensor_side = expr.lhs if isinstance(expr.lhs, TensorExpr) else expr.rhs
            if not getattr(tensor_side, "_explicitly_grouped", False):
                self.diagnostics.append(
                    {
                        "code": "TENSOR_GROUPING_ERROR",
                        "line": expr.span.line,
                        "col": expr.span.col,
                        "message": (
                            "tensor product mixed with arithmetic requires explicit "
                            "parentheses"
                        ),
                    }
                )
        left = self._infer(expr.lhs)
        right = self._infer(expr.rhs)
        # A bare numeric literal defaults to State-typed sugar (`pi / 2.0`),
        # but combined with an otherwise-Classical operand it is classical
        # arithmetic, not a genuine State mix. Reinterpret the literal side
        # as Classical here, before any kind-based dispatch below, so the
        # already-correct "Classical op Classical" logic (payload/dimension
        # preservation, RELATIONAL -> Bool, &&/|| -> Bool) handles it
        # uniformly -- previously this case hardcoded every operator's
        # result to Classical<Float>, discarding the other operand's real
        # payload and dimension entirely (e.g. `Energy e; e * 2.0` lost its
        # Energy dimension), and bypassing RELATIONAL/&&/|| altogether.
        if (
            left.kind == "Classical"
            and right.kind == "State"
            and isinstance(expr.rhs, (LitInt, LitFloat))
            and right.dim.is_dimensionless()
        ):
            right = Ty("Classical", right.payload, right.dim)
        elif (
            right.kind == "Classical"
            and left.kind == "State"
            and isinstance(expr.lhs, (LitInt, LitFloat))
            and left.dim.is_dimensionless()
        ):
            left = Ty("Classical", left.payload, left.dim)
        if left.kind == "Operator" or right.kind == "Operator":
            if left.kind != "Operator" or right.kind != "Operator":
                self.diagnostics.append(
                    {
                        "code": "SECOND_QUANTIZATION_TYPE_ERROR",
                        "line": expr.span.line,
                        "col": expr.span.col,
                        "message": "second-quantized algebra cannot mix Operator and State values",
                    }
                )
                return Ty("Operator", "SecondQuantized", DIMLESS)
            left_family = left.payload.split("<", 1)[0]
            right_family = right.payload.split("<", 1)[0]
            atoms = {"SecondQuantized", "SecondQuantizedAtom"}
            if left_family not in atoms and right_family not in atoms and left_family != right_family:
                self.diagnostics.append(
                    {
                        "code": "SECOND_QUANTIZATION_TYPE_ERROR",
                        "line": expr.span.line,
                        "col": expr.span.col,
                        "message": f"cannot combine `{left_family}` with `{right_family}`",
                    }
                )
            return Ty("Operator", left.payload, DIMLESS)
        semantic_kinds = {"Meta", "Execution", "Discrete"}
        if left.kind in semantic_kinds or right.kind in semantic_kinds:
            self.diagnostics.append(
                {
                    "code": "SEMANTIC_CARRIER_OPERATION_ERROR",
                    "line": expr.span.line,
                    "col": expr.span.col,
                    "message": (
                        f"operator `{expr.op}` is not defined for semantic carriers "
                        f"`{left}` and `{right}`"
                    ),
                }
            )
            return Ty("State", "Any", DIMLESS)
        # Classical scalars (`expect`, prelude `pi`, …) must not mix into State wires
        if left.kind == "Classical" or right.kind == "Classical":
            if left.kind == "State" or right.kind == "State":
                # `pi / 2.0` / `2 * pi` with a bare dimensionless literal is
                # already reinterpreted as Classical above, so this branch
                # now only ever sees a genuine classical-scalar / quantum-
                # State mix (a non-literal State expression).
                # LISS-0133: Type-First classical quantities may scale State
                # values via * / with dimensional algebra (Never Leave the State
                # keeps the result as State — not a classical control island).
                classical = left if left.kind == "Classical" else right
                quantum = right if left.kind == "Classical" else left
                if expr.op in {"*", "/"} and (
                    not classical.dim.is_dimensionless()
                    or classical.payload
                    in ELABORATION_COEFFICIENT_HEADS
                    or classical.payload.startswith("Delta<")
                ):
                    if expr.op == "*":
                        out_dim = classical.dim.mul(quantum.dim)
                    else:
                        # classical / state or state / classical
                        if left.kind == "Classical":
                            out_dim = classical.dim.div(quantum.dim)
                        else:
                            out_dim = quantum.dim.div(classical.dim)
                    return Ty("State", quantum.payload, out_dim)
                self.diagnostics.append(
                    {
                        "code": "TYPE_MISMATCH",
                        "line": expr.span.line,
                        "col": expr.span.col,
                        "message": (
                            "cannot mix classical Float (e.g. `pi` / `expect`) "
                            f"with quantum State via `{expr.op}` "
                            "(Never Leave the State / Born-rule boundary)"
                        ),
                    }
                )
                # Legacy alias still used by SV-18 / HARD_CODES
                self.diagnostics.append(
                    {
                        "code": "EXPECT_CLASSICAL_ONLY_ERROR",
                        "line": expr.span.line,
                        "col": expr.span.col,
                        "message": (
                            "cannot mix classical scalar with quantum State "
                            f"via `{expr.op}` (Born rule / Hilbert space confusion)"
                        ),
                    }
                )
            # Classical ⊕ Classical → classical quantity with dim algebra.
            # A physical-dimension payload (Energy/Time/...) wins over a
            # bare numeric one and must survive the addition/subtraction
            # (e.g. `Energy + Energy` must stay Energy, not collapse to
            # the legacy bare-numeric "always promotes to Float" rule,
            # which still applies when neither side carries a physical
            # payload, e.g. `Int + Int`).
            if expr.op in {"+", "-"}:
                if not left.dim.matches(right.dim):
                    self._dim_error(
                        expr.span.line, expr.span.col, left.dim, right.dim, expr.op
                    )
                self._check_mixed_units(left, right, expr)
                _bare_numeric = {"Int", "Float", "Bool", "String", "Any"}
                if left.payload not in _bare_numeric:
                    payload = left.payload
                elif right.payload not in _bare_numeric:
                    payload = right.payload
                else:
                    payload = "Float"
                return Ty(
                    "Classical",
                    payload,
                    left.dim,
                    unit=self._promoted_result_unit(left, right),
                )
            if expr.op == "*":
                dim = left.dim.mul(right.dim)
                payload = _payload_for_dim(dim, _promote(left.payload, right.payload))
                return Ty("Classical", payload, dim)
            if expr.op == "/":
                dim = left.dim.div(right.dim)
                payload = _payload_for_dim(dim, _promote(left.payload, right.payload))
                return Ty("Classical", payload, dim)
            if expr.op in RELATIONAL:
                if not left.dim.matches(right.dim):
                    self._dim_error(
                        expr.span.line, expr.span.col, left.dim, right.dim, expr.op
                    )
                self._check_mixed_units(left, right, expr)
                return Ty("Classical", "Bool", DIMLESS)
            if expr.op in {"&&", "||"}:
                # ADR 0196: total-pushforward Boolean combinators -- both
                # operands must already be Bool, no implicit truthiness
                # coercion from other classical types.
                if left.payload != "Bool" or right.payload != "Bool":
                    self.diagnostics.append(
                        {
                            "code": "TYPE_MISMATCH",
                            "line": expr.span.line,
                            "col": expr.span.col,
                            "message": (
                                f"`{expr.op}` requires two Bool operands, got "
                                f"`{left.payload}` and `{right.payload}`"
                            ),
                        }
                    )
                return Ty("Classical", "Bool", DIMLESS)
            return Ty("Classical", "Float", DIMLESS)
        if expr.op in RELATIONAL:
            # Both sides must match; one-sided dimensionless bypass is banned
            if not left.dim.matches(right.dim):
                self._dim_error(
                    expr.span.line, expr.span.col, left.dim, right.dim, expr.op
                )
            self._check_mixed_units(left, right, expr)
            return Ty("State", "Bool", DIMLESS)
        if expr.op in {"&&", "||"}:
            # ADR 0196: total-pushforward Boolean combinators -- both
            # operands must already be Bool, no implicit truthiness
            # coercion from other State-carrier types.
            if left.payload != "Bool" or right.payload != "Bool":
                self.diagnostics.append(
                    {
                        "code": "TYPE_MISMATCH",
                        "line": expr.span.line,
                        "col": expr.span.col,
                        "message": (
                            f"`{expr.op}` requires two Bool operands, got "
                            f"`{left.payload}` and `{right.payload}`"
                        ),
                    }
                )
            return Ty("State", "Bool", DIMLESS)
        if expr.op in {"+", "-"}:
            if not left.dim.matches(right.dim):
                self._dim_error(
                    expr.span.line, expr.span.col, left.dim, right.dim, expr.op
                )
            self._check_mixed_units(left, right, expr)
            payload = _promote(left.payload, right.payload)
            # Prefer dimensioned payload name when present
            if not left.dim.is_dimensionless():
                payload = left.payload if left.payload not in {"Int", "Float", "Any"} else right.payload
            return Ty(
                "State",
                payload,
                left.dim,
                unit=self._promoted_result_unit(left, right),
            )
        if expr.op == "*":
            dim = left.dim.mul(right.dim)
            payload = _payload_for_dim(dim, _promote(left.payload, right.payload))
            return Ty("State", payload, dim)
        if expr.op == "/":
            dim = left.dim.div(right.dim)
            payload = _payload_for_dim(dim, _promote(left.payload, right.payload))
            return Ty("State", payload, dim)
        return Ty("State", "Any", DIMLESS)

    def _check_mixed_units(self, left: Ty, right: Ty, expr: BinOp) -> None:
        """ADR 0155: mixed units ok iff they share a canonical family; else error."""
        from .dimensions import unit_canonical

        if left.unit is None or right.unit is None:
            return
        if left.unit == right.unit:
            return
        lc = unit_canonical(left.unit)
        rc = unit_canonical(right.unit)
        if lc is not None and lc == rc:
            return
        self.diagnostics.append(
            {
                "code": "UNIT_MIXED_ARITHMETIC_ERROR",
                "line": expr.span.line,
                "col": expr.span.col,
                "message": (
                    f"cannot apply `{expr.op}` to incompatible units "
                    f"`{left.unit}` and `{right.unit}` "
                    "(no shared canonical; ADR 0155)"
                ),
            }
        )

    @staticmethod
    def _promoted_result_unit(left: Ty, right: Ty) -> str | None:
        """ADR 0155 promote + ADR 0186: mixed shared-family → LHS display unit."""
        from .dimensions import unit_canonical

        if left.unit and right.unit:
            if left.unit == right.unit:
                return left.unit
            lc = unit_canonical(left.unit)
            rc = unit_canonical(right.unit)
            if lc is not None and lc == rc:
                return left.unit
            return None
        if left.unit and right.unit is None:
            return left.unit
        if right.unit and left.unit is None:
            return right.unit
        return None

    def _infer_call(self, expr: Call) -> Ty:
        # Math.sin(x) / sin(x) / cis(theta): argument must be dimensionless
        op_name = _call_op_name(expr)
        self._check_call_effects(expr)
        if (
            op_name == "tomography"
            and isinstance(expr.callee, Var)
            and op_name not in self.fun_returns
        ):
            for arg in expr.args:
                self._infer(arg)
            self.diagnostics.append(
                {
                    "code": "OBSERVATION_CAPABILITY_UNSUPPORTED",
                    "line": expr.span.line,
                    "col": expr.span.col,
                    "message": (
                        "`tomography` is a Host observation protocol and is "
                        "not executable in the Static Kernel lane"
                    ),
                }
            )
            return Ty("Host", "ObservationReport", DIMLESS)
        if op_name == "tensor":
            if len(expr.args) != 2:
                self.diagnostics.append(
                    {
                        "code": "TENSOR_ARITY_ERROR",
                        "line": expr.span.line,
                        "col": expr.span.col,
                        "message": (
                            "tensor requires exactly two arguments; use explicit "
                            "nesting for three or more factors"
                        ),
                    }
                )
                for arg in expr.args:
                    self._infer(arg)
                return Ty("State", "Any", DIMLESS)
            left = self._infer(expr.args[0])
            right = self._infer(expr.args[1])
            return Ty(
                "State",
                product_payload([left.payload, right.payload]),
                DIMLESS,
            )
        if op_name in self.interface_names:
            self.diagnostics.append(
                {
                    "code": "SYSTEM_EXPRESSION_ERROR",
                    "line": expr.span.line,
                    "col": expr.span.col,
                    "message": "interfaces, including `System`, are not value constructors",
                }
            )
            return Ty("State", "Any", DIMLESS)
        if op_name in {"create", "annihilate", "spin_raise", "spin_lower"}:
            for arg in expr.args:
                self._infer(arg)
            return Ty("Operator", "SecondQuantizedAtom", DIMLESS)
        if op_name == "map":
            for arg in expr.args:
                self._infer(arg)
            return Ty("Operator", "QubitOperator<Qubits>", DIMLESS)
        if op_name in {"adjoint", "outer", "projector", "commutator", "anticommutator"}:
            return self._check_algebra_call(expr)
        if op_name == "inner":
            return self._check_algebra_call(expr)
        if isinstance(expr, Call) and self._is_qft_call(expr):
            # LISS-0220: the QFT family yields an Operator over the register it
            # acts on. Without this branch the call fell through to the
            # `State` catch-all at the end of this method, so any analysis
            # reading `TypeChecker.typed` saw an Operator as quantum state.
            # `_check_qft_call` already validates register shape and budget.
            for arg in expr.args:
                self._infer(arg)
            return Ty("Operator", "Qubit", DIMLESS)
        if op_name == "system":
            return Ty("Register", "Qubit", DIMLESS)
        if op_name == "parameter":
            return Ty("Param", "Any", DIMLESS)
        if op_name == "ComputationalBasis":
            return Ty("POVM", "Qubit", DIMLESS)
        if op_name == "apply" and expr.args:
            operator_arg = expr.args[0]
            allow_mvp_d3 = self._expr_is_identity_atom(operator_arg)
            if isinstance(operator_arg, Var):
                operator_ty = self.env.get(operator_arg.name)
                if (
                    operator_ty is None
                    and operator_arg.name not in _PAULI_ATOM_NAMES
                ) or (operator_ty is not None and operator_ty.kind != "Operator"):
                    self.diagnostics.append(
                        {
                            "code": "LEXICAL_SCOPE_ERROR",
                            "line": operator_arg.span.line,
                            "col": operator_arg.span.col,
                            "message": (
                                f"Operator `{operator_arg.name}` is not in the current scope; "
                                "pass it as a parameter or return it explicitly"
                            ),
                        }
                    )
                elif operator_ty is not None:
                    self._check_unsupported_qudit_runtime_ty(
                        operator_ty, expr.span.line, expr.span.col
                    )
            for state_arg in expr.args[1:]:
                self._check_unsupported_qudit_runtime_ty(
                    self._infer(state_arg),
                    expr.span.line,
                    expr.span.col,
                    allow_mvp_d3=allow_mvp_d3,
                )
        if op_name == "index" and expr.args:
            arg = expr.args[0]
            if isinstance(arg, Var) and self.env.get(arg.name, Ty("State", "Any")).kind == "Wire":
                self.diagnostics.append(
                    {
                        "code": "QPU_CLASSICAL_CONTROL_ERROR",
                        "line": arg.span.line,
                        "col": arg.span.col,
                        "message": "a `forEach` element handle cannot become a classical index",
                    }
                )
            return Ty("Meta", "Index", DIMLESS)
        if op_name == "basis":
            return Ty("Discrete", "Basis", DIMLESS)
        for a in expr.args:
            if isinstance(a, Hole):
                continue
            at = self._infer(a)
            if op_name in TRIG_AND_TRANS and not at.dim.is_dimensionless():
                self.diagnostics.append(
                    {
                        "code": "DIMENSION_MISMATCH_ERROR",
                        "line": expr.span.line,
                        "col": expr.span.col,
                        "message": (
                            f"`{op_name}` requires a dimensionless argument, got {at.dim}"
                        ),
                    }
                )
        if isinstance(expr.callee, Attr):
            recv = self._infer(expr.callee.obj)
            if not (isinstance(expr.callee.obj, Var) and expr.callee.obj.name == "this"):
                self._check_external_member_access(
                    recv,
                    expr.callee.name,
                    expr.span.line,
                    expr.span.col,
                )
        elif not isinstance(expr.callee, Var):
            self._infer(expr.callee)
        # ADR 0123 / 0131: Call on a bound Partial fills holes left-to-right.
        if isinstance(expr.callee, Var):
            partial_ty = self.env.get(expr.callee.name)
            if partial_ty is not None and partial_ty.kind == "Partial":
                fun_name, _, hole_s = partial_ty.payload.partition("#")
                try:
                    need = int(hole_s)
                except ValueError:
                    need = -1
                n_args = len(expr.args)
                if n_args == 0 or n_args > need:
                    self.diagnostics.append(
                        {
                            "code": "FUNCTION_ARITY_ERROR",
                            "line": expr.span.line,
                            "col": expr.span.col,
                            "message": (
                                f"Partial `{expr.callee.name}` expects 1..{need} "
                                f"remaining args, got {n_args}"
                            ),
                        }
                    )
                for arg in expr.args:
                    if isinstance(arg, Hole):
                        self.diagnostics.append(
                            {
                                "code": "PARSE_ERROR",
                                "line": arg.span.line,
                                "col": arg.span.col,
                                "message": (
                                    "nested Partial holes on Partial calls "
                                    "are not in this ADR slice"
                                ),
                            }
                        )
                    else:
                        self._infer(arg)
                if 0 < n_args < need:
                    # ADR 0131: stepwise fill → smaller Partial.
                    return Ty("Partial", f"{fun_name}#{need - n_args}", DIMLESS)
                if fun_name in self.fun_returns:
                    return self.fun_returns[fun_name][1]
                return Ty("State", "Any", DIMLESS)
        if isinstance(expr.callee, Var) and expr.callee.name in self.fun_returns:
            fun, result_ty = self.fun_returns[expr.callee.name]
            hole_count = sum(1 for arg in expr.args if isinstance(arg, Hole))
            if hole_count:
                if len(expr.args) != len(fun.params):
                    self.diagnostics.append(
                        {
                            "code": "FUNCTION_ARITY_ERROR",
                            "line": expr.span.line,
                            "col": expr.span.col,
                            "message": (
                                f"`{fun.name}` Partial expects {len(fun.params)} "
                                f"argument slots, got {len(expr.args)}"
                            ),
                        }
                    )
                for arg in expr.args:
                    if not isinstance(arg, Hole):
                        self._infer(arg)
                if self._call_effects(expr):
                    self.diagnostics.append(
                        {
                            "code": "PIPE_EFFECT_ERROR",
                            "line": expr.span.line,
                            "col": expr.span.col,
                            "message": "effectful functions cannot form Partial values",
                        }
                    )
                # Payload encodes callee + remaining holes for pipe checks.
                return Ty("Partial", f"{fun.name}#{hole_count}", DIMLESS)
            if len(expr.args) != len(fun.params):
                self.diagnostics.append(
                    {
                        "code": "FUNCTION_ARITY_ERROR",
                        "line": expr.span.line,
                        "col": expr.span.col,
                        "message": (
                            f"`{fun.name}` expects {len(fun.params)} args, "
                            f"got {len(expr.args)}"
                        ),
                    }
                )
            return result_ty
        if isinstance(expr.callee, Attr):
            recv_ty = self._infer(expr.callee.obj)
            cls = self.class_meta.get(recv_ty.payload)
            if cls is not None:
                method = next(
                    (m for m in cls.methods if m.name == expr.callee.name), None
                )
                if method is not None and method.return_type is not None:
                    if len(expr.args) != len(method.params):
                        self.diagnostics.append(
                            {
                                "code": "FUNCTION_ARITY_ERROR",
                                "line": expr.span.line,
                                "col": expr.span.col,
                                "message": (
                                    f"`{method.name}` expects {len(method.params)} args, "
                                    f"got {len(expr.args)}"
                                ),
                            }
                        )
                    return self._ty_from_ref(method.return_type)
        # phase(src, theta): theta dimensionless
        if op_name == "phase" and len(expr.args) >= 2:
            th = self._infer(expr.args[1])
            if not th.dim.is_dimensionless():
                self.diagnostics.append(
                    {
                        "code": "DIMENSION_MISMATCH_ERROR",
                        "line": expr.span.line,
                        "col": expr.span.col,
                        "message": f"`phase` angle must be dimensionless, got {th.dim}",
                    }
                )
            if expr.args:
                return self._infer(expr.args[0])
        if op_name == "dirac" and expr.args:
            return self._infer(expr.args[0])
        if op_name == "controlled":
            # Coherent control is a state-preserving operation, distinct from
            # the probabilistic `mix` composition surface.
            for arg in expr.args:
                self._infer(arg)
            return Ty("State", "Any", DIMLESS)
        if op_name == "finiteize":
            # ADR 0185 Lane A: Host histogram → finite State (not Continuous)
            return Ty("State", "Any", DIMLESS)
        if op_name == "expect":
            # ⟨O⟩ is a classical scalar — not a quantum State coordinate
            return Ty("Classical", "Float", DIMLESS)
        if op_name == "inspect":
            # ADR 0189: an inspection view is diagnostic, never a State or
            # terminal measurement result.
            return Ty("DiagnosticView", "Any", DIMLESS)
        if op_name == "occupation":
            # |⟨k|ψ⟩|² Born weight — classical Float
            return Ty("Classical", "Float", DIMLESS)
        if op_name == "converged":
            if expr.args and isinstance(expr.args[0], Var):
                return Ty("Classical", "Bool", DIMLESS)
            return Ty("Classical", "Bool", DIMLESS)
        if op_name == "trace_out":
            # Discard named subsystem; remaining joint stays State (placeholder bind)
            if expr.args and isinstance(expr.args[0], Var):
                traced = expr.args[0].name
                # Drop traced coordinate from env knowledge for subsequent use
                # (bind name is Classical placeholder; other coords keep types)
                _ = traced
            return Ty("State", "Any", DIMLESS)
        if op_name == "register":
            return Ty("Register", "Qubit", DIMLESS)
        return Ty("State", "Any", DIMLESS)

    def _infer_evolve(self, expr: EvolveExpr) -> Ty:
        allow_mvp_d3 = (
            expr.hamiltonian is not None
            and self._expr_is_identity_atom(expr.hamiltonian)
        )
        seed_tys = [self._infer(s) for s in expr.seeds]
        for seed_ty in seed_tys:
            self._check_unsupported_qudit_runtime_ty(
                seed_ty,
                expr.span.line,
                expr.span.col,
                allow_mvp_d3=allow_mvp_d3,
            )
        if expr.suzuki is not None:
            self._check_suzuki_policy(expr.suzuki)
        if expr.until_predicate is not None:
            self._check_evolve_until_contract(expr)
        if expr.hamiltonian is not None:
            hamiltonian_ty = self._infer(expr.hamiltonian)
            self._check_unsupported_qudit_runtime_ty(
                hamiltonian_ty, expr.span.line, expr.span.col
            )
            if expr.duration is not None:
                dt = self._infer(expr.duration)
                # Same rule as block evolve: Time / Delta<Time> / dimensionless phase
                if not (
                    dt.dim.matches(Dim(T=1))
                    or dt.dim.is_dimensionless()
                ):
                    self.diagnostics.append(
                        {
                            "code": "DIMENSION_MISMATCH_ERROR",
                            "line": expr.span.line,
                            "col": expr.span.col,
                            "message": (
                                f"`evolve … under H for` expects Time / Delta<Time> "
                                f"(or dimensionless angle), got {dt.dim}"
                            ),
                        }
                    )
            # Schrödinger evolve preserves qubit State payload
            return seed_tys[0] if seed_tys else Ty("State", "Int", DIMLESS)
        if expr.duration is not None:
            dt = self._infer(expr.duration)
            # Delta<Time> / Time / dimensionless step count
            if not (
                dt.dim.matches(Dim(T=1))
                or dt.dim.is_dimensionless()
            ):
                self.diagnostics.append(
                    {
                        "code": "DIMENSION_MISMATCH_ERROR",
                        "line": expr.span.line,
                        "col": expr.span.col,
                        "message": (
                            f"`evolve … for` expects Time / Delta<Time> "
                            f"(or dimensionless steps), got {dt.dim}"
                        ),
                    }
                )
        if expr.body is None:
            return seed_tys[0] if seed_tys else Ty("State", "Any", DIMLESS)
        for let in expr.body.lets:
            self.env[let.name] = self._infer(let.expr)
        return self._infer(expr.body.result)

    def _static_scalar_value(self, expr: Expr) -> float | None:
        """Resolve a classical scalar expression at typecheck time (LISS-0371).

        Covers literals and named classical constants already tracked in
        `self.static_scalars`; any other shape is not a closed value yet
        (mirrors the fail-closed stance of the runtime `_eval_float`
        resolver in `backend/qasm/trotter.py`, but at typecheck time).
        """
        if isinstance(expr, LitInt):
            return float(expr.value)
        if isinstance(expr, LitFloat):
            return float(expr.value)
        if isinstance(expr, Var):
            return self.static_scalars.get(expr.name)
        return None

    def _check_suzuki_policy(self, policy) -> None:
        """Validate the static S2/S4 lowering policy accepted by ADR 0084."""
        order_ok = isinstance(policy.order, LitInt) and policy.order.value in {2, 4}
        if not order_ok:
            resolved_order = self._static_scalar_value(policy.order)
            order_ok = resolved_order is not None and int(resolved_order) in {2, 4}
        if not order_ok:
            self.diagnostics.append(
                {
                    "code": "SUZUKI_ORDER_ERROR",
                    "line": policy.span.line,
                    "col": policy.span.col,
                    "message": "Suzuki supports order 2 or 4",
                }
            )
        if policy.steps is not None and policy.tolerance is not None:
            self.diagnostics.append(
                {
                    "code": "SUZUKI_POLICY_ERROR",
                    "line": policy.span.line,
                    "col": policy.span.col,
                    "message": "Suzuki `steps` and `tolerance` are mutually exclusive",
                }
            )
        if policy.steps is None and policy.tolerance is None:
            self.diagnostics.append(
                {
                    "code": "SUZUKI_POLICY_ERROR",
                    "line": policy.span.line,
                    "col": policy.span.col,
                    "message": "Suzuki requires either `steps` or `tolerance`",
                }
            )
        if policy.steps is not None:
            if not isinstance(policy.steps, LitInt) or policy.steps.value <= 0:
                self.diagnostics.append(
                    {
                        "code": "SUZUKI_POLICY_ERROR",
                        "line": policy.span.line,
                        "col": policy.span.col,
                        "message": "Suzuki `steps` must be a positive integer",
                    }
                )
            if policy.error_mode is not None:
                self.diagnostics.append(
                    {
                        "code": "SUZUKI_POLICY_ERROR",
                        "line": policy.span.line,
                        "col": policy.span.col,
                        "message": "Suzuki `error` is allowed only with `tolerance`",
                    }
                )
        if policy.tolerance is not None:
            if not isinstance(policy.tolerance, (LitInt, LitFloat)) or policy.tolerance.value <= 0:
                self.diagnostics.append(
                    {
                        "code": "SUZUKI_POLICY_ERROR",
                        "line": policy.span.line,
                        "col": policy.span.col,
                        "message": "Suzuki `tolerance` must be positive",
                    }
                )
            if policy.error_mode not in {"Bound", "EmpiricalEstimate"}:
                self.diagnostics.append(
                    {
                        "code": "SUZUKI_POLICY_ERROR",
                        "line": policy.span.line,
                        "col": policy.span.col,
                        "message": "Suzuki tolerance requires `Bound` or `EmpiricalEstimate`",
                    }
                )

    def _check_evolve_until_contract(self, expr: EvolveExpr) -> None:
        """Validate the pure bounded Kernel termination contract."""
        if not (isinstance(expr.max_steps, LitInt) and expr.max_steps.value > 0):
            self.diagnostics.append(
                {
                    "code": "EVOLVE_UNTIL_BOUND_ERROR",
                    "line": expr.span.line,
                    "col": expr.span.col,
                    "message": "evolve until requires a positive literal `max` bound",
                }
            )
        if isinstance(expr.until_predicate, MeasureExpr):
            self.diagnostics.append(
                {
                    "code": "EVOLVE_UNTIL_EFFECT_ERROR",
                    "line": expr.until_predicate.span.line,
                    "col": expr.until_predicate.span.col,
                    "message": "evolve until predicates cannot measure or consume RNG",
                }
            )
        self._infer(expr.until_predicate)


def _call_op_name(expr: Call) -> str:
    from .ast_nodes import Attr, Var

    cal = expr.callee
    if isinstance(cal, Var):
        return cal.name
    if isinstance(cal, Attr):
        return cal.name
    return ""


def _payload_for_dim(dim: Dim, fallback: str) -> str:
    if dim.is_dimensionless():
        return fallback if fallback in {"Int", "Float", "Any"} else "Float"
    for name, d in TYPE_DIMS.items():
        if name in {"Int", "Float", "Bool", "String", "Any", "Angle", "Dimensionless"}:
            continue
        if d.matches(dim):
            return name
    return fallback


def _promote(a: str, b: str) -> str:
    if a == b:
        return a
    if {a, b} <= {"Int", "Float"}:
        return "Float"
    if a == "Any":
        return b
    if b == "Any":
        return a
    # Prefer physical payload over numeric
    if a in TYPE_DIMS and a not in {"Int", "Float", "Bool", "String", "Any"}:
        return a
    if b in TYPE_DIMS and b not in {"Int", "Float", "Bool", "String", "Any"}:
        return b
    return "Any"


def assert_expr_is_state(checker: TypeChecker, expr: Expr) -> bool:
    """Helper for harness assertTypeIsState against typed AST."""
    ty = checker.type_of(expr) or checker._infer(expr)
    return ty.kind == "State"


def lit_lift_demo(value: Any) -> Ty:
    if isinstance(value, bool):
        return Ty("State", "Bool", DIMLESS)
    if isinstance(value, int):
        return Ty("State", "Int", DIMLESS)
    if isinstance(value, float):
        return Ty("State", "Float", DIMLESS)
    if isinstance(value, str):
        return Ty("State", "String", DIMLESS)
    return Ty("State", "Any", DIMLESS)
