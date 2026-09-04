"""AT-TDD: LISS-0177 imperial pound mass (ADR 0145)."""

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

_LB_KG = 0.45359237


def test_lb_table() -> None:
    assert UNIT_TABLE["lb"][0] == "Mass"
    assert UNIT_SCALE_TO_CANONICAL["lb"] == ("kg", _LB_KG)


def test_lb_kg_round_trip() -> None:
    codes = {
        d.get("code", "")
        for d in compile_source(
            """
            package t
            pub fn main() -> Unit {
                Mass m = 1.0.lb to kg
                Mass p = 0.45359237.kg to lb
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
            Mass m = 1.0.lb to kg
            Mass raw = 1.0.lb
            Mass p = 0.45359237.kg to lb
            Mass g = 1.0.lb to g
            State a = |0>
            Measure a
        }
        """
    )
    ev = Evaluator(seed=0)
    run_canonical(compiled, ev)
    assert abs(ev.scalars["m"] - _LB_KG) < 1e-12
    assert abs(ev.scalars["raw"] - 1.0) < 1e-12
    assert abs(ev.scalars["p"] - 1.0) < 1e-12
    assert abs(ev.scalars["g"] - _LB_KG * 1000.0) < 1e-9


if __name__ == "__main__":
    test_lb_table()
    print("PASS test_lb_table")
    test_lb_kg_round_trip()
    print("PASS test_lb_kg_round_trip")
