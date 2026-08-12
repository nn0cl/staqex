"""LISS-0295: selective import transitively links sibling free-fn callees."""

from __future__ import annotations

from pathlib import Path

from compiler.staqex.host import compile_path, run_path


def test_selective_import_nested_freefn_executes(tmp_path: Path) -> None:
    """Outer free-fn may call a sibling not named in the import braces."""
    domain = tmp_path / "domain"
    domain.mkdir()
    (domain / "scores.sqx").write_text(
        """
package demo.domain

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
""",
        encoding="utf-8",
    )
    main = tmp_path / "main.sqx"
    main.write_text(
        """
package demo
import demo.domain.scores.{Item, Queue, queue_pressure}
pub fn main() -> Unit {
  Item a = Item(0.9)
  Item b = Item(0.7)
  Queue q = Queue(a, b)
  Float p = queue_pressure(q)
  State s = dirac(p)
  measure s
}
""",
        encoding="utf-8",
    )
    r = run_path(str(main), settings={"seed": 0})
    assert r.status == "succeeded", r.diagnostics
    assert r.measurements[-1].value == 16.0


def test_selective_import_does_not_pull_unused_sibling(tmp_path: Path) -> None:
    """Unused free-fns in the same module stay unlinked when not selected."""
    domain = tmp_path / "domain"
    domain.mkdir()
    (domain / "scores.sqx").write_text(
        """
package demo.domain
pub struct Box { val n: Float }
pub fn used(b: Box) -> Float { return b.n }
pub fn unused(b: Box) -> Float { return b.n * 99.0 }
""",
        encoding="utf-8",
    )
    main = tmp_path / "main.sqx"
    main.write_text(
        """
package demo
import demo.domain.scores.{Box, used}
pub fn main() -> Unit {
  Box b = Box(2.0)
  Float v = used(b)
  State s = dirac(v)
  measure s
}
""",
        encoding="utf-8",
    )
    c = compile_path(str(main))
    assert c.unit is not None
    fun_names = {
        d.name
        for d in c.unit.decls
        if type(d).__name__ == "FunDecl"
    }
    assert "used" in fun_names
    assert "unused" not in fun_names


def test_selective_import_bare_pipe_stage_transitive(tmp_path: Path) -> None:
    """Bare pipe stages (``seed |> dbl``) transitively link unary free-fns."""
    domain = tmp_path / "domain"
    domain.mkdir()
    (domain / "pipe.sqx").write_text(
        """
package demo.domain
pub fn add_ten(x: State<Int>) -> State<Int> {
  return x + 10
}
pub fn dbl(s: State<Int>) -> State<Int> {
  return s * 2
}
pub fn compose(seed: State<Int>) -> State<Int> {
  return seed |> add_ten |> dbl
}
""",
        encoding="utf-8",
    )
    main = tmp_path / "main.sqx"
    main.write_text(
        """
package demo
import demo.domain.pipe.{compose}
pub fn main() -> Unit {
  State out = compose(3)
  measure out
}
""",
        encoding="utf-8",
    )
    r = run_path(str(main), settings={"seed": 0})
    assert r.status == "succeeded", r.diagnostics
    # (3 + 10) * 2 = 26
    assert r.measurements[-1].value == 26.0
