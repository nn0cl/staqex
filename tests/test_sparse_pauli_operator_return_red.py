"""AT-TDD: LISS-0136 sparse Pauli Operator return from helper fn.

Named Float coefficients inside a factory must remain usable after return
(same evolve path as inline B08).
"""

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


_FACTORY_NAMED_FLOAT = """
package t
pub fn build_ising() -> Operator {
    Float J = 1.0545718e-19
    Float h = 5.272859e-20
    Operator H = -J * (Z[0] * Z[1]) - h * (X[0] + X[1])
    return H
}
pub fn main() -> Unit {
    Operator H = build_ising()
    state s0 = |+>
    state s1 = |+>
    state (s0, s1) = evolve { (s0, s1) under H for 0.7.fs using Suzuki(order = 2, steps = 6) }.run()
    state zz = expect(ZZ, s0, s1)
    state viewed = inspect(zz)
    state s1 = |0>
    measure s0
}
"""


_FACTORY_LITERAL = """
package t
pub fn build_ising() -> Operator {
    Operator H = -1.0545718e-19 * (Z[0] * Z[1]) - 5.272859e-20 * (X[0] + X[1])
    return H
}
pub fn main() -> Unit {
    Operator H = build_ising()
    state s0 = |+>
    state s1 = |+>
    state (s0, s1) = evolve { (s0, s1) under H for 0.7.fs using Suzuki(order = 2, steps = 6) }.run()
    state zz = expect(ZZ, s0, s1)
    state viewed = inspect(zz)
    state s1 = |0>
    measure s0
}
"""


def test_operator_factory_literal_coeffs_still_runs() -> None:
    result = run_source(
        _FACTORY_LITERAL,
        settings={"target": "local", "seed": 0},
        stdout=io.StringIO(),
    )
    assert result.status == "succeeded", _hard(result.diagnostics)


def test_operator_factory_named_float_coeffs_runs() -> None:
    result = run_source(
        _FACTORY_NAMED_FLOAT,
        settings={"target": "local", "seed": 0},
        stdout=io.StringIO(),
    )
    assert result.status == "succeeded", _hard(result.diagnostics)


if __name__ == "__main__":
    test_operator_factory_literal_coeffs_still_runs()
    test_operator_factory_named_float_coeffs_runs()
    print("OK — LISS-0136")
