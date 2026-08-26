"""LISS-0292: Type-First object args on classical free functions."""

from __future__ import annotations

from compiler.staqex.host import run_source


def test_typefirst_class_arg_multi_stmt_body() -> None:
    src = """
package p
namespace D {
  pub class Q {
    pub val road_km: Length
    fn init(road_km: Length) { this.road_km = road_km }
  }
}
pub fn road_m(q: D.Q) -> Length {
  Length road = q.road_km to m
  return road
}
pub fn main() -> Unit {
  D.Q qty = D.Q(12.0.km)
  Length r = road_m(qty)
  State s = Dirac(1)
  Measure s
}
"""
    r = run_source(src, settings={"seed": 0})
    assert r.status == "succeeded", r.diagnostics


def test_typefirst_class_arg_return_convert() -> None:
    src = """
package p
namespace D {
  pub class Q {
    pub val water_kg: Mass
    fn init(water_kg: Mass) { this.water_kg = water_kg }
  }
}
pub fn water_g(q: D.Q) -> Mass {
  return q.water_kg to g
}
pub fn main() -> Unit {
  D.Q qty = D.Q(2.0.kg)
  Mass m = water_g(qty)
  State s = Dirac(1)
  Measure s
}
"""
    r = run_source(src, settings={"seed": 0})
    assert r.status == "succeeded", r.diagnostics


def test_float_struct_arg_still_works() -> None:
    src = """
package p
namespace D {
  pub struct Item { val n: Float }
}
pub fn dbl(i: D.Item) -> Float {
  return i.n * 2.0
}
pub fn main() -> Unit {
  D.Item a = D.Item(3.0)
  Float t = dbl(a)
  State s = Dirac(t)
  Measure s
}
"""
    r = run_source(src, settings={"seed": 0})
    assert r.status == "succeeded", r.diagnostics
    assert r.measurements[-1].value == 6.0
