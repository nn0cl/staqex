"""R01–R06: inferred Wire numeric rejection, with positive neighbors.

The original public q + 1 case stays in its LISS-0583 file and is selected
unchanged alongside this suite. It is not copied or imported here.
"""

import pytest

from compiler.staqex.ast_nodes import (
    BinOp, Block, ExprStmt, ForEachStmt, LitFloat, LitInt, Span,
    StateBind, TypeRef, Var,
)
from compiler.staqex.codegen_qasm import OpenQASM3Generator
from compiler.staqex.dimensions import DIMLESS, TYPE_DIMS
from compiler.staqex.pipeline import compile_source
from compiler.staqex.typecheck import Ty, TypeChecker

OPS = ("+", "-", "*", "/", "^")
SPAN = Span(12, 8)
SOURCE = """package t
pub fn main() -> Unit {
    QubitRegister<3> reg = system()
    ForEach q in reg {
        BODY
    }
    State<Int> answer = Coin()
    Measure answer
}
"""


def numeric_diagnostic(diagnostics):
    matches = [d for d in diagnostics if d.get("code") == "QPU_CLASSICAL_CONTROL_ERROR"]
    assert matches, diagnostics
    return matches


@pytest.mark.parametrize("op", OPS)
@pytest.mark.parametrize("side", ("left", "right"))
def test_wire_operand_rejects_with_binary_source_diagnostic(op, side):
    checker = TypeChecker()
    checker.env["element"] = Ty("Wire", "Qubit", DIMLESS)
    operands = [Var("element", Span(12, 2)), LitInt(2, Span(12, 20))]
    if side == "right":
        operands.reverse()
    checker._infer(BinOp(op, *operands, SPAN))
    diagnostics = numeric_diagnostic(checker.diagnostics)
    assert any((d.get("line"), d.get("col")) == (12, 8) for d in diagnostics)
    message = " ".join(d.get("message", "").lower() for d in diagnostics)
    assert "opaque" in message and "element" in message
    assert "numeric" in message or "arithmetic" in message


PUBLIC_CASES = [(op, side) for op in OPS for side in ("left", "right")
                if (op, side) != ("+", "left")]


@pytest.mark.parametrize("op,side", PUBLIC_CASES)
def test_public_compile_rejects_other_wire_numeric_forms(op, side):
    expression = f"q {op} 2" if side == "left" else f"2 {op} q"
    compiled = compile_source(SOURCE.replace("BODY", f"Float k = {expression}"))
    numeric_diagnostic(compiled.diagnostics)
    assert not compiled.ok


@pytest.mark.parametrize("body,element", [
    ("Int alias = q\n        Int k = alias + 1", "q"),
    ("Int k = (q + 1) * 2", "q"),
    ("Int k = 2 * (1 + q)", "q"),
    ("Int k = factor + 1", "factor"),
])
def test_alias_nested_and_renamed_handles_remain_rejected(body, element):
    source = SOURCE.replace("ForEach q", f"ForEach {element}").replace("BODY", body)
    compiled = compile_source(source)
    numeric_diagnostic(compiled.diagnostics)
    assert not compiled.ok


@pytest.mark.parametrize("operator", ("H", "X"))
def test_legal_gate_operation_retains_all_ordered_qasm_members(operator):
    compiled = compile_source(SOURCE.replace("BODY", f"apply({operator}, q)"))
    assert compiled.ok, compiled.diagnostics
    text = OpenQASM3Generator(route=False).generate(compiled.unit)
    prefix = operator.lower()
    operations = [line.split("//", 1)[0].rstrip() for line in text.splitlines()
                  if line.startswith(f"{prefix} q[")]
    assert operations == [f"{prefix} q[{i}];" for i in range(3)]


@pytest.mark.parametrize("kind,payload,op,expected_kind,expected_payload", [
    ("State", "Int", "+", "State", "Int"),
    ("State", "Int", "-", "State", "Int"),
    ("State", "Int", "*", "State", "Int"),
    ("State", "Int", "/", "State", "Int"),
    ("State", "Int", "^", "State", "Float"),
    ("State", "Qubit", "+", "State", "Qubit"),
    ("Classical", "Float", "+", "Classical", "Float"),
    ("Classical", "Int", "*", "Classical", "Int"),
    ("Classical", "Energy", "*", "Classical", "Energy"),
    ("Classical", "Energy", "/", "Classical", "Energy"),
])
def test_non_wire_numeric_kind_payload_and_dimension_are_preserved(
    kind, payload, op, expected_kind, expected_payload,
):
    checker = TypeChecker()
    dimension = TYPE_DIMS.get(payload, DIMLESS)
    checker.env["q"] = Ty(kind, payload, dimension)
    literal = LitFloat(2.0, SPAN) if payload == "Energy" else LitInt(2, SPAN)
    result = checker._infer(BinOp(op, Var("q", SPAN), literal, SPAN))
    assert (result.kind, result.payload, result.dim) == (
        expected_kind, expected_payload, dimension,
    )
    assert checker.diagnostics == []


def test_numeric_named_q_outside_foreach_remains_valid():
    source = """pub fn main() -> Unit {
        Int q = 2
        Float k = q + 1
        State answer = Dirac(k)
        Measure answer
    }"""
    compiled = compile_source(source)
    assert compiled.ok, compiled.diagnostics
    assert "QPU_CLASSICAL_CONTROL_ERROR" not in {d.get("code") for d in compiled.diagnostics}


def test_no_wire_numeric_expression_inside_foreach_is_not_blanket_rejected():
    compiled = compile_source(SOURCE.replace("BODY", "Int k = 2 + 1"))
    # Compile characterization only: runtime operation-only body is unchanged.
    assert compiled.ok, compiled.diagnostics


def test_alias_kind_and_nested_loop_environments_do_not_leak():
    checker = TypeChecker()
    outer_q = Ty("State", "Int", DIMLESS)
    checker.env.update({"q": outer_q, "reg": Ty("Register", "3", DIMLESS)})
    previous = checker.env
    alias_use, inner_use, restored_outer_use = Var("alias", SPAN), Var("q", SPAN), Var("q", SPAN)
    nested = ForEachStmt("q", Var("reg", SPAN), Block([ExprStmt(inner_use, SPAN)], SPAN), SPAN)
    body = Block([
        StateBind(["alias"], Var("q", SPAN), SPAN, TypeRef("Int")),
        ExprStmt(alias_use, SPAN), nested, ExprStmt(restored_outer_use, SPAN),
    ], SPAN)
    checker._check_foreach_stmt(ForEachStmt("q", Var("reg", SPAN), body, SPAN))
    assert checker.diagnostics == []
    assert all(checker.type_of(expr).kind == "Wire" for expr in (alias_use, inner_use, restored_outer_use))
    assert checker.type_of(inner_use) is not checker.type_of(alias_use)
    assert checker.type_of(restored_outer_use) is checker.type_of(alias_use)
    assert checker.env is previous and checker.env["q"] is outer_q
    assert "alias" not in checker.env
