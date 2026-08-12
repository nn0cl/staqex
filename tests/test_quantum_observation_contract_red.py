"""AT-TDD Phase 1 Red: typed observation capability boundary (ADR 0189).

These tests intentionally describe the next observation-contract boundary.
They must remain failing until the compiler has a typed observation family and
an explicit capability diagnostic; production code is out of scope for this
phase.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {
        diagnostic.get("code", "")
        for diagnostic in compile_source(source).diagnostics
    }


def test_unsupported_tomography_is_rejected_as_an_observation_capability() -> None:
    """Tomography belongs to the Host protocol lane, not an implicit State call."""

    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            State psi = |+>
            Host report = tomography(psi)
            Measure psi
        }
        """
    )

    assert "OBSERVATION_CAPABILITY_UNSUPPORTED" in codes
    assert "LINEAR_DUPLICATE_USE" not in codes


if __name__ == "__main__":
    test_unsupported_tomography_is_rejected_as_an_observation_capability()
    print("RED - typed observation capability boundary is not implemented")
