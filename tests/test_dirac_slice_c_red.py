"""AT-TDD Phase 1 Red: LISS-0073 Slice C — bra–op–ket matrix element."""

from __future__ import annotations

import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.ast_nodes import BraLit, Call, KetLit, StateBind, Var
from compiler.staqex.pipeline import compile_source

BRA_OPEN = "<"
KET_CLOSE = ">"
EBNF_PATH = _REPO / "docs" / "specs" / "grammar" / "staqex.ebnf"


def _codes(compiled) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compiled.diagnostics}


def _main_binds(compiled) -> list[StateBind]:
    assert compiled.unit is not None, compiled.diagnostics
    assert compiled.unit.main is not None, "expected MainDecl"
    return [stmt for stmt in compiled.unit.main.body.stmts if isinstance(stmt, StateBind)]


def _matrix_element_source() -> str:
    # <0|X|1> -> inner(<0|, X(|1>)) per Slice C plan.
    return f"""
        package t
        pub fn main() -> Unit {{
            State m = {BRA_OPEN}0|X|1{KET_CLOSE}
            State observed = coin()
            measure observed
        }}
        """


def test_matrix_element_parses_as_inner_of_bra_and_op_on_ket() -> None:
    compiled = compile_source(_matrix_element_source())

    assert "PARSE_ERROR" not in _codes(compiled), compiled.diagnostics
    binds = [bind for bind in _main_binds(compiled) if bind.name == "m"]
    assert len(binds) == 1
    expr = binds[0].expr
    assert isinstance(expr, Call)
    assert isinstance(expr.callee, Var) and expr.callee.name == "inner"
    assert len(expr.args) == 2
    assert isinstance(expr.args[0], BraLit) and expr.args[0].label == "0"
    applied = expr.args[1]
    assert isinstance(applied, Call)
    assert isinstance(applied.callee, Var) and applied.callee.name == "X"
    assert len(applied.args) == 1
    assert isinstance(applied.args[0], KetLit) and applied.args[0].label == "1"


def test_matrix_element_typechecks_like_inner_phi_A_psi() -> None:
    compiled = compile_source(_matrix_element_source())

    assert compiled.ok, compiled.diagnostics
    assert "OPERATOR_ALGEBRA_TYPE_ERROR" not in _codes(compiled)


def test_matrix_element_rejects_state_middle_with_algebra_error() -> None:
    compiled = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            State psi = |+>
            State m = {BRA_OPEN}0|psi|1{KET_CLOSE}
            State observed = coin()
            measure observed
        }}
        """
    )

    assert "OPERATOR_ALGEBRA_TYPE_ERROR" in _codes(compiled)


def test_slice_b_inner_without_middle_still_works() -> None:
    compiled = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            State overlap = inner({BRA_OPEN}0|, |1{KET_CLOSE})
            State observed = coin()
            measure observed
        }}
        """
    )

    assert compiled.ok, compiled.diagnostics
    binds = [bind for bind in _main_binds(compiled) if bind.name == "overlap"]
    assert isinstance(binds[0].expr, Call)
    assert isinstance(binds[0].expr.callee, Var) and binds[0].expr.callee.name == "inner"
    assert isinstance(binds[0].expr.args[1], KetLit)


def test_ebnf_documents_bra_op_ket_matrix_element() -> None:
    text = EBNF_PATH.read_text(encoding="utf-8")
    assert "bra_op_ket" in text or re.search(
        r"bra_lit.*operator|matrix.?element|bra_op_ket", text, re.I
    ), "EBNF must document <phi|A|psi> matrix-element surface"


def main() -> None:
    test_matrix_element_parses_as_inner_of_bra_and_op_on_ket()
    print("PASS test_matrix_element_parses_as_inner_of_bra_and_op_on_ket")
    test_matrix_element_typechecks_like_inner_phi_A_psi()
    print("PASS test_matrix_element_typechecks_like_inner_phi_A_psi")
    test_matrix_element_rejects_state_middle_with_algebra_error()
    print("PASS test_matrix_element_rejects_state_middle_with_algebra_error")
    test_slice_b_inner_without_middle_still_works()
    print("PASS test_slice_b_inner_without_middle_still_works")
    test_ebnf_documents_bra_op_ket_matrix_element()
    print("PASS test_ebnf_documents_bra_op_ket_matrix_element")
    print("OK - LISS-0073 Slice C Phase 1 Red")


if __name__ == "__main__":
    main()
