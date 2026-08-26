"""AT-TDD: LISS-0349 -- fix Classical */ payload-collapse bug in
typecheck.py (sibling of LISS-0343's already-fixed +/- branch).

Design decision: docs/issues/LISS-0349-typecheck-classical-mul-div-payload-fix.md
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex import compile_source  # noqa: E402


def _hard(diags: list[dict]) -> list[dict]:
    return [
        d
        for d in diags
        if not str(d.get("code", "")).startswith("QSEM_")
        and d.get("code") != "MULTI_REGISTER_INDEX_AMBIGUOUS"
    ]


def test_energy_div_length_preserves_force_payload() -> None:
    src = """
    fn force_from_energy(e: Energy, len: Length) -> Force {
        return e / len
    }

    pub fn main() -> Unit {
        Energy e = 1.0.eV to J
        Length len = 1.0.m
        Force f = force_from_energy(e, len)
        State s = |0>
        Measure s
    }
    """
    compiled = compile_source(src)
    hard = _hard(compiled.diagnostics)
    assert compiled.ok and not hard, hard


def test_int_times_int_still_type_checks_in_state_context() -> None:
    src = """
    class Box {
        val x: Int
        fn init(value: Int) { this.x = value }
        fn squared() -> State<Int> {
            return Dirac(this.x * this.x)
        }
    }

    pub fn main() -> Unit {
        Box b = Box(3)
        State s = b.squared()
        Measure s
    }
    """
    compiled = compile_source(src)
    hard = _hard(compiled.diagnostics)
    assert compiled.ok and not hard, hard
