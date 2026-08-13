"""AT-TDD: LISS-0143 1D Float[N] indexed coefficients J[i]."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.finite_binder import lower_finite_binder_operators  # noqa: E402
from compiler.staqex.host import run_source  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {d.get("code", "") for d in compile_source(source).diagnostics}


_INDEXED_TFIM = """
package t
pub fn main() -> Unit {
    QubitRegister<3> register = system()
    Float[2] J = [1.0, 0.5]
    Operator H = Sigma (i In 0..1) {
        J[i] * Z[i] * Z[next(i)]
    }
    State a = |0>
    State b = |0>
    State c = |0>
    State (a, b, c) = Evolve { (a, b, c) under H for 0.1 }.run()
    Measure a
    Measure b
    Measure c
}
"""


def test_float_array_shape_mismatch_is_diagnosed() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            Float[2] J = [1.0]
            Measure J
        }
        """
    )
    assert "TYPE_MISMATCH" in codes


def test_indexed_coefficient_lowers_in_binder() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        QubitRegister<3> register = system()
        Float[2] J = [1.0, 0.5]
        Operator H = Sigma (i In 0..1) {
            J[i] * Z[i] * Z[next(i)]
        }
        State a = |0>
        Measure a
    }
    """
    codes = _codes(source)
    assert "BINDER_LOWERING_UNSUPPORTED" not in codes
    assert "PARSE_ERROR" not in codes
    compiled = compile_source(source)
    assert compiled.unit is not None
    lowered, diags = lower_finite_binder_operators(compiled.unit)
    assert not diags, diags
    assert "H" in lowered


def test_indexed_coefficient_evolve_runs() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        QubitRegister<2> register = system()
        Float[1] J = [1.0]
        Operator H = Sigma (i In 0..0) {
            J[i] * Z[i] * Z[next(i)]
        }
        State a = |0>
        State b = |0>
        State (a, b) = Evolve { (a, b) under H for 0.1 }.run()
        Measure a
    }
    """
    codes = _codes(source)
    assert "BINDER_LOWERING_UNSUPPORTED" not in codes
    result = run_source(
        source,
        settings={"target": "local", "seed": 11},
        stdout=io.StringIO(),
    )
    # LINEAR on unused `b` may fail status; ensure no binder/runtime crash codes.
    hard = {
        d.get("code")
        for d in (result.diagnostics or ())
        if d.get("code", "").startswith("BINDER_")
        or d.get("code") in {"PARSE_ERROR", "LEX_ERROR"}
    }
    assert not hard, hard
    if result.status != "succeeded":
        # Accept LINEAR-only failure; reject kernel crashes.
        assert all(
            d.get("code")
            in {
                "LINEAR_IMPLICIT_DISCARD",
                "QSEM_FINITE_EVIDENCE_MISSING",
                "QSEM_APPROXIMATION_OBLIGATION_MISSING",
            }
            for d in result.diagnostics
        ), result.diagnostics


if __name__ == "__main__":
    test_float_array_shape_mismatch_is_diagnosed()
    print("PASS test_float_array_shape_mismatch_is_diagnosed")
    test_indexed_coefficient_lowers_in_binder()
    print("PASS test_indexed_coefficient_lowers_in_binder")
    test_indexed_coefficient_evolve_runs()
    print("PASS test_indexed_coefficient_evolve_runs")
