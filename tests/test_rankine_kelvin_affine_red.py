"""AT-TDD: LISS-0176 Rankine affine (ADR 0144)."""

from __future__ import annotations

from canonical_execution import run_canonical

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.dimensions import UNIT_AFFINE_TO_CANONICAL, UNIT_TABLE  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402

_R_SCALE = 5.0 / 9.0


def test_rankine_table() -> None:
    assert UNIT_TABLE["R"][0] == "Temperature"
    assert UNIT_AFFINE_TO_CANONICAL["R"] == ("K", _R_SCALE, 0.0)


def test_r_to_k_f_and_c() -> None:
    codes = {
        d.get("code", "")
        for d in compile_source(
            """
            package t
            pub fn main() -> Unit {
                Temperature k = 491.67.R to K
                Temperature f = 491.67.R to F
                Temperature c = 491.67.R to C
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
            Temperature k = 491.67.R to K
            Temperature f = 491.67.R to F
            Temperature c = 491.67.R to C
            Temperature raw = 491.67.R
            State a = |0>
            Measure a
        }
        """
    )
    ev = Evaluator(seed=0)
    run_canonical(compiled, ev)
    assert abs(ev.scalars["k"] - 273.15) < 1e-9
    assert abs(ev.scalars["f"] - 32.0) < 1e-9
    assert abs(ev.scalars["c"] - 0.0) < 1e-9
    assert abs(ev.scalars["raw"] - 491.67) < 1e-12


def test_k_to_r() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Temperature r = 273.15.K to R
            State a = |0>
            Measure a
        }
        """
    )
    ev = Evaluator(seed=0)
    run_canonical(compiled, ev)
    assert abs(ev.scalars["r"] - 491.67) < 1e-9


if __name__ == "__main__":
    test_rankine_table()
    print("PASS test_rankine_table")
    test_r_to_k_f_and_c()
    print("PASS test_r_to_k_f_and_c")
    test_k_to_r()
    print("PASS test_k_to_r")
