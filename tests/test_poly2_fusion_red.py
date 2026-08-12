"""AT-TDD: LISS-0190 polynomial ≥2 Operator Fusion (ADR 0157)."""

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


def test_parse_poly_quadratic() -> None:
    sp = Span(0, 0)
    x = Var(name="s", span=sp)
    # s * s + 1
    expr = BinOp(
        op="+",
        lhs=BinOp(op="*", lhs=x, rhs=x, span=sp),
        rhs=LitInt(value=1, span=sp),
        span=sp,
    )
    parsed = Evaluator._parse_poly(expr, "s")
    assert parsed == [1.0, 0.0, 1.0]


def test_quadratic_pipe_collapses_to_single_map() -> None:
    result = run_source(
        """
        package t
        fn sq(s: State<Int>) -> State<Int> {
            return s * s
        }
        fn add1(s: State<Int>) -> State<Int> {
            return s + 1
        }
        pub fn main() -> Unit {
            State z = 3
            State w = z |> sq |> add1
            Measure w
        }
        """,
        stdout=io.StringIO(),
    )
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 10
    assert result.eval.last_poly_fusion == (1.0, 0.0, 1.0)
    assert result.eval.last_algebraic_fusion is None


def test_quadratic_pipe_matches_sequential() -> None:
    fused_src = """
    package t
    fn sq(s: State<Int>) -> State<Int> { return s * s }
    fn dbl(s: State<Int>) -> State<Int> { return s * 2 }
    pub fn main() -> Unit {
        State z = 4
        State w = z |> sq |> dbl
        Measure w
    }
    """
    seq_src = """
    package t
    fn sq(s: State<Int>) -> State<Int> { return s * s }
    fn dbl(s: State<Int>) -> State<Int> { return s * 2 }
    pub fn main() -> Unit {
        State z = 4
        State t1 = sq(z)
        State w = dbl(t1)
        Measure w
    }
    """
    fused = run_source(fused_src, stdout=io.StringIO())
    sequential = run_source(seq_src, stdout=io.StringIO())
    assert fused.compile_ok and sequential.compile_ok
    assert fused.eval.measure is not None and sequential.eval.measure is not None
    assert fused.eval.measure.value == sequential.eval.measure.value == 32
    assert fused.eval.last_poly_fusion == (0.0, 0.0, 2.0)


def test_affine_still_records_algebraic_fusion() -> None:
    result = run_source(
        """
        package t
        fn add10(s: State<Int>) -> State<Int> { return s + 10 }
        fn dbl(s: State<Int>) -> State<Int> { return s * 2 }
        pub fn main() -> Unit {
            State z = 3
            State w = z |> add10 |> dbl
            Measure w
        }
        """,
        stdout=io.StringIO(),
    )
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 26
    assert result.eval.last_algebraic_fusion == (2.0, 20.0)
    assert result.eval.last_poly_fusion is None


def test_when_return_still_fuses_sequentially() -> None:
    result = run_source(
        """
        package t
        fn flip(s: State<Int>) -> State<Int> {
            return Mix (s) { 0 -> 1, else -> 0 }
        }
        fn id(s: State<Int>) -> State<Int> {
            return s
        }
        pub fn main() -> Unit {
            State x = 0
            State r = x |> flip |> id
            Measure r
        }
        """,
        stdout=io.StringIO(),
    )
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 1
    assert result.eval.last_poly_fusion is None


if __name__ == "__main__":
    test_parse_poly_quadratic()
    test_quadratic_pipe_collapses_to_single_map()
    test_quadratic_pipe_matches_sequential()
    test_affine_still_records_algebraic_fusion()
    test_when_return_still_fuses_sequentially()
    print("ok")
