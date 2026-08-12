"""LISS-0271 selective import + LISS-0272 lane annotation."""

from __future__ import annotations

from pathlib import Path

from compiler.staqex.host import run_path, run_source
from compiler.staqex.pipeline import compile_source


def test_selective_import_braces(tmp_path: Path) -> None:
    domain = tmp_path / "domain"
    domain.mkdir()
    (domain / "ops.sqx").write_text(
        """
package demo.domain
pub class Keep {
    pub val x: Float
    fn init(x: Float) { this.x = x }
    pub fn get() -> Float { return this.x }
}
pub class Drop {
    pub val y: Float
    fn init(y: Float) { this.y = y }
}
""",
        encoding="utf-8",
    )
    main = tmp_path / "main.sqx"
    main.write_text(
        """
package demo
import demo.domain.ops.{Keep}
pub fn main() -> Unit {
    Keep k = Keep(2.0)
    Float v = k.get() * 0.5
    State s = dirac(v)
    measure s
}
""",
        encoding="utf-8",
    )
    r = run_path(str(main), settings={"seed": 0})
    assert r.status == "succeeded", r.diagnostics
    assert r.measurements[-1].value == 1.0


def test_enum_use_star_parses() -> None:
    src = """
package p
enum Phase { Tonight, Day }
use Phase.*
pub fn main() -> Unit {
    Phase p = Phase.Tonight
    State s = mix (p) {
      Tonight -> |0>,
      else -> |1>,
    }
    measure s
}
"""
    r = run_source(src, settings={"seed": 0})
    assert r.status == "succeeded", r.diagnostics


def test_lane_soft_foreach_under_experiment() -> None:
    src = """
// staqex-profile: experiment
// staqex-lane: experiment
QubitRegister<1> r = system()
forEach q in r {
  apply(H, q)
}
State s = |0>
measure s
"""
    c = compile_source(src)
    codes = {d.get("code") for d in c.diagnostics}
    assert "LANE_SOFT_CIRCUIT_IN_EXPERIMENT" in codes


def test_lane_circuit_suppresses_soft() -> None:
    src = """
// staqex-profile: experiment
// staqex-lane: circuit
QubitRegister<1> r = system()
forEach q in r {
  apply(H, q)
}
State s = |0>
measure s
"""
    c = compile_source(src)
    codes = {d.get("code") for d in c.diagnostics}
    assert "LANE_SOFT_CIRCUIT_IN_EXPERIMENT" not in codes
