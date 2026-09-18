"""Evolution-family entrypoint during the incremental evaluator extraction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ...ast_nodes import BinOp, Call, Expr, LitFloat, LitInt, Var
from .context import EvaluatorContext


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
