"""Terminal measurement seam for future evaluator extraction units."""

from __future__ import annotations

from typing import Any, Protocol


class MeasurementContext(Protocol):
    """Callbacks needed by pure and mixed terminal measurement."""

    def _measure_mixed(self, joint: Any, stmt: Any) -> Any: ...

    def _emit_measure_text(self, result: Any, *, stdout: Any = None) -> None: ...

    def _emit_sink(self, result: Any) -> None: ...


__all__ = ["MeasurementContext"]
