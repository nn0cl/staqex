"""Top-level grammar entrypoint during incremental extraction."""

from __future__ import annotations

from typing import Any

from .context import ParserContext


def parse_declaration(
    context: ParserContext, *args: Any, **kwargs: Any
) -> Any:
    """Delegate declaration parsing without duplicating parser state."""
    return context._legacy_parse_declaration(*args, **kwargs)
