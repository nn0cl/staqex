"""Phase 1 Red contracts for ADR-0215 polynomial-fusion hardening."""

from __future__ import annotations

import math

from compiler.staqex.runtime.evaluator import Evaluator


def test_nonzero_tiny_coefficient_is_not_trimmed_from_fused_polynomial() -> None:
    """A finite coefficient remains executable even when it is near zero."""

    composed = Evaluator._compose_poly([0.0, 1.0, 1e-16], [0.0, 1.0])

    assert composed == [0.0, 1.0, 1e-16]


def test_nonfinite_coefficient_fails_before_fused_projection() -> None:
    """Non-finite coefficients must select the safe fallback, not fuse."""

    composed = Evaluator._compose_poly([0.0, 1.0], [0.0, math.inf])

    assert composed is None


if __name__ == "__main__":
    test_nonzero_tiny_coefficient_is_not_trimmed_from_fused_polynomial()
    test_nonfinite_coefficient_fails_before_fused_projection()
    print("RED - polynomial fusion numeric closure is not implemented")
