"""Capture deterministic Joint coordinates in the live classical environment."""

from __future__ import annotations

from fractions import Fraction
from typing import MutableMapping, Protocol

from ..joint import Joint


class ClassicalScalarContext(Protocol):
    """Read/write view of the existing owner's scalar environment."""

    scalars: MutableMapping[str, float | Fraction]


def maybe_capture_classical_scalar(
    context: ClassicalScalarContext, joint: Joint, name: str
) -> None:
    """Promote a deterministic classical Joint coordinate into scalars.

        Used when Type-First `Float x = …` was bound via a method Call (not
        `_is_closed`), so `evolve … for x` and Operator OpVars can resolve it
        (LISS-0137).
        """
    if name in context.scalars:
        return
    try:
        marg = joint.marginal(name)
    except Exception:
        return
    if len(marg) != 1:
        return
    raw = next(iter(marg))
    try:
        if isinstance(raw, Fraction):
            context.scalars[name] = raw
        else:
            context.scalars[name] = float(raw)
    except (TypeError, ValueError):
        pass
