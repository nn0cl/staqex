"""Declaration-family entrypoint during incremental extraction."""

from __future__ import annotations

from typing import Any

from .context import TypeCheckContext


def check_declaration(context: TypeCheckContext, *args: Any, **kwargs: Any) -> Any:
    """Delegate declaration checks without copying checker state."""
    return context._legacy_check_declaration(*args, **kwargs)
