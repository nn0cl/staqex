"""Dimension-family entrypoint during incremental extraction."""

from __future__ import annotations

from typing import Any

from .context import TypeCheckContext


def check_assignment(
    context: TypeCheckContext, *args: Any, **kwargs: Any
) -> Any:
    """Delegate dimension/assignment checks through the shared context."""
    return context._legacy_check_dimensions(*args, **kwargs)
