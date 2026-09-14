"""Runtime-plan family selection, independent of Evaluator state storage."""

from __future__ import annotations

from typing import Any, TextIO

from ...ast_nodes import CompilationUnit
from .context import EvaluatorContext


def dispatch_runtime_plan(
    context: EvaluatorContext,
    plan: Any,
    unit: CompilationUnit,
    *,
    stdout: TextIO | None = None,
) -> Any:
    """Select a runtime-plan family and invoke the owning context callback."""
    family_handlers = {
        "evolution": context._execute_evolution_plan,
        "control_mixture": context._execute_control_mixture_plan,
        "pure_transformation": context._execute_pure_transformation_plan,
        "binder": context._execute_binder_plan,
        "callable": context._execute_callable_plan,
        "dynamic_lane": context._execute_dynamic_lane_plan,
    }
    handler = family_handlers.get(getattr(plan, "family", None))
    if handler is not None:
        return handler(plan, unit, stdout=stdout)
    if context._is_first_runtime_family(unit, plan):
        return context._execute_first_runtime_family(unit, stdout=stdout)
    return context._run_legacy_ast_body(unit, stdout=stdout)
