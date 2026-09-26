"""Compatibility wiring for incrementally extracted evaluator families."""

from __future__ import annotations

from typing import Any

from .unitary_ops import (
    bind_apply,
    bind_apply_multi,
    bind_capply,
    bind_cnot_multi,
    is_unitary_name,
    qft_family_matrix,
    resolve_unitary_matrix,
    split_capply_args,
)
from .evolution_ops import (
    ExplicitPropagator,
    bind_evolve,
    bind_evolve_hamiltonian,
    bind_explicit_evolve,
    eval_max_steps,
    eval_until_predicate,
    explicit_propagator,
    joint_l2_distance,
)
from .hamiltonian_evolution import (
    evolve_precomputed_grid,
    hamiltonian_evolve_one_step,
    hamiltonian_evolve_tuple_coordinate,
)
from .operators import (
    bind_second_quantized, build_projector_sum_operator, expr_arg_to_source_expr,
    lookup_set_comprehension_value, lower_operator_value, looks_like_operator_rhs,
    operator_array_context, operator_name, resolve_op_call, resolve_operator,
    resolve_operator_factory_call, resolve_operator_method_call, resolve_operator_tree,
)
from .calls import bind_call
from .classical import (
    construct_instance,
    construct_struct,
    evaluate_classical_value,
    evaluate_unit_convert,
    evaluate_value,
    evaluate_value_with_unit,
    attr_field_unit,
    attr_host,
    attr_is_object_field,
    resolve_attribute,
    resolve_receiver_instance,
    apply_value_op,
)
from .classical_calls import (
    eval_classical_call,
    eval_classical_method_call,
    eval_classical_user_fun,
    eval_classical_user_fun_value,
)
from .classical_operator_eval import (
    eval_classical_op_binder,
    eval_op_expr_classical,
)
from .operator_projection import project_onto_operator
from .continuous import (
    bind_continuous_compose,
    bind_field_from_host,
    bind_finiteize,
    bind_finiteize_continuous,
)
from .execution import execute_legacy_ast_body
from .frames import bind_method, bind_user_function
from .binding import bind, bind_names
from .constructors import construct_instance, construct_struct
from .assignments import execute_assignment
from .pipes import (
    add_poly,
    bind_block_expr,
    compose_affine_pipe,
    compose_poly,
    compose_poly_pipe,
    eval_fused_stage,
    eval_poly,
    flatten_pipe,
    fuse_simple_return,
    is_finite_poly,
    mul_poly,
    parse_affine,
    parse_poly,
    piped_call,
    resolve_fuse_stage,
    trim_exact_zero_tail,
    try_bind_fused_unary_pipe,
)
from .state_ops import (
    bind_inner,
    bind_ket,
    bind_ket_sum_binder,
    bind_prepare_selection,
    bind_scaled_state,
    bind_state_divided_by_norm,
    compute_norm,
    is_state_producing_bind_expr,
    materialize_outer,
)


def install_call_compatibility(evaluator_type: type[Any]) -> None:
    """Keep the private call-binding hook during the facade migration."""
    evaluator_type._bind_call = bind_call


def install_binding_compatibility(evaluator_type: type[Any]) -> None:
    """Install binder dispatchers while retaining the Evaluator state owner."""
    evaluator_type._bind_names = bind_names
    evaluator_type._bind = bind


def run_unit_body(
    context: Any, unit: Any, *, stdout: Any = None
) -> Any:
    """Retain the historical unit-body hook during execution extraction."""
    return execute_legacy_ast_body(context, unit, stdout=stdout)


def install_execution_compatibility(evaluator_type: type[Any]) -> None:
    """Install execution successors without retaining facade method bodies."""
    evaluator_type._run_legacy_ast_body = execute_legacy_ast_body
    evaluator_type._run_unit_body = run_unit_body


def install_frame_compatibility(evaluator_type: type[Any]) -> None:
    """Install frame entrypoints behind the evaluator facade."""
    evaluator_type._bind_method = bind_method
    evaluator_type._bind_user_fun = bind_user_function


def install_constructor_compatibility(evaluator_type: type[Any]) -> None:
    """Install class and struct construction successor entrypoints."""
    evaluator_type._construct_instance = construct_instance
    evaluator_type._construct_struct = construct_struct


def install_assignment_compatibility(evaluator_type: type[Any]) -> None:
    """Install the field-assignment successor entrypoint."""
    evaluator_type._execute_assignment = execute_assignment


def install_pipe_compatibility(evaluator_type: type[Any]) -> None:
    """Install pipe and polynomial successors behind legacy helper names."""
    evaluator_type._bind_block_expr = bind_block_expr
    evaluator_type._try_bind_fused_unary_pipe = try_bind_fused_unary_pipe
    evaluator_type._resolve_fuse_stage = resolve_fuse_stage
    evaluator_type._eval_fused_stage = eval_fused_stage
    evaluator_type._compose_affine_pipe = staticmethod(compose_affine_pipe)
    evaluator_type._compose_poly_pipe = staticmethod(compose_poly_pipe)
    evaluator_type._eval_poly = staticmethod(eval_poly)
    evaluator_type._compose_poly = staticmethod(compose_poly)
    evaluator_type._mul_poly = staticmethod(mul_poly)
    evaluator_type._add_poly = staticmethod(add_poly)
    evaluator_type._is_finite_poly = staticmethod(is_finite_poly)
    evaluator_type._trim_exact_zero_tail = staticmethod(trim_exact_zero_tail)
    evaluator_type._parse_poly = staticmethod(parse_poly)
    evaluator_type._parse_affine = staticmethod(parse_affine)
    evaluator_type._flatten_pipe = staticmethod(flatten_pipe)
    evaluator_type._fuse_simple_return = staticmethod(fuse_simple_return)
    evaluator_type._piped_call = staticmethod(piped_call)


