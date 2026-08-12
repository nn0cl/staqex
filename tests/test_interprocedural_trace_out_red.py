"""AT-TDD: LISS-0191 interprocedural Trace-Out GC (ADR 0158)."""

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


def test_dead_caller_axis_traced_out_after_library_call() -> None:
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
    assert "r" in coords, coords
    assert "x" not in coords, coords
    assert "y" not in coords, coords


def test_live_caller_axis_preserved_when_used_later() -> None:
    result = run_source(
        """
        package t
        fn double(y: State<Int>) -> State<Int> {
            return y * 2
        }
        pub fn main() -> Unit {
            State x = 3
            State r = double(x)
            State s = r + 1
            State viewed = Inspect(r)
            Measure s
        }
        """,
        stdout=io.StringIO(),
    )
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 7
    coords = _coords(result)
    assert "s" in coords, coords
    assert "y" not in coords, coords


def test_unrelated_live_coord_preserved() -> None:
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
    test_dead_caller_axis_traced_out_after_library_call()
    print("PASS test_dead_caller_axis_traced_out_after_library_call")
    test_live_caller_axis_preserved_when_used_later()
    print("PASS test_live_caller_axis_preserved_when_used_later")
    test_unrelated_live_coord_preserved()
    print("PASS test_unrelated_live_coord_preserved")
