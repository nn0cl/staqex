"""Operator-family entrypoint during incremental extraction."""

from __future__ import annotations

from typing import Any

from .context import TypeCheckContext


def check_operator_expr(
    context: TypeCheckContext, *args: Any, **kwargs: Any
) -> Any:
    """Delegate operator checks without changing diagnostic ownership."""
    return context._legacy_check_operator(*args, **kwargs)
