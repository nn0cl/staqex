"""Phase 1 Red contracts for WP-0167 / LISS-0573 Unit C."""

from __future__ import annotations

import ast
import io
import math
from pathlib import Path

from compiler.staqex.ast_nodes import BinOp, LitInt, Span, Var
from compiler.staqex.run import run_source
from compiler.staqex.runtime.evaluator import Evaluator


ROOT = Path(__file__).resolve().parents[1]
EVALUATOR = ROOT / "compiler/staqex/runtime/evaluator.py"
PIPES = ROOT / "compiler/staqex/runtime/evaluation/pipes.py"
COMPATIBILITY = ROOT / "compiler/staqex/runtime/evaluation/compatibility.py"
CONTEXT = ROOT / "compiler/staqex/runtime/evaluation/context.py"


def _evaluator_method_names() -> set[str]:
    tree = ast.parse(EVALUATOR.read_text(encoding="utf-8"))
    evaluator = next(
        node for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "Evaluator"
    )
    return {
        node.name for node in evaluator.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def test_pipe_successor_file_exists() -> None:
    assert PIPES.is_file()


def test_pipe_and_polynomial_bodies_leave_the_facade() -> None:
    remaining = _evaluator_method_names() & {
        "_bind_block_expr",
        "_try_bind_fused_unary_pipe",
        "_resolve_fuse_stage",
        "_eval_fused_stage",
        "_compose_affine_pipe",
        "_compose_poly_pipe",
        "_eval_poly",
        "_compose_poly",
        "_mul_poly",
        "_add_poly",
        "_is_finite_poly",
        "_trim_exact_zero_tail",
        "_parse_poly",
        "_parse_affine",
        "_flatten_pipe",
        "_fuse_simple_return",
        "_piped_call",
    }
    assert not remaining, sorted(remaining)


def test_pipe_compatibility_wiring_is_declared() -> None:
    source = COMPATIBILITY.read_text(encoding="utf-8")
    for name in (
        "install_pipe_compatibility",
        "try_bind_fused_unary_pipe",
        "bind_block_expr",
        "piped_call",
    ):
        assert name in source


def test_pipe_context_declares_narrow_callbacks() -> None:
    source = CONTEXT.read_text(encoding="utf-8")
    for callback in (
        "_joint_coord_names",
        "_trace_out_dead_fn_locals",
        "_set_fusion_evidence",
    ):
        assert f"def {callback}" in source


def test_pipe_successor_has_no_public_facade_dependency() -> None:
    assert PIPES.is_file()
    source = PIPES.read_text(encoding="utf-8")
    assert "runtime.evaluator" not in source
    assert "from ..evaluator" not in source
    assert "Evaluator(" not in source


def test_bare_block_characterization_remains_successful() -> None:
    result = run_source(
        """
package t
pub fn main() -> Unit {
  State w = {
    let z = 3
    let temp = z * 2
    temp + 5
  }
  Measure w
}
""",
        stdout=io.StringIO(),
    )
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 11


def test_affine_pipe_characterization_remains_successful() -> None:
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


def test_polynomial_pipe_characterization_remains_successful() -> None:
    result = run_source(
        """
package t
fn sq(s: State<Int>) -> State<Int> { return s * s }
fn add1(s: State<Int>) -> State<Int> { return s + 1 }
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


def test_polynomial_non_finite_rejection_characterization_remains_successful() -> None:
    assert Evaluator._compose_poly([0.0, math.inf], [0.0, 1.0]) is None


def test_multi_hole_pipe_characterization_remains_successful() -> None:
    result = run_source(
        """
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
  Measure r
}
""",
        stdout=io.StringIO(),
    )
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 6


def test_affine_parser_characterization_remains_successful() -> None:
    span = Span(0, 0)
    expr = BinOp(
        op="+",
        lhs=BinOp(
            op="*",
            lhs=Var(name="s", span=span),
            rhs=LitInt(value=2, span=span),
            span=span,
        ),
        rhs=LitInt(value=1, span=span),
        span=span,
    )
    assert Evaluator._parse_affine(expr, "s") == (2.0, 1.0)
