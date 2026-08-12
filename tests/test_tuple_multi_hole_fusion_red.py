"""AT-TDD: LISS-0184 tuple multi-hole pipe / Fusion fill (ADR 0152)."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.run import run_source  # noqa: E402


def test_tuple_fills_multi_hole_call() -> None:
    result = run_source(
        """
        package t
        fn add(x: State<Int>, y: State<Int>) -> State<Int> {
            return x + y
        }
        pub fn main() -> Unit {
            State r = (1, 2) |> add(_, _)
            measure r
        }
        """,
        stdout=io.StringIO(),
    )
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 3


def test_tuple_multi_hole_then_fuse_chain() -> None:
    fused = run_source(
        """
        package t
        fn add(x: State<Int>, y: State<Int>) -> State<Int> {
            return x + y
        }
        fn dbl(s: State<Int>) -> State<Int> {
            return s * 2
        }
        fn inc(s: State<Int>) -> State<Int> {
            return s + 1
        }
        pub fn main() -> Unit {
            State r = (10, 3) |> add(_, _) |> dbl |> inc
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
        fn inc(s: State<Int>) -> State<Int> {
            return s + 1
        }
        pub fn main() -> Unit {
            State t = add(10, 3)
            State u = dbl(t)
            State r = inc(u)
            measure r
        }
        """,
        stdout=io.StringIO(),
    )
    assert fused.compile_ok, fused.diagnostics
    assert sequential.compile_ok, sequential.diagnostics
    assert fused.eval.measure is not None and sequential.eval.measure is not None
    assert fused.eval.measure.value == sequential.eval.measure.value == 27


def test_tuple_fills_multi_hole_partial() -> None:
    result = run_source(
        """
        package t
        fn add(x: State<Int>, y: State<Int>) -> State<Int> {
            return x + y
        }
        pub fn main() -> Unit {
            State p = add(_, _)
            State r = (4, 5) |> p
            measure r
        }
        """,
        stdout=io.StringIO(),
    )
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 9


def test_one_hole_call_fusion_regression() -> None:
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
            State z = 3
            State r = z |> add(10, _) |> dbl
            measure r
        }
        """,
        stdout=io.StringIO(),
    )
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 26


if __name__ == "__main__":
    test_tuple_fills_multi_hole_call()
    print("PASS test_tuple_fills_multi_hole_call")
    test_tuple_multi_hole_then_fuse_chain()
    print("PASS test_tuple_multi_hole_then_fuse_chain")
    test_tuple_fills_multi_hole_partial()
    print("PASS test_tuple_fills_multi_hole_partial")
    test_one_hole_call_fusion_regression()
    print("PASS test_one_hole_call_fusion_regression")
