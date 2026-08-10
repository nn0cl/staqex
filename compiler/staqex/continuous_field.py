"""Continuous field Host port + Kernel-side opaque handle (ADR 0204 / LISS-0399).

`Continuous<T>` values are never Joint-compatible and never evaluated
Kernel-side; the actual continuous function lives entirely behind this
port, on the Host. The Kernel only ever holds a `ContinuousFieldValue`
handle, used for provenance / linear-use bookkeeping.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol


class ContinuousFieldPort(Protocol):
    """Host boundary for injecting and discretizing continuous fields."""

    def field(self, source: str, domain: str) -> str:
        """Return an opaque Host-side reference token for (source, domain)."""
        ...

    def discretize(
        self,
        value: "ContinuousFieldValue",
        *,
        lo: float,
        hi: float,
        n_bins: int,
        seed: int | None,
    ) -> Mapping[Any, float]:
        """Evaluate the composed handle tree Host-side and bucket it
        (ADR 0163 equal-width histogram lineage) into `n_bins` over
        `[lo, hi)`. Returns bin label -> probability mass -- the Kernel
        never evaluates the underlying continuous function itself (LISS-0401).
        """
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


def continuous_pipeline_ops(value: ContinuousFieldValue) -> tuple[str, ...]:
    """Flatten a composed handle tree into an ordered op-name provenance
    list (ADR 0204 Decision 4 `continuous_pipeline`) -- leaves
    (`field_from_host`) excluded, composition ops in application order,
    de-duplicated. Pure Kernel-side bookkeeping; no Host call.
    """
    if not value.inputs:
        return ()
    ops: list[str] = []
    for child in value.inputs:
        ops.extend(continuous_pipeline_ops(child))
    ops.append(value.op)
    seen: set[str] = set()
    out: list[str] = []
    for op in ops:
        if op not in seen:
            seen.add(op)
            out.append(op)
    return tuple(out)


__all__ = ["ContinuousFieldPort", "ContinuousFieldValue", "continuous_pipeline_ops"]
