"""Evolution-contract entrypoint during incremental extraction."""

from __future__ import annotations

from typing import Any

from .context import TypeCheckContext


def check_evolution(
    context: TypeCheckContext, *args: Any, **kwargs: Any
) -> Any:
    """Delegate Evolve/Suzuki checks through the shared checker context."""
    return context._legacy_check_evolution(*args, **kwargs)
