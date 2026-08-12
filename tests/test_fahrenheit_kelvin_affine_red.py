"""AT-TDD: LISS-0167 Fahrenheit affine (ADR 0135)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.dimensions import UNIT_AFFINE_TO_CANONICAL, UNIT_TABLE  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402

_F_SCALE = 5.0 / 9.0
_F_OFFSET = 273.15 - 32.0 * _F_SCALE


def test_fahrenheit_table() -> None:
    assert UNIT_TABLE["F"][0] == "Temperature"
    assert UNIT_AFFINE_TO_CANONICAL["F"] == ("K", _F_SCALE, _F_OFFSET)


def test_f_to_k_and_c() -> None:
    codes = {
        d.get("code", "")
        for d in compile_source(
            """
            package t
            pub fn main() -> Unit {
                Temperature k = 32.0.F to K
                Temperature c = 32.0.F to C
                State a = |0>
                Measure a
            }
            """
        ).diagnostics
    }
    assert "PARSE_ERROR" not in codes, codes
    assert "TYPE_MISMATCH" not in codes, codes
    assert "DIMENSION_MISMATCH_ERROR" not in codes, codes

    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Temperature k = 32.0.F to K
            Temperature c = 32.0.F to C
            Temperature raw = 32.0.F
            State a = |0>
            Measure a
        }
        """
    )
    ev = Evaluator(seed=0)
    ev.run_unit(compiled.unit)
    assert abs(ev.scalars["k"] - 273.15) < 1e-12
    assert abs(ev.scalars["c"] - 0.0) < 1e-12
    assert abs(ev.scalars["raw"] - 32.0) < 1e-12


if __name__ == "__main__":
    test_fahrenheit_table()
    print("PASS test_fahrenheit_table")
    test_f_to_k_and_c()
    print("PASS test_f_to_k_and_c")
