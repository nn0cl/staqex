"""Expression-inference entrypoint during incremental extraction."""

from __future__ import annotations

from typing import Any

from .context import TypeCheckContext


def infer_expression(
    context: TypeCheckContext, *args: Any, **kwargs: Any
) -> Any:
    """Delegate inference while keeping the TypeChecker environment authoritative."""
    return context._legacy_infer_expression(*args, **kwargs)
