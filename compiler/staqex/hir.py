"""Immutable phase-resolved typed HIR view (LISS-0080).

Additive extraction from TypeChecker — no evaluator rewire in Slices A–D.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .ast_nodes import (
    Attr,
    BinOp,
    Block,
    Call,
    Coin,
    CompilationUnit,
    Dirac,
    DynamicQpuStmt,
    EvolveExpr,
    ForEachStmt,
    FunDecl,
    Inspect,
    KetLit,
    ListExpr,
    MatchStmt,
    Measure,
    MeasureExpr,
    Pipe,
    ResetStmt,
    ReturnStmt,
    ScientificScopeContract,
    Span,
    StateBind,
    TensorExpr,
    TupleExpr,
    UnaryNot,
    Vacuum,
    Var,
    WhenExpr,
    SuperposeExpr,
)
from .typecheck import Ty, TypeChecker
from .runtime.uncompute import LINEAR_UNCOMPUTE_AMPLITUDE_TOL

_KERNEL_PHASE = "kernel"

# LISS-0114 Slice B / R1: authoritative linear consume kinds.
# Gate / apply / hadamard rebinds are not listed here — Call moves are
# governed by ADR 0168 (result-type driven), not by this kind set.
LINEAR_CONSUME_KINDS = frozenset({
    "measure",
    "static_uncompute_zero_reset",
})

# LISS-0114 Slice C / R2: alias policy (Adjudicator-locked 2026-07-29).
# "strict" → ``State alias = q`` is LINEAR_DUPLICATE_USE (no silent rename).
LINEAR_ALIAS_POLICY = "strict"

# LISS-0114 Slice D / R4: linear carriers at module-symbol + Type-First heads.
# DensityState is stored as Ty(kind="Object", payload="DensityState").
LINEAR_CARRIER_KINDS = frozenset({"State", "DensityState"})

# LINEAR_UNCOMPUTE_AMPLITUDE_TOL imported from runtime.uncompute (Slice F).

_KNOWN_PHASES = frozenset({
    "theory", "experiment", "workflow", "execution", "report",
    "system", _KERNEL_PHASE,
})

_KNOWN_EFFECTS = frozenset({"Measure", "Snapshot", "Inspect", "Host", "Uncompute"})
_LINEAR_DUPLICATE_USE = "LINEAR_DUPLICATE_USE"
_LINEAR_IMPLICIT_DISCARD = "LINEAR_IMPLICIT_DISCARD"
_UNCOMPUTE_WITNESS_MISSING = "UNCOMPUTE_WITNESS_MISSING"


@dataclass(frozen=True, slots=True)
class HirSpan:
    """Decl-level source location."""

    line: int
    col: int


@dataclass(frozen=True, slots=True)
class HirDecl:
    """Top-level declaration with resolved scientific phase, effects, and span."""

    name: str
    phase: str
    effects: frozenset[str] = field(default_factory=frozenset)
    span: HirSpan | None = None


@dataclass(frozen=True, slots=True)
class HirModule:
    """Immutable HIR module snapshot (symbols + typed expression map)."""

    symbols: Mapping[str, Ty]
    typed: Mapping[int, Ty]
    declarations: Mapping[str, HirDecl]
    linear_diagnostics: tuple[dict, ...] = ()


def _span_from(ast_node: Any) -> HirSpan | None:
    s = getattr(ast_node, "span", None)
    if s is None:
        return None
    return HirSpan(line=s.line, col=s.col)


def _build_declarations(
    checker: TypeChecker,
    scope_contracts: Mapping[str, ScientificScopeContract] | None,
    unit: CompilationUnit | None,
) -> Mapping[str, HirDecl]:
    decls: dict[str, HirDecl] = {}

    # Build name→span index from AST decls when unit is available.
    span_index: dict[str, HirSpan | None] = {}
    if unit is not None:
        for d in unit.decls:
            name = getattr(d, "name", None)
            if name:
                span_index[name] = _span_from(d)
        if unit.main is not None:
            span_index["main"] = _span_from(unit.main)

    if scope_contracts:
        for name, contract in scope_contracts.items():
            decls[name] = HirDecl(
                name=name,
                phase=contract.kind,
                effects=frozenset(),
                span=span_index.get(name),
            )

    for name in checker.fun_returns:
        if "." in name or name in decls:
            continue
        effects = checker.fun_effects.get(name, frozenset())
        decls[name] = HirDecl(
            name=name,
            phase=_KERNEL_PHASE,
            effects=frozenset(effects),
            span=span_index.get(name),
        )

    if checker.has_entry_main and "main" not in decls:
        decls["main"] = HirDecl(
            name="main",
            phase=_KERNEL_PHASE,
            effects=frozenset(),
            span=span_index.get("main"),
        )

    return MappingProxyType(decls)


def build_hir(
    checker: TypeChecker,
    *,
    scope_contracts: Mapping[str, ScientificScopeContract] | None = None,
    unit: CompilationUnit | None = None,
) -> HirModule:
    """Build an immutable HIR view from a completed TypeChecker.

    Slice A: symbol table + typed expression map.
    Slice B: declaration phases from sealed scientific-scope contracts.
    Slice C: ``effects {…}`` plus static Uncompute witnesses from ``unit``.
    Slice D: decl-level source provenance via optional ``unit``.
    """
    symbols = MappingProxyType(dict(checker.env))
    typed = MappingProxyType(dict(checker.typed))
    decls = dict(_build_declarations(checker, scope_contracts, unit))

    if unit is not None:
        # Provisional Slice C: static |0>/vacuum rebind witnesses (R9).
        for name in _scopes_with_uncompute_witness(unit, symbols, typed):
            if name not in decls:
                continue
            decl = decls[name]
            decls[name] = HirDecl(
                name=decl.name,
                phase=decl.phase,
                effects=frozenset(decl.effects | {"Uncompute"}),
                span=decl.span,
            )

    module = HirModule(
        symbols=symbols,
        typed=typed,
        declarations=MappingProxyType(decls),
    )
    if unit is None:
        return module

    # Slice D: wire HirLinearVerifier into build_hir.
    linear_diags = tuple(HirLinearVerifier().verify(module, unit=unit))
    return HirModule(
        symbols=module.symbols,
        typed=module.typed,
        declarations=module.declarations,
        linear_diagnostics=linear_diags,
    )


_VERIFIER_DIAGNOSTICS_CODE = "HIR_INVARIANT_ERROR"


def verify_hir(module: HirModule) -> list[dict]:
    """Lightweight HIR invariant checker.

    Returns a list of diagnostic dicts (empty means valid).
    Checks that all declaration phases and effects are known values.
    """
    diags: list[dict] = []
    for name, decl in module.declarations.items():
        if decl.phase not in _KNOWN_PHASES:
            diags.append({
                "code": _VERIFIER_DIAGNOSTICS_CODE,
                "message": (
                    f"HIR decl '{name}' has unknown phase '{decl.phase}'; "
                    f"expected one of {sorted(_KNOWN_PHASES)}"
                ),
            })
        unknown_effects = decl.effects - _KNOWN_EFFECTS
        if unknown_effects:
            diags.append({
                "code": _VERIFIER_DIAGNOSTICS_CODE,
                "message": (
                    f"HIR decl '{name}' has unknown effect(s) "
                    f"{sorted(unknown_effects)}; "
                    f"expected subset of {sorted(_KNOWN_EFFECTS)}"
                ),
            })
    return diags


@dataclass
class _LinearUseState:
    """Per-block alias roots, introduced State roots, and consumed roots."""

    aliases: dict[str, str]
    introduced: dict[str, Span]
    consumed: set[str]
    uncompute_witnessed: bool = False
    # LISS-0202: inferred type per bound expression (``id(expr) → Ty``), so the
    # linear obligation follows the carrier type instead of the binding
    # keyword. Covers ``fn``-local names, which never reach ``TypeChecker.env``.
    expr_types: Mapping[int, Ty] = MappingProxyType({})


def _linear_diag(code: str, span: Span, message: str) -> dict:
    return {
        "code": code,
        "line": span.line,
        "col": span.col,
        "message": message,
    }


def is_linear_carrier_ty(ty: Ty) -> bool:
    """True when ``ty`` is a linear quantum carrier (State or DensityState).

    Classical elaboration coefficients (ADR 0114 Type-First ``Float`` etc.)
    are intentionally excluded.
    """
    if ty.kind == "State":
        return True
    return ty.kind == "Object" and ty.payload == "DensityState"


def _is_state_binding(name: str, module_symbols: Mapping[str, Ty]) -> bool:
    ty = module_symbols.get(name)
    return ty is not None and is_linear_carrier_ty(ty)


def _stmt_binds_state(
    stmt: StateBind,
    module_symbols: Mapping[str, Ty],
    state: _LinearUseState,
) -> bool:
    """True when the bind is a linear State (symbols and/or Type-First head).

    Fun-local names are often absent from TypeChecker.env after check_unit
    (R10); fall back to ``State`` / ``DensityState`` type heads, ``state``
    keyword binds (ADR 0115 / LISS-0133), and in-block introductions.
    """
    if len(stmt.names) != 1:
        return False
    name = stmt.names[0]
    # ``inspect`` yields a non-destructive classical-ish view (LISS-0114 E).
    if isinstance(stmt.expr, Inspect):
        return False
    # LISS-0202: the carrier type decides, not the binding keyword. A `state`
    # bind whose value is a Dirac scalar (`⟨0|1⟩`, `⟨0|X|1⟩` → Classical) or an
    # Operator (`adjoint(X)`) carries no quantum resource: there is nothing to
    # measure and nothing the no-cloning theorem restricts. Bras stay linear —
    # `⟨ψ|` is the adjoint of `|ψ⟩`, the same resource viewed dually, and
    # ADR 0087 types both sides of `inner` as `State<V>`.
    #
    # A declared Type-First head is the most reliable carrier evidence. Raw
    # expression inference is only consulted for inference-only `state x = …`
    # binds: some builtin calls infer coarsely (`qft(reg)` infers `State` while
    # it is declared and used as `Operator`), so it must not override a
    # declaration.
    if stmt.ty is not None and not (stmt.ty.name == "State" and not stmt.ty.args):
        # ADR 0204 / LISS-0399: Continuous roots use the same
        # introduced/consumed LINEAR machinery as State roots -- consumed
        # only by finiteize (LISS-0401); an untouched root discards the
        # same as an unmeasured State.
        return stmt.ty.name in {"State", "DensityState", "Continuous"}
    if stmt.ty is not None:
        # LISS-0418: bare `State x = e` (Type-First, no `<T>`) is not a
        # deliberate "this IS definitely linear" declaration the way
        # `State<Qubit> x = e` is -- it is the canonical replacement for
        # the old, always-inference-driven `state x = e`, so it must fall
        # through to the same precise-inference check `via_state_keyword`
        # already uses below, not the blind "declared State -> always
        # linear" assumption (which mis-flagged e.g. a Partial-application
        # value bound via bare `State` as an undischarged linear root).
        bound_ty = state.expr_types.get(id(stmt.expr))
        if bound_ty is not None:
            return is_linear_carrier_ty(bound_ty)
        return True
    if stmt.via_state_keyword:
        bound_ty = state.expr_types.get(id(stmt.expr))
        if bound_ty is not None:
            return is_linear_carrier_ty(bound_ty)
        return True
    if name in state.introduced or name in state.aliases:
        return True
    return _is_state_binding(name, module_symbols)


def _is_state_var_alias(
    expr: object,
    module_symbols: Mapping[str, Ty],
    state: _LinearUseState,
) -> bool:
    if not isinstance(expr, Var):
        return False
    if expr.name in state.introduced or expr.name in state.aliases:
        return True
    return _is_state_binding(expr.name, module_symbols)


def _is_zero_reset(expr: object) -> bool:
    """Static uncompute witness: Vacuum or ket |0> (R9 provisional)."""
    if isinstance(expr, Vacuum):
        return True
    return isinstance(expr, KetLit) and expr.label == "0"


def _linear_root(name: str, aliases: Mapping[str, str]) -> str:
    root = aliases.get(name, name)
    while root in aliases and aliases[root] != root:
        root = aliases[root]
    return root


def _check_finiteize_continuous_reuse(
    stmt: StateBind, state: _LinearUseState
) -> dict | None:
    """ADR 0204 Decision 5 / LISS-0401: a `Continuous` root may be consumed
    by `finiteize` at most once (`CH-field-fork` deferred). The generic
    Call-argument consumption path (`_mark_linear_var_use`) does not
    detect reuse of an already-consumed root by design -- it only adds to
    a set, silently on duplicates -- so this dedicated check closes that
    gap specifically for `finiteize`'s first argument, mirroring
    `_check_reset_stmt`'s pattern of a small pre-check ahead of the
    generic consumption call.
    """
    expr = stmt.expr
    if not isinstance(expr, Call) or not expr.args:
        return None
    if not isinstance(expr.callee, Var) or expr.callee.name != "finiteize":
        return None
    first = expr.args[0]
    if not isinstance(first, Var):
        return None
    root = _linear_root(first.name, state.aliases)
    if root in state.consumed:
        return _linear_diag(
            _LINEAR_DUPLICATE_USE,
            stmt.span,
            f"`finiteize` reuses already-consumed Continuous root `{root}`",
        )
    return None


def _check_reset_stmt(stmt: ResetStmt, state: _LinearUseState) -> dict | None:
    """LISS-0390 (ADR 0199 Amendment): `reset wire` requires `wire` to
    already be a known local root in this dynamic-lane scope (introduced
    or aliased earlier); resetting an unknown name fails closed. Marking
    consumed (mirroring the Controller-measure treatment) is safe for the
    same reason: this checker does not yet re-inspect consumed roots for
    duplicate use, so a later measure/reset/apply of the same wire is not
    spuriously rejected -- the wire is genuinely usable again (the
    evaluator physically reinitializes it, LISS-0390 Decision 7).

    Extracted (LISS-0394) so the same check applies verbatim whether
    `reset` appears at the top level of a dynamic-lane scope or inside a
    `match` arm of that same scope.
    """
    root = _linear_root(stmt.target, state.aliases)
    if root not in state.introduced and stmt.target not in state.aliases:
        return _linear_diag(
            "DYN_RESET_UNKNOWN_WIRE",
            stmt.span,
            f"reset of unknown wire `{stmt.target}`",
        )
    state.consumed.add(root)
    return None


def _is_controller_measure_stmt(stmt: object) -> bool:
    """LISS-0387 (ADR 0200 Decision 4) shape: `Controller<T> = measure
    wire`. Extracted (LISS-0395) so the same recognition applies verbatim
    whether the bind appears at the top level of a dynamic-lane scope or
    inside a `match` arm of that same scope.
    """
    return (
        isinstance(stmt, StateBind)
        and stmt.ty is not None
        and stmt.ty.name == "Controller"
        and isinstance(stmt.expr, MeasureExpr)
        and isinstance(stmt.expr.expr, Var)
    )


def _consume_controller_measure_wire(stmt: StateBind, state: _LinearUseState) -> None:
    """Marks the measured wire consumed (LISS-0387 Decision 4 rationale:
    the wire is not physically dead -- it may still be gated/applied to
    inside `match` arms -- but nothing later in this pass re-inspects a
    consumed root for duplicate use, so marking it here is safe).
    """
    wire_root = _linear_root(stmt.expr.expr.name, state.aliases)
    state.consumed.add(wire_root)


def _analyze_dynamic_lane_match(stmt: MatchStmt, state: _LinearUseState) -> list[dict]:
    """LISS-0394: check every arm of a dynamic-lane `match` against the
    shared enclosing `state` (arms are mutually-exclusive continuations
    of the same scope, not independent nested scopes -- see this
    function's caller in `_analyze_block` for why a seeded-recursion
    design was rejected).
    """
    diags: list[dict] = []
    for arm in stmt.arms:
        diags.extend(_analyze_dynamic_lane_arm_stmts(arm.body.stmts, state))
    return diags


def _analyze_dynamic_lane_arm_stmts(
    stmts: list[object], state: _LinearUseState
) -> list[dict]:
    """Process one `match` arm's statements against the shared `state`.
    Mirrors exactly the statement kinds
    `evaluator.py::_run_dynamic_arm_body` executes for arm bodies (LISS-0395
    unified that function with the top-level dynamic-qpu-block dispatcher,
    so arm bodies now run the same vocabulary as the block top level, at
    any nesting depth): Controller-measure (LISS-0395, dedicated -- mirrors
    the top-level `_analyze_block` treatment exactly), `ResetStmt`
    (LISS-0390, dedicated), nested `MatchStmt` (recursion). Bare
    `ExprStmt`/`Call` stays untracked here, same as everywhere else in this
    checker. A generic `StateBind` that is *not* Controller-measure-shaped
    is intentionally left unhandled, matching the top-level
    `_analyze_block`'s own scope (this checker does not track arbitrary
    quantum-carrier binds inside dynamic-lane scopes at all, top level
    included).
    """
    diags: list[dict] = []
    for stmt in stmts:
        if _is_controller_measure_stmt(stmt):
            _consume_controller_measure_wire(stmt, state)
            continue
        if isinstance(stmt, ResetStmt):
            diag = _check_reset_stmt(stmt, state)
            if diag is not None:
                diags.append(diag)
            continue
        if isinstance(stmt, MatchStmt):
            diags.extend(_analyze_dynamic_lane_match(stmt, state))
            continue
    return diags


def _linear_scopes(
    unit: CompilationUnit,
) -> list[tuple[str, Block, Mapping[str, Span]]]:
    scopes: list[tuple[str, Block, Mapping[str, Span]]] = []
    if unit.main is not None:
        scopes.append(("main", unit.main.body, {}))
    for decl in unit.decls:
        if isinstance(decl, FunDecl):
            seeds = {
                param.name: decl.span
                for param in decl.params
                if param.ty is not None
                and param.ty.name in {"State", "DensityState"}
            }
            scopes.append((decl.name, decl.body, seeds))
    return scopes


def _source_declared_uncompute(unit: CompilationUnit) -> set[str]:
    names: set[str] = set()
    for decl in unit.decls:
        if isinstance(decl, FunDecl) and "Uncompute" in decl.effects:
            names.add(decl.name)
    return names


def _analyze_block(
    block: Block,
    module_symbols: Mapping[str, Ty],
    *,
    seed_linear: Mapping[str, Span] | None = None,
    move_call_names: frozenset[str] | None = None,
    expr_types: Mapping[int, Ty] | None = None,
) -> tuple[list[dict], _LinearUseState]:
    state = _LinearUseState(
        aliases={},
        introduced={},
        consumed=set(),
        expr_types=expr_types if expr_types is not None else MappingProxyType({}),
    )
    if seed_linear:
        for name, span in seed_linear.items():
            state.introduced.setdefault(name, span)
            state.aliases.setdefault(name, name)
    move_names = move_call_names or frozenset()
    diags: list[dict] = []

    for stmt in block.stmts:
        if _is_controller_measure_stmt(stmt):
            # LISS-0387 (ADR 0200 Decision 4): `Controller<T> = measure wire`
            # inside a dynamic qpu block consumes `wire` for linear-use
            # purposes, unlike Static `state` bindings which stay
            # unconsumed until an explicit `measure` statement. Unlike
            # Static terminal `measure`, the wire is not physically dead
            # (ADR 0197 Decision 2) — it may still be gated/applied to
            # inside `match` arms, including nested Controller-measures
            # (LISS-0395) — nothing later in this pass re-inspects a
            # consumed root for duplicate use.
            _consume_controller_measure_wire(stmt, state)
            continue
        if isinstance(stmt, ResetStmt):
            diag = _check_reset_stmt(stmt, state)
            if diag is not None:
                diags.append(diag)
            continue
        if isinstance(stmt, MatchStmt):
            # LISS-0394: match arms are mutually-exclusive continuations
            # of this same enclosing scope, not a separate nested scope
            # (unlike ForEachStmt/DynamicQpuStmt below) -- processed
            # against this same `state` object directly, no new
            # _LinearUseState, no seed_linear, no independent discard
            # check. See LISS-0394 Plan "Design verification" for why a
            # seeded-recursion design was traced and rejected (it would
            # false-positive LINEAR_IMPLICIT_DISCARD on every wire
            # already consumed before the match).
            diags.extend(_analyze_dynamic_lane_match(stmt, state))
            continue
        if isinstance(stmt, StateBind):
            diag = _check_state_bind(stmt, module_symbols, state)
            if diag is not None:
                diags.append(diag)
            reuse_diag = _check_finiteize_continuous_reuse(stmt, state)
            if reuse_diag is not None:
                diags.append(reuse_diag)
            # LISS-0114 Slice E: when / inspect uses consume outer roots.
            _consume_when_linear_uses(stmt.expr, state)
            _consume_inspect_linear_uses(stmt.expr, state)
            # LISS-0221 / ADR 0168: Calls whose result is a linear carrier move
            # linear args (plus user-fn move names).
            bind_ty = stmt.ty.name if stmt.ty is not None else None
            _consume_transforming_call_linear_args(
                stmt.expr,
                state,
                move_names,
                enclosing_bind_ty=bind_ty,
                is_bind_rhs=True,
            )
            # ADR 0173: ``trace_out`` consumes its State arg even when the bind
            # head is Classical / placeholder (Companion amendment).
            _consume_trace_out_call_args(stmt.expr, state)
            # LISS-0201 / LISS-0238: `w |> partial` is a Pipe, not a Call.
            # Always move linear carriers on the **lhs** (payload): multi-hole
            # Partial fill yields `State<fn#k>` (non-linear), so bind-ty gates
            # must not skip the payload move (ADR 0149).
            if isinstance(stmt.expr, Pipe):
                _mark_all_linear_vars(stmt.expr.lhs, state)
                if (
                    bind_ty in {"State", "DensityState"}
                    or (
                        stmt.via_state_keyword
                        and _stmt_binds_state(stmt, module_symbols, state)
                    )
                ):
                    _mark_all_linear_vars(stmt.expr.rhs, state)
            # In-place rebinds (`Name = transform(..., Name, …)`) open a fresh
            # obligation after the Call consumes the old root (incl. apply).
            _revive_inplace_linear_rebinds(
                stmt,
                state,
                move_names,
                enclosing_bind_ty=bind_ty,
            )
        elif isinstance(stmt, ReturnStmt):
            # LISS-0133: return moves linear roots out of the callee.
            _mark_all_linear_vars(stmt.expr, state)
        elif isinstance(stmt, Measure) and isinstance(stmt.expr, Var):
            diags.extend(_check_measure(stmt, state))
        elif isinstance(stmt, (ForEachStmt, DynamicQpuStmt)):
            nested_diags, nested = _analyze_block(
                stmt.body,
                module_symbols,
                move_call_names=move_names,
                expr_types=state.expr_types,
            )
            diags.extend(nested_diags)
            state.consumed |= nested.consumed
            if nested.uncompute_witnessed:
                state.uncompute_witnessed = True

    diags.extend(_discard_diags(state))
    return diags, state


def _mark_linear_var_use(expr: object, state: _LinearUseState) -> None:
    if not isinstance(expr, Var):
        return
    root = _linear_root(expr.name, state.aliases)
    if root in state.introduced or expr.name in state.aliases:
        state.consumed.add(root)


def _expr_children(expr: object) -> tuple[object, ...]:
    """Return child expressions for LINEAR / when walks (LISS-0125).

    ``BinOp`` uses ``lhs``/``rhs``; ``TensorExpr`` uses ``left``/``right``.
    """
    if isinstance(expr, (WhenExpr, SuperposeExpr)):
        return (expr.ctrl, *(arm.body for arm in expr.arms))
    if isinstance(expr, Call):
        return tuple(expr.args)
    if isinstance(expr, BinOp):
        return (expr.lhs, expr.rhs)
    if isinstance(expr, TensorExpr):
        return (expr.left, expr.right)
    if isinstance(expr, Pipe):
        return (expr.lhs, expr.rhs)
    if isinstance(expr, Attr):
        return (expr.obj,)
    if isinstance(expr, Inspect):
        return (expr.expr,)
    if isinstance(expr, UnaryNot):
        return (expr.expr,)
    if isinstance(expr, (TupleExpr, ListExpr)):
        return tuple(expr.items)
    return ()


def _mark_all_linear_vars(expr: object, state: _LinearUseState) -> None:
    if isinstance(expr, WhenExpr):
        _consume_when_linear_uses(expr, state)
        return
    if isinstance(expr, Var):
        _mark_linear_var_use(expr, state)
        return
    for child in _expr_children(expr):
        _mark_all_linear_vars(child, state)


def _consume_when_linear_uses(expr: object, state: _LinearUseState) -> None:
    """Consume linear roots used as ``when``/``mix`` or ``superpose`` scrutinee
    or arm values (Slice E; LISS-0320 extends this to `SuperposeExpr`)."""
    if isinstance(expr, (WhenExpr, SuperposeExpr)):
        _mark_linear_var_use(expr.ctrl, state)
        for arm in expr.arms:
            _mark_all_linear_vars(arm.body, state)
        return
    for child in _expr_children(expr):
        _consume_when_linear_uses(child, state)


def _consume_inspect_linear_uses(expr: object, state: _LinearUseState) -> None:
    """``inspect(x)`` uses ``x`` for linear lifetime (non-destructive view)."""
    if isinstance(expr, Inspect):
        _mark_all_linear_vars(expr.expr, state)
        return
    for child in _expr_children(expr):
        _consume_inspect_linear_uses(child, state)


def _revive_inplace_linear_rebinds(
    stmt: StateBind,
    state: _LinearUseState,
    move_call_names: frozenset[str],
    *,
    enclosing_bind_ty: str | None,
) -> None:
    """Undo consume for wires rebound by a transforming Call (LISS-0221/0228)."""
    expr = stmt.expr
    if not isinstance(expr, Call):
        return
    if not _call_moves_linear_args(
        expr,
        state,
        move_call_names,
        enclosing_bind_ty=enclosing_bind_ty,
        is_bind_rhs=True,
    ):
        return
    wire_names = {
        arg.name for arg in expr.args if isinstance(arg, Var)
    }
    for name in stmt.names:
        if name not in wire_names:
            continue
        root = _linear_root(name, state.aliases)
        state.consumed.discard(root)
        state.introduced[name] = stmt.span
        state.aliases[name] = name


def _call_result_is_linear_carrier(
    expr: Call,
    state: _LinearUseState,
    *,
    enclosing_bind_ty: str | None,
    is_bind_rhs: bool,
) -> bool:
    typed = state.expr_types.get(id(expr))
    if typed is not None:
        return is_linear_carrier_ty(typed)
    if is_bind_rhs and enclosing_bind_ty in {"State", "DensityState"}:
        return True
    return False


def _call_moves_linear_args(
    expr: Call,
    state: _LinearUseState,
    move_call_names: frozenset[str],
    *,
    enclosing_bind_ty: str | None,
    is_bind_rhs: bool,
) -> bool:
    callee_name = expr.callee.name if isinstance(expr.callee, Var) else None
    if callee_name is not None and callee_name in move_call_names:
        return True
    return _call_result_is_linear_carrier(
        expr,
        state,
        enclosing_bind_ty=enclosing_bind_ty,
        is_bind_rhs=is_bind_rhs,
    )


def _consume_transforming_call_linear_args(
    expr: object,
    state: _LinearUseState,
    move_call_names: frozenset[str],
    *,
    enclosing_bind_ty: str | None = None,
    is_bind_rhs: bool = False,
) -> None:
    """Move linear args of Calls whose result is a linear carrier (ADR 0168)."""
    if isinstance(expr, Call):
        if _call_moves_linear_args(
            expr,
            state,
            move_call_names,
            enclosing_bind_ty=enclosing_bind_ty,
            is_bind_rhs=is_bind_rhs,
        ):
            for arg in expr.args:
                _mark_all_linear_vars(arg, state)
        for child in expr.args:
            _consume_transforming_call_linear_args(
                child,
                state,
                move_call_names,
            )
        return
    for child in _expr_children(expr):
        _consume_transforming_call_linear_args(
            child,
            state,
            move_call_names,
        )


def _tuple_item_introduces_linear(
    item: object,
    module_symbols: Mapping[str, Ty],
    state: _LinearUseState,
) -> bool:
    """True when a multi-bind RHS item creates a new linear State root.

    Classical multi-bind items (literals, pure classical trees) stay non-linear
    (ADR 0184). Ket / coin / when / State-forming Dirac introduce roots
    (LISS-0309).
    """
    if isinstance(item, (KetLit, Coin, WhenExpr, Vacuum)):
        return True
    if isinstance(item, Dirac):
        return True
    if isinstance(item, (Call, EvolveExpr, TensorExpr, Pipe)):
        typed = state.expr_types.get(id(item))
        if typed is not None:
            return is_linear_carrier_ty(typed)
        # evolve / tensor product RHS for multi-name product binds
        return isinstance(item, (EvolveExpr, TensorExpr))
    if isinstance(item, Var):
        return _is_state_var_alias(item, module_symbols, state)
    return False


def _check_multi_state_bind(
    stmt: StateBind,
    module_symbols: Mapping[str, Ty],
    state: _LinearUseState,
) -> dict | None:
    """Introduce linear roots for multi-name **tuple** binds (LISS-0309).

    Covers ``s0, s1 = |+>, |+>``. Product evolve / tensor multi-binds keep
    their pre-existing introduction/consume paths (do not force-introduce
    here — that double-counts or invents roots for classical/tensor mixes).
    """
    expr = stmt.expr
    if not (isinstance(expr, TupleExpr) and len(expr.items) == len(stmt.names)):
        return None
    for name, item in zip(stmt.names, expr.items):
        if isinstance(item, Var) and _is_state_var_alias(
            item, module_symbols, state
        ):
            root = _linear_root(item.name, state.aliases)
            state.aliases[name] = root
            continue
        if _tuple_item_introduces_linear(item, module_symbols, state):
            state.aliases.setdefault(name, name)
            state.introduced.setdefault(name, stmt.span)
    return None

def _check_state_bind(
    stmt: StateBind,
    module_symbols: Mapping[str, Ty],
    state: _LinearUseState,
) -> dict | None:
    if len(stmt.names) != 1:
        return _check_multi_state_bind(stmt, module_symbols, state)

    bound_name = stmt.names[0]
    if not _stmt_binds_state(stmt, module_symbols, state):
        return None

    # Same-name reset to |0>/vacuum: static uncompute witness (Slice C / R9).
    if bound_name in state.introduced and _is_zero_reset(stmt.expr):
        root = _linear_root(bound_name, state.aliases)
        state.consumed.add(root)
        state.uncompute_witnessed = True
        return None

    state.aliases.setdefault(bound_name, bound_name)

    if not _is_state_var_alias(stmt.expr, module_symbols, state):
        state.introduced.setdefault(bound_name, stmt.span)
        return None

    assert isinstance(stmt.expr, Var)
    root = _linear_root(stmt.expr.name, state.aliases)
    state.aliases[bound_name] = root
    if stmt.expr.name == bound_name:
        return None

    return _linear_diag(
        _LINEAR_DUPLICATE_USE,
        stmt.span,
        (
            f"quantum state `{stmt.expr.name}` cannot be rebound as "
            f"`{bound_name}`; root `{root}` is linear"
        ),
    )


def _consume_tracing_out_leftovers(
    stmt: Measure,
    state: _LinearUseState,
    *,
    primary: str,
    primary_root: str,
) -> list[dict]:
    """ADR 0173: consume named leftovers; reject primary / duplicates / dead names."""
    diags: list[dict] = []
    seen_roots: set[str] = set()
    for name in stmt.tracing_out:
        root = _linear_root(name, state.aliases)
        if name == primary or root == primary_root:
            diags.append(
                _linear_diag(
                    _LINEAR_DUPLICATE_USE,
                    stmt.span,
                    (
                        f"quantum state `{name}` cannot appear in both "
                        f"`measure` and `tracing_out`"
                    ),
                )
            )
            continue
        if root in seen_roots:
            diags.append(
                _linear_diag(
                    _LINEAR_DUPLICATE_USE,
                    stmt.span,
                    f"duplicate `tracing_out` name `{name}`",
                )
            )
            continue
        seen_roots.add(root)
        if root in state.consumed:
            diags.append(
                _linear_diag(
                    _LINEAR_DUPLICATE_USE,
                    stmt.span,
                    (
                        f"quantum state `{name}` reuses consumed root "
                        f"`{root}` in `tracing_out`"
                    ),
                )
            )
            continue
        if root not in state.introduced and name not in state.aliases:
            diags.append(
                _linear_diag(
                    _LINEAR_DUPLICATE_USE,
                    stmt.span,
                    f"`tracing_out` name `{name}` is not a live linear carrier",
                )
            )
            continue
        state.consumed.add(root)
    return diags


def _check_measure(stmt: Measure, state: _LinearUseState) -> list[dict]:
    assert isinstance(stmt.expr, Var)
    primary = stmt.expr.name
    primary_root = _linear_root(primary, state.aliases)
    diags = _consume_tracing_out_leftovers(
        stmt, state, primary=primary, primary_root=primary_root
    )

    if primary_root in state.consumed:
        diags.append(
            _linear_diag(
                _LINEAR_DUPLICATE_USE,
                stmt.span,
                (
                    f"quantum state `{primary}` reuses consumed root "
                    f"`{primary_root}`"
                ),
            )
        )
        return diags

    state.consumed.add(primary_root)
    return diags


def _consume_trace_out_call_args(expr: object, state: _LinearUseState) -> None:
    """ADR 0173 companion: builtin ``trace_out`` always consumes its State arg."""
    if isinstance(expr, Call):
        callee = expr.callee.name if isinstance(expr.callee, Var) else None
        if callee == "trace_out":
            for arg in expr.args:
                _mark_all_linear_vars(arg, state)
        for child in expr.args:
            _consume_trace_out_call_args(child, state)
        return
    for child in _expr_children(expr):
        _consume_trace_out_call_args(child, state)


def _discard_diags(state: _LinearUseState) -> list[dict]:
    return [
        _linear_diag(
            _LINEAR_IMPLICIT_DISCARD,
            span,
            (
                f"quantum state `{root}` is discarded without measure "
                f"or uncomputation"
            ),
        )
        for root, span in state.introduced.items()
        if root not in state.consumed
    ]


def _user_fun_names(unit: CompilationUnit) -> frozenset[str]:
    return frozenset(
        decl.name for decl in unit.decls if isinstance(decl, FunDecl)
    )


def _scopes_with_uncompute_witness(
    unit: CompilationUnit,
    module_symbols: Mapping[str, Ty],
    expr_types: Mapping[int, Ty] | None = None,
) -> set[str]:
    names: set[str] = set()
    move_names = _user_fun_names(unit)
    for scope_name, block, seeds in _linear_scopes(unit):
        _, state = _analyze_block(
            block,
            module_symbols,
            seed_linear=seeds,
            move_call_names=move_names,
            expr_types=expr_types,
        )
        if state.uncompute_witnessed:
            names.add(scope_name)
    return names


class HirLinearVerifier:
    """HIR-level linear-use verifier for quantum state consumption.

    Slice A: reject ``State`` alias rebinding; track duplicate ``measure``.
    Slice B: reject introduced ``State`` roots left unconsumed at block exit.
    Slice C: static ``|0>`` / vacuum rebind as uncompute witness; require a
    witness when source declares ``effects { Uncompute }`` (R9 provisional).

    Consumption (see ``LINEAR_CONSUME_KINDS``): ``measure`` and same-name
    ``|0>`` / vacuum rebind only for bind-level kinds. Slice E additionally
    treats ``when`` scrutinee/arm Vars and ``inspect`` operands as uses.
    LISS-0133: ``return`` and user-``fn`` Call args also consume.
    ADR 0168 / LISS-0221: any Call whose result is a linear carrier moves
    linear argument carriers; Classical-result Calls (``expect``, ``inner``,
    …) do not. Same-name transforming rebinds open a fresh obligation.
    ADR 0173 / LISS-0250: ``measure … tracing_out …`` consumes named leftovers;
    builtin ``trace_out`` always consumes its State argument.
    """

    def verify(
        self,
        module: HirModule,
        *,
        unit: CompilationUnit | None = None,
    ) -> list[dict]:
        if unit is None:
            return []

        declared = _source_declared_uncompute(unit)
        move_names = _user_fun_names(unit)
        diags: list[dict] = []
        for scope_name, block, seeds in _linear_scopes(unit):
            block_diags, state = _analyze_block(
                block,
                module.symbols,
                seed_linear=seeds,
                move_call_names=move_names,
                expr_types=module.typed,
            )
            diags.extend(block_diags)

            if scope_name in declared and not state.uncompute_witnessed:
                decl = module.declarations.get(scope_name)
                line = decl.span.line if decl is not None and decl.span else 1
                col = decl.span.col if decl is not None and decl.span else 1
                diags.append({
                    "code": _UNCOMPUTE_WITNESS_MISSING,
                    "line": line,
                    "col": col,
                    "message": (
                        f"`{scope_name}` declares effect Uncompute but has no "
                        f"static |0>/vacuum uncompute witness"
                    ),
                })

        return diags
