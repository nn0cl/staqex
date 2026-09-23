"""Compatibility exports for the extracted evolution-family services."""

from __future__ import annotations

from typing import Any

from .unitary_ops import (
    bind_apply, bind_apply_multi, bind_capply, bind_cnot_multi, is_unitary_name,
    qft_family_matrix, resolve_unitary_matrix, split_capply_args,
)
from .evolution_ops import (
    ExplicitPropagator, bind_evolve, bind_evolve_hamiltonian,
    bind_explicit_evolve, eval_max_steps, eval_until_predicate,
    execute_evolution, explicit_propagator, joint_l2_distance,
)
from .hamiltonian_evolution import (
    evolve_precomputed_grid, hamiltonian_evolve_one_step,
    hamiltonian_evolve_tuple_coordinate,
)
from .context import EvaluatorContext


def execute_stateful_evolution(
    context: EvaluatorContext, joint: Any, names: list[str], expr: Any
) -> Any:
    """Retain the historical stateful-evolution entrypoint."""
    return context._legacy_hamiltonian_evolve_one_step(joint, names, expr)
