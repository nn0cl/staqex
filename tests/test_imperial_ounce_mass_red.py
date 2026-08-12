"""AT-TDD: LISS-0178 imperial ounce mass (ADR 0146)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.dimensions import UNIT_SCALE_TO_CANONICAL, UNIT_TABLE  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402

_OZ_KG = 0.45359237 / 16.0


def test_oz_table() -> None:
    assert UNIT_TABLE["oz"][0] == "Mass"
    assert UNIT_SCALE_TO_CANONICAL["oz"] == ("kg", _OZ_KG)


def test_oz_lb_kg_conversions() -> None:
    codes = {
        d.get("code", "")
        for d in compile_source(
            """
            package t
            pub fn main() -> Unit {
                Mass m = 16.0.oz to lb
                Mass k = 16.0.oz to kg
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
            Mass m = 16.0.oz to lb
            Mass k = 16.0.oz to kg
            Mass raw = 16.0.oz
            Mass back = 1.0.lb to oz
            State a = |0>
            Measure a
        }
        """
    )
    ev = Evaluator(seed=0)
    ev.run_unit(compiled.unit)
    assert abs(ev.scalars["m"] - 1.0) < 1e-12
    assert abs(ev.scalars["k"] - 0.45359237) < 1e-12
    assert abs(ev.scalars["raw"] - 16.0) < 1e-12
    assert abs(ev.scalars["back"] - 16.0) < 1e-12


if __name__ == "__main__":
    test_oz_table()
    print("PASS test_oz_table")
    test_oz_lb_kg_conversions()
    print("PASS test_oz_lb_kg_conversions")
