"""AT-TDD: LISS-0137 classical Float → Operator / evolve for (+ param factory)."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex import run_source  # noqa: E402


def _hard(diags: list[dict]) -> list[dict]:
    return [
        d
        for d in diags
        if not str(d.get("code", "")).startswith("QSEM_")
        and d.get("code") != "MULTI_REGISTER_INDEX_AMBIGUOUS"
    ]


def _run(src: str):
    return run_source(
        src,
        settings={"target": "local", "seed": 0},
        stdout=io.StringIO(),
    )


_PARAM_FACTORY = """
package t
pub fn tfim(J: Float, h: Float) -> Operator {
    Operator H = -J * (Z[0] * Z[1]) - h * (X[0] + X[1])
    return H
}
pub fn main() -> Unit {
    Operator H = tfim(1.0545718e-19, 5.272859e-20)
    State s0 = |+>
    State s1 = |+>
    State (s0, s1) = evolve { (s0, s1) under H for 0.7.fs using Suzuki(order = 2, steps = 6) }.run()
    State zz = expect(ZZ, s0, s1)
    State viewed = inspect(zz)
    State s1 = |0>
    measure s0
}
"""

_FIELD_TO_FLOAT = """
package t
namespace D {
    pub struct C {
        val J: Float
        val h: Float
    }
}
pub fn main() -> Unit {
    D.C c = D.C(1.0545718e-19, 5.272859e-20)
    Float J = c.J
    Float h = c.h
    Operator H = -J * (Z[0] * Z[1]) - h * (X[0] + X[1])
    State s0 = |+>
    State s1 = |+>
    State (s0, s1) = evolve { (s0, s1) under H for 0.7.fs using Suzuki(order = 2, steps = 6) }.run()
    State s1 = |0>
    measure s0
}
"""

_EVOLVE_FOR_METHOD_FLOAT = """
package t
namespace P {
    pub class Schedule {
        pub val duration: Time
        fn init(t: Time) {
            this.duration = t
        }
        pub fn t() -> Time {
            Time out = this.duration
            return out
        }
    }
}
pub fn main() -> Unit {
    P.Schedule s = P.Schedule(0.7.fs)
    Time duration = s.t()
    Operator H = -1.0545718e-19 * (Z[0] * Z[1]) - 5.272859e-20 * (X[0] + X[1])
    State s0 = |+>
    State s1 = |+>
    State (s0, s1) = evolve { (s0, s1) under H for duration using Suzuki(order = 2, steps = 6) }.run()
    State s1 = |0>
    measure s0
}
"""


def test_parametrized_operator_factory_runs() -> None:
    result = _run(_PARAM_FACTORY)
    assert result.status == "succeeded", _hard(result.diagnostics)


def test_struct_field_float_coeffs_in_operator_run() -> None:
    result = _run(_FIELD_TO_FLOAT)
    assert result.status == "succeeded", _hard(result.diagnostics)


def test_evolve_for_method_returned_float_runs() -> None:
    result = _run(_EVOLVE_FOR_METHOD_FLOAT)
    assert result.status == "succeeded", _hard(result.diagnostics)


if __name__ == "__main__":
    test_parametrized_operator_factory_runs()
    test_struct_field_float_coeffs_in_operator_run()
    test_evolve_for_method_returned_float_runs()
    print("OK — LISS-0137")
