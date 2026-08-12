"""AT-TDD: LISS-0192 CPU data-parallel Joint world workers (ADR 0159)."""

from __future__ import annotations

import io
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.run import run_source  # noqa: E402
from compiler.staqex.runtime.joint import Joint, World, current_world_workers, world_workers  # noqa: E402


SRC = """
package t
pub fn main() -> Unit {
    State b = coin()
    State r = mix (b) { 0 -> 0, else -> 1 }
    measure r
}
"""


def test_world_workers_contextvar() -> None:
    assert current_world_workers() == 1
    with world_workers(4):
        assert current_world_workers() == 4
    assert current_world_workers() == 1


def test_parallel_pushforward_matches_sequential() -> None:
    def bump(a: dict) -> int:
        return int(a["x"]) + 1

    base = Joint(
        worlds=[
            World(assign={"x": 0}, amp=0.5 + 0.0j),
            World(assign={"x": 1}, amp=0.5 + 0.0j),
        ]
    )
    with world_workers(1):
        seq = base.bind_pushforward("y", bump)
    with world_workers(4):
        par = base.bind_pushforward("y", bump)
    assert [w.assign for w in seq.worlds] == [w.assign for w in par.worlds]
    assert [w.amp for w in seq.worlds] == [w.amp for w in par.worlds]


def test_run_source_parallel_matches_sequential_seed() -> None:
    seq = run_source(SRC, seed=7, stdout=io.StringIO(), data_parallel_workers=1)
    par = run_source(SRC, seed=7, stdout=io.StringIO(), data_parallel_workers=4)
    assert seq.compile_ok and par.compile_ok, (seq.diagnostics, par.diagnostics)
    assert seq.eval.measure is not None and par.eval.measure is not None
    assert seq.eval.measure.value == par.eval.measure.value
    assert par.eval.data_parallel_workers == 4
    assert seq.eval.data_parallel_workers == 1


def test_default_workers_is_one() -> None:
    result = run_source(SRC, seed=1, stdout=io.StringIO())
    assert result.compile_ok, result.diagnostics
    assert result.eval.data_parallel_workers == 1


if __name__ == "__main__":
    test_world_workers_contextvar()
    print("PASS test_world_workers_contextvar")
    test_parallel_pushforward_matches_sequential()
    print("PASS test_parallel_pushforward_matches_sequential")
    test_run_source_parallel_matches_sequential_seed()
    print("PASS test_run_source_parallel_matches_sequential_seed")
    test_default_workers_is_one()
    print("PASS test_default_workers_is_one")
