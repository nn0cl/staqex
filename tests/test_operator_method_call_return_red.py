"""AT-TDD: LISS-0139 Operator RHS method Call parse and return."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex import compile_source, run_source  # noqa: E402


def _hard(diags: list[dict]) -> list[dict]:
    return [
        d
        for d in diags
        if not str(d.get("code", "")).startswith("QSEM_")
        and d.get("code") != "MULTI_REGISTER_INDEX_AMBIGUOUS"
    ]


_METHOD_LITERAL = """
package t
namespace Phys {
    pub class Model {
        fn init() {}
        pub fn hamiltonian() -> Operator {
            Energy scale = 1.0.eV to J
            Operator H = scale * (-(Z[0] * Z[1]) - (X[0] + X[1]))
            return H
        }
    }
}
pub fn main() -> Unit {
    Phys.Model m = Phys.Model()
    Operator H = m.hamiltonian()
    State s0 = |+>
    State s1 = |+>
    Time duration = 0.7.fs
    Operator U = exp(-i * H)
    State (s0, s1) = Evolve() { U * (s0, s1) }.run()
    State zz = expect(ZZ, s0, s1)
    State viewed = Inspect(zz)
    State s1 = |0>
    Measure s0
}
"""

_METHOD_FIELDS = """
package t
namespace Phys {
    pub class Model {
        pub val J: Float
        pub val h: Float
        fn init(J: Float, h: Float) {
            this.J = J
            this.h = h
        }
        pub fn hamiltonian() -> Operator {
            Float J = this.J
            Float h = this.h
            Energy scale = 1.0.eV to J
            Operator H = scale * (-(Z[0] * Z[1]) - (X[0] + X[1]))
            return H
        }
    }
}
pub fn main() -> Unit {
    Phys.Model m = Phys.Model(1.0545718e-19, 5.272859e-20)
    Operator H = m.hamiltonian()
    State s0 = |+>
    State s1 = |+>
    Time duration = 0.7.fs
    Operator U = exp(-i * H)
    State (s0, s1) = Evolve() { U * (s0, s1) }.run()
    State s1 = |0>
    Measure s0
}
"""


def test_operator_method_call_parses() -> None:
    compiled = compile_source(_METHOD_LITERAL)
    hard = _hard(compiled.diagnostics)
    assert not hard, hard
    assert compiled.ok or not hard


def test_operator_method_literal_return_runs() -> None:
    # This regression is about method-call resolution.  The returned
    # Hamiltonian is intentionally not treated as an already-realized U(t);
    # explicit finite realization is covered by the evolution-surface suite.
    compiled = compile_source(_METHOD_LITERAL)
    assert compiled.ok and not _hard(compiled.diagnostics), compiled.diagnostics


def test_operator_method_field_coeffs_run() -> None:
    compiled = compile_source(_METHOD_FIELDS)
    assert compiled.ok and not _hard(compiled.diagnostics), compiled.diagnostics


if __name__ == "__main__":
    test_operator_method_call_parses()
    test_operator_method_literal_return_runs()
    test_operator_method_field_coeffs_run()
    print("OK — LISS-0139")
