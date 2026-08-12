"""AT-TDD: LISS-0175 Call/Partial pipe Fusion MVP (ADR 0143)."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.run import run_source  # noqa: E402


def test_call_with_hole_pipe_chain_fuses() -> None:
    fused = run_source(
        """
        package t
        fn add(x: State<Int>, y: State<Int>) -> State<Int> {
            return x + y
        }
        fn dbl(s: State<Int>) -> State<Int> {
            return s * 2
        }
        pub fn main() -> Unit {
            State z = 3
            State r = z |> add(10, _) |> dbl
            measure r
        }
        """,
        stdout=io.StringIO(),
    )
    sequential = run_source(
        """
        package t
        fn add(x: State<Int>, y: State<Int>) -> State<Int> {
            return x + y
        }
        fn dbl(s: State<Int>) -> State<Int> {
            return s * 2
        }
        pub fn main() -> Unit {
            State z = 3
            State t = add(10, z)
            State r = dbl(t)
            measure r
        }
        """,
        stdout=io.StringIO(),
    )
    assert fused.compile_ok, fused.diagnostics
    assert sequential.compile_ok, sequential.diagnostics
    assert fused.eval.measure is not None and sequential.eval.measure is not None
    assert fused.eval.measure.value == sequential.eval.measure.value == 26


def test_partial_var_pipe_chain_fuses() -> None:
    result = run_source(
        """
        package t
        fn add(x: State<Int>, y: State<Int>) -> State<Int> {
            return x + y
        }
        fn dbl(s: State<Int>) -> State<Int> {
            return s * 2
        }
        pub fn main() -> Unit {
            State p = add(10, _)
            State z = 3
            State r = z |> p |> dbl
            measure r
        }
        """,
        stdout=io.StringIO(),
    )
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 26


def test_bare_unary_fusion_still_works() -> None:
    result = run_source(
        """
        package t
        fn double(x: State<Int>) -> State<Int> { return x * 2 }
        fn inc(x: State<Int>) -> State<Int> { return x + 1 }
        pub fn main() -> Unit {
            State x = 3
            State r = x |> double |> inc
            measure r
        }
        """,
        stdout=io.StringIO(),
    )
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 7


if __name__ == "__main__":
    test_call_with_hole_pipe_chain_fuses()
    print("PASS test_call_with_hole_pipe_chain_fuses")
    test_partial_var_pipe_chain_fuses()
    print("PASS test_partial_var_pipe_chain_fuses")
    test_bare_unary_fusion_still_works()
    print("PASS test_bare_unary_fusion_still_works")
