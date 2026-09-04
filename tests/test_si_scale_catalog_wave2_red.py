"""AT-TDD: LISS-0161 SI scale catalog wave-2 (ADR 0129)."""

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


def _codes(source: str) -> set[str]:
    return {d.get("code", "") for d in compile_source(source).diagnostics}


def test_wave2_table_rows() -> None:
    assert UNIT_TABLE["us"][0] == "Time"
    assert UNIT_TABLE["km"][0] == "Length"
    assert UNIT_TABLE["kHz"][0] == "Frequency"
    assert UNIT_TABLE["MHz"][0] == "Frequency"
    assert UNIT_SCALE_TO_CANONICAL["ps"] == ("s", 1e-12)
    assert UNIT_SCALE_TO_CANONICAL["us"] == ("s", 1e-6)
    assert UNIT_SCALE_TO_CANONICAL["km"] == ("m", 1e3)
    assert UNIT_SCALE_TO_CANONICAL["kHz"] == ("Hz", 1e3)
    assert UNIT_SCALE_TO_CANONICAL["MHz"] == ("Hz", 1e6)


def test_wave2_converts_and_bare_stays_raw() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            Time t = 2.0.ps to s
            Time u = 3.0.us to s
            Length x = 4.0.km to m
            Frequency f = 5.0.kHz to Hz
            Frequency g = 6.0.MHz to Hz
            State a = |0>
            Measure a
        }
        """
    )
    assert "PARSE_ERROR" not in codes, codes
    assert "TYPE_MISMATCH" not in codes, codes
    assert "DIMENSION_MISMATCH_ERROR" not in codes, codes

    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Time t = 2.0.ps to s
            Time raw = 2.0.ps
            State a = |0>
            Measure a
        }
        """
    )
    ev = Evaluator(seed=0)
    run_canonical(compiled, ev)
    assert abs(ev.scalars["t"] - 2e-12) < 1e-24
    assert abs(ev.scalars["raw"] - 2.0) < 1e-12


def test_unsupported_mass_scale_still_hard_fails() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            Mass m = 1.0.kg to bob
            State a = |0>
            Measure a
        }
        """
    )
    assert "TYPE_MISMATCH" in codes or "PARSE_ERROR" in codes


if __name__ == "__main__":
    test_wave2_table_rows()
    print("PASS test_wave2_table_rows")
    test_wave2_converts_and_bare_stays_raw()
    print("PASS test_wave2_converts_and_bare_stays_raw")
    test_unsupported_mass_scale_still_hard_fails()
    print("PASS test_unsupported_mass_scale_still_hard_fails")
