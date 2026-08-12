"""LISS-0115 Slice C acceptance tests for Equation/Unit consumption."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.hir import build_hir
from compiler.staqex.physics_equation import Coefficient, EquationNode, Unit
from compiler.staqex.pipeline import compile_source
from compiler.staqex.physics_ir import SourceOrigin


def _load_api():
    from compiler.staqex.physics_ir_lower import (
        lower_hir_to_physics_ir,
        verify_lowered_physics_ir,
    )

    return lower_hir_to_physics_ir, verify_lowered_physics_ir


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


def test_slice_c_lowering_consumes_equation_dto_without_rewriting_it() -> None:
    lower_hir_to_physics_ir, verify_lowered_physics_ir = _load_api()
    compiled, hir = _hir_fixture()
    equation = _equation()

    module = lower_hir_to_physics_ir(
        hir,
        unit=compiled.unit,
        equations=(equation,),
    )

    assert equation in module.nodes
    assert equation.coefficients[0].unit.symbol == "J"
    assert equation.origin in module.origins
    assert verify_lowered_physics_ir(module) == []


def test_slice_c_lowering_preserves_equation_order_and_is_deterministic() -> None:
    lower_hir_to_physics_ir, _ = _load_api()
    compiled, hir = _hir_fixture()
    first_equation = _equation()
    second_equation = EquationNode(
        kind="equality",
        left="E",
        right="hbar * omega",
        coefficients=first_equation.coefficients,
        origin=first_equation.origin,
    )

    first = lower_hir_to_physics_ir(
        hir,
        unit=compiled.unit,
        equations=(first_equation, second_equation),
    )
    second = lower_hir_to_physics_ir(
        hir,
        unit=compiled.unit,
        equations=(first_equation, second_equation),
    )

    assert tuple(node.kind for node in first.nodes if isinstance(node, EquationNode)) == (
        "dynamics",
        "equality",
    )
    assert first.nodes == second.nodes
    assert first.origins == second.origins


def test_slice_c_verification_reports_invalid_nested_equation_contracts() -> None:
    lower_hir_to_physics_ir, verify_lowered_physics_ir = _load_api()
    compiled, hir = _hir_fixture()
    origin = SourceOrigin(source_id="ising.sqx", line=4, col=2)
    invalid = EquationNode(
        kind="equality",
        left="H",
        right="J * Z",
        coefficients=(Coefficient(expression="J", unit=None, origin=origin),),
        origin=None,
    )

    module = lower_hir_to_physics_ir(hir, unit=compiled.unit, equations=(invalid,))
    codes = {diagnostic["code"] for diagnostic in verify_lowered_physics_ir(module)}

    assert "PHYSICS_EQUATION_PROVENANCE_ERROR" in codes
    assert "PHYSICS_EQUATION_UNIT_ERROR" in codes


def test_slice_c_lowering_rejects_untyped_generic_equation_payloads() -> None:
    lower_hir_to_physics_ir, _ = _load_api()
    compiled, hir = _hir_fixture()

    try:
        lower_hir_to_physics_ir(hir, unit=compiled.unit, equations=("H = J * Z",))
    except TypeError as exc:
        assert "EquationNode" in str(exc)
    else:
        raise AssertionError("generic equation payload must not be silently coerced")


if __name__ == "__main__":
    for test in (
        test_slice_c_lowering_consumes_equation_dto_without_rewriting_it,
        test_slice_c_lowering_preserves_equation_order_and_is_deterministic,
        test_slice_c_verification_reports_invalid_nested_equation_contracts,
        test_slice_c_lowering_rejects_untyped_generic_equation_payloads,
    ):
        test()
    print("OK — LISS-0115 Slice C")
