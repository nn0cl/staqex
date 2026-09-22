"""Phase 1 Red contracts for WP-0167 / LISS-0572 Unit B."""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

from compiler.staqex.host import run_source


ROOT = Path(__file__).resolve().parents[1]
EVALUATOR = ROOT / "compiler/staqex/runtime/evaluator.py"
PACKAGE = "compiler.staqex.runtime.evaluation"
FRAMES = ROOT / "compiler/staqex/runtime/evaluation/frames.py"
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


def test_constructor_successor_file_exists() -> None:
    assert (ROOT / "compiler/staqex/runtime/evaluation/constructors.py").is_file()


def test_assignment_successor_file_exists() -> None:
    assert (ROOT / "compiler/staqex/runtime/evaluation/assignments.py").is_file()


def test_frames_constructors_and_assignment_bodies_leave_the_facade() -> None:
    remaining = _evaluator_method_names() & {
        "_legacy_bind_method",
        "_legacy_bind_user_fun",
        "_legacy_construct_instance",
        "_run_init",
        "_legacy_construct_struct",
        "_exec_assign",
    }
    assert not remaining, sorted(remaining)


def test_frame_successor_no_longer_delegates_to_legacy_bodies() -> None:
    source = FRAMES.read_text(encoding="utf-8")
    assert "_legacy_bind_method" not in source
    assert "_legacy_bind_user_fun" not in source


def test_constructor_assignment_compatibility_wiring_is_declared() -> None:
    source = COMPATIBILITY.read_text(encoding="utf-8")
    for name in (
        "install_constructor_compatibility",
        "install_assignment_compatibility",
        "construct_instance",
        "construct_struct",
        "execute_assignment",
    ):
        assert name in source


def test_context_declares_narrow_unit_b_callbacks() -> None:
    source = CONTEXT.read_text(encoding="utf-8")
    for callback in (
        "_construct_instance_body",
        "_construct_struct_body",
        "_run_init_body",
        "_execute_assignment_body",
    ):
        assert f"def {callback}" in source


def test_function_frame_characterization_remains_successful() -> None:
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


def test_method_receiver_frame_characterization_remains_successful() -> None:
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


def test_class_init_and_assignment_characterization_remains_successful() -> None:
    result = run_source(
        """
package t
class Model {
  var value: Int
  fn init(value: Int) { this.value = value }
  pub fn state() -> State<Int> { return Dirac(this.value) }
}
pub fn main() -> Unit {
  Model model = Model(3)
  State<Int> observed = model.state()
  Measure observed
}
""",
        settings={"seed": 0},
    )
    assert result.status == "succeeded", result.diagnostics


def test_struct_constructor_characterization_remains_successful() -> None:
    result = run_source(
        """
package t
struct Point { x: Float, y: Float }
fn make_point(a: Float, b: Float) -> Point { return Point(a, b) }
pub fn main() -> Unit {
  Point p = make_point(1.0, 2.0)
  State s = |0>
  Measure s
}
""",
        settings={"seed": 0},
    )
    assert result.status == "succeeded", result.diagnostics
