"""AT-TDD: LISS-0164 exact SI eV ↔ J (ADR 0132)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.dimensions import UNIT_SCALE_TO_CANONICAL  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402

_E = 1.602176634e-19


def test_ev_scale_table() -> None:
    assert UNIT_SCALE_TO_CANONICAL["eV"] == ("J", _E)
    assert UNIT_SCALE_TO_CANONICAL["J"] == ("J", 1.0)


def test_ev_to_j_and_reverse() -> None:
    codes = {
        d.get("code", "")
        for d in compile_source(
            """
            package t
            pub fn main() -> Unit {
                Energy e = 1.0.eV to J
                Energy back = 1.602176634e-19.J to eV
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
            Energy e = 1.0.eV to J
            Energy raw = 1.0.eV
            Energy back = 1.602176634e-19.J to eV
            State a = |0>
            Measure a
        }
        """
    )
    ev = Evaluator(seed=0)
    ev.run_unit(compiled.unit)
    assert abs(ev.scalars["e"] - _E) < 1e-30
    assert abs(ev.scalars["raw"] - 1.0) < 1e-12
    assert abs(ev.scalars["back"] - 1.0) < 1e-12


if __name__ == "__main__":
    test_ev_scale_table()
    print("PASS test_ev_scale_table")
    test_ev_to_j_and_reverse()
    print("PASS test_ev_to_j_and_reverse")
