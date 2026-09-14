"""Call-family entrypoint during the incremental evaluator extraction."""

from __future__ import annotations

from typing import Any

from .context import EvaluatorContext


def bind_call(
    context: EvaluatorContext, joint: Any, name: str, expr: Any
) -> Any:
    """Delegate call binding while preserving frame and RNG behavior."""
    return context._legacy_bind_call(joint, name, expr)
