"""AT-TDD: LISS-0165 pipeline leftmost hole fill (ADR 0133)."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.run import run_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {d.get("code", "") for d in compile_source(source).diagnostics}


def test_pipe_fills_leftmost_hole() -> None:
    src = """
    package t
    fn second(x: State<Bit>, y: State<Bit>) -> State<Bit> {
        State x = |0>
        return y
    }
    pub fn main() -> Unit {
        State z = |0>
        State w = |1>
        State r = w |> second(z, _)
        measure r
    }
    """
    codes = _codes(src)
    assert "PARSE_ERROR" not in codes, codes
    assert "FUNCTION_ARITY_ERROR" not in codes, codes
    result = run_source(src, stdout=io.StringIO())
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 1


def test_pipe_into_two_holes_yields_partial() -> None:
    src = """
    package t
    fn second(x: State<Bit>, y: State<Bit>) -> State<Bit> {
        State x = |0>
        return y
    }
    pub fn main() -> Unit {
        State a = |1>
        State p = a |> second(_, _)
        State a = |0>
        State w = |0>
        State r = w |> p
        measure r
    }
    """
    codes = _codes(src)
    assert "FUNCTION_ARITY_ERROR" not in codes, codes
    assert "PIPE_CALLABLE_ERROR" not in codes, codes
    result = run_source(src, stdout=io.StringIO())
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 0


if __name__ == "__main__":
    test_pipe_fills_leftmost_hole()
    print("PASS test_pipe_fills_leftmost_hole")
    test_pipe_into_two_holes_yields_partial()
    print("PASS test_pipe_into_two_holes_yields_partial")
