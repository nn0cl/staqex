"""Scientific grammar entrypoint during incremental extraction."""

from __future__ import annotations

from typing import Any

from .context import ParserContext


def parse_scientific_scope(
    context: ParserContext, *args: Any, **kwargs: Any
) -> Any:
    """Delegate scientific-scope parsing through shared parser state."""
    return context._legacy_parse_scientific_scope(*args, **kwargs)
