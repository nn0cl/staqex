"""Phase 1 Red contracts for WP-0166 / LISS-0569.

The structural assertions intentionally fail until the approved classical
value body is moved out of ``Evaluator``. The characterization cases protect
the existing literal, attribute, unit, constructor, and binder behavior.
"""

from __future__ import annotations

import ast
import importlib
import inspect
from pathlib import Path

from compiler.staqex.host import run_source


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


def test_classical_successor_exposes_the_complete_value_boundary() -> None:
    classical = importlib.import_module(f"{PACKAGE}.classical")
    for name in (
        "evaluate_value",
        "evaluate_value_with_unit",
        "evaluate_unit_convert",
        "resolve_attribute",
        "resolve_receiver_instance",
        "construct_instance",
        "construct_struct",
    ):
        assert callable(getattr(classical, name, None)), name


def test_classical_successor_does_not_delegate_to_legacy_value_body() -> None:
    source = inspect.getsource(importlib.import_module(f"{PACKAGE}.classical"))
    assert "_legacy_evaluate_value" not in source


def test_values_entrypoint_routes_to_classical_successor() -> None:
    source = inspect.getsource(importlib.import_module(f"{PACKAGE}.values"))
    assert "_legacy_evaluate_value" not in source
    assert "evaluation.classical" in source or ".classical import" in source


def test_context_declares_classical_value_callbacks() -> None:
    source = inspect.getsource(importlib.import_module(f"{PACKAGE}.context"))
    for callback in (
        "_evaluate_unit_convert",
        "_resolve_receiver_instance",
        "_construct_instance",
        "_construct_struct",
        "_evaluate_classical_value",
    ):
        assert f"def {callback}" in source


def test_evaluator_no_longer_declares_the_legacy_value_body() -> None:
    assert "_legacy_evaluate_value" not in _evaluator_method_names()


def test_literal_and_when_characterization_remains_successful() -> None:
    result = run_source(
        """
package t
pub fn main() -> Unit {
  State<Int> value = Dirac(1 + 2)
  Measure value
}
""",
        settings={"seed": 0},
    )
    assert result.status == "succeeded", result.diagnostics


def test_attribute_constructor_and_unit_characterization_remains_successful() -> None:
    result = run_source(
        """
package t
class Box {
  Float x = 3.0
  pub fn doubled() -> Float { return this.x + this.x }
}
pub fn main() -> Unit {
  Box b = Box()
  Float y = b.doubled()
  Mass mass = 1.0.kg to g
  State observed = Coin()
  Measure observed
}
""",
        settings={"seed": 0},
    )
    assert result.status == "succeeded", result.diagnostics


def test_classical_binder_characterization_remains_successful() -> None:
    result = run_source(
        """
package t
pub fn main() -> Unit {
  Int total = Sigma (i In 0..2) { i }
  State observed = Dirac(total)
  Measure observed
}
""",
        settings={"seed": 0},
    )
    assert result.status == "succeeded", result.diagnostics
