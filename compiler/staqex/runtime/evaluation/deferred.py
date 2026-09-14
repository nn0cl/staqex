"""Deferred execution seam for future evaluator extraction units.

This module intentionally contains only contracts in the first dispatch slice;
materialization remains implemented by the single Evaluator state owner until
its separately reviewed extraction.
"""

from __future__ import annotations

from typing import Any, Protocol

from ...ast_nodes import CompilationUnit


class DeferredExecutionContext(Protocol):
    """Callbacks needed by deferred-cone analysis and materialization."""

    def _main_deferred_eligible(self, stmts: list[Any]) -> bool: ...

    def _deferred_bind_cone(self, unit: CompilationUnit) -> set[str]: ...


__all__ = ["DeferredExecutionContext"]
