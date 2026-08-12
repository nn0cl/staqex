"""AT-TDD: LISS-0183 troy ounce mass (ADR 0151)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.dimensions import UNIT_SCALE_TO_CANONICAL, UNIT_TABLE  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402

_OZ_T_KG = 31.1034768e-3


def test_troy_table() -> None:
    assert UNIT_TABLE["oz_t"][0] == "Mass"
    assert UNIT_SCALE_TO_CANONICAL["oz_t"] == ("kg", _OZ_T_KG)


def test_troy_g_kg_oz_bridge() -> None:
    codes = {
        d.get("code", "")
        for d in compile_source(
            """
            package t
            pub fn main() -> Unit {
                Mass g = 1.0.oz_t to g
                Mass kg = 1.0.oz_t to kg
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
            Mass g = 1.0.oz_t to g
            Mass kg = 1.0.oz_t to kg
            Mass raw = 1.0.oz_t
            Mass back = 31.1034768.g to oz_t
            Mass av = 1.0.oz_t to oz
            State a = |0>
            Measure a
        }
        """
    )
    ev = Evaluator(seed=0)
    ev.run_unit(compiled.unit)
    assert abs(ev.scalars["g"] - 31.1034768) < 1e-9
    assert abs(ev.scalars["kg"] - _OZ_T_KG) < 1e-15
    assert abs(ev.scalars["raw"] - 1.0) < 1e-12
    assert abs(ev.scalars["back"] - 1.0) < 1e-12
    # troy ≠ avoirdupois
    assert abs(ev.scalars["av"] - 31.1034768 / (0.45359237 / 16.0 * 1000.0)) < 1e-9


if __name__ == "__main__":
    test_troy_table()
    print("PASS test_troy_table")
    test_troy_g_kg_oz_bridge()
    print("PASS test_troy_g_kg_oz_bridge")
