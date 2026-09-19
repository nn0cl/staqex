"""Compatibility wiring for incrementally extracted evaluator families."""

from __future__ import annotations

from typing import Any

from .evolution import (
    bind_apply,
    bind_capply,
    bind_apply_multi,
    bind_cnot_multi,
    bind_evolve,
    bind_evolve_hamiltonian,
    bind_explicit_evolve,
    eval_max_steps,
    eval_until_predicate,
    evolve_precomputed_grid,
    hamiltonian_evolve_one_step,
    hamiltonian_evolve_tuple_coordinate,
    is_unitary_name,
    qft_family_matrix,
    resolve_unitary_matrix,
    split_capply_args,
    joint_l2_distance,
    explicit_propagator,
)
from .operators import build_projector_sum_operator, expr_arg_to_source_expr


def install_evolution_compatibility(evaluator_type: type[Any]) -> None:
    """Keep legacy evolution names available without facade method bodies."""

    evaluator_type._bind_apply_multi = bind_apply_multi
    evaluator_type._bind_evolve = bind_evolve
    evaluator_type._bind_explicit_evolve = bind_explicit_evolve
    evaluator_type._explicit_propagator = staticmethod(explicit_propagator)
    evaluator_type._eval_max_steps = eval_max_steps
    evaluator_type._eval_until_predicate = eval_until_predicate
    evaluator_type._joint_l2_distance = staticmethod(joint_l2_distance)
    evaluator_type._bind_evolve_hamiltonian = bind_evolve_hamiltonian
    evaluator_type._legacy_hamiltonian_evolve_one_step = (
        hamiltonian_evolve_one_step
    )
    evaluator_type._hamiltonian_evolve_tuple_coordinate = (
        hamiltonian_evolve_tuple_coordinate
    )
    evaluator_type._evolve_precomputed_grid = evolve_precomputed_grid
    evaluator_type._resolve_unitary_matrix = resolve_unitary_matrix
    evaluator_type._qft_family_matrix = qft_family_matrix
    evaluator_type._bind_apply = bind_apply
    evaluator_type._is_unitary_name = is_unitary_name
    evaluator_type._split_capply_args = split_capply_args
    evaluator_type._bind_cnot_multi = bind_cnot_multi
    evaluator_type._bind_capply = bind_capply


def install_operator_compatibility(evaluator_type: type[Any]) -> None:
    """Keep legacy operator names available without facade method bodies."""

    evaluator_type._operator_name = evaluator_type._operator_legacy_operator_name
    evaluator_type._looks_like_operator_rhs = (
        evaluator_type._operator_legacy_looks_like_operator_rhs
    )
    evaluator_type._legacy_resolve_operator = (
        evaluator_type._operator_legacy_resolve_operator
    )
    evaluator_type._operator_array_context = evaluator_type._operator_legacy_array_context
    evaluator_type._op_expr_arg_to_source_expr = staticmethod(expr_arg_to_source_expr)
    evaluator_type._resolve_op_call = evaluator_type._operator_legacy_resolve_op_call
    evaluator_type._resolve_operator_tree = (
        evaluator_type._operator_legacy_resolve_operator_tree
    )
    evaluator_type._lookup_set_comprehension_value = (
        evaluator_type._operator_legacy_lookup_set_comprehension_value
    )
    evaluator_type._build_projector_sum_operator = staticmethod(
        build_projector_sum_operator
    )
    evaluator_type._lower_operator_value = (
        evaluator_type._operator_legacy_lower_operator_value
    )
    evaluator_type._resolve_operator_factory_call = (
        evaluator_type._operator_legacy_resolve_operator_factory_call
    )
    evaluator_type._resolve_operator_method_call = (
        evaluator_type._operator_legacy_resolve_operator_method_call
    )
    evaluator_type._bind_second_quantized = (
        evaluator_type._operator_legacy_bind_second_quantized
    )
