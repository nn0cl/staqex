"""Phase 1 Red contracts for WP-0170 / LISS-0577."""

from __future__ import annotations

import ast
import importlib
import inspect
from pathlib import Path
from unittest.mock import patch

from compiler.staqex.ast_nodes import Call, Span, Var
from compiler.staqex.host import run_source
from compiler.staqex.pipeline import compile_source
from compiler.staqex.runtime.evaluator import ClassInstance, Evaluator


ROOT = Path(__file__).resolve().parents[1]
EVALUATOR = ROOT / "compiler/staqex/runtime/evaluator.py"
PACKAGE = "compiler.staqex.runtime.evaluation"
METHODS = {
    "_eval_classical_call",
    "_eval_classical_method_call",
    "_eval_classical_user_fun",
    "_eval_classical_user_fun_value",
}


def _classical_calls_module():
    successor_path = ROOT / "compiler/staqex/runtime/evaluation/classical_calls.py"
    assert successor_path.is_file(), "missing classical_calls.py successor"
    return importlib.import_module(f"{PACKAGE}.classical_calls")


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


def _compiled_function():
    compiled = compile_source(
        """
package t
fn plus_one(x: Float) -> Float { return x + 1.0 }
pub fn main() -> Unit {
  State x = Dirac(0)
  Measure x
}
"""
    )
    assert compiled.ok, compiled.diagnostics
    return next(
        declaration
        for declaration in compiled.unit.decls
        if getattr(declaration, "name", None) == "plus_one"
    )


def test_classical_call_successor_owns_all_four_evaluator_bodies() -> None:
    successor = _classical_calls_module()
    expected = {
        "eval_classical_call",
        "eval_classical_method_call",
        "eval_classical_user_fun",
        "eval_classical_user_fun_value",
    }
    assert expected <= set(vars(successor))
    assert not (METHODS & _evaluator_method_names())


def test_classical_call_successor_has_narrow_non_owning_context() -> None:
    successor = _classical_calls_module()
    source = inspect.getsource(successor)
    assert "ClassicalCallContext" in source
    assert "runtime.evaluator" not in source
    assert "from ..evaluator" not in source
    assert "Evaluator(" not in source
    for owned_state in (
        "self.objects",
        "self.scalars",
        "self._this",
        "self._frame_units",
        "self._call_local_units",
    ):
        assert owned_state not in source


def test_classical_call_compatibility_hooks_keep_successor_identity() -> None:
    successor = _classical_calls_module()
    assert Evaluator._eval_classical_call is successor.eval_classical_call
    assert Evaluator._eval_classical_method_call is successor.eval_classical_method_call
    assert Evaluator._eval_classical_user_fun is successor.eval_classical_user_fun
    assert (
        Evaluator._eval_classical_user_fun_value
        is successor.eval_classical_user_fun_value
    )


def test_nested_classical_call_behavior_remains_compatible() -> None:
    result = run_source(
        """
package t
fn twice(x: Float) -> Float { return x + x }
fn plus_one(x: Float) -> Float { return twice(x) + 1.0 }
pub fn main() -> Unit {
  Float result = plus_one(1.25)
  State observed = Dirac(result)
  Measure observed
}
""",
        settings={"seed": 0},
    )
    assert result.status == "succeeded", result.diagnostics
    assert result.measurements[-1].value == 3.5


def test_classical_call_restores_receiver_and_unit_frames_after_success() -> None:
    evaluator = Evaluator(seed=0)
    function = _compiled_function()
    evaluator.funs[function.name] = function
    receiver = ClassInstance("Outer", {})
    frame_units = {"outer_frame": "m"}
    call_units = {"outer_call": "s"}
    evaluator._this = receiver
    evaluator._frame_units = frame_units
    evaluator._call_local_units = call_units
    span = Span(line=1, col=1)
    call = Call(
        callee=Var(name="plus_one", span=span),
        args=[Var(name="input", span=span)],
        span=span,
    )

    value = evaluator._eval_classical_user_fun_value(
        function, call, {"input": 2.5}
    )

    assert value == (3.5, None)
    assert evaluator._this is receiver
    assert evaluator._frame_units is frame_units
    assert evaluator._call_local_units is call_units


def test_classical_call_restores_receiver_and_unit_frames_after_failure() -> None:
    evaluator = Evaluator(seed=0)
    function = _compiled_function()
    evaluator.funs[function.name] = function
    receiver = ClassInstance("Outer", {})
    frame_units = {"outer_frame": "m"}
    call_units = {"outer_call": "s"}
    evaluator._this = receiver
    evaluator._frame_units = frame_units
    evaluator._call_local_units = call_units
    span = Span(line=1, col=1)
    call = Call(
        callee=Var(name="plus_one", span=span),
        args=[Var(name="input", span=span)],
        span=span,
    )

    with patch.object(
        evaluator,
        "_eval_value_with_unit",
        side_effect=RuntimeError("forced nested value failure"),
    ):
        try:
            evaluator._eval_classical_user_fun_value(
                function, call, {"input": 2.5}
            )
        except RuntimeError as error:
            assert str(error) == "forced nested value failure"
        else:
            raise AssertionError("expected the injected nested evaluation failure")

    assert evaluator._this is receiver
    assert evaluator._frame_units is frame_units
    assert evaluator._call_local_units is call_units
