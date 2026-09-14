"""Dynamic-lane evaluation seam for future evaluator extraction units."""

from __future__ import annotations

from typing import Any, Protocol


class DynamicEvaluationContext(Protocol):
    """Callbacks needed by dynamic block, reset, and collapse execution."""

    def _run_dynamic_qpu_block(self, joint: Any, stmt: Any) -> Any: ...

    def _reset_dynamic_wire(self, joint: Any, wire: str, span: Any) -> Any: ...

    def _collapse_dynamic_wire(self, joint: Any, wire: str, outcome: str) -> Any: ...


__all__ = ["DynamicEvaluationContext"]
