"""AT-TDD: LISS-0153 SI base dims Current / Temperature (ADR 0121)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.dimensions import Dim, TYPE_DIMS, UNIT_TABLE  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402


def test_dim_five_axis_and_tables() -> None:
    assert TYPE_DIMS["Current"].matches(Dim(I=1))
    assert TYPE_DIMS["Temperature"].matches(Dim(Theta=1))
    assert UNIT_TABLE["A"][0] == "Current"
    assert UNIT_TABLE["K"][0] == "Temperature"
    # Legacy three-axis zero-fill
    assert Dim(L=1).matches(Dim(L=1, M=0, T=0, I=0, Theta=0))


def test_current_temperature_typecheck() -> None:
    codes = {
        d.get("code", "")
        for d in compile_source(
            """
            package t
            pub fn main() -> Unit {
                Current i = 1.0.A
                Temperature t = 300.0.K
                Length x = 1.0.m
                Length bad = i
                State a = |0>
                measure a
            }
            """
        ).diagnostics
    }
    assert "PARSE_ERROR" not in codes, codes
    assert "DIMENSION_MISMATCH_ERROR" in codes or "TYPE_MISMATCH" in codes or "PRODUCT_TYPE_MISMATCH" in codes


if __name__ == "__main__":
    test_dim_five_axis_and_tables()
    print("PASS test_dim_five_axis_and_tables")
    test_current_temperature_typecheck()
    print("PASS test_current_temperature_typecheck")
