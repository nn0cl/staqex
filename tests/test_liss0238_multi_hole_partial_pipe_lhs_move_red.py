"""AT-TDD: LISS-0238 multi-hole Partial pipe moves lhs (ADR 0149)."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.run import run_source  # noqa: E402


def test_pipe_into_multi_hole_partial_moves_lhs() -> None:
    """`x |> p` with p still multi-hole must not LINEAR_IMPLICIT_DISCARD x."""
    src = """
    package t
    fn add3(a: State<Int>, b: State<Int>, c: State<Int>) -> State<Int> {
        return a + b + c
    }
    pub fn main() -> Unit {
        State p = add3(1, _, _)
        State x = 2
        State q = x |> p
        State y = 3
        State r = y |> q
        measure r
    }
    """
    codes = {d.get("code", "") for d in compile_source(src).diagnostics}
    assert "LINEAR_IMPLICIT_DISCARD" not in codes, codes
    assert "PARSE_ERROR" not in codes, codes

    result = run_source(src, stdout=io.StringIO())
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 6


def test_one_hole_partial_pipe_still_moves() -> None:
    src = """
    package t
    fn add(x: State<Int>, y: State<Int>) -> State<Int> {
        return x + y
    }
    pub fn main() -> Unit {
        State p = add(10, _)
        State z = 3
        State r = z |> p
        measure r
    }
    """
    codes = {d.get("code", "") for d in compile_source(src).diagnostics}
    assert "LINEAR_IMPLICIT_DISCARD" not in codes, codes
    result = run_source(src, stdout=io.StringIO())
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 13


if __name__ == "__main__":
    test_pipe_into_multi_hole_partial_moves_lhs()
    print("PASS multi-hole move")
    test_one_hole_partial_pipe_still_moves()
    print("PASS one-hole")
    print("OK — LISS-0238")
