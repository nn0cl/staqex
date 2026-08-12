"""AT-TDD: LISS-0169 thin pipeline Operator Fusion MVP (ADR 0137)."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.run import run_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402
from compiler.staqex.ast_nodes import Pipe, Var  # noqa: E402


def test_fused_unary_pipe_matches_sequential() -> None:
    fused_src = """
    package t
    fn double(x: State<Int>) -> State<Int> {
        return x * 2
    }
    fn inc(x: State<Int>) -> State<Int> {
        return x + 1
    }
    pub fn main() -> Unit {
        State x = 3
        State r = x |> double |> inc
        measure r
    }
    """
    seq_src = """
    package t
    fn double(x: State<Int>) -> State<Int> {
        return x * 2
    }
    fn inc(x: State<Int>) -> State<Int> {
        return x + 1
    }
    pub fn main() -> Unit {
        State x = 3
        State t = double(x)
        State r = inc(t)
        measure r
    }
    """
    fused = run_source(fused_src, stdout=io.StringIO())
    sequential = run_source(seq_src, stdout=io.StringIO())
    assert fused.compile_ok, fused.diagnostics
    assert sequential.compile_ok, sequential.diagnostics
    assert fused.eval.measure is not None
    assert sequential.eval.measure is not None
    assert fused.eval.measure.value == sequential.eval.measure.value == 7


def test_flatten_pipe_helper() -> None:
    # Synthetic: (x |> f) |> g
    from compiler.staqex.ast_nodes import Span

    sp = Span(0, 0)
    x = Var(name="x", span=sp)
    f = Var(name="f", span=sp)
    g = Var(name="g", span=sp)
    chain = Pipe(lhs=Pipe(lhs=x, rhs=f, span=sp), rhs=g, span=sp)
    base, stages = Evaluator._flatten_pipe(chain)
    assert isinstance(base, Var) and base.name == "x"
    assert [s.name for s in stages if isinstance(s, Var)] == ["f", "g"]


def test_non_unary_bare_pipe_still_arity_error() -> None:
    codes = {
        d.get("code", "")
        for d in compile_source(
            """
            package t
            fn second(x: State<Bit>, y: State<Bit>) -> State<Bit> {
                return y
            }
            pub fn main() -> Unit {
                State a = |0>
                State r = a |> second
                measure r
            }
            """
        ).diagnostics
    }
    assert "FUNCTION_ARITY_ERROR" in codes or "PIPE_CALLABLE_ERROR" in codes


if __name__ == "__main__":
    test_flatten_pipe_helper()
    print("PASS test_flatten_pipe_helper")
    test_fused_unary_pipe_matches_sequential()
    print("PASS test_fused_unary_pipe_matches_sequential")
    test_non_unary_bare_pipe_still_arity_error()
    print("PASS test_non_unary_bare_pipe_still_arity_error")
