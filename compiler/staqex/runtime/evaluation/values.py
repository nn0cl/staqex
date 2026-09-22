"""Value-family entrypoint during the incremental evaluator extraction."""

from __future__ import annotations

from typing import Any

from .context import EvaluatorContext
from .classical import evaluate_value as evaluate_classical_value


def evaluate_value(
    context: EvaluatorContext, expr: Any, assign: dict[str, Any]
) -> Any:
    """Delegate value evaluation while the compatibility facade is active."""
    return evaluate_classical_value(context, expr, assign)
