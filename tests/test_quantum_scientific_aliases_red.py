"""AT-TDD Phase 1 Red: compact scientific symbols and aliases (ADR 0189)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.ast_nodes import Call, Measure, StateBind, Var
from compiler.staqex.pipeline import compile_source


def _main_binds(compiled) -> list[StateBind]:
    assert compiled.unit is not None, compiled.diagnostics
    assert compiled.unit.main is not None, "expected MainDecl"
    return [
        stmt
        for stmt in compiled.unit.main.body.stmts
        if isinstance(stmt, StateBind)
    ]


def _bind(compiled, name: str) -> StateBind:
    binds = [bind for bind in _main_binds(compiled) if bind.name == name]
    assert len(binds) == 1, (name, compiled.diagnostics)
    return binds[0]


def test_ascii_commutator_alias_has_the_same_meaning_as_brackets() -> None:
    bracketed = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Operator C = [X, Y]
            State observed = coin()
            measure observed
        }
        """
    )
    aliased = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Operator C = cm(X, Y)
            State observed = coin()
            measure observed
        }
        """
    )

    bracket_expr = _bind(bracketed, "C").expr
    alias_expr = _bind(aliased, "C").expr
    assert isinstance(bracket_expr, Call)
    assert isinstance(alias_expr, Call)
    assert isinstance(bracket_expr.callee, Var)
    assert isinstance(alias_expr.callee, Var)
    assert alias_expr.callee.name == bracket_expr.callee.name == "commutator"


def test_ascii_scientific_state_alias_normalizes_to_blackboard_symbol() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State psi = |+>
            measure psi
        }
        """
    )

    assert _bind(compiled, "psi").name == "psi"


def test_ascii_wavefunction_name_is_the_canonical_binding_identity() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State psi = |+>
            measure psi
        }
        """
    )

    binds = _main_binds(compiled)
    assert [bind.name for bind in binds if bind.name == "psi"] == ["psi"]
    assert compiled.unit is not None and compiled.unit.main is not None
    measures = [
        stmt for stmt in compiled.unit.main.body.stmts if isinstance(stmt, Measure)
    ]
    assert len(measures) == 1
    assert isinstance(measures[0].expr, Var)
    assert measures[0].expr.name == "psi"


if __name__ == "__main__":
    test_ascii_commutator_alias_has_the_same_meaning_as_brackets()
    test_ascii_scientific_state_alias_normalizes_to_blackboard_symbol()
    test_ascii_wavefunction_name_is_the_canonical_binding_identity()
    print("RED - compact scientific symbol aliases are not implemented")
