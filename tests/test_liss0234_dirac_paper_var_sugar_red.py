"""AT-TDD Phase 1 Red: LISS-0234 Dirac paper sugar with Var operands (ADR 0169)."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.ast_nodes import BraLit, Call, KetLit, StateBind, Var  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.run import run_source  # noqa: E402

BRA = "<"
KET = ">"


def _codes(compiled) -> set[str]:
    return {d.get("code", "") for d in compiled.diagnostics}


def _bind(compiled, name: str) -> StateBind:
    assert compiled.unit is not None and compiled.unit.main is not None
    binds = [
        s
        for s in compiled.unit.main.body.stmts
        if isinstance(s, StateBind) and name in s.names
    ]
    assert len(binds) == 1, compiled.diagnostics
    return binds[0]


def test_paper_inner_with_ident_labels_desugars_to_inner_vars() -> None:
    """⟨phi|psi⟩ → inner(Var(phi), Var(psi)), not BraLit/KetLit labels."""
    src = f"""
    package t
    pub fn main() -> Unit {{
        State phi = |0{KET}
        State psi = |0{KET}
        State ov = inner(phi, psi)
        State viewed = Inspect(ov)
        State phi = |0>
        State psi = |0>
        Measure viewed
    }}
    """
    compiled = compile_source(src)
    assert "PARSE_ERROR" not in _codes(compiled), compiled.diagnostics
    expr = _bind(compiled, "ov").expr
    assert isinstance(expr, Call)
    assert isinstance(expr.callee, Var) and expr.callee.name == "inner"
    assert len(expr.args) == 2
    assert isinstance(expr.args[0], Var) and expr.args[0].name == "phi"
    assert isinstance(expr.args[1], Var) and expr.args[1].name == "psi"
    assert compiled.ok, compiled.diagnostics

    result = run_source(src, stdout=io.StringIO())
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 1.0


def test_numeric_bra_ket_inner_still_uses_lits() -> None:
    """⟨0|1⟩ remains BraLit/KetLit (LISS-0073 baseline)."""
    src = f"""
    package t
    pub fn main() -> Unit {{
        State overlap = inner({BRA}0|, |1{KET})
        State observed = Coin()
        Measure observed
    }}
    """
    compiled = compile_source(src)
    expr = _bind(compiled, "overlap").expr
    assert isinstance(expr, Call) and expr.callee.name == "inner"
    assert isinstance(expr.args[0], BraLit) and expr.args[0].label == "0"
    assert isinstance(expr.args[1], KetLit) and expr.args[1].label == "1"


def test_paper_outer_with_ident_labels_desugars_to_outer_vars() -> None:
    src = f"""
    package t
    pub fn main() -> Unit {{
        State psi = |0{KET}
        State phi = |1{KET}
        Operator P = outer(|psi{KET}, {BRA}phi|)
        State psi = |0>
        State phi = |0>
        State bit = Coin()
        Measure bit
    }}
    """
    compiled = compile_source(src)
    assert "PARSE_ERROR" not in _codes(compiled), compiled.diagnostics
    expr = _bind(compiled, "P").expr
    assert isinstance(expr, Call)
    assert isinstance(expr.callee, Var) and expr.callee.name == "outer"
    assert isinstance(expr.args[0], KetLit) and expr.args[0].label == "psi"
    assert isinstance(expr.args[1], BraLit) and expr.args[1].label == "phi"
    assert compiled.ok, compiled.diagnostics


def test_matching_ident_outer_desugars_to_projector_var() -> None:
    src = f"""
    package t
    pub fn main() -> Unit {{
        State psi = |+{KET}
        Operator P = projector(|psi{KET})
        State psi = |0>
        State bit = Coin()
        Measure bit
    }}
    """
    compiled = compile_source(src)
    expr = _bind(compiled, "P").expr
    assert isinstance(expr, Call)
    assert isinstance(expr.callee, Var) and expr.callee.name == "projector"
    assert isinstance(expr.args[0], KetLit) and expr.args[0].label == "psi"


def test_pipeline_and_comparison_unaffected() -> None:
    codes = _codes(
        compile_source(
            f"""
            package t
            fn id(x: State<Bit>) -> State<Bit> {{ return x }}
            pub fn main() -> Unit {{
                State x = |0{KET}
                State y = x |> id
                State flag = 1 > 0
                State y = |0>
                Measure flag
            }}
            """
        )
    )
    assert "PARSE_ERROR" not in codes, codes


def test_anticommutator_and_bare_block_still_parse() -> None:
    codes = _codes(
        compile_source(
            """
            package t
            pub fn main() -> Unit {
                Operator C = {X, Y}
                State w = {
                    let t = 7
                    t
                }
                Measure w
            }
            """
        )
    )
    assert "PARSE_ERROR" not in codes, codes


if __name__ == "__main__":
    test_paper_inner_with_ident_labels_desugars_to_inner_vars()
    print("PASS test_paper_inner_with_ident_labels_desugars_to_inner_vars")
    test_numeric_bra_ket_inner_still_uses_lits()
    print("PASS test_numeric_bra_ket_inner_still_uses_lits")
    test_paper_outer_with_ident_labels_desugars_to_outer_vars()
    print("PASS test_paper_outer_with_ident_labels_desugars_to_outer_vars")
    test_matching_ident_outer_desugars_to_projector_var()
    print("PASS test_matching_ident_outer_desugars_to_projector_var")
    test_pipeline_and_comparison_unaffected()
    print("PASS test_pipeline_and_comparison_unaffected")
    test_anticommutator_and_bare_block_still_parse()
    print("PASS test_anticommutator_and_bare_block_still_parse")
    print("OK — LISS-0234 Phase 1 Red")
