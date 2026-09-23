"""Evolution ops for evaluator evolution."""

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
    TupleExpr,
    Var,
)
from .context import EvaluatorContext
from .errors import KernelDiagnosticError, KernelError
from ..joint import Joint
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


def joint_l2_distance(left: Joint, right: Joint) -> float:
    """Return the Euclidean distance between two joint amplitude maps."""
    def amplitudes(joint: Joint) -> dict[str, complex]:
        result: dict[str, complex] = {}
        for world in joint.worlds:
            key = repr(sorted(world.assign.items(), key=lambda item: item[0]))
            result[key] = result.get(key, 0j) + world.amp
        return result

    lhs = amplitudes(left)
    rhs = amplitudes(right)
    keys = set(lhs) | set(rhs)
    squared_distance = sum(
        abs(lhs.get(key, 0j) - rhs.get(key, 0j)) ** 2 for key in keys
    )
    return squared_distance**0.5


def execute_evolution(
    context: EvaluatorContext, joint: Any, names: list[str], expr: Any
) -> Any:
    """Delegate evolution while preserving ordering and mutable state ownership."""
    return context._legacy_hamiltonian_evolve_one_step(joint, names, expr)


def _bounded_evolution_provenance(
    iteration_count: int, max_steps: int, stop_reason: str
) -> dict[str, Any]:
    return {
        "source_transform": "Operator * State",
        "predicate": "converged",
        "metric": "full_state_l2_difference",
        "numeric_type": "Float64",
        "tolerance": 1e-9,
        "iteration_count": iteration_count,
        "max_steps": max_steps,
        "stop_reason": stop_reason,
        "realization": "simulator_exact_step",
        "predicate_effect": "non_collapsing",
    }


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
            joint,
            names,
            expr.until_predicate,
            previous=previous,
            allow_single_alias=True,
        ):
            context.evolution_provenance = _bounded_evolution_provenance(
                iteration, max_steps, "predicate"
            )
            return joint
        previous = joint
    if expr.until_predicate is not None:
        provenance = _bounded_evolution_provenance(
            max_steps, max_steps, "max_exhausted"
        )
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
    *,
    previous: Joint | None = None,
    allow_single_alias: bool = False,
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
