"""AT-TDD: LISS-0168 gram ↔ kilogram (ADR 0136)."""

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


def test_gram_table() -> None:
    assert UNIT_TABLE["g"][0] == "Mass"
    assert UNIT_SCALE_TO_CANONICAL["g"] == ("kg", 1e-3)
    assert UNIT_SCALE_TO_CANONICAL["kg"] == ("kg", 1.0)


def test_g_kg_round_trip() -> None:
    codes = {
        d.get("code", "")
        for d in compile_source(
            """
            package t
            pub fn main() -> Unit {
                Mass m = 1000.0.g to kg
                Mass g = 1.0.kg to g
                State a = |0>
                Measure a
            }
            """
        ).diagnostics
    }
    assert "PARSE_ERROR" not in codes, codes
    assert "TYPE_MISMATCH" not in codes, codes

    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Mass m = 1000.0.g to kg
            Mass raw = 1000.0.g
            Mass g = 1.0.kg to g
            State a = |0>
            Measure a
        }
        """
    )
    ev = Evaluator(seed=0)
    run_canonical(compiled, ev)
    assert abs(ev.scalars["m"] - 1.0) < 1e-12
    assert abs(ev.scalars["raw"] - 1000.0) < 1e-12
    assert abs(ev.scalars["g"] - 1000.0) < 1e-12


if __name__ == "__main__":
    test_gram_table()
    print("PASS test_gram_table")
    test_g_kg_round_trip()
    print("PASS test_g_kg_round_trip")