def install_state_ops_compatibility(evaluator_type: type[Any]) -> None:
    """Install state construction and algebra successors behind old hooks."""
    evaluator_type._bind_ket = bind_ket
    evaluator_type._bind_ket_sum_binder = bind_ket_sum_binder
    evaluator_type._is_state_producing_bind_expr = staticmethod(
        is_state_producing_bind_expr
    )
    evaluator_type._bind_scaled_state = bind_scaled_state
    evaluator_type._bind_state_divided_by_norm = bind_state_divided_by_norm
    evaluator_type._compute_norm = compute_norm
    evaluator_type._bind_prepare_selection = bind_prepare_selection
    evaluator_type._bind_inner = bind_inner
    evaluator_type._materialize_outer = materialize_outer


def install_classical_compatibility(evaluator_type: type[Any]) -> None:
    """Install classical entrypoints behind the public evaluator facade."""
    evaluator_type._construct_instance = construct_instance
    evaluator_type._construct_struct = construct_struct
    evaluator_type._evaluate_classical_value = evaluate_classical_value
    evaluator_type._eval_classical_op_binder = eval_classical_op_binder
    evaluator_type._eval_op_expr_classical = eval_op_expr_classical


def install_operator_projection_compatibility(evaluator_type: type[Any]) -> None:
    """Retain the call-dispatch hook while projection leaves the facade."""
    evaluator_type._project_onto_operator = project_onto_operator


def install_classical_call_compatibility(evaluator_type: type[Any]) -> None:
    """Install classical call successors behind the existing private hooks."""
    evaluator_type._eval_classical_call = eval_classical_call
    evaluator_type._eval_classical_method_call = eval_classical_method_call
    evaluator_type._eval_classical_user_fun = eval_classical_user_fun
    evaluator_type._eval_classical_user_fun_value = eval_classical_user_fun_value


def install_value_compatibility(evaluator_type: type[Any]) -> None:
    """Install the value successor entrypoints behind legacy names."""
    evaluator_type._evaluate_value_successor = evaluate_value
    evaluator_type._evaluate_value_with_unit_successor = evaluate_value_with_unit
    evaluator_type._resolve_classical_attribute = resolve_attribute
    evaluator_type._eval_value = evaluate_value
    evaluator_type._evaluate_value = evaluate_value
    evaluator_type._legacy_evaluate_value = evaluate_value
    evaluator_type._eval_value_with_unit = evaluate_value_with_unit
    evaluator_type._eval_unit_convert = evaluate_unit_convert
    evaluator_type._attr_host = attr_host
    evaluator_type._attr_is_object_field = attr_is_object_field
    evaluator_type._attr_field_unit = attr_field_unit
    evaluator_type._resolve_receiver_instance = resolve_receiver_instance
    evaluator_type._apply_value_op = staticmethod(apply_value_op)


def install_continuous_compatibility(evaluator_type: type[Any]) -> None:
    """Install continuous binders while preserving private hook identities."""
    evaluator_type._bind_finiteize = bind_finiteize
    evaluator_type._bind_finiteize_continuous = bind_finiteize_continuous
    evaluator_type._bind_field_from_host = bind_field_from_host
    evaluator_type._bind_continuous_compose = bind_continuous_compose


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
    evaluator_type._legacy_hamiltonian_evolve_one_step = hamiltonian_evolve_one_step
    evaluator_type._hamiltonian_evolve_tuple_coordinate = hamiltonian_evolve_tuple_coordinate
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
    for legacy, function in {
        "_operator_legacy_operator_name": operator_name,
        "_operator_legacy_looks_like_operator_rhs": looks_like_operator_rhs,
        "_operator_legacy_resolve_operator": resolve_operator,
        "_operator_legacy_array_context": operator_array_context,
        "_operator_legacy_resolve_op_call": resolve_op_call,
        "_operator_legacy_resolve_operator_tree": resolve_operator_tree,
        "_operator_legacy_lookup_set_comprehension_value": lookup_set_comprehension_value,
        "_operator_legacy_lower_operator_value": lower_operator_value,
        "_operator_legacy_resolve_operator_factory_call": resolve_operator_factory_call,
        "_operator_legacy_resolve_operator_method_call": resolve_operator_method_call,
        "_operator_legacy_bind_second_quantized": bind_second_quantized,
    }.items(): setattr(evaluator_type, legacy, function)
    evaluator_type._operator_name = operator_name
    evaluator_type._looks_like_operator_rhs = looks_like_operator_rhs
    evaluator_type._resolve_operator = resolve_operator
    evaluator_type._legacy_resolve_operator = resolve_operator
    evaluator_type._operator_array_context = operator_array_context
    evaluator_type._op_expr_arg_to_source_expr = staticmethod(expr_arg_to_source_expr)
    evaluator_type._resolve_op_call = resolve_op_call
    evaluator_type._resolve_operator_tree = resolve_operator_tree
    evaluator_type._lookup_set_comprehension_value = lookup_set_comprehension_value
    evaluator_type._build_projector_sum_operator = staticmethod(build_projector_sum_operator)
    evaluator_type._lower_operator_value = lower_operator_value
    evaluator_type._resolve_operator_factory_call = resolve_operator_factory_call
    evaluator_type._resolve_operator_method_call = resolve_operator_method_call
    evaluator_type._bind_second_quantized = bind_second_quantized
