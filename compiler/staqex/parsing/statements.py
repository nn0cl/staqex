"""Statement grammar entrypoint during incremental extraction."""

from __future__ import annotations

from typing import Any

from .context import ParserContext


def parse_statement(
    context: ParserContext, *args: Any, **kwargs: Any
) -> Any:
    """Delegate statement parsing through shared parser state."""
    return context._legacy_parse_statement(*args, **kwargs)
