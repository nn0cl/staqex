"""LISS-0306: nested OpAttr free-fn coeffs + effects sample."""

from __future__ import annotations

from pathlib import Path

from compiler.staqex.host import run_path, run_source


def test_nested_opattr_on_struct_free_fn() -> None:
    src = """
// staqex-lane: experiment
namespace N {
  pub struct Inner { val c: Float }
  pub struct Outer { val inner: N.Inner }
}
pub fn h_of(o: N.Outer) -> Operator {
  return o.inner.c * Z[0]
}
i = Inner(1.0545718e-19)
o = Outer(i)
H = h_of(o)
State s = |+>
State s = evolve { s under H for 0.1.fs }.run()
measure s
"""
    r = run_source(src, settings={"seed": 0})
    assert r.status == "succeeded", r.diagnostics


def test_class_receiver_opattr_free_fn() -> None:
    src = """
// staqex-lane: experiment
namespace N {
  pub class Drive {
    pub val c: Float
    fn init(c: Float) { this.c = c }
  }
}
pub fn h_of(d: N.Drive) -> Operator {
  return d.c * Z[0]
}
D = Drive(1.0545718e-19)
H = h_of(D)
State s = |+>
State s = evolve { s under H for 0.1.fs }.run()
measure s
"""
    r = run_source(src, settings={"seed": 0})
    assert r.status == "succeeded", r.diagnostics


def test_b16_effect_marking_sample() -> None:
    path = (
        Path(__file__).resolve().parents[1]
        / "examples/basics/B16_effect_marking/effect_marking.sqx"
    )
    r = run_path(str(path), settings={"seed": 0})
    assert r.status == "succeeded", r.diagnostics
