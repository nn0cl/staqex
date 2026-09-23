"""Phase 1 Red contracts for WP-0167 / LISS-0574 Unit D."""

from __future__ import annotations

import ast
import io
from pathlib import Path

from canonical_execution import run_canonical

from compiler.staqex.ast_nodes import KetLit, Span
from compiler.staqex.host import run_source
from compiler.staqex.pipeline import compile_source
from compiler.staqex.runtime.evaluator import Evaluator
from compiler.staqex.runtime.joint import Joint


ROOT = Path(__file__).resolve().parents[1]
EVALUATOR = ROOT / "compiler/staqex/runtime/evaluator.py"
STATE_OPS = ROOT / "compiler/staqex/runtime/evaluation/state_ops.py"
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


def test_state_ops_successor_file_exists() -> None:
    assert STATE_OPS.is_file()


def test_state_construction_and_algebra_bodies_leave_the_facade() -> None:
    remaining = _evaluator_method_names() & {
        "_bind_ket",
        "_bind_ket_sum_binder",
        "_is_state_producing_bind_expr",
        "_bind_scaled_state",
        "_bind_state_divided_by_norm",
        "_compute_norm",
        "_bind_prepare_selection",
        "_bind_inner",
        "_materialize_outer",
    }
    assert not remaining, sorted(remaining)


def test_state_ops_compatibility_wiring_is_declared() -> None:
    source = COMPATIBILITY.read_text(encoding="utf-8")
    for name in (
        "install_state_ops_compatibility",
        "bind_ket",
        "bind_ket_sum_binder",
        "bind_scaled_state",
        "bind_state_divided_by_norm",
        "compute_norm",
        "bind_prepare_selection",
        "bind_inner",
        "materialize_outer",
    ):
        assert name in source


def test_state_ops_context_declares_narrow_callbacks() -> None:
    source = CONTEXT.read_text(encoding="utf-8")
    for callback in (
        "_bind_ket",
        "_bind_ket_sum_binder",
        "_evaluate_nested_value",
        "_resolve_scientific_binding",
        "_materialize_outer",
    ):
        assert f"def {callback}" in source


def test_state_ops_has_no_public_facade_dependency() -> None:
    assert STATE_OPS.is_file()
    source = STATE_OPS.read_text(encoding="utf-8")
    assert "runtime.evaluator" not in source
    assert "from ..evaluator" not in source
    assert "Evaluator(" not in source


def test_ket_literal_characterization_remains_successful() -> None:
    evaluator = Evaluator(seed=0)
    span = Span(line=1, col=1)
    joint = evaluator._bind_ket(Joint.unit(), "q", KetLit(label="+", span=span))
    assert len(joint.worlds) == 2
    assert abs(sum(abs(world.amp) ** 2 for world in joint.worlds) - 1.0) < 1e-9


def test_prepare_selection_characterization_remains_equal_weighted() -> None:
    result = run_source(
        """
package t
pub fn main() -> Unit {
  State selection = prepare_selection(2)
  Measure selection
}
""",
        settings={"target": "local", "seed": 0},
        stdout=io.StringIO(),
    )
    assert result.status == "succeeded", result.diagnostics
    assert len(result.measurements) == 1
    assert isinstance(result.measurements[0].value, tuple)


def test_inner_characterization_remains_state_to_classical() -> None:
    result = run_source(
        """
package t
pub fn main() -> Unit {
  State a = |+>
  State b = |+>
  State overlap = inner(a, b)
  Measure overlap
}
""",
        settings={"seed": 0},
        stdout=io.StringIO(),
    )
    assert result.status == "succeeded", result.diagnostics


def test_outer_characterization_remains_operator_only() -> None:
    result = run_source(
        """
package t
pub fn main() -> Unit {
  State a = |+>
  State b = |0>
  Operator P = outer(a, b)
  State w = |0>
  State w = apply(P, w)
  Measure w
}
""",
        settings={"seed": 0},
        stdout=io.StringIO(),
    )
    assert result.status == "succeeded", result.diagnostics


def test_bare_sigma_characterization_remains_unnormalized() -> None:
    compiled = compile_source(
        """
package t
pub fn main() -> Unit {
  State psi = Sigma (x In {0,1}^2) { |x> }
  Measure psi
}
"""
    )
    assert compiled.unit is not None, compiled.diagnostics
    result = run_canonical(compiled, Evaluator(seed=0))
    assert result.measure is not None
    assert abs(sum(result.measure.marginal.values()) - 4.0) < 1e-9


def test_explicit_norm_division_characterization_remains_normalizing() -> None:
    compiled = compile_source(
        """
package t
pub fn main() -> Unit {
  State psi = Sigma (x In {0,1}^2) { |x> }
  State normalized = psi / ||psi||
  Measure normalized
}
"""
    )
    assert compiled.unit is not None, compiled.diagnostics
    result = run_canonical(compiled, Evaluator(seed=0))
    assert result.measure is not None
    assert abs(sum(result.measure.marginal.values()) - 1.0) < 1e-9
