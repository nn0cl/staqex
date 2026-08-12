"""WP-0089 sugar: ADR 0180–0183 Kernel Red/Green tests."""

from __future__ import annotations

from pathlib import Path

from compiler.staqex.host import run_path, run_source
from compiler.staqex.pipeline import compile_source


def test_0182_default_experiment_profile_no_package() -> None:
    src = """
State s = dirac(7)
measure s
"""
    c = compile_source(src)
    assert c.ok, c.diagnostics
    assert c.unit is not None
    assert c.unit.package is not None
    assert c.unit.package.path == ["staqex", "experiment"]
    r = run_source(src, settings={"seed": 0})
    assert r.status == "succeeded", r.diagnostics
    assert r.measurements[-1].value == 7


def test_0182_packaged_still_requires_main() -> None:
    src = """
package demo.pkg
State s = dirac(1)
measure s
"""
    c = compile_source(src)
    codes = {d.get("code") for d in c.diagnostics}
    assert "TOPLEVEL_EXECUTION_ERROR" in codes


def test_0180_inferred_classical_and_operator() -> None:
    src = """
// staqex-profile: experiment
J = 1.0545718e-19
h = 5.272859e-20
H = -J * (Z[0] * Z[1]) - h * (X[0] + X[1])
State s0 = |+>
State s1 = |+>
State (s0, s1) = evolve { (s0, s1) under H for 0.3.fs using Suzuki(order = 2, steps = 2) }.run()
measure s0 tracing_out s1
"""
    r = run_source(src, settings={"seed": 0})
    assert r.status == "succeeded", r.diagnostics
    assert not r.measurements[-1].vacuum


def test_0181_named_struct_and_nested() -> None:
    src = """
package p
namespace D {
  pub struct Item { val n: Float }
  pub struct Board {
    val a: D.Item
    val b: D.Item
  }
}
pub fn main() -> Unit {
  D.Item a = D.Item { n: 1.0 }
  D.Item b = D.Item { n: 2.0 }
  D.Board board = D.Board(a, b)
  Float t = board.a.n + board.b.n
  State s = dirac(t)
  measure s
}
"""
    r = run_source(src, settings={"seed": 0})
    assert r.status == "succeeded", r.diagnostics
    assert r.measurements[-1].value == 3.0


def test_0183_relative_import(tmp_path: Path) -> None:
    domain = tmp_path / "domain"
    domain.mkdir()
    (domain / "ops.sqx").write_text(
        """
package demo.domain
pub struct Keep {
  val x: Float
}
""",
        encoding="utf-8",
    )
    main = tmp_path / "main.sqx"
    main.write_text(
        """
package demo
import .domain.ops.{Keep}
pub fn main() -> Unit {
  Keep k = Keep { x: 2.0 }
  Float v = k.x * 0.5
  State s = dirac(v)
  measure s
}
""",
        encoding="utf-8",
    )
    r = run_path(str(main), settings={"seed": 0})
    assert r.status == "succeeded", r.diagnostics
    assert r.measurements[-1].value == 1.0


def test_0183_parent_relative_import(tmp_path: Path) -> None:
    """`import ..domain` from a sibling package (lexer RANGE token)."""
    domain = tmp_path / "domain"
    domain.mkdir()
    (domain / "ops.sqx").write_text(
        """
package demo.domain
pub struct Keep {
  val x: Float
}
""",
        encoding="utf-8",
    )
    lane = tmp_path / "lane"
    lane.mkdir()
    main = lane / "main.sqx"
    main.write_text(
        """
package demo.lane
import ..domain.ops.{Keep}
pub fn main() -> Unit {
  Keep k = Keep { x: 4.0 }
  State s = dirac(k.x)
  measure s
}
""",
        encoding="utf-8",
    )
    r = run_path(str(main), settings={"seed": 0})
    assert r.status == "succeeded", r.diagnostics
    assert r.measurements[-1].value == 4.0
