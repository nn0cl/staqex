"""AT-TDD: LISS-0314 display-unit restore after promote (ADR 0186)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.dimensions import from_canonical_magnitude, to_canonical_magnitude
from compiler.staqex.pipeline import compile_source
from compiler.staqex.runtime.evaluator import Evaluator


def test_from_canonical_roundtrip_g() -> None:
    canon, u = to_canonical_magnitude(1000.0, "g")
    assert u == "kg"
    assert abs(from_canonical_magnitude(canon, "g") - 1000.0) < 1e-12


def test_lhs_g_plus_kg_restores_g() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Mass a = 1.0.g + 1.0.kg
            State x = |0>
            Measure x
        }
        """
    )
    assert "UNIT_MIXED_ARITHMETIC_ERROR" not in {
        d.get("code", "") for d in compiled.diagnostics
    }
    ev = Evaluator(seed=0)
    ev.run_unit(compiled.unit)
    assert abs(ev.scalars["a"] - 1001.0) < 1e-9
    assert ev.scalar_units.get("a") == "g"


def test_lhs_kg_plus_g_stays_kg() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Mass a = 1.0.kg + 1.0.g
            State x = |0>
            Measure x
        }
        """
    )
    ev = Evaluator(seed=0)
    ev.run_unit(compiled.unit)
    assert abs(ev.scalars["a"] - 1.001) < 1e-12
    assert ev.scalar_units.get("a") == "kg"


def test_lhs_f_plus_c_restores_f() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Temperature t = 32.0.F + 0.0.C
            State x = |0>
            Measure x
        }
        """
    )
    ev = Evaluator(seed=0)
    ev.run_unit(compiled.unit)
    # 32°F + 0°C in K → 546.3 K → restore to F
    expected = from_canonical_magnitude(546.3, "F")
    assert abs(ev.scalars["t"] - expected) < 1e-9
    assert ev.scalar_units.get("t") == "F"
