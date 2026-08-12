"""AT-TDD Phase 1 Red: LISS-0254 — Type-First field unit retention (ADR 0174).

Gherkin (Then clauses drive assertions):

Feature: dimful class/struct fields retain units
  Scenario: class Mass field converts with to
    Given `pub val stock: Mass` initialized with `1.0.kg`
    When a method returns `this.stock to g`
    Then compile succeeds without TYPE_MISMATCH / DIMENSION_MISMATCH
    And the bound Mass magnitude is ≈ 1000 with unit `g`

  Scenario: class Mass fields mixed + promote
    Given fields `a=1.0.kg` and `b=500.0.g`
    When a method returns `this.a + this.b`
    Then magnitude is ≈ 1.5 with unit `kg` (not raw 501)

  Scenario: struct Mass field converts with to
    Given `struct Pack { pub val water: Mass }` constructed with `1.0.kg`
    When `p.water to g` is bound
    Then compile succeeds and magnitude ≈ 1000 with unit `g`

  Scenario: Float field does not invent Mass units
    Given `pub val x: Float`
    When `this.x to kg` is attempted
    Then DIMENSION_MISMATCH_ERROR (or equivalent fail-closed)
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402


def _hard_codes(compiled) -> set[str]:
    return {
        str(d.get("code", ""))
        for d in compiled.diagnostics
        if str(d.get("code", ""))
        in {
            "TYPE_MISMATCH",
            "DIMENSION_MISMATCH_ERROR",
            "PRODUCT_TYPE_MISMATCH",
            "PARSE_ERROR",
            "LEX_ERROR",
            "UNIT_MIXED_ARITHMETIC_ERROR",
        }
    }


def test_class_mass_field_to_g_retains_source_unit() -> None:
    src = """
    package t
    class Box {
        pub val stock: Mass
        fn init(stock: Mass) {
            this.stock = stock
        }
        pub fn as_g() -> Mass {
            Mass x = this.stock to g
            return x
        }
    }
    pub fn main() -> Unit {
        Box b = Box(1.0.kg)
        Mass grams = b.as_g()
        State q = coin()
        measure q
    }
    """
    compiled = compile_source(src)
    hard = _hard_codes(compiled)
    assert "TYPE_MISMATCH" not in hard, compiled.diagnostics
    assert "DIMENSION_MISMATCH_ERROR" not in hard, compiled.diagnostics
    assert "PARSE_ERROR" not in hard, compiled.diagnostics
    assert compiled.ok and compiled.unit is not None, compiled.diagnostics
    ev = Evaluator(seed=0)
    ev.run_unit(compiled.unit)
    assert abs(float(ev.scalars["grams"]) - 1000.0) < 1e-9, ev.scalars.get("grams")
    assert ev.scalar_units.get("grams") == "g", ev.scalar_units


def test_class_mass_fields_mixed_plus_promotes_to_kg() -> None:
    src = """
    package t
    class Box {
        pub val a: Mass
        pub val b: Mass
        fn init(a: Mass, b: Mass) {
            this.a = a
            this.b = b
        }
        pub fn sum_kg() -> Mass {
            Mass s = this.a + this.b
            return s
        }
    }
    pub fn main() -> Unit {
        Box b = Box(1.0.kg, 500.0.g)
        Mass total = b.sum_kg()
        State q = coin()
        measure q
    }
    """
    compiled = compile_source(src)
    hard = _hard_codes(compiled)
    assert "UNIT_MIXED_ARITHMETIC_ERROR" not in hard, compiled.diagnostics
    assert "PARSE_ERROR" not in hard, compiled.diagnostics
    assert compiled.ok and compiled.unit is not None, compiled.diagnostics
    ev = Evaluator(seed=0)
    ev.run_unit(compiled.unit)
    # Must promote 500 g → 0.5 kg, not raw 1+500=501.
    assert abs(float(ev.scalars["total"]) - 1.5) < 1e-9, ev.scalars.get("total")
    assert ev.scalar_units.get("total") == "kg", ev.scalar_units


def test_struct_mass_field_to_g_retains_source_unit() -> None:
    src = """
    package t
    struct Pack {
        pub val water: Mass
    }
    pub fn main() -> Unit {
        Pack p = Pack(1.0.kg)
        Mass grams = p.water to g
        State q = coin()
        measure q
    }
    """
    compiled = compile_source(src)
    hard = _hard_codes(compiled)
    assert "TYPE_MISMATCH" not in hard, compiled.diagnostics
    assert "DIMENSION_MISMATCH_ERROR" not in hard, compiled.diagnostics
    assert "PRODUCT_TYPE_MISMATCH" not in hard, compiled.diagnostics
    assert "PARSE_ERROR" not in hard, compiled.diagnostics
    assert compiled.ok and compiled.unit is not None, compiled.diagnostics
    ev = Evaluator(seed=0)
    ev.run_unit(compiled.unit)
    assert abs(float(ev.scalars["grams"]) - 1000.0) < 1e-9, ev.scalars.get("grams")
    assert ev.scalar_units.get("grams") == "g", ev.scalar_units


def test_float_field_to_kg_remains_fail_closed() -> None:
    src = """
    package t
    class Box {
        pub val x: Float
        fn init(x: Float) {
            this.x = x
        }
        pub fn as_mass() -> Mass {
            Mass m = this.x to kg
            return m
        }
    }
    pub fn main() -> Unit {
        Box b = Box(1.0)
        Mass m = b.as_mass()
        State q = coin()
        measure q
    }
    """
    codes = {str(d.get("code", "")) for d in compile_source(src).diagnostics}
    assert "DIMENSION_MISMATCH_ERROR" in codes, codes


if __name__ == "__main__":
    test_class_mass_field_to_g_retains_source_unit()
    print("PASS class to g")
    test_class_mass_fields_mixed_plus_promotes_to_kg()
    print("PASS mixed +")
    test_struct_mass_field_to_g_retains_source_unit()
    print("PASS struct to g")
    test_float_field_to_kg_remains_fail_closed()
    print("PASS float fail-closed")
    print("OK")
