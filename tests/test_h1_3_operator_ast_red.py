"""Phase 1 Red tests for structured H1 operators."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {str(diagnostic.get("code", "")) for diagnostic in compile_source(source).diagnostics}


def test_h1_3_operator_has_structured_expression_and_parameters() -> None:
    compiled = compile_source(
        """
        theory Ising {
          parameter J: Energy
          parameter h: Energy
          operator H(J, h) = -J * (Z[0] * Z[1]) - h * (X[0] + X[1])
        }
        experiment run(J = 1.0, h = 0.5) { Measure H }
        """
    )

    assert not compiled.diagnostics
    assert compiled.unit is not None
    theory = next(declaration for declaration in compiled.unit.decls if type(declaration).__name__ == "TheoryDecl")
    operator = theory.operators[0]
    assert operator.parameters == ["J", "h"]
    assert operator.expression is not None
    assert type(operator.expression).__name__ in {"OpBin", "OperatorExpr"}
    assert operator.expression.span.line > 0


def test_h1_3_dimensionally_valid_hamiltonian_is_retained() -> None:
    compiled = compile_source(
        """
        theory Ising {
          parameter J: Energy
          parameter h: Energy
          operator H(J, h) = -J * Z[0] - h * X[0]
        }
        experiment run(J = 1.0, h = 0.5) { Measure H }
        """
    )

    assert not compiled.diagnostics
    operator = next(declaration for declaration in compiled.unit.decls if type(declaration).__name__ == "TheoryDecl").operators[0]
    assert operator.type_ref.name == "Operator"
    assert operator.dimension == "Energy"


def test_h1_3_dimension_mismatch_rejects_operator_artifact() -> None:
    codes = _codes(
        """
        theory Invalid {
          parameter J: Energy
          parameter dt: Time
          operator H(J, dt) = J + dt
        }
        experiment run(J = 1.0, dt = 0.1) { Measure H }
        """
    )

    assert "DIMENSION_MISMATCH_ERROR" in codes


def test_h1_3_non_hermitian_hamiltonian_is_rejected() -> None:
    codes = _codes(
        """
        theory Invalid {
          operator H = i * X
        }
        experiment run() { Measure H }
        """
    )

    assert "NON_HERMITIAN_OPERATOR_ERROR" in codes


def test_h1_3_physics_ir_contains_structured_operator_node() -> None:
    compiled = compile_source(
        """
        theory Ising {
          parameter J: Energy
          operator H(J) = -J * Z[0]
        }
        experiment run(J = 1.0) { Measure H }
        """
    )

    assert compiled.physics_ir is not None
    operator_nodes = [
        node for node in compiled.physics_ir.nodes
        if getattr(node, "kind", "") == "H1Operator"
    ]
    assert operator_nodes
    assert operator_nodes[0].atoms
    assert operator_nodes[0].typed_reference is not None


if __name__ == "__main__":
    for test in (
        test_h1_3_operator_has_structured_expression_and_parameters,
        test_h1_3_dimensionally_valid_hamiltonian_is_retained,
        test_h1_3_dimension_mismatch_rejects_operator_artifact,
        test_h1_3_non_hermitian_hamiltonian_is_rejected,
        test_h1_3_physics_ir_contains_structured_operator_node,
    ):
        test()
