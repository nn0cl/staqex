"""ADR 0060 / 0061 — Joint preserve, classical phase/times, config harvest."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_path, compile_source  # noqa: E402
from compiler.staqex.run import run_path, run_source  # noqa: E402


def test_float_survives_grover_diffuse() -> None:
    src = """
package t
pub fn main() -> Unit {
    Float cfg = 2.0
    State b0 = coin()
    State b1 = coin()
    State idx = b0 * 2 + b1
    State marked = phase(idx, pi, cfg)
    State amplified = grover_diffuse(marked)
    State viewed = inspect(cfg)
    State b0 = |0>
    State b1 = |0>
    measure amplified
}
"""
    buf = io.StringIO()
    r = run_source(src, seed=0, stdout=buf)
    assert r.compile_ok, r.diagnostics
    assert r.eval.measure is not None
    assert "2.0" in buf.getvalue()


def test_phase_only_from_float_scalar() -> None:
    src = """
package t
pub fn main() -> Unit {
    Float target = 2.0
    State b0 = coin()
    State b1 = coin()
    State idx = b0 * 2 + b1
    State marked = phase(idx, pi, target)
    State amplified = grover_diffuse(marked)
    State b0 = |0>
    State b1 = |0>
    measure amplified
}
"""
    r = run_source(src, seed=0, stdout=io.StringIO())
    assert r.compile_ok, r.diagnostics
    assert r.eval.measure is not None
    assert r.eval.measure.value == 2


def test_evolve_times_classical_float() -> None:
    src = """
package t
pub fn step(c: State<Qubit>, x: State<Position>) -> State<(Qubit, Position)> {
    Operator CoinOp = 0.7071067811865476 * (X + Z)
    State<Qubit> c = apply(CoinOp, c)
    State<Position> x = walk_shift(c, x)
    return c *|* x
}
pub fn main() -> Unit {
    Float n_steps = 2.0
    State<Qubit> c = |+>
    State<Position> x = dirac(0)
    State<(Qubit, Position)> (c, x) = c *|* x
    State (c, x) = evolve (c, x) times n_steps {
        step(c, x)
    }
    State c = |0>
    measure x
}
"""
    r = run_source(src, seed=0, stdout=io.StringIO())
    assert r.compile_ok, r.diagnostics
    assert r.eval.measure is not None


def test_classical_harvest_from_pub_fun(tmp_path: Path) -> None:
    lib = tmp_path / "hints.sqx"
    lib.write_text(
        """
package demo.hints
pub class Hints {
    Float r = 4.0
}
""",
        encoding="utf-8",
    )
    main = tmp_path / "main.sqx"
    main.write_text(
        """
package demo
import demo.hints
pub fn main() -> Unit {
    State viewed = inspect(r)
    State bit = coin()
    measure bit
}
""",
        encoding="utf-8",
    )
    compiled = compile_path(main)
    assert not any(
        d.get("code") == "CONFIG_HARVEST_COLLISION_ERROR" for d in compiled.diagnostics
    )
    buf = io.StringIO()
    r = run_path(main, seed=0, stdout=buf)
    assert r.compile_ok, r.diagnostics
    assert "4.0" in buf.getvalue()


def test_harvest_collision_diagnostic(tmp_path: Path) -> None:
    lib = tmp_path / "hints.sqx"
    lib.write_text(
        """
package demo.hints
pub class Hints {
    Float r = 4.0
}
""",
        encoding="utf-8",
    )
    main = tmp_path / "main.sqx"
    main.write_text(
        """
package demo
import demo.hints
pub fn main() -> Unit {
    Float r = 9.0
    State v = inspect(r)
    State bit = coin()
    measure bit
}
""",
        encoding="utf-8",
    )
    compiled = compile_path(main)
    assert any(
        d.get("code") == "CONFIG_HARVEST_COLLISION_ERROR" for d in compiled.diagnostics
    )


def test_city_route_example_linked() -> None:
    path = _REPO / "examples/applied/A04_hp_protein_folding/main_hp_protein_folding.sqx"
    r = run_path(path, seed=0, stdout=io.StringIO())
    assert r.compile_ok
    assert r.eval.measure is not None
    # Seed-0 collapse under current HP folding narrative.
    assert r.eval.measure.value in {1, 2}
