"""AT-TDD: LISS-0180 metric tonne mass (ADR 0148)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.dimensions import UNIT_SCALE_TO_CANONICAL, UNIT_TABLE  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402


def test_tonne_table() -> None:
    assert UNIT_TABLE["t"][0] == "Mass"
    assert UNIT_SCALE_TO_CANONICAL["t"] == ("kg", 1e3)


def test_tonne_kg_g_conversions() -> None:
    codes = {
        d.get("code", "")
        for d in compile_source(
            """
            package t
            pub fn main() -> Unit {
                Mass kg = 1.0.t to kg
                Mass g = 1.0.t to g
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
            Mass kg = 1.0.t to kg
            Mass g = 1.0.t to g
            Mass raw = 1.0.t
            Mass back = 1000.0.kg to t
            State a = |0>
            measure a
        }
        """
    )
    ev = Evaluator(seed=0)
    ev.run_unit(compiled.unit)
    assert abs(ev.scalars["kg"] - 1000.0) < 1e-12
    assert abs(ev.scalars["g"] - 1e6) < 1e-6
    assert abs(ev.scalars["raw"] - 1.0) < 1e-12
    assert abs(ev.scalars["back"] - 1.0) < 1e-12


if __name__ == "__main__":
    test_tonne_table()
    print("PASS test_tonne_table")
    test_tonne_kg_g_conversions()
    print("PASS test_tonne_kg_g_conversions")
