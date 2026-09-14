"""Operator-family entrypoint during the incremental evaluator extraction."""

from __future__ import annotations

from typing import Any

from .context import EvaluatorContext


def resolve_operator(context: EvaluatorContext, expr: Any) -> Any:
    """Delegate operator resolution while preserving evaluator state ownership."""
    return context._legacy_resolve_operator(expr)
