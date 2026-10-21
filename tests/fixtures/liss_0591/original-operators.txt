"""Operator grammar entrypoint during incremental extraction."""

from __future__ import annotations

from typing import Any

from .context import ParserContext


def parse_operator_expression(
    context: ParserContext, *args: Any, **kwargs: Any
) -> Any:
    """Delegate operator parsing without a second token cursor."""
    return context._legacy_parse_operator_expression(*args, **kwargs)
