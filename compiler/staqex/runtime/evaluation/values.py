"""Value-family entrypoint during the incremental evaluator extraction."""

from __future__ import annotations

from typing import Any

from .context import EvaluatorContext


def evaluate_value(
    context: EvaluatorContext, expr: Any, assign: dict[str, Any]
) -> Any:
    """Delegate value evaluation while the compatibility facade is active."""
    return context._legacy_evaluate_value(expr, assign)
