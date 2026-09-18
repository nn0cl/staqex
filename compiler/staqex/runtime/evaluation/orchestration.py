"""Evaluator orchestration behind the public runtime facade.

This module selects the compile-owned runtime-plan family and invokes the
corresponding callback on the single live ``Evaluator`` state owner.  It does
not copy runtime maps or create another evaluator.
"""

from __future__ import annotations

from typing import Any, TextIO

from ...ast_nodes import CompilationUnit
from .context import EvaluatorContext


def execute_canonical_unit(
    context: EvaluatorContext,
    unit: CompilationUnit,
    semantic_ir: Any,
    *,
    stdout: TextIO | None = None,
) -> Any:
    """Build the canonical runtime plan and route it through this boundary."""

    from ...scientific_semantic_ir import build_runtime_execution_plan

    plan = build_runtime_execution_plan(semantic_ir)
    return dispatch_runtime_plan(context, plan, unit, stdout=stdout)


def dispatch_runtime_plan(
    context: EvaluatorContext,
    plan: Any,
    unit: CompilationUnit,
    *,
    stdout: TextIO | None = None,
) -> Any:
    """Select a runtime-plan family without taking ownership of its state."""

    family_handlers = {
        "evolution": execute_evolution_plan,
        "control_mixture": execute_control_mixture_plan,
        "pure_transformation": execute_pure_transformation_plan,
        "binder": execute_binder_plan,
        "callable": execute_callable_plan,
        "dynamic_lane": execute_dynamic_lane_plan,
    }
    handler = family_handlers.get(getattr(plan, "family", None))
    if handler is not None:
        return handler(context, plan, unit, stdout=stdout)
    if context._is_first_runtime_family(unit, plan):
        return context._execute_first_runtime_family(unit, stdout=stdout)
    return context._run_legacy_ast_body(unit, stdout=stdout)


def _require_runtime_plan_family(
    context: EvaluatorContext,
    plan: Any,
    family: str,
    payload_name: str,
) -> None:
    """Validate one plan family before entering shared runtime mechanics."""

    context._require_runtime_plan_family(plan, family, payload_name)


def execute_pure_transformation_plan(
    context: EvaluatorContext,
    plan: Any,
    unit: CompilationUnit,
    *,
    stdout: TextIO | None = None,
) -> Any:
    """Execute canonical pure transformations before terminal Measure."""

    _require_runtime_plan_family(context, plan, "pure_transformation", "transformations")
    return context._execute_deferred_state_measure_plan(unit, stdout=stdout)


def execute_control_mixture_plan(
    context: EvaluatorContext,
    plan: Any,
    unit: CompilationUnit,
    *,
    stdout: TextIO | None = None,
) -> Any:
    """Execute canonical single-level control mixtures."""

    _require_runtime_plan_family(context, plan, "control_mixture", "controls")
    if not context._main_deferred_eligible(
        unit.main.body.stmts if unit.main else []
    ):
        return context._run_legacy_ast_body(unit, stdout=stdout)
    return context._execute_deferred_state_measure_plan(unit, stdout=stdout)


def execute_evolution_plan(
    context: EvaluatorContext,
    plan: Any,
    unit: CompilationUnit,
    *,
    stdout: TextIO | None = None,
) -> Any:
    """Execute canonical local evolution before terminal Measure."""

    _require_runtime_plan_family(context, plan, "evolution", "evolutions")
    if not context._is_minimal_local_evolution(unit):
        return context._run_legacy_ast_body(unit, stdout=stdout)
    return context._execute_deferred_state_measure_plan(
        context._evolution_runtime_unit(unit), stdout=stdout
    )


def execute_binder_plan(
    context: EvaluatorContext,
    plan: Any,
    unit: CompilationUnit,
    *,
    stdout: TextIO | None = None,
) -> Any:
    """Execute the bounded local State/Measure slice around an operator binder."""

    _require_runtime_plan_family(context, plan, "binder", "binders")
    if unit.main is None or not context._main_deferred_eligible(unit.main.body.stmts):
        return context._run_legacy_ast_body(unit, stdout=stdout)
    return context._execute_deferred_state_measure_plan(
        context._binder_runtime_unit(unit), stdout=stdout
    )


def execute_callable_plan(
    context: EvaluatorContext,
    plan: Any,
    unit: CompilationUnit,
    *,
    stdout: TextIO | None = None,
) -> Any:
    """Execute the bounded local callable/object State/Measure slice."""

    _require_runtime_plan_family(context, plan, "callable", "callables")
    if not context._is_deferred_callable_eligible(unit):
        return context._run_legacy_ast_body(unit, stdout=stdout)
    return context._execute_deferred_state_measure_plan(unit, stdout=stdout)


def execute_dynamic_lane_plan(
    context: EvaluatorContext,
    plan: Any,
    unit: CompilationUnit,
    *,
    stdout: TextIO | None = None,
) -> Any:
    """Execute dynamic lanes through the existing capability-gated path."""

    _require_runtime_plan_family(context, plan, "dynamic_lane", "dynamic_lanes")
    return context._run_legacy_ast_body(unit, stdout=stdout)
