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
    """Kernel-side opaque handle for a Continuous value -- never a Joint World.

    `host_ref` is set only for a `field_from_host` leaf. `weight`/`mask`
    (LISS-0400) compose existing handles via `inputs`, never touching
    `host_ref` themselves -- the actual pointwise math stays Host-side,
    deferred until `finiteize` (LISS-0401) forces a concrete pass.
    """

    op: str
    host_ref: str | None = None
    inputs: tuple["ContinuousFieldValue", ...] = ()


__all__ = ["ContinuousFieldPort", "ContinuousFieldValue"]
