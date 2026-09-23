"""Phase 1 Red contracts for WP-0163 / LISS-0566-D Unit D."""

from __future__ import annotations

import ast
import importlib
import inspect
from pathlib import Path

from compiler.staqex.host import run_source
from compiler.staqex.runtime.evaluator import Evaluator


ROOT = Path(__file__).resolve().parents[1]
EVALUATOR = ROOT / "compiler/staqex/runtime/evaluator.py"
PACKAGE = "compiler.staqex.runtime.evaluation"


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


def test_unit_d_calls_module_exposes_bounded_successor_entrypoints() -> None:
    calls = importlib.import_module(f"{PACKAGE}.calls")
    for name in ("bind_call", "resolve_call_target", "bind_function_call", "bind_method_call"):
        assert callable(getattr(calls, name, None)), name


def test_unit_d_call_binding_body_leaves_the_evaluator_facade() -> None:
    assert "_legacy_bind_call" not in _evaluator_method_names()


def test_unit_d_call_entrypoint_does_not_delegate_to_legacy_body() -> None:
    calls = importlib.import_module(f"{PACKAGE}.calls")
    source = inspect.getsource(calls)
    assert "_legacy_bind_call" not in source


def test_unit_d_context_declares_frame_and_receiver_callbacks() -> None:
    context = inspect.getsource(importlib.import_module(f"{PACKAGE}.context"))
    for callback in (
        "_current_receiver",
        "_set_current_receiver",
        "_resolve_receiver_instance",
        "_execute_assignment",
        "_function_environment",
        "_object_environment",
    ):
        assert f"def {callback}" in context


def test_unit_d_compatibility_wiring_uses_call_successor() -> None:
    calls = importlib.import_module(f"{PACKAGE}.calls")
    assert Evaluator._bind_call is calls.bind_call


def test_unit_d_call_module_has_no_public_facade_dependency() -> None:
    source = inspect.getsource(importlib.import_module(f"{PACKAGE}.calls"))
    assert "runtime.evaluator" not in source
    assert "from ..evaluator" not in source
    assert "Evaluator(" not in source
    assert "self.operators" not in source
    assert "self.scalars" not in source


def test_unit_d_function_call_keeps_existing_local_runtime_behavior() -> None:
    result = run_source(
        """
package t
fn advance(x: State<Int>) -> State<Int> { return x + 1 }
pub fn main() -> Unit {
  State<Int> value = advance(Dirac(1))
  Measure value
}
""",
        settings={"seed": 0},
    )
    assert result.status == "succeeded", result.diagnostics


def test_unit_d_method_call_restores_receiver_after_nested_call() -> None:
    result = run_source(
        """
package t
class Model {
  pub fn value() -> State<Int> { return Dirac(2) }
}
pub fn main() -> Unit {
  Model model = Model()
  State<Int> value = model.value()
  Measure value
}
""",
        settings={"seed": 0},
    )
    assert result.status == "succeeded", result.diagnostics
