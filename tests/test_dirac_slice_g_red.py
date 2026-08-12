"""AT-TDD Phase 1 Red: LISS-0073 Slice G — formula→AST freeze proof."""

from __future__ import annotations

import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.ast_nodes import (
    BraLit,
    Call,
    KetLit,
    ListExpr,
    StateBind,
    TensorExpr,
    Var,
)
from compiler.staqex.pipeline import compile_source

BRA = "<"
KET = ">"
TENSOR = "*|*"
PLAN_PATH = _REPO / "docs" / "specs" / "staqex-v1-dirac-algebra-ast-plan.md"


def _codes(compiled) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compiled.diagnostics}


def _main_binds(compiled) -> list[StateBind]:
    assert compiled.unit is not None, compiled.diagnostics
    assert compiled.unit.main is not None, "expected MainDecl"
    return [stmt for stmt in compiled.unit.main.body.stmts if isinstance(stmt, StateBind)]


def _bind(compiled, name: str) -> StateBind:
    binds = [b for b in _main_binds(compiled) if b.name == name]
    assert len(binds) == 1, (name, compiled.diagnostics)
    return binds[0]


def test_formula_table_frozen_without_if_approved() -> None:
    """§4 must record shipped bracket rules, not provisional 'if approved'."""
    text = PLAN_PATH.read_text(encoding="utf-8")
    assert "## 4." in text or "formula" in text.lower()
    assert "(if approved)" not in text, (
        "Slice G must freeze §4: remove provisional '(if approved)' from "
        "[A,B] / {A,B} rows and document Operator-context / brace rules"
    )
    assert re.search(
        r"Operator-context|Operator bind|ListExpr",
        text,
    ), "Frozen table must document Operator-context vs ListExpr for [A,B]"


def test_formatter_emit_policy_section_present() -> None:
    text = PLAN_PATH.read_text(encoding="utf-8")
    assert re.search(
        r"formatter emit policy|## Formatter emit|### Formatter emit",
        text,
        re.IGNORECASE,
    ), "Slice G must add an explicit formatter emit policy section"
    assert "dual-accept" in text.lower() or "M-P06" in text


def test_alone_bra_row() -> None:
    compiled = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            State b = {BRA}0|
            State observed = Coin()
            Measure observed
        }}
        """
    )
    assert "PARSE_ERROR" not in _codes(compiled), compiled.diagnostics
    assert isinstance(_bind(compiled, "b").expr, BraLit)


def test_inner_row() -> None:
    compiled = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            State m = inner({BRA}0|, |1{KET})
            State observed = Coin()
            Measure observed
        }}
        """
    )
    assert "PARSE_ERROR" not in _codes(compiled), compiled.diagnostics
    expr = _bind(compiled, "m").expr
    assert isinstance(expr, Call)
    assert isinstance(expr.callee, Var) and expr.callee.name == "inner"


def test_matrix_element_row() -> None:
    compiled = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            State m = {BRA}0|X|1{KET}
            State observed = Coin()
            Measure observed
        }}
        """
    )
    assert "PARSE_ERROR" not in _codes(compiled), compiled.diagnostics
    expr = _bind(compiled, "m").expr
    assert isinstance(expr, Call)
    assert isinstance(expr.callee, Var) and expr.callee.name == "inner"
    assert isinstance(expr.args[1], Call)


def test_outer_and_projector_rows() -> None:
    outer = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            Operator O = outer(|0{KET}, {BRA}1|)
            State observed = Coin()
            Measure observed
        }}
        """
    )
    proj = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            Operator P = projector(|0{KET})
            State observed = Coin()
            Measure observed
        }}
        """
    )
    assert "PARSE_ERROR" not in _codes(outer), outer.diagnostics
    assert "PARSE_ERROR" not in _codes(proj), proj.diagnostics
    o = _bind(outer, "O").expr
    p = _bind(proj, "P").expr
    assert isinstance(o, Call) and isinstance(o.callee, Var) and o.callee.name == "outer"
    assert isinstance(p, Call) and isinstance(p.callee, Var) and p.callee.name == "projector"


def test_adjoint_dagger_row() -> None:
    compiled = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            State a = adjoint(X)
            State observed = Coin()
            Measure observed
        }}
        """
    )
    assert "PARSE_ERROR" not in _codes(compiled), compiled.diagnostics
    expr = _bind(compiled, "a").expr
    assert isinstance(expr, Call)
    assert isinstance(expr.callee, Var) and expr.callee.name == "adjoint"


def test_tensor_row() -> None:
    compiled = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            State t = |0{KET} {TENSOR} |1{KET}
            State observed = Coin()
            Measure observed
        }}
        """
    )
    assert "PARSE_ERROR" not in _codes(compiled), compiled.diagnostics
    assert isinstance(_bind(compiled, "t").expr, TensorExpr)


def test_commutator_anticommutator_rows() -> None:
    comm = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Operator C = [X, Y]
            State observed = Coin()
            Measure observed
        }
        """
    )
    anti = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Operator A = {X, Y}
            State observed = Coin()
            Measure observed
        }
        """
    )
    assert "PARSE_ERROR" not in _codes(comm), comm.diagnostics
    assert "PARSE_ERROR" not in _codes(anti), anti.diagnostics
    c = _bind(comm, "C").expr
    a = _bind(anti, "A").expr
    assert isinstance(c, Call) and isinstance(c.callee, Var) and c.callee.name == "commutator"
    assert isinstance(a, Call) and isinstance(a.callee, Var) and a.callee.name == "anticommutator"


def test_expr_list_not_stolen_by_commutator() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State xs = [X, Y]
            State observed = Coin()
            Measure observed
        }
        """
    )
    assert "PARSE_ERROR" not in {d.get("code", "") for d in compiled.diagnostics}, (
        compiled.diagnostics
    )
    assert isinstance(_bind(compiled, "xs").expr, ListExpr)


def main() -> None:
    test_formula_table_frozen_without_if_approved()
    print("PASS test_formula_table_frozen_without_if_approved")
    test_formatter_emit_policy_section_present()
    print("PASS test_formatter_emit_policy_section_present")
    test_alone_bra_row()
    print("PASS test_alone_bra_row")
    test_inner_row()
    print("PASS test_inner_row")
    test_matrix_element_row()
    print("PASS test_matrix_element_row")
    test_outer_and_projector_rows()
    print("PASS test_outer_and_projector_rows")
    test_adjoint_dagger_row()
    print("PASS test_adjoint_dagger_row")
    test_tensor_row()
    print("PASS test_tensor_row")
    test_commutator_anticommutator_rows()
    print("PASS test_commutator_anticommutator_rows")
    test_expr_list_not_stolen_by_commutator()
    print("PASS test_expr_list_not_stolen_by_commutator")
    print("OK - LISS-0073 Slice G")


if __name__ == "__main__":
    main()
