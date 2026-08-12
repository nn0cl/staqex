"""LISS-0294: nested classical free-fn object args + local shadowing."""

from __future__ import annotations

from compiler.staqex.host import run_source


def test_nested_freefn_object_param() -> None:
    """Outer free-fn may call another free-fn with the same object param."""
    src = """
package p
namespace D {
  pub struct Edge { val open_weight: Float }
  pub struct Corridor { val e01: D.Edge val e12: D.Edge }
}
pub fn open_score(c: D.Corridor) -> Float {
  return c.e01.open_weight + c.e12.open_weight
}
pub fn blockage(c: D.Corridor) -> Float {
  return 4.0 - open_score(c)
}
pub fn main() -> Unit {
  D.Edge e1 = D.Edge(1.0)
  D.Edge e2 = D.Edge(0.5)
  D.Corridor map = D.Corridor(e1, e2)
  Float b = blockage(map)
  State s = dirac(b)
  measure s
}
"""
    r = run_source(src, settings={"seed": 0})
    assert r.status == "succeeded", r.diagnostics
    assert r.measurements[-1].value == 2.5


def test_nested_freefn_field_projection_arg() -> None:
    """Nested free-fn may take a field of a free-fn local struct."""
    src = """
package p
namespace D {
  pub struct Item { val effect: Float }
  pub struct Queue { val a: D.Item val b: D.Item }
}
pub fn priority(item: D.Item) -> Float {
  return item.effect * 10.0
}
pub fn queue_pressure(q: D.Queue) -> Float {
  return priority(q.a) + priority(q.b)
}
pub fn main() -> Unit {
  D.Item a = D.Item(0.9)
  D.Item b = D.Item(0.7)
  D.Queue queue = D.Queue(a, b)
  Float p = queue_pressure(queue)
  State s = dirac(p)
  measure s
}
"""
    r = run_source(src, settings={"seed": 0})
    assert r.status == "succeeded", r.diagnostics
    assert r.measurements[-1].value == 16.0


def test_freefn_param_shadows_outer_object() -> None:
    """Free-fn param name may match an outer object without leaking fields."""
    src = """
package p
namespace D {
  pub struct Cmd { val phase_code: Float }
  pub struct Site { val open_weight: Float }
  pub struct Board { val coastal: D.Site }
}
pub fn site_rem(s: D.Site) -> Float {
  return s.open_weight
}
pub fn total(board: D.Board) -> Float {
  return site_rem(board.coastal)
}
pub fn main() -> Unit {
  D.Cmd board = D.Cmd(1.0)
  D.Site coastal = D.Site(3.0)
  D.Board shelters = D.Board(coastal)
  Float t = total(shelters)
  State s = dirac(t)
  measure s
}
"""
    r = run_source(src, settings={"seed": 0})
    assert r.status == "succeeded", r.diagnostics
    assert r.measurements[-1].value == 3.0
