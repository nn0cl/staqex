"""AT-TDD Phase 1 Red: LISS-0054 unified indexed-operator notation.

ADR 0096 D1 makes ``Op[index]`` the single operator spelling everywhere and
retires parenthesised indexed atoms without an alias. These tests pin the
breaking boundary before parser/typechecker migration begins.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.ast_nodes import Call, OpBin, OpIndexed, OpPauli  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402


def _operator_bind(compiled, name: str = "H"):
    assert compiled.unit is not None
    for stmt in compiled.unit.main.body.stmts:
        if getattr(stmt, "names", None) == [name]:
            return stmt.expr
    raise AssertionError(f"no `{name}` bind found")


def _codes(source: str) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compile_source(source).diagnostics}


def test_bracketed_pauli_is_one_indexed_operator_ast_node_everywhere() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Operator H = Z[0]
            State psi = |0>
            measure psi
        }
        """
    )

    assert compiled.ok, compiled.diagnostics
    expr = _operator_bind(compiled)
    assert isinstance(expr, OpIndexed)
    assert isinstance(expr.base, OpPauli)
    assert expr.base.kind == "Z"


def test_bracketed_second_quantized_atoms_work_in_their_family_bind() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            FermionOperator<Orbitals> H = create[0] * annihilate[0]
            State observed = coin()
            measure observed
        }
        """
    )

    assert compiled.ok, compiled.diagnostics
    expr = _operator_bind(compiled)
    assert isinstance(expr, OpBin)
    assert expr.op == "*"
    assert isinstance(expr.lhs, OpIndexed)
    assert isinstance(expr.rhs, OpIndexed)


def test_parenthesized_operator_index_is_retired_without_alias() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            Operator H = Z(0)
            State psi = |0>
            measure psi
        }
        """
    )

    assert "RETIRED_OPERATOR_INDEX_SYNTAX" in codes


def test_user_callable_named_like_operator_atom_is_not_rejected_by_name() -> None:
    compiled = compile_source(
        """
        package t
        fn Z(x: Int) -> Operator {
            Operator k = X
            return k
        }
        pub fn main() -> Unit {
            Operator H = Z(0)
            State psi = |0>
            measure psi
        }
        """
    )

    assert compiled.ok, compiled.diagnostics
    expr = _operator_bind(compiled)
    assert isinstance(expr, Call)
    assert expr.callee.name == "Z"


if __name__ == "__main__":
    tests = [
        test_bracketed_pauli_is_one_indexed_operator_ast_node_everywhere,
        test_bracketed_second_quantized_atoms_work_in_their_family_bind,
        test_parenthesized_operator_index_is_retired_without_alias,
        test_user_callable_named_like_operator_atom_is_not_rejected_by_name,
    ]
    passed, failed = 0, 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as exc:  # noqa: BLE001 -- Red run report only
            failed += 1
            print(f"RED (expected): {test.__name__}: {type(exc).__name__}: {exc}")
    print(f"\n{passed} passed, {failed} failed (Phase 2 Green)")
