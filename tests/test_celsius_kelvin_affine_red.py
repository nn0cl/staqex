"""AT-TDD: LISS-0166 affine °C ↔ K (ADR 0134)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.dimensions import UNIT_AFFINE_TO_CANONICAL, UNIT_TABLE  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402


def test_celsius_table() -> None:
    assert UNIT_TABLE["C"][0] == "Temperature"
    assert UNIT_AFFINE_TO_CANONICAL["C"] == ("K", 1.0, 273.15)
    assert UNIT_AFFINE_TO_CANONICAL["K"] == ("K", 1.0, 0.0)


def test_c_to_k_and_reverse() -> None:
    codes = {
        d.get("code", "")
        for d in compile_source(
            """
            package t
            pub fn main() -> Unit {
                Temperature t = 0.0.C to K
                Temperature c = 273.15.K to C
                State a = |0>
                measure a
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
            Temperature t = 0.0.C to K
            Temperature raw = 0.0.C
            Temperature c = 273.15.K to C
            State a = |0>
            measure a
        }
        """
    )
    ev = Evaluator(seed=0)
    ev.run_unit(compiled.unit)
    assert abs(ev.scalars["t"] - 273.15) < 1e-12
    assert abs(ev.scalars["raw"] - 0.0) < 1e-12
    assert abs(ev.scalars["c"] - 0.0) < 1e-12


if __name__ == "__main__":
    test_celsius_table()
    print("PASS test_celsius_table")
    test_c_to_k_and_reverse()
    print("PASS test_c_to_k_and_reverse")
