"""Recovery-family entrypoint during incremental extraction."""

from __future__ import annotations

from typing import Any

from .context import ParserContext


def recover_top_level(
    context: ParserContext, *args: Any, **kwargs: Any
) -> Any:
    """Delegate top-level resynchronization through the shared cursor."""
    return context._legacy_recover_top_level(*args, **kwargs)
