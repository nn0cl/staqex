"""Continuous field Host port + Kernel-side opaque handle (ADR 0204 / LISS-0399).

`Continuous<T>` values are never Joint-compatible and never evaluated
Kernel-side; the actual continuous function lives entirely behind this
port, on the Host. The Kernel only ever holds a `ContinuousFieldValue`
handle, used for provenance / linear-use bookkeeping.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class ContinuousFieldPort(Protocol):
    """Host boundary for injecting a named continuous field description."""

    def field(self, source: str, domain: str) -> str:
        """Return an opaque Host-side reference token for (source, domain)."""
        ...


@dataclass(frozen=True)
class ContinuousFieldValue:
    """Kernel-side opaque handle for a Continuous value -- never a Joint World."""

    op: str
    host_ref: str


__all__ = ["ContinuousFieldPort", "ContinuousFieldValue"]
