"""Evolution-family entrypoint during the incremental evaluator extraction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from ...ast_nodes import (
    BinOp,
    Call,
    EvolveExpr,
    Expr,
    LitBool,
    LitFloat,
    LitInt,
    OpAttr,
    OpBin,
    OpBinder,
    OpCall,
    OpGridQuad,
    OpHop,
    OpIdentity,
    OpIndexed,
    OpLit,
    OpNumber,
    OpPauli,
    OpPow,
    OpQuadrature,
    OpVar,
    TupleExpr,
    Var,
)
from ...continuous_lowering import GridHamiltonian, GridHamiltonianRef
from ...dimensions import UNIT_TABLE, to_canonical_magnitude
from .context import EvaluatorContext
from .errors import KernelDiagnosticError, KernelError
from ..joint import EPS, Joint
from ..op_attr_elaboration import OpAttrElaborationError, materialize_op_attrs
from .values import evaluate_value


@dataclass(frozen=True)
class ExplicitPropagator:
    """Runtime record for an explicitly written propagator expression."""

    hamiltonian: Expr
    duration: Expr


def explicit_propagator(expr: Expr) -> ExplicitPropagator | None:
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


def joint_l2_distance(left: Any, right: Any) -> float:
    """Return the Euclidean distance between two joint amplitude maps."""
    def amplitudes(joint: Any) -> dict[str, complex]:
        result: dict[str, complex] = {}
        for world in joint.worlds:
            key = repr(sorted(world.assign.items(), key=lambda item: item[0]))
            result[key] = result.get(key, 0j) + world.amp
        return result

    lhs = amplitudes(left)
    rhs = amplitudes(right)
    keys = set(lhs) | set(rhs)
    return sum(abs(lhs.get(key, 0j) - rhs.get(key, 0j)) ** 2 for key in keys) ** 0.5


def execute_evolution(
    context: EvaluatorContext, joint: Any, names: list[str], expr: Any
) -> Any:
    """Delegate evolution while preserving ordering and mutable state ownership."""
    return context._legacy_hamiltonian_evolve_one_step(joint, names, expr)

def bind_apply_multi(
    context: EvaluatorContext, joint: Joint, names: list[str], expr: Call
) -> Joint:
    """apply(U, w…) rebound as ``state (n…) = apply(U, w…)`` (LISS-0228)."""
    from ..unitaries import apply_unitary_on_wires

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
    u_mat = context._resolve_unitary_matrix(u_expr, len(wires))
    try:
        updated = apply_unitary_on_wires(joint, wires, u_mat)
    except ValueError as e:
        raise KernelError(str(e)) from e
    if list(names) == wires:
        return updated
    # Relabel wire coordinates to bind names when they differ.
    from ..joint import World, _coalesce

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


def bind_cnot_multi(
    context: EvaluatorContext, joint: Joint, names: list[str], expr: Call
) -> Joint:
    """``state (c, t) = cnot(c, t)`` — keep both wires after CNOT (linear)."""
    from ..joint import World, _coalesce
    from ..quantum_ops import cnot_bit

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


def bind_evolve(
    context: EvaluatorContext, joint: Joint, names: list[str], expr: EvolveExpr
) -> Joint:
    if expr.explicit_transform:
        return context._bind_explicit_evolve(joint, names, expr)
    if len(expr.seeds) != len(names):
        raise KernelError(
            f"evolve seeds {len(expr.seeds)} != bind names {len(names)}"
        )

    # Hamiltonian path: evolve psi under H for t  (ADR 0038 / 0041)
    if expr.hamiltonian is not None:
        return context._bind_evolve_hamiltonian(joint, names, expr)

    pre_live = context._joint_coord_names(joint)

    # Initialize working coordinates from seeds (correlated copy / eval).
    init: dict[str, Callable[[dict[str, Any]], Any]] = {}
    for name, seed in zip(names, expr.seeds):
        if isinstance(seed, Var):
            sn = seed.name
            init[name] = lambda a, sn=sn: a[sn]
        else:
            init[name] = lambda a, s=seed: evaluate_value(context, s, a)
    joint = joint.bind_multi(init)

    if expr.body is None:
        raise KernelError("block evolve requires a `{ … }` body")

    n_times = context._eval_times(expr.times)
    for _step in range(n_times):
        for let in expr.body.lets:
            ln = let.name
            le = let.expr
            # Gate / walk Call must use Joint transformers, not scalar eval
            if isinstance(le, Call):
                joint = context._bind(joint, ln, le)
            else:
                joint = joint.bind_pushforward(
                    ln, lambda a, e=le: evaluate_value(context, e, a)
                )
        res = expr.body.result
        if isinstance(res, Call) and isinstance(res.callee, Var):
            fun = context.funs.get(res.callee.name)
            if fun is not None:
                joint = context._bind_user_fun(joint, names, res, fun)
                continue
        if isinstance(res, TupleExpr):
            if len(res.items) != len(names):
                raise KernelError("evolve result tuple arity mismatch")
            updates = {
                name: (lambda a, e=item: evaluate_value(context, e, a))
                for name, item in zip(names, res.items)
            }
            joint = joint.bind_multi(updates)
        else:
            if len(names) != 1:
                raise KernelError("evolve scalar result requires a single bind name")
            if isinstance(res, Call):
                joint = context._bind(joint, names[0], res)
            else:
                joint = joint.bind_pushforward(
                    names[0], lambda a, e=res: evaluate_value(context, e, a)
                )
    # ADR 0142: drop evolve-local let axes (and other non-live coords).
    return context._trace_out_dead_fn_locals(joint, pre_live, names)


def bind_explicit_evolve(
    context: EvaluatorContext, joint: Joint, names: list[str], expr: EvolveExpr
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
        context.operators.get(result.lhs.name)
        if isinstance(result.lhs, Var)
        else context._explicit_propagator(result.lhs)
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
    max_steps = context._eval_max_steps(expr.max_steps) if expr.until_predicate else 1
    previous = joint
    for iteration in range(1, max_steps + 1):
        joint = context._bind_evolve_hamiltonian(joint, names, lowered)
        if expr.until_predicate is None:
            break
        if context._eval_until_predicate(
            joint, names, expr.until_predicate, previous=previous,
            allow_single_alias=True,
        ):
            context.evolution_provenance = {
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
        context.evolution_provenance = provenance
        raise KernelDiagnosticError(
            "EVOLVE_UNTIL_MAX_STEPS_ERROR",
            "evolve until reached max steps without predicate success",
            line=expr.span.line,
            col=expr.span.col,
            provenance=provenance,
        )
    return joint


def eval_max_steps(context: EvaluatorContext, max_steps: Expr | None) -> int:
    if not isinstance(max_steps, LitInt) or max_steps.value <= 0:
        raise KernelError("evolve until requires a positive compile-time `max` bound")
    return max_steps.value


def eval_until_predicate(
    context: EvaluatorContext, joint: Joint, names: list[str], predicate: Expr,
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
            return context._joint_l2_distance(previous, joint) <= 1e-9
    raise KernelError(
        "evolve until predicates support `converged(state)` or literal booleans only"
    )


def bind_evolve_hamiltonian(
    context: EvaluatorContext, joint: Joint, names: list[str], expr: EvolveExpr
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
            init[name] = lambda a, s=seed: evaluate_value(context, s, a)
    joint = joint.bind_multi(init)

    if expr.until_predicate is None:
        return execute_evolution(context, joint, names, expr)

    max_n = context._eval_max_steps(expr.max_steps)
    for _ in range(max_n):
        joint = execute_evolution(context, joint, names, expr)
        if context._eval_until_predicate(joint, names, expr.until_predicate):
            return joint
    raise KernelDiagnosticError(
        "EVOLVE_UNTIL_MAX_STEPS_ERROR",
        "evolve until reached max steps without predicate success",
        line=expr.span.line,
        col=expr.span.col,
    )


def hamiltonian_evolve_one_step(
    context: EvaluatorContext, joint: Joint, names: list[str], expr: EvolveExpr
) -> Joint:
    from ..hamiltonian import compile_hamiltonian, hop_basis_dim, op_n_qubits
    from ..joint import World, _coalesce
    from ..matrix import apply_mat, expm_ih
    from ..quantum_ops import apply_u2, pauli_u
    from ...ast_nodes import (
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
    from ...dimensions import UNIT_TABLE

    # ADR 0195: evolve's duration must resolve to a real Time unit --
    # a bare dimensionless duration can no longer be silently treated
    # as "already in seconds" under the old hbar=1 convention.
    # LISS-0357: resolve via the already-general _eval_value_with_unit
    # (Var, struct-field Attr via ADR 0174 field_units, and
    # literal-suffix Attr) instead of a bare-Var-only check, so
    # `evolve ... for config.duration` and `evolve ... for 0.25.fs`
    # are recognized the same as a pre-bound Time variable.
    t_raw_val, duration_unit = context._eval_value_with_unit(expr.duration, {})
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
    from ...dimensions import to_canonical_magnitude

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
        if hop.name not in context.operators:
            # bare Pauli already handled; unknown
            raise KernelError(f"unknown Operator / Hamiltonian `{hop.name}`")
        op_ast = context.operators[hop.name]
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
            op_ast, context.objects, operators=context.operators
        )
    except OpAttrElaborationError as exc:
        raise KernelError(str(exc)) from exc

    declared_space = (
        context.operator_spaces.get(hop.name)
        if isinstance(hop, Var)
        else None
    )
    if isinstance(op_ast, GridHamiltonianRef):
        gh = context.grid_hamiltonians[op_ast.alias]
        return context._evolve_precomputed_grid(joint, names, gh, t)
    try:
        nq = (
            declared_space
            if declared_space is not None
            else op_n_qubits(op_ast, context.operators, context.scalars)
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
        dim = max(dim, hop_basis_dim(op_ast, context.operators, context.scalars), 2)
        try:
            hmat = compile_hamiltonian(
                op_ast,
                env=context.operators,
                scalars=context.scalars,
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
                env=context.operators,
                scalars=context.scalars,
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
            from ..sparse_pauli import compile_sparse_pauli

            try:
                terms = compile_sparse_pauli(
                    op_ast,
                    env=context.operators,
                    scalars=context.scalars,
                    n_qubits=nq,
                )
            except ValueError as e:
                raise KernelError(str(e)) from e
            return context._hamiltonian_evolve_tuple_coordinate(joint, src, nq, terms, t)

    # Multi-qubit Pauli H on names[0..nq) — sparse Pauli-sum + Taylor e^{-iHt}
    if len(names) < nq:
        raise KernelError(
            f"Operator needs {nq} qubit wires, bind has {len(names)}"
        )
    wires = names[:nq]
    from ..sparse_pauli import compile_sparse_pauli, expm_ih_apply

    try:
        terms = compile_sparse_pauli(
            op_ast,
            env=context.operators,
            scalars=context.scalars,
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


def hamiltonian_evolve_tuple_coordinate(
    context: EvaluatorContext,
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

    from ..joint import World, _coalesce
    from ..sparse_pauli import expm_ih_apply

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


def evolve_precomputed_grid(
    context: EvaluatorContext,
    joint: Joint,
    names: list[str],
    grid: GridHamiltonian,
    t: float,
) -> Joint:
    from ..joint import World, _coalesce
    from ..matrix import apply_mat, expm_ih

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


def execute_stateful_evolution(
    context: EvaluatorContext, joint: Any, names: list[str], expr: Any
) -> Any:
    """Execute one stateful Hamiltonian evolution step through the family module."""
    return context._legacy_hamiltonian_evolve_one_step(joint, names, expr)
