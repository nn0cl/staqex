"""Operator-family entrypoint during the incremental evaluator extraction."""

from __future__ import annotations

from typing import Any

from .context import EvaluatorContext


def resolve_operator(
    context: EvaluatorContext,
    expr: Any,
    *,
    objects: dict[str, Any] | None = None,
    extra_arrays: dict[str, Any] | None = None,
) -> Any:
    """Delegate operator resolution while preserving evaluator state ownership."""
    return context._legacy_resolve_operator(
        expr, objects=objects, extra_arrays=extra_arrays
    )
