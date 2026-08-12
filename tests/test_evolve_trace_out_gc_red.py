"""AT-TDD: LISS-0174 evolve-block Trace-Out GC MVP (ADR 0142)."""

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


def test_evolve_let_temps_traced_out() -> None:
    result = run_source(
        """
        package t
        pub fn main() -> Unit {
            State z = 3
            State w = evolve (z) times 1 {
                let temp1 = z * 2
                let temp2 = temp1 + 5
                temp2
            }
            State viewed_z = inspect(z)
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
    assert "w" in coords and "z" in coords, coords


def test_evolve_preserves_unrelated_live_coord() -> None:
    result = run_source(
        """
        package t
        pub fn main() -> Unit {
            State keep = |1>
            State z = 0
            State w = evolve (z) times 1 {
                let t = z + 1
                t
            }
            State viewed_w = inspect(w)
            State viewed_z = inspect(z)
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


def test_multi_step_evolve_drops_lets() -> None:
    result = run_source(
        """
        package t
        pub fn main() -> Unit {
            State z = 1
            State w = evolve (z) times 2 {
                let t = w + 1
                t
            }
            State viewed_z = inspect(z)
            measure w
        }
        """,
        stdout=io.StringIO(),
    )
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 3
    assert "t" not in _coords(result)


if __name__ == "__main__":
    test_evolve_let_temps_traced_out()
    print("PASS test_evolve_let_temps_traced_out")
    test_evolve_preserves_unrelated_live_coord()
    print("PASS test_evolve_preserves_unrelated_live_coord")
    test_multi_step_evolve_drops_lets()
    print("PASS test_multi_step_evolve_drops_lets")
