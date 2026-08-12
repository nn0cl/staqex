"""AT-TDD: LISS-0200 — single HARD_CODES set; run_source refuses hard programs."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex import pipeline as pipeline_mod  # noqa: E402
from compiler.staqex import run as run_mod  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.run import run_source  # noqa: E402


EFFECT_SRC = """
package t
fn inspect_state(x: State<Float>) -> State<Float> effects { Inspect } {
    return Inspect(x)
}
fn pure_wrapper(x: State<Float>) -> State<Float> {
    return inspect_state(x)
}
pub fn main() -> Unit {
    State psi = Dirac(0.0)
    State viewed = pure_wrapper(psi)
    Measure viewed
}
"""


def test_hard_codes_are_one_object() -> None:
    assert run_mod.HARD_CODES is pipeline_mod.HARD_CODES
    assert "EFFECT_VIOLATION_ERROR" in pipeline_mod.HARD_CODES
    assert "CONFIG_HARVEST_COLLISION_ERROR" in pipeline_mod.HARD_CODES
    assert "LINEAR_IMPLICIT_DISCARD" in pipeline_mod.HARD_CODES


def test_run_source_refuses_effect_violation() -> None:
    compiled = compile_source(EFFECT_SRC)
    assert compiled.ok is False
    result = run_source(EFFECT_SRC, stdout=io.StringIO())
    assert result.compile_ok is False
    assert result.eval.measure is None
    assert any(d.get("code") == "EFFECT_VIOLATION_ERROR" for d in result.diagnostics)


def main() -> None:
    test_hard_codes_are_one_object()
    print("PASS test_hard_codes_are_one_object")
    test_run_source_refuses_effect_violation()
    print("PASS test_run_source_refuses_effect_violation")
    print("OK - LISS-0200")


if __name__ == "__main__":
    main()
