"""AT-TDD Phase 1 Red: LISS-0021 function signatures and returns."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.run import run_source  # noqa: E402


def test_zero_argument_function_returns_final_state_expression() -> None:
    src = """
package t
fn origin() -> State<Int> {
    return Dirac(0)
}
pub fn main() -> Unit {
    State<Int> result = origin()
    Measure result
}
"""
    result = run_source(src, seed=0, stdout=io.StringIO())
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 0


def test_multi_argument_function_preserves_unmeasured_state_until_main() -> None:
    src = """
package t
fn add(a: State<Int>, b: State<Int>) -> State<Int> {
    return a + b
}
pub fn main() -> Unit {
    State<Int> a = Coin()
    State<Int> b = Dirac(2)
    State<Int> result = add(a, b)
    Measure result
}
"""
    result = run_source(src, seed=0, stdout=io.StringIO())
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value in {2, 3}


def test_class_method_has_explicit_return_type_and_final_expression() -> None:
    src = """
package t
class Box {
    val x: Int

    fn init(value: Int) {
        this.x = value
    }

    fn doubled() -> State<Float> {
        return Dirac(this.x + this.x)
    }
}
pub fn main() -> Unit {
    Box box = Box(3)
    State<Float> result = box.doubled()
    Measure result
}
"""
    result = run_source(src, seed=0, stdout=io.StringIO())
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 6


def test_function_measure_remains_forbidden_inside_measure_free_boundary() -> None:
    src = """
package t
fn bad() -> State<Int> {
    State<Int> value = Coin()
    Measure value
    return Dirac(0)
}
pub fn main() -> Unit {
    State<Int> result = bad()
    Measure result
}
"""
    compiled = compile_source(src)
    assert not compiled.ok, compiled.diagnostics


if __name__ == "__main__":
    tests = [
        test_zero_argument_function_returns_final_state_expression,
        test_multi_argument_function_preserves_unmeasured_state_until_main,
        test_class_method_has_explicit_return_type_and_final_expression,
        test_function_measure_remains_forbidden_inside_measure_free_boundary,
    ]
    for test in tests:
        test()
    print("OK — LISS-0021 Red tests")
