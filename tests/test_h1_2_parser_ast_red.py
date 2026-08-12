"""Acceptance tests for formal H1 Parser/AST ownership."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


_H1_SOURCE = """
theory Ising {
  parameter J: Energy
  parameter h: Energy
  operator H(J, h) = -J * (Z[0] * Z[1]) - h * (X[0] + X[1])
}

experiment run(J = 1.0, h = 0.5) {
  State psi = |+>
  psi |> Evolve under Ising.H(J, h) for 0.7
  observable energy = expect(Ising.H, psi)
  Measure psi
}
"""


def test_h1_2_parser_returns_compilation_unit_and_theory_ast() -> None:
    compiled = compile_source(_H1_SOURCE)

    assert not compiled.diagnostics
    assert compiled.unit is not None
    theory = next(
        declaration
        for declaration in compiled.unit.decls
        if type(declaration).__name__ == "TheoryDecl"
    )
    assert theory.name == "Ising"
    assert theory.parameters
    assert theory.operators
    assert theory.span.line > 0


def test_h1_2_parser_preserves_experiment_statement_order() -> None:
    compiled = compile_source(_H1_SOURCE)

    assert compiled.unit is not None
    experiment = next(
        declaration
        for declaration in compiled.unit.decls
        if type(declaration).__name__ == "ExperimentDecl"
    )
    assert [type(statement).__name__ for statement in experiment.body] == [
        "H1Prepare",
        "H1Evolve",
        "H1Observable",
        "H1Measure",
    ]


def test_h1_2_physics_ir_is_lowered_from_formal_source() -> None:
    compiled = compile_source(_H1_SOURCE)

    assert compiled.physics_ir is not None
    assert compiled.physics_ir.source_origin is not None
    assert any(
        getattr(node, "kind", "") == "H1Theory" for node in compiled.physics_ir.nodes
    )
    assert compiled.unit is not None


def test_h1_2_legacy_scientific_scope_does_not_enter_h1_ast() -> None:
    compiled = compile_source(
        """
        theory Ising { Operator H = X + Z }
        experiment GroundState { theory = Ising }
        """
    )

    assert compiled.unit is not None
    assert all(
        type(declaration).__name__ != "TheoryDecl"
        for declaration in compiled.unit.decls
    )


if __name__ == "__main__":
    for test in (
        test_h1_2_parser_returns_compilation_unit_and_theory_ast,
        test_h1_2_parser_preserves_experiment_statement_order,
        test_h1_2_physics_ir_is_lowered_from_formal_source,
        test_h1_2_legacy_scientific_scope_does_not_enter_h1_ast,
    ):
        test()
