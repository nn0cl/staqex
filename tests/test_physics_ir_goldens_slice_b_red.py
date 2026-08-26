"""AT-TDD: LISS-0117 Slice B — golden verify against LISS-0115 lowered IR."""

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


def _equation() -> EquationNode:
    origin = SourceOrigin(source_id="oscillator.sqx", line=12, col=1)
    unit = Unit(symbol="J", dimensions=(1, 1, -2), origin=origin)
    coefficient = Coefficient(expression="omega", unit=unit, origin=origin)
    return EquationNode(
        kind="dynamics",
        left="H",
        right="omega * N",
        coefficients=(coefficient,),
        origin=origin,
    )


def test_verify_against_lowered_is_importable() -> None:
    _, verify_golden_against_lowered, _ = _load_api()
    assert callable(verify_golden_against_lowered)


def test_oscillator_golden_matches_lowered_equation_module() -> None:
    load_physics_ir_goldens, verify_golden_against_lowered, lower = _load_api()
    compiled, hir = _hir_fixture()
    equation = _equation()

    goldens = {
        golden.golden_id: golden for golden in load_physics_ir_goldens(_FIXTURES)
    }
    golden = goldens["PIR-G-OSCILLATOR-001"]
    module = lower(hir, unit=compiled.unit, equations=(equation,))

    assert verify_golden_against_lowered(golden, module) == []
    assert golden.oracle_promoted is False


def test_oscillator_golden_rejects_module_without_equation() -> None:
    load_physics_ir_goldens, verify_golden_against_lowered, lower = _load_api()
    compiled, hir = _hir_fixture()

    goldens = {
        golden.golden_id: golden for golden in load_physics_ir_goldens(_FIXTURES)
    }
    golden = goldens["PIR-G-OSCILLATOR-001"]
    module = lower(hir, unit=compiled.unit, equations=())

    diagnostics = verify_golden_against_lowered(golden, module)
    assert any(
        diagnostic.get("code") == "PHYSICS_IR_GOLDEN_ERROR"
        for diagnostic in diagnostics
    ), diagnostics


if __name__ == "__main__":
    try:
        test_verify_against_lowered_is_importable()
        test_oscillator_golden_matches_lowered_equation_module()
        test_oscillator_golden_rejects_module_without_equation()
    except Exception as exc:
        print(f"RED: {type(exc).__name__}: {exc}")
        raise SystemExit(1) from exc
    print("OK — LISS-0117 Slice B")
