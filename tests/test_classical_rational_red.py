"""AT-TDD: LISS-0193 classical Fraction literals → f64 at State (ADR 0160)."""

from __future__ import annotations

import io
import sys
from fractions import Fraction
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.run import run_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator, _apply_op  # noqa: E402


def test_int_div_is_fraction() -> None:
    assert _apply_op("/", 1, 3) == Fraction(1, 3)
    assert _apply_op("/", Fraction(1, 2), 2) == Fraction(1, 4)


def test_float_div_stays_float() -> None:
    out = _apply_op("/", 1.0, 3.0)
    assert isinstance(out, float)
    assert abs(out - 1.0 / 3.0) < 1e-15


def test_classical_float_keeps_fraction() -> None:
    from compiler.staqex.pipeline import compile_source

    src = """
        package t
        pub fn main() -> Unit {
            Float x = 1 / 3
            State s = x
            Measure s
        }
        """
    compiled = compile_source(src)
    assert compiled.unit is not None
    ev = Evaluator(seed=1)
    # Capture scalar before measure by evaluating only the Float bind path:
    result = run_source(src, stdout=io.StringIO())
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert abs(float(result.eval.measure.value) - (1.0 / 3.0)) < 1e-12
    for w in result.eval.joint.worlds:
        assert "s" in w.assign
        assert isinstance(w.assign["s"], float)
    # Direct closed classical eval retains Fraction.
    assert _apply_op("/", 1, 3) == Fraction(1, 3)
    unit = compiled.unit
    assert unit.main is not None
    # Re-bind classical Float through evaluator scalar capture.
    ev2 = Evaluator(seed=1)
    from compiler.staqex.ast_nodes import StateBind

    for stmt in unit.main.body.stmts:
        if isinstance(stmt, StateBind) and stmt.ty is not None and stmt.ty.name == "Float":
            val, _ = ev2._eval_value_with_unit(stmt.expr, {})
            assert val == Fraction(1, 3)
            break
    else:
        raise AssertionError("Float bind not found")


def test_state_literal_div_is_float_on_joint() -> None:
    result = run_source(
        """
        package t
        pub fn main() -> Unit {
            State s = 1 / 3
            Measure s
        }
        """,
        stdout=io.StringIO(),
    )
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert abs(float(result.eval.measure.value) - (1.0 / 3.0)) < 1e-12
    for w in result.eval.joint.worlds:
        assert isinstance(w.assign["s"], float)


if __name__ == "__main__":
    test_int_div_is_fraction()
    print("PASS test_int_div_is_fraction")
    test_float_div_stays_float()
    print("PASS test_float_div_stays_float")
    test_classical_float_keeps_fraction()
    print("PASS test_classical_float_keeps_fraction")
    test_state_literal_div_is_float_on_joint()
    print("PASS test_state_literal_div_is_float_on_joint")
