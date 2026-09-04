"""AT-TDD: LISS-0156 explicit SI scale `to` (ADR 0124)."""

from __future__ import annotations

from canonical_execution import run_canonical

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.dimensions import UNIT_SCALE_TO_CANONICAL  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402


def _codes(source: str) -> set[str]:
    return {d.get("code", "") for d in compile_source(source).diagnostics}


def test_scale_table_mvp_pairs() -> None:
    assert UNIT_SCALE_TO_CANONICAL["ms"] == ("s", 1e-3)
    assert UNIT_SCALE_TO_CANONICAL["nm"] == ("m", 1e-9)
    assert UNIT_SCALE_TO_CANONICAL["GHz"] == ("Hz", 1e9)


def test_explicit_to_converts_magnitude() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            Time t = 5.0.ms to s
            Length x = 2.0.nm to m
            Frequency f = 1.0.GHz to Hz
            State a = |0>
            Measure a
        }
        """
    )
    assert "PARSE_ERROR" not in codes, codes
    assert "DIMENSION_MISMATCH_ERROR" not in codes, codes
    assert "TYPE_MISMATCH" not in codes, codes

    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Time t = 5.0.ms to s
            State a = |0>
            Measure a
        }
        """
    )
    assert not [
        d
        for d in compiled.diagnostics
        if d.get("code")
        in {"PARSE_ERROR", "TYPE_MISMATCH", "DIMENSION_MISMATCH_ERROR"}
    ]
    ev = Evaluator(seed=0)
    result = run_canonical(compiled, ev)
    assert abs(ev.scalars["t"] - 0.005) < 1e-12
    assert result.measure is not None


def test_bare_suffix_stays_raw() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Time t = 5.0.ms
            State a = |0>
            Measure a
        }
        """
    )
    ev = Evaluator(seed=0)
    run_canonical(compiled, ev)
    assert abs(ev.scalars["t"] - 5.0) < 1e-12


def test_dim_mismatch_and_unknown_pair() -> None:
    mismatch = _codes(
        """
        package t
        pub fn main() -> Unit {
            Time t = 5.0.ms to m
            State a = |0>
            Measure a
        }
        """
    )
    assert "DIMENSION_MISMATCH_ERROR" in mismatch or "TYPE_MISMATCH" in mismatch

    unknown = _codes(
        """
        package t
        pub fn main() -> Unit {
            Mass m = 1.0.kg to bob
            State a = |0>
            Measure a
        }
        """
    )
    assert "TYPE_MISMATCH" in unknown or "PARSE_ERROR" in unknown


if __name__ == "__main__":
    test_scale_table_mvp_pairs()
    print("PASS test_scale_table_mvp_pairs")
    test_explicit_to_converts_magnitude()
    print("PASS test_explicit_to_converts_magnitude")
    test_bare_suffix_stays_raw()
    print("PASS test_bare_suffix_stays_raw")
    test_dim_mismatch_and_unknown_pair()
    print("PASS test_dim_mismatch_and_unknown_pair")
