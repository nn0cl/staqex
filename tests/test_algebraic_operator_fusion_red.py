"""AT-TDD: LISS-0173 algebraic Operator Fusion MVP (ADR 0141)."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.ast_nodes import BinOp, LitInt, Span, Var  # noqa: E402
from compiler.staqex.run import run_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402


def test_parse_affine_add_mul_sub() -> None:
    sp = Span(0, 0)
    x = Var(name="s", span=sp)
    # (s + 10) * 2 - 5
    expr = BinOp(
        op="-",
        lhs=BinOp(
            op="*",
            lhs=BinOp(op="+", lhs=x, rhs=LitInt(value=10, span=sp), span=sp),
            rhs=LitInt(value=2, span=sp),
            span=sp,
        ),
        rhs=LitInt(value=5, span=sp),
        span=sp,
    )
    parsed = Evaluator._parse_affine(expr, "s")
    assert parsed == (2.0, 15.0)


def test_affine_pipe_collapses_to_single_map() -> None:
    result = run_source(
        """
        package t
        fn add10(s: State<Int>) -> State<Int> {
            return s + 10
        }
        fn dbl(s: State<Int>) -> State<Int> {
            return s * 2
        }
        fn sub5(s: State<Int>) -> State<Int> {
            return s - 5
        }
        pub fn main() -> Unit {
            State z = 3
            State w = z |> add10 |> dbl |> sub5
            measure w
        }
        """,
        stdout=io.StringIO(),
    )
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    # (3+10)*2-5 = 21
    assert result.eval.measure.value == 21


def test_affine_pipe_matches_sequential() -> None:
    fused_src = """
    package t
    fn add10(s: State<Int>) -> State<Int> { return s + 10 }
    fn dbl(s: State<Int>) -> State<Int> { return s * 2 }
    fn sub5(s: State<Int>) -> State<Int> { return s - 5 }
    pub fn main() -> Unit {
        State z = 7
        State w = z |> add10 |> dbl |> sub5
        measure w
    }
    """
    seq_src = """
    package t
    fn add10(s: State<Int>) -> State<Int> { return s + 10 }
    fn dbl(s: State<Int>) -> State<Int> { return s * 2 }
    fn sub5(s: State<Int>) -> State<Int> { return s - 5 }
    pub fn main() -> Unit {
        State z = 7
        State t1 = add10(z)
        State t2 = dbl(t1)
        State w = sub5(t2)
        measure w
    }
    """
    fused = run_source(fused_src, stdout=io.StringIO())
    sequential = run_source(seq_src, stdout=io.StringIO())
    assert fused.compile_ok and sequential.compile_ok
    assert fused.eval.measure is not None and sequential.eval.measure is not None
    assert fused.eval.measure.value == sequential.eval.measure.value == 29


def test_non_affine_return_still_fuses_sequentially() -> None:
    """`when` return body is not affine; ADR 0137 multi-pass fusion still applies."""
    result = run_source(
        """
        package t
        fn flip(s: State<Int>) -> State<Int> {
            return mix (s) { 0 -> 1, else -> 0 }
        }
        fn id(s: State<Int>) -> State<Int> {
            return s
        }
        pub fn main() -> Unit {
            State x = 0
            State r = x |> flip |> id
            measure r
        }
        """,
        stdout=io.StringIO(),
    )
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 1


if __name__ == "__main__":
    test_parse_affine_add_mul_sub()
    print("PASS test_parse_affine_add_mul_sub")
    test_affine_pipe_collapses_to_single_map()
    print("PASS test_affine_pipe_collapses_to_single_map")
    test_affine_pipe_matches_sequential()
    print("PASS test_affine_pipe_matches_sequential")
    test_non_affine_return_still_fuses_sequentially()
    print("PASS test_non_affine_return_still_fuses_sequentially")
