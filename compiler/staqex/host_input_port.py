"""Host-computed structured classical input port (ADR 0194).

Carries Host-computed, slot-indexed structural data -- never candidate
identity -- into a local Kernel run. First consumer: the
`pairwise_compatible`/`diversity_at_least` selection predicates
(`compiler/staqex/runtime/evaluator.py`'s `project` op), but the port
itself is general-purpose, matching `RngPort`/`MeasureSinkPort`.
"""

from __future__ import annotations

from typing import Any, Mapping, Protocol


class HostInputPort(Protocol):
    """Kernel-side read access to Host-bound named classical values."""

    def get(self, name: str) -> Any | None:
        """Return the bound value for ``name``, or ``None`` if unbound."""
        ...


class MappingHostInputAdapter:
    """Adapter that wraps a plain mapping of bound Host input values."""

    def __init__(self, values: Mapping[str, Any]) -> None:
        self._values = dict(values)

    def get(self, name: str) -> Any | None:
        return self._values.get(name)


__all__ = ["HostInputPort", "MappingHostInputAdapter"]
