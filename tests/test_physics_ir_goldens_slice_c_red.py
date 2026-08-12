"""AT-TDD: LISS-0117 Slice C — Equation/Unit assertions + catalog closeout."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.hir import build_hir
from compiler.staqex.physics_equation import Coefficient, EquationNode, Unit
from compiler.staqex.physics_ir import SourceOrigin
from compiler.staqex.pipeline import compile_source

_FIXTURES = _REPO / "tests" / "fixtures" / "physics_ir"
_CATALOG = _REPO / "docs" / "specs" / "staqex-v1-physics-ir-golden-catalog.md"


def _load_api():
    from compiler.staqex.physics_ir_goldens import (
        load_physics_ir_goldens,
        verify_golden_against_lowered,
    )
    from compiler.staqex.physics_ir_lower import lower_hir_to_physics_ir

    return load_physics_ir_goldens, verify_golden_against_lowered, lower_hir_to_physics_ir


def _hir_fixture():
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Operator H = X + Z
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )
    assert compiled.ok, compiled.diagnostics
    assert compiled.checker is not None
    assert compiled.unit is not None
    hir = build_hir(
        compiled.checker,
        scope_contracts=compiled.scope_contracts,
        unit=compiled.unit,
    )
    return compiled, hir


def _equation(*, with_unit: bool) -> EquationNode:
    origin = SourceOrigin(source_id="oscillator.sqx", line=12, col=1)
    unit = Unit(symbol="J", dimensions=(1, 1, -2), origin=origin) if with_unit else None
    coefficient = Coefficient(expression="omega", unit=unit, origin=origin)
    return EquationNode(
        kind="dynamics",
        left="H",
        right="omega * N",
        coefficients=(coefficient,),
        origin=origin,
    )


def test_oscillator_golden_requires_coefficient_unit() -> None:
    load_physics_ir_goldens, verify_golden_against_lowered, lower = _load_api()
    compiled, hir = _hir_fixture()
    golden = {
        item.golden_id: item for item in load_physics_ir_goldens(_FIXTURES)
    }["PIR-G-OSCILLATOR-001"]

    module = lower(hir, unit=compiled.unit, equations=(_equation(with_unit=False),))
    diagnostics = verify_golden_against_lowered(golden, module)
    assert any(
        diagnostic.get("code")
        in {"PHYSICS_EQUATION_UNIT_ERROR", "PHYSICS_IR_GOLDEN_ERROR"}
        for diagnostic in diagnostics
    ), diagnostics


def test_oscillator_golden_accepts_equation_with_unit() -> None:
    load_physics_ir_goldens, verify_golden_against_lowered, lower = _load_api()
    compiled, hir = _hir_fixture()
    golden = {
        item.golden_id: item for item in load_physics_ir_goldens(_FIXTURES)
    }["PIR-G-OSCILLATOR-001"]

    module = lower(hir, unit=compiled.unit, equations=(_equation(with_unit=True),))
    assert verify_golden_against_lowered(golden, module) == []


def test_catalog_records_oscillator_lowered_ir_evidence() -> None:
    catalog = _CATALOG.read_text()
    assert "not a promoted runtime oracle" in catalog
    assert "PIR-G-OSCILLATOR-001" in catalog
    assert "lowered-IR evidence" in catalog
    assert "LISS-0117" in catalog


if __name__ == "__main__":
    try:
        test_oscillator_golden_requires_coefficient_unit()
        test_oscillator_golden_accepts_equation_with_unit()
        test_catalog_records_oscillator_lowered_ir_evidence()
    except Exception as exc:
        print(f"RED: {type(exc).__name__}: {exc}")
        raise SystemExit(1) from exc
    print("OK — LISS-0117 Slice C")
