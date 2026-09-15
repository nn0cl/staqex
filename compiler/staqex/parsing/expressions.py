"""Expression grammar entrypoint during incremental extraction."""

from __future__ import annotations

from typing import Any

from .context import ParserContext


def parse_expression(
    context: ParserContext, *args: Any, **kwargs: Any
) -> Any:
    """Delegate expression parsing through shared parser state."""
    return context._legacy_parse_expression(*args, **kwargs)
