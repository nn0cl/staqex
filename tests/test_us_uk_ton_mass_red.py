"""AT-TDD: LISS-0182 US/UK ton mass (ADR 0150)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.dimensions import UNIT_SCALE_TO_CANONICAL, UNIT_TABLE  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402

_LB = 0.45359237


def test_us_uk_ton_table() -> None:
    assert UNIT_TABLE["ton_us"][0] == "Mass"
    assert UNIT_TABLE["ton_uk"][0] == "Mass"
    assert UNIT_SCALE_TO_CANONICAL["ton_us"] == ("kg", _LB * 2000.0)
    assert UNIT_SCALE_TO_CANONICAL["ton_uk"] == ("kg", _LB * 2240.0)


def test_short_ton_lb_kg_conversions() -> None:
    codes = {
        d.get("code", "")
        for d in compile_source(
            """
            package t
            pub fn main() -> Unit {
                Mass lb = 1.0.ton_us to lb
                Mass kg = 1.0.ton_us to kg
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
            Mass lb = 1.0.ton_us to lb
            Mass kg = 1.0.ton_us to kg
            Mass raw = 1.0.ton_us
            Mass back = 2000.0.lb to ton_us
            State a = |0>
            measure a
        }
        """
    )
    ev = Evaluator(seed=0)
    ev.run_unit(compiled.unit)
    assert abs(ev.scalars["lb"] - 2000.0) < 1e-9
    assert abs(ev.scalars["kg"] - _LB * 2000.0) < 1e-9
    assert abs(ev.scalars["raw"] - 1.0) < 1e-12
    assert abs(ev.scalars["back"] - 1.0) < 1e-12


def test_long_ton_and_metric_tonne_bridge() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Mass lb = 1.0.ton_uk to lb
            Mass t = 1.0.ton_uk to t
            Mass us = 1.0.ton_uk to ton_us
            State a = |0>
            measure a
        }
        """
    )
    assert not [
        d
        for d in compiled.diagnostics
        if d.get("code")
        in {"PARSE_ERROR", "TYPE_MISMATCH", "DIMENSION_MISMATCH_ERROR"}
    ], compiled.diagnostics
    ev = Evaluator(seed=0)
    ev.run_unit(compiled.unit)
    assert abs(ev.scalars["lb"] - 2240.0) < 1e-9
    assert abs(ev.scalars["t"] - (_LB * 2240.0) / 1000.0) < 1e-12
    assert abs(ev.scalars["us"] - 2240.0 / 2000.0) < 1e-12


if __name__ == "__main__":
    test_us_uk_ton_table()
    print("PASS test_us_uk_ton_table")
    test_short_ton_lb_kg_conversions()
    print("PASS test_short_ton_lb_kg_conversions")
    test_long_ton_and_metric_tonne_bridge()
    print("PASS test_long_ton_and_metric_tonne_bridge")
