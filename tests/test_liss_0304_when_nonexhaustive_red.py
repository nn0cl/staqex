"""LISS-0304: closed-enum `when` must be exhaustive without `else`."""

from __future__ import annotations

from compiler.staqex.host import run_source
from compiler.staqex.pipeline import HARD_CODES, compile_source


def test_incomplete_enum_when_hard_fails() -> None:
    src = """
// staqex-lane: experiment
namespace M {
  pub enum Phase { Tonight, Morning, Day }
}
M.Phase p = M.Phase.Day
State s = Mix (p) {
  Tonight -> |0>,
  Morning -> |+>,
}
Measure s
"""
    c = compile_source(src)
    codes = {d.get("code") for d in c.diagnostics}
    assert "WHEN_NONEXHAUSTIVE" in codes
    assert any(d.get("code") in HARD_CODES for d in c.diagnostics)


def test_exhaustive_enum_when_without_else_ok() -> None:
    src = """
// staqex-lane: experiment
namespace M {
  pub enum Phase { Tonight, Morning, Day }
}
M.Phase p = M.Phase.Day
State s = Mix (p) {
  Tonight -> |0>,
  Morning -> |+>,
  Day -> |1>,
}
Measure s
"""
    r = run_source(src, settings={"seed": 0})
    assert r.status == "succeeded", r.diagnostics
    assert r.measurements[-1].value == 1.0


def test_else_covers_missing_variants() -> None:
    src = """
// staqex-lane: experiment
namespace M {
  pub enum Phase { Tonight, Morning, Day }
}
M.Phase p = M.Phase.Day
State s = Mix (p) {
  Tonight -> |0>,
  else -> |1>,
}
Measure s
"""
    r = run_source(src, settings={"seed": 0})
    assert r.status == "succeeded", r.diagnostics
    assert r.measurements[-1].value == 1.0
