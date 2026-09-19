"""Phase 1 Red contracts for WP-0164 / LISS-0567.

The structural assertions intentionally fail until the approved classical and
frame successor modules exist. The runtime cases are characterization guards
for the existing function, method, and struct-frame behavior.
"""

from __future__ import annotations

import importlib
import inspect

from compiler.staqex.host import run_source


PACKAGE = "compiler.staqex.runtime.evaluation"


def test_classical_frame_successor_modules_expose_bounded_entrypoints() -> None:
    frames = importlib.import_module(f"{PACKAGE}.frames")
    classical = importlib.import_module(f"{PACKAGE}.classical")
    for name in ("bind_method", "bind_user_function", "restore_frame"):
        assert callable(getattr(frames, name, None)), name
    for name in (
        "evaluate_classical_value",
        "construct_instance",
        "construct_struct",
    ):
        assert callable(getattr(classical, name, None)), name


def test_classical_frame_successor_has_no_public_facade_dependency() -> None:
    for module_name in ("frames", "classical"):
        module = importlib.import_module(f"{PACKAGE}.{module_name}")
        source = inspect.getsource(module)
        assert "runtime.evaluator" not in source
        assert "from ..evaluator" not in source
        assert "Evaluator(" not in source


def test_context_declares_classical_and_frame_successor_callbacks() -> None:
    context = inspect.getsource(importlib.import_module(f"{PACKAGE}.context"))
    for callback in (
        "_frame_environment",
        "_restore_frame",
        "_evaluate_classical_value",
        "_construct_instance",
        "_construct_struct",
    ):
        assert f"def {callback}" in context


def test_compatibility_wires_classical_and_frame_successors() -> None:
    compatibility = inspect.getsource(
        importlib.import_module(f"{PACKAGE}.compatibility")
    )
    assert "install_frame_compatibility" in compatibility
    assert "install_classical_compatibility" in compatibility


def test_successor_modules_do_not_define_a_second_mutable_state_owner() -> None:
    for module_name in ("frames", "classical"):
        module = importlib.import_module(f"{PACKAGE}.{module_name}")
        source = inspect.getsource(module)
        assert "self.objects" not in source
        assert "self._frame_units" not in source
        assert "self._this" not in source


def test_function_frame_behavior_remains_successful() -> None:
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


def test_method_receiver_frame_behavior_remains_successful() -> None:
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


def test_struct_return_frame_behavior_remains_successful() -> None:
    result = run_source(
        """
package t
struct Point { x: Float, y: Float }
fn make_point(a: Float, b: Float) -> Point {
  return Point(a, b)
}
pub fn main() -> Unit {
  Point p = make_point(1.0, 2.0)
  State s = |0>
  Measure s
}
""",
        settings={"seed": 0},
    )
    assert result.status == "succeeded", result.diagnostics
