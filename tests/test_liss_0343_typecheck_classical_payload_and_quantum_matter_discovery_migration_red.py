"""AT-TDD: LISS-0343 -- fix Classical +/- payload-collapse bug in
typecheck.py, then migrate quantum_matter_discovery to real units
(WP-0095 work unit 11).

Design decision: docs/issues/LISS-0343-typecheck-classical-payload-and-quantum-matter-discovery-migration.md
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex import compile_source, compile_path, run_path  # noqa: E402

_QMD_PATH = str(
    _REPO
    / "examples/showcase/quantum_matter_discovery/main_quantum_matter_discovery.sqx"
)


def _hard(diags: list[dict]) -> list[dict]:
    return [
        d
        for d in diags
        if not str(d.get("code", "")).startswith("QSEM_")
        and d.get("code") != "MULTI_REGISTER_INDEX_AMBIGUOUS"
    ]


# --- Part A: typecheck.py Classical +/- payload-collapse bug ---------------


def test_energy_plus_energy_preserves_energy_payload() -> None:
    src = """
    fn add_energy(a: Energy, b: Energy) -> Energy {
        return a + b
    }

    pub fn main() -> Unit {
        Energy x = 1.0.eV to J
        Energy y = 2.0.eV to J
        Energy z = add_energy(x, y)
        State s = |0>
        Measure s
    }
    """
    compiled = compile_source(src)
    hard = _hard(compiled.diagnostics)
    assert compiled.ok and not hard, hard


def test_int_plus_int_still_promotes_to_float_legacy_convention() -> None:
    src = """
    class Box {
        val x: Int
        fn init(value: Int) { this.x = value }
        fn doubled() -> State<Float> {
            return Dirac(this.x + this.x)
        }
    }

    pub fn main() -> Unit {
        Box b = Box(3)
        State s = b.doubled()
        Measure s
    }
    """
    compiled = compile_source(src)
    hard = _hard(compiled.diagnostics)
    assert compiled.ok and not hard, hard


# --- Part B: quantum_matter_discovery real-unit migration ------------------


def test_quantum_matter_discovery_compiles_and_runs_to_a_real_terminal_measurement() -> (
    None
):
    compiled = compile_path(_QMD_PATH)
    hard_compile = _hard(compiled.diagnostics)
    assert compiled.ok and not hard_compile, hard_compile

    result = run_path(
        _QMD_PATH, settings={"target": "local", "seed": 0}, stdout=io.StringIO()
    )
    hard_run = _hard(result.diagnostics)
    assert result.status == "succeeded" and not hard_run, (result.status, hard_run)
    assert result.measurements
    assert not result.measurements[0].vacuum
