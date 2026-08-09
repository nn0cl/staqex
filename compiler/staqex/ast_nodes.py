"""Staqex AST nodes (design baseline subset for Phase 2.1)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Union

# Modern visibility (ADR 0058 revised):
#   public  — `pub` (cross-module API; semantic AST spelling)
#   module  — default (same compilation module only)
#   private — leading `_` or legacy `private` keyword (class / same-file)
# Legacy alias: "package" is treated as "module" by access checks.
Visibility = Literal["public", "module", "private", "package"]


@dataclass
class Span:
    line: int
    col: int


# --- Expressions ---


@dataclass
class LitInt:
    value: int
    span: Span


@dataclass
class LitFloat:
    value: float
    span: Span


@dataclass
class LitBool:
    value: bool
    span: Span


@dataclass
class LitString:
    value: str
    span: Span


@dataclass
class Var:
    name: str
    span: Span


@dataclass
class Coin:
    span: Span


@dataclass
class Dirac:
    arg: "Expr"
    span: Span


@dataclass
class KetLit:
    """Dirac ket literal: `|0>`, `|+>`, `|01>`, … (ADR 0038)."""

    label: str
    span: Span


@dataclass
class BraLit:
    """Dirac bra literal: `<0|`, `<+|`, … (ASCII source form)."""

    label: str
    span: Span


@dataclass
class Vacuum:
    span: Span


@dataclass
class BinOp:
    op: str  # + - * / == != < <= > >=
    lhs: "Expr"
    rhs: "Expr"
    span: Span


@dataclass
class Call:
    callee: "Expr"
    args: list["Expr"]
    span: Span
    # ADR 0181: named struct fields `Type { a: e, b: f }` (and optional Call kwargs).
    kwargs: list[tuple[str, "Expr"]] | None = None


@dataclass
class WhenArm:
    pat: Any  # literal value or None for else
    body: "Expr"
    is_else: bool = False


@dataclass
class WhenExpr:
    ctrl: "Expr"
    arms: list[WhenArm]
    span: Span


@dataclass
class SuperposeArm:
    """LISS-0320: coherent-lane arm, structurally parallel to `WhenArm` but
    never unioned with it — `superpose` is not `mix`."""

    pat: Any  # literal value or None for else
    body: "Expr"
    is_else: bool = False


@dataclass
class SuperposeExpr:
    """LISS-0320: `superpose (control) { pat -> expr, … }` ordinary-surface
    grammar. Distinct from `WhenExpr` (mix) and from the shallow
    `H1Superposition` H1-authoring heuristic (PR #344)."""

    ctrl: "Expr"
    arms: list[SuperposeArm]
    span: Span


@dataclass
class Pipe:
    lhs: "Expr"
    rhs: "Expr"
    span: Span


@dataclass
class Lambda:
    """Unary fn sugar: `x -> expr` (map / project)."""

    param: str
    body: "Expr"
    span: Span


@dataclass
class Attr:
    """Attribute / static path segment: `Math.sin` or `x.inspect`."""

    obj: "Expr"
    name: str
    span: Span


@dataclass
class Hole:
    """Partial-application hole `_` in a call argument list (ADR 0123)."""

    span: Span


@dataclass
class UnitConvert:
    """Explicit SI scale conversion `expr to unit` (ADR 0124)."""

    expr: "Expr"
    target_unit: str
    span: Span


@dataclass
class Inspect:
    """Non-destructive debug view (ADR 0030); identity on joint."""

    expr: "Expr"
    label: str | None
    span: Span


@dataclass
class TupleExpr:
    """Product / simultaneous values: (x, p)."""

    items: list["Expr"]
    span: Span


@dataclass
class BlockExpr:
    """Bare `{ let …; result }` expression (ADR 0153 Trace-Out GC)."""

    lets: list["LetBind"]
    result: "Expr"
    span: Span


@dataclass
class ListExpr:
    """Explicit list value used by numeric domain constructors."""

    items: list["Expr"]
    span: Span


@dataclass
class LetBind:
    """`let name = expr` inside evolve body."""

    name: str
    expr: "Expr"
    span: Span


@dataclass
class EvolveBody:
    lets: list[LetBind]
    result: "Expr"
    span: Span


@dataclass
class SuzukiPolicy:
    """Static QASM lowering policy for `using Suzuki(...)`."""

    order: "Expr"
    steps: "Expr | None"
    tolerance: "Expr | None"
    error_mode: str | None
    span: Span


@dataclass
class EvolveExpr:
    """Block evolve or Hamiltonian `evolve psi under H for t` (ADR 0038)."""

    seeds: list["Expr"]
    times: "Expr | int"  # Expr after ADR 0060; int kept for under/for default
    body: EvolveBody | None
    span: Span
    duration: "Expr | None" = None
    hamiltonian: "Expr | None" = None  # set for `under H`
    until_predicate: "Expr | None" = None
    max_steps: "Expr | None" = None
    suzuki: SuzukiPolicy | None = None


@dataclass
class OpPauli:
    """Pauli atom: `X` / `Z(1)` inside Operator expressions."""

    kind: str  # I X Y Z
    site: int | None  # None → single-qubit / global
    span: Span


@dataclass
class OpNumber:
    """Number operator N on Fock levels."""

    span: Span


@dataclass
class OpQuadrature:
    """Position/momentum in truncated Fock: Q, P (ℏ=m=ω=1)."""

    kind: str  # Q | P
    span: Span


@dataclass
class OpGridQuad:
    """Deprecated alias node — grid uses bare X/P via context (ADR 0053)."""

    kind: str  # Xx | Px (legacy parse only)
    span: Span


@dataclass
class OpLit:
    """Scalar coefficient in an operator polynomial (multiplies identity)."""

    value: float
    span: Span


@dataclass
class OpIdentity:
    """Internal identity for an empty sum/product fold."""

    kind: str  # sum = additive zero, product = multiplicative identity
    acting_space: int | None
    span: Span


@dataclass
class OpBin:
    op: str  # + - *
    lhs: "OpExpr"
    rhs: "OpExpr"
    span: Span


@dataclass
class OpPow:
    base: "OpExpr"
    exp: int
    span: Span


@dataclass
class OpHop:
    """Tight-binding matrix unit `|i⟩⟨j|` on a discrete site basis (SSH / TB)."""

    i: int
    j: int
    span: Span


@dataclass
class OpVar:
    """Reference to a bound Operator name or elaboration coefficient."""

    name: str
    span: Span


@dataclass
class OpAttr:
    """Field projection in OpDSL, e.g. ``couplings.h_x * X`` (LISS-0121 / ADR 0114)."""

    obj: "OpExpr"
    name: str
    span: Span


@dataclass
class OpCall:
    """Pure symbolic operator helper call, e.g. `next(i)` or `wrap(i)`."""

    name: str
    args: list["OpExpr"]
    span: Span


@dataclass
class OpIndexed:
    """Indexed symbolic operator access, e.g. `Z[i]`."""

    base: "OpExpr"
    index: "OpExpr"
    span: Span


@dataclass
class BinderOrigin:
    """Source provenance for a binder normalized from a surface head."""

    source_span: Span
    variables: tuple[str, ...]
    desugared: bool


@dataclass
class OpBinder:
    """Finite mathematical binder retained before resolution/lowering."""

    kind: str  # sum | product
    variable: str
    domain: "OpExpr | TypeRef | IndexDomain | RevDomain"
    body: "OpExpr"
    span: Span
    guard: "OpExpr | None" = None
    origin: BinderOrigin | None = None


OpExpr = Union[
    OpPauli,
    OpNumber,
    OpQuadrature,
    OpGridQuad,
    OpHop,
    OpLit,
    OpIdentity,
    OpBin,
    OpPow,
    OpVar,
    OpAttr,
    OpCall,
    OpIndexed,
    OpBinder,
]


@dataclass
class TensorExpr:
    """State tensor product: `a *|* b` or `tensor(a, b)`."""

    left: "Expr"
    right: "Expr"
    span: Span


@dataclass
class UnaryNot:
    """Open-control polarity: `!c` in `capply(c0, !c1, X, t)` (ADR 0048)."""

    expr: "Expr"
    span: Span


@dataclass
class MeasureExpr:
    """Measurement syntax encountered where an expression is required.

    It is retained only to produce a precise early-collapse diagnostic; it is
    never a valid runtime expression in the Kernel.
    """

    expr: "Expr"
    span: Span


@dataclass
class TypeRef:
    name: str
    args: list["TypeRef"] = field(default_factory=list)

    @property
    def is_inclusive_range(self) -> bool:
        return self.name == "Index" and len(self.args) == 2


@dataclass
class IndexDomain:
    """Inclusive Index<a..b> with static endpoint expressions (ADR 0117)."""

    start: "OpExpr"
    end: "OpExpr"
    span: Span


@dataclass
class RevDomain:
    """Descending enumeration wrapper `rev(D)` (ADR 0117 D5)."""

    inner: "TypeRef | IndexDomain | RevDomain"
    span: Span


Expr = Union[
    LitInt,
    LitFloat,
    LitBool,
    LitString,
    Var,
    Coin,
    Dirac,
    KetLit,
    BraLit,
    Vacuum,
    BinOp,
    Call,
    WhenExpr,
    SuperposeExpr,
    Pipe,
    Lambda,
    Attr,
    Hole,
    UnitConvert,
    Inspect,
    TupleExpr,
    BlockExpr,
    ListExpr,
    EvolveExpr,
    TensorExpr,
    UnaryNot,
    MeasureExpr,
]


# --- Statements / decls ---


@dataclass
class StateBind:
    """`state x = e`, Type-First `Mass m = e` / `Operator H = …`, or `(x, p) = e`.

    ADR 0115: when ``via_state_keyword`` is True and ``ty`` is set, the source
    was ``state name: State<…> = e`` (colon annotation on the ``state`` form).
    """

    names: list[str]
    expr: Any  # Expr | OpExpr
    span: Span
    ty: TypeRef | None = None  # Type-First head or state annotation; None for inferred `state` / bare tuple
    visibility: Visibility = "module"
    via_state_keyword: bool = False

    @property
    def name(self) -> str:
        return self.names[0]


@dataclass
class Measure:
    expr: Expr
    span: Span
    sink: str | None = None
    povm: Expr | None = None
    # ADR 0173: leftover linear carriers discarded via Born partial trace.
    tracing_out: list[str] = field(default_factory=list)


@dataclass
class Snapshot:
    expr: Expr
    sink: str
    span: Span


@dataclass
class ReturnStmt:
    """Terminal explicit result of an ordinary function or method."""

    expr: Expr
    span: Span


@dataclass
class ExprStmt:
    """A side-effect-free Kernel operation statement such as `apply(...)`."""

    expr: Expr
    span: Span


@dataclass
class ForEachStmt:
    """Static circuit elaboration over a finite register/wire collection."""

    element: str
    collection: Expr
    body: "Block"
    span: Span


@dataclass
class DynamicQpuStmt:
    """Explicit future dynamic-QPU lane; currently rejected at the boundary."""

    body: "Block"
    span: Span
    # ADR 0193 / LISS-0381: optional `dynamic qpu within <name>` timing intent.
    timing_intent: str | None = None


@dataclass
class MatchArm:
    """One finite feed-forward arm: `<pattern> => { … }` (ADR 0197)."""

    pattern: str
    body: "Block"
    span: Span


@dataclass
class MatchStmt:
    """Lane-local finite `match` over a Controller token (ADR 0197 / LISS-0382).

    `match` is a contextual soft keyword (not a global hard keyword).
    """

    scrutinee: str
    arms: list[MatchArm]
    span: Span


Stmt = Union[
    StateBind,
    Measure,
    Snapshot,
    ReturnStmt,
    ExprStmt,
    ForEachStmt,
    DynamicQpuStmt,
    MatchStmt,
]


@dataclass
class Block:
    stmts: list[Stmt]
    span: Span
    # Compatibility field for consumers that inspect the terminal result.
    # New source must represent it with a ReturnStmt.
    result: Expr | None = None


@dataclass
class Param:
    name: str
    ty: TypeRef | None


@dataclass
class MainDecl:
    params: list[Param]
    body: Block
    span: Span
    return_type: TypeRef | None = None


@dataclass
class FieldDecl:
    """`val name: Type [= expr]` / `var name: Type [= expr]` (ADR 0056 OOP)."""

    name: str
    ty: TypeRef
    mutable: bool
    default: "Expr | None"
    span: Span
    visibility: Visibility = "module"


@dataclass
class EnumDecl:
    """`enum BoundaryCondition { Periodic, Open }` (ADR 0055/0056 OOP)."""

    name: str
    variants: list[str]
    span: Span
    namespace: list[str] = field(default_factory=list)
    visibility: Visibility = "module"

    @property
    def qualified_name(self) -> str:
        if self.namespace:
            return ".".join([*self.namespace, self.name])
        return self.name


@dataclass
class StructDecl:
    """`struct SSHParams { val v: Energy, val w: Energy }` — immutable value type."""

    name: str
    fields: list[FieldDecl]
    span: Span
    namespace: list[str] = field(default_factory=list)
    visibility: Visibility = "module"

    @property
    def qualified_name(self) -> str:
        if self.namespace:
            return ".".join([*self.namespace, self.name])
        return self.name


@dataclass
class AssignStmt:
    """`this.field = expr` or `obj.field = expr` (mutable `var` only)."""

    target: "Expr"  # Attr
    value: "Expr"
    span: Span


@dataclass
class ClassDecl:
    name: str
    ifaces: list[str]
    span: Span
    fields: list[StateBind] = field(default_factory=list)  # Type-First
    members: list[FieldDecl] = field(default_factory=list)  # val/var :
    methods: list[FunDecl] = field(default_factory=list)
    namespace: list[str] = field(default_factory=list)  # ADR 0055
    visibility: Visibility = "module"

    @property
    def qualified_name(self) -> str:
        if self.namespace:
            return ".".join([*self.namespace, self.name])
        return self.name


@dataclass
class NamespaceDecl:
    """`namespace A.B { … }` (ADR 0055). Flattened before typecheck/eval."""

    path: list[str]
    decls: list[Any]
    span: Span


@dataclass
class InterfaceDecl:
    name: str
    span: Span
    type_params: tuple[str, ...] = ()


@dataclass
class ImplDecl:
    interface: TypeRef
    target: TypeRef
    methods: list[FunDecl]
    span: Span


@dataclass
class FunDecl:
    name: str
    params: list[Param]
    body: Block
    span: Span
    return_type: TypeRef | None = None
    visibility: Visibility = "module"
    namespace: list[str] = field(default_factory=list)  # ADR 0055
    effects: tuple[str, ...] = ()
    generic_bounds: tuple[tuple[str, str], ...] = ()

    @property
    def qualified_name(self) -> str:
        if self.namespace:
            return ".".join([*self.namespace, self.name])
        return self.name


@dataclass
class ModuleInfoDecl:
    """`module com.foo { exports …; requires …; }` (ADR 0058)."""

    name: list[str]
    exports: list[list[str]]
    requires: list[list[str]]
    span: Span

    @property
    def qualified_name(self) -> str:
        return ".".join(self.name)


@dataclass
class PackageDecl:
    path: list[str]
    span: Span


@dataclass
class ImportDecl:
    path: list[str]
    name: str
    span: Span
    # ADR 0177: None = whole module; list = selective short names (e.g. {A, B}).
    selected: list[str] | None = None


@dataclass
class EnumUseDecl:
    """`use OpsPhase.*` — bare when-arm variants (ADR 0177)."""

    enum_name: str
    span: Span


@dataclass(frozen=True)
class ScientificScopeContract:
    """Sealed cross-scope contract produced after scientific resolution."""

    kind: str
    name: str
    references: tuple[str, ...]
    symbols: tuple[str, ...]
    sealed: bool = True


@dataclass
class ScientificScopeDecl:
    """Phase-separated scientific scope declaration (LISS-0034)."""

    kind: str
    name: str
    references: list[str]
    symbols: list[str]
    span: Span
    body_declarations: tuple[Any, ...] = ()
    workflow_fields: tuple[tuple[str, str], ...] = ()
    workflow_parameter_types: tuple[str, ...] = ()
    registers: tuple[tuple[str, int], ...] = ()
    # Simple `lhs = rhs` IDENT bindings (LISS-0076 field RHS visibility).
    field_bindings: tuple[tuple[str, str, Span], ...] = ()


@dataclass
class H1ParameterDecl:
    """Typed theory parameter in the H1 equation-authoring surface."""

    name: str
    ty: TypeRef
    span: Span


@dataclass
class H1OperatorDecl:
    """Structured operator declaration for the H1 surface."""

    name: str
    parameters: list[str]
    source_tokens: tuple[str, ...]
    span: Span
    expression: object | None = None
    type_ref: TypeRef = field(default_factory=lambda: TypeRef(name="Operator", args=[]))
    dimension: str | None = None
    parameter_types: dict[str, str] = field(default_factory=dict)


@dataclass
class H1BasisDecl:
    """Formal `basis <name> = <expr>` domain declaration in a theory body."""

    name: str
    expression: object | None
    source_tokens: tuple[str, ...]
    span: Span


@dataclass
class H1CoordinateDecl:
    """Formal `coordinate <name>: <Kind><Size>` domain declaration in a
    theory body (e.g. `coordinate site: Lattice<128>`)."""

    name: str
    kind: str
    size: int | None
    span: Span


@dataclass
class H1RealizeDecl:
    """Top-level `realize qpu:<target>` H1 target-selection declaration."""

    target: str
    span: Span


@dataclass
class H1Prepare:
    source_tokens: tuple[str, ...]
    span: Span
    state_name: str | None = None
    bound_to: tuple[str, str] | None = None


@dataclass
class H1Evolve:
    source_tokens: tuple[str, ...]
    span: Span
    state_name: str | None = None
    theory_name: str | None = None


@dataclass
class H1Observable:
    source_tokens: tuple[str, ...]
    span: Span


@dataclass
class H1Measure:
    source_tokens: tuple[str, ...]
    span: Span


@dataclass
class H1Mixture:
    """H1 probabilistic/classified state composition via `when`."""

    source_tokens: tuple[str, ...]
    span: Span


@dataclass
class H1Superposition:
    """H1 coherent amplitude composition, distinct from probabilistic `mix`."""

    source_tokens: tuple[str, ...]
    span: Span


@dataclass
class H1CoherentControl:
    """H1 state-valued coherent control, distinct from `when`."""

    source_tokens: tuple[str, ...]
    span: Span


@dataclass
class H1DynamicControl:
    """H1 measurement-dependent control requiring the Dynamic QPU lane."""

    source_tokens: tuple[str, ...]
    span: Span


@dataclass
class H1TraceOut:
    """H1 terminal disposal of a state resource."""

    source_tokens: tuple[str, ...]
    span: Span


@dataclass
class H1Uncompute:
    """H1 reversible disposal backed by an explicit witness."""

    source_tokens: tuple[str, ...]
    span: Span


@dataclass
class TheoryDecl:
    """Formal H1 theory declaration, distinct from legacy phase metadata."""

    name: str
    parameters: list[H1ParameterDecl]
    operators: list[H1OperatorDecl]
    span: Span
    basis: H1BasisDecl | None = None
    coordinate: H1CoordinateDecl | None = None


@dataclass
class ExperimentDecl:
    """Formal H1 experiment declaration with ordered experiment statements."""

    name: str
    parameters: list[Param]
    body: list[object]
    span: Span


@dataclass
class DiscretizationDecl:
    """Top-level explicit continuous-to-finite representation contract."""

    name: str
    fields: tuple[tuple[str, str], ...]
    span: Span


@dataclass
class DiscretizationBridgeDecl:
    """`use Grid for Theory.Operator as finite_operator`."""

    contract: str
    source: str
    alias: str
    span: Span


@dataclass
class CompilationUnit:
    package: PackageDecl | None
    imports: list[ImportDecl]
    decls: list[Any]
    main: MainDecl | None
    span: Span
    source_version: str | None = None
    # ADR 0178: optional source lane (experiment|circuit|open); None = default experiment.
    lane: str | None = None
