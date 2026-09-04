"""AT-TDD: LISS-0179 imperial stone mass (ADR 0147)."""

from __future__ import annotations

from canonical_execution import run_canonical

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.dimensions import UNIT_SCALE_TO_CANONICAL, UNIT_TABLE  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402

_ST_KG = 0.45359237 * 14.0


def test_st_table() -> None:
    assert UNIT_TABLE["st"][0] == "Mass"
    assert UNIT_SCALE_TO_CANONICAL["st"] == ("kg", _ST_KG)


def test_st_lb_oz_kg_conversions() -> None:
    codes = {
        d.get("code", "")
        for d in compile_source(
            """
            package t
            pub fn main() -> Unit {
                Mass lb = 1.0.st to lb
                Mass oz = 1.0.st to oz
                Mass kg = 1.0.st to kg
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
            Mass lb = 1.0.st to lb
            Mass oz = 1.0.st to oz
            Mass kg = 1.0.st to kg
            Mass raw = 1.0.st
            Mass back = 14.0.lb to st
            State a = |0>
            Measure a
        }
        """
    )
    ev = Evaluator(seed=0)
    run_canonical(compiled, ev)
    assert abs(ev.scalars["lb"] - 14.0) < 1e-12
    assert abs(ev.scalars["oz"] - 224.0) < 1e-12
    assert abs(ev.scalars["kg"] - _ST_KG) < 1e-12
    assert abs(ev.scalars["raw"] - 1.0) < 1e-12
    assert abs(ev.scalars["back"] - 1.0) < 1e-12


if __name__ == "__main__":
    test_st_table()
    print("PASS test_st_table")
    test_st_lb_oz_kg_conversions()
    print("PASS test_st_lb_oz_kg_conversions")
