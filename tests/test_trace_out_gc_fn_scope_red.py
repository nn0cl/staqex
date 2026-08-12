"""AT-TDD: LISS-0170 Trace-Out GC MVP for library fn scopes (ADR 0138)."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.run import run_source  # noqa: E402


def _coords(result) -> set[str]:
    names: set[str] = set()
    for w in result.eval.joint.worlds:
        names.update(w.assign)
    return names


def test_fn_param_axis_traced_out_after_call() -> None:
    result = run_source(
        """
        package t
        fn double(y: State<Int>) -> State<Int> {
            return y * 2
        }
        pub fn main() -> Unit {
            State x = 3
            State r = double(x)
            Measure r
        }
        """,
        stdout=io.StringIO(),
    )
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 6
    coords = _coords(result)
    assert "y" not in coords, coords
    assert "r" in coords, coords
    # ADR 0158: caller `x` is dead after Call when only `r` is live-out.
    assert "x" not in coords, coords


def test_caller_live_coords_preserved() -> None:
    result = run_source(
        """
        package t
        fn id(y: State<Bit>) -> State<Bit> {
            return y
        }
        pub fn main() -> Unit {
            State keep = |1>
            State x = |0>
            State r = id(x)
            State viewed = Inspect(r)
            Measure keep
        }
        """,
        stdout=io.StringIO(),
    )
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 1
    coords = _coords(result)
    assert "keep" in coords, coords
    assert "y" not in coords, coords


if __name__ == "__main__":
    test_fn_param_axis_traced_out_after_call()
    print("PASS test_fn_param_axis_traced_out_after_call")
    test_caller_live_coords_preserved()
    print("PASS test_caller_live_coords_preserved")
