"""AT-TDD: LISS-0185 bare-block Trace-Out GC (ADR 0153)."""

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


def test_bare_block_let_temps_traced_out() -> None:
    result = run_source(
        """
        package t
        pub fn main() -> Unit {
            State w = {
                let z = 3
                let temp1 = z * 2
                let temp2 = temp1 + 5
                temp2
            }
            measure w
        }
        """,
        stdout=io.StringIO(),
    )
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 11
    coords = _coords(result)
    assert "temp1" not in coords and "temp2" not in coords, coords
    assert "z" not in coords, coords
    assert "w" in coords, coords


def test_bare_block_preserves_unrelated_live_coord() -> None:
    result = run_source(
        """
        package t
        pub fn main() -> Unit {
            State keep = |1>
            State w = {
                let t = 7
                t
            }
            State viewed = inspect(w)
            measure keep
        }
        """,
        stdout=io.StringIO(),
    )
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 1
    coords = _coords(result)
    assert "keep" in coords, coords
    assert "t" not in coords, coords


if __name__ == "__main__":
    test_bare_block_let_temps_traced_out()
    print("PASS test_bare_block_let_temps_traced_out")
    test_bare_block_preserves_unrelated_live_coord()
    print("PASS test_bare_block_preserves_unrelated_live_coord")
