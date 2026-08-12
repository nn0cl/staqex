"""AT-TDD: LISS-0188 / LISS-0189 SI residuals (ADR 0156)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.dimensions import UNIT_SCALE_TO_CANONICAL, UNIT_TABLE  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402

_U_KG = 1.66053906892e-27
_LB = 0.45359237


def test_u_and_ton_tables() -> None:
    assert UNIT_TABLE["u"][0] == "Mass"
    assert UNIT_TABLE["ton"][0] == "Mass"
    assert UNIT_SCALE_TO_CANONICAL["u"] == ("kg", _U_KG)
    assert UNIT_SCALE_TO_CANONICAL["ton"] == UNIT_SCALE_TO_CANONICAL["ton_us"]


def test_atomic_mass_to_kg() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Mass kg = 1.0.u to kg
            Mass raw = 1.0.u
            State a = |0>
            measure a
        }
        """
    )
    codes = {d.get("code", "") for d in compiled.diagnostics}
    assert "PARSE_ERROR" not in codes, codes
    ev = Evaluator(seed=0)
    ev.run_unit(compiled.unit)
    assert abs(ev.scalars["kg"] - _U_KG) < 1e-36
    assert abs(ev.scalars["raw"] - 1.0) < 1e-12


def test_bare_ton_matches_ton_us() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Mass lb = 1.0.ton to lb
            Mass us = 1.0.ton to ton_us
            State a = |0>
            measure a
        }
        """
    )
    codes = {d.get("code", "") for d in compiled.diagnostics}
    assert "UNIT_MIXED_ARITHMETIC_ERROR" not in codes, codes
    assert "PARSE_ERROR" not in codes, codes
    ev = Evaluator(seed=0)
    ev.run_unit(compiled.unit)
    assert abs(ev.scalars["lb"] - 2000.0) < 1e-9
    assert abs(ev.scalars["us"] - 1.0) < 1e-12


if __name__ == "__main__":
    test_u_and_ton_tables()
    print("PASS test_u_and_ton_tables")
    test_atomic_mass_to_kg()
    print("PASS test_atomic_mass_to_kg")
    test_bare_ton_matches_ton_us()
    print("PASS test_bare_ton_matches_ton_us")
