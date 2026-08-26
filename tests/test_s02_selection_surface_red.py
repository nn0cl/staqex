"""AT-TDD Phase 1 Red: S02 selection surface and control taxonomy.

These tests intentionally describe the reviewed future surface. They must fail
against the current v1 compiler until a later Phase 2 implementation is
approved. No production fallback from ``when`` to ``Mix`` is permitted.
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
        str(diagnostic.get("code", ""))
        for diagnostic in compile_source(source).diagnostics
    }


def test_removed_when_fails_without_mix_fallback() -> None:
    source = """
    package s02
    pub fn main() -> Unit {
      State control = Coin()
      State result = when (control) {
        0 -> |0>,
        1 -> |1>,
      }
      Measure result
    }
    """

    codes = _codes(source)

    assert "RETIRED_KEYWORD" in codes
    assert "MIX_FALLBACK" not in codes


def test_mix_is_the_state_valued_non_collapsing_surface() -> None:
    source = """
    package s02
    pub fn main() -> Unit {
      State control = Coin()
      State result = Mix (control) {
        0 -> |0>,
        1 -> |1>,
      }
      Measure result
    }
    """

    compiled = compile_source(source)

    assert compiled.ok, compiled.diagnostics
    assert compiled.state_transform_plan is not None
    kinds = [step.kind for step in compiled.state_transform_plan.steps]
    assert "Mixture" in kinds
    assert "TerminalMeasure" in kinds


def test_controlled_is_not_lowered_to_mixture() -> None:
    source = """
    package s02
    pub fn main() -> Unit {
      State control = |+>
      State target = |0>
      State result = controlled(control, Hadamard, target)
      Measure result
    }
    """

    compiled = compile_source(source)

    assert compiled.ok, compiled.diagnostics
    assert compiled.state_transform_plan is not None
    kinds = [step.kind for step in compiled.state_transform_plan.steps]
    assert "CoherentControl" in kinds
    assert "Mixture" not in kinds


if __name__ == "__main__":
    test_removed_when_fails_without_mix_fallback()
    test_mix_is_the_state_valued_non_collapsing_surface()
    test_controlled_is_not_lowered_to_mixture()
    print("RED — S02 selection surface")
