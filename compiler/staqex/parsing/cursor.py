"""Cursor-family entrypoint during incremental extraction."""

from __future__ import annotations

from typing import Any

from .context import ParserContext


def peek(context: ParserContext, *args: Any, **kwargs: Any) -> Any:
    """Delegate lookahead through the shared parser cursor."""
    return context._peek(*args, **kwargs)
