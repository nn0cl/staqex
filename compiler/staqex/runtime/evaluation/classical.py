"""Classical/value successor boundary for the evaluator runtime."""

from __future__ import annotations

from typing import Any

from .context import EvaluatorContext


def evaluate_classical_value(
    context: EvaluatorContext, expr: Any, assign: dict[str, Any]
) -> Any:
    """Evaluate a classical value using the evaluator-owned compatibility body."""
    return context._legacy_evaluate_value(expr, assign)


def construct_instance(
    context: EvaluatorContext, class_name: str, expr: Any
) -> Any:
    """Construct a class instance without taking ownership of runtime state."""
    return context._legacy_construct_instance(class_name, expr)


def construct_struct(
    context: EvaluatorContext,
    struct_name: str,
    expr: Any,
    assign: dict[str, Any] | None = None,
) -> Any:
    """Construct a struct through the evaluator-owned value environment."""
    return context._legacy_construct_struct(struct_name, expr, assign)
