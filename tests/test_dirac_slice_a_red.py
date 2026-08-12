"""AT-TDD Phase 1 Red: LISS-0073 Slice A — BraLit primary wiring."""

from __future__ import annotations

import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.ast_nodes import StateBind
from compiler.staqex.pipeline import compile_source

BRA_OPEN = "<"
EBNF_PATH = _REPO / "docs" / "specs" / "grammar" / "staqex.ebnf"


def _codes(compiled) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compiled.diagnostics}


def _main_binds(compiled) -> list[StateBind]:
    assert compiled.unit is not None, compiled.diagnostics
    assert compiled.unit.main is not None, "expected MainDecl"
    return [stmt for stmt in compiled.unit.main.body.stmts if isinstance(stmt, StateBind)]


def test_bralit_node_is_exported() -> None:
    from compiler.staqex.ast_nodes import BraLit

    assert "label" in BraLit.__dataclass_fields__
    assert "span" in BraLit.__dataclass_fields__


def test_alone_bra_parses_to_bralit() -> None:
    from compiler.staqex.ast_nodes import BraLit

    compiled = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            State bra = {BRA_OPEN}0|
            State observed = Coin()
            Measure observed
        }}
        """
    )

    assert "PARSE_ERROR" not in _codes(compiled), compiled.diagnostics
    binds = _main_binds(compiled)
    bra_binds = [bind for bind in binds if bind.name == "bra"]
    assert len(bra_binds) == 1
    assert isinstance(bra_binds[0].expr, BraLit)
    assert bra_binds[0].expr.label == "0"


def test_alone_bra_typechecks_as_algebra_primary() -> None:
    compiled = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            State bra = {BRA_OPEN}0|
            State bra = |0>
            State observed = Coin()
            Measure observed
        }}
        """
    )

    assert compiled.ok, compiled.diagnostics
    assert "OPERATOR_ALGEBRA_TYPE_ERROR" not in _codes(compiled)


def test_ebnf_primary_includes_bra_lit() -> None:
    text = EBNF_PATH.read_text(encoding="utf-8")
    match = re.search(r"(?ms)^primary\s*=(.*?);", text)
    assert match is not None, "primary production missing from EBNF"
    primary_body = match.group(1)
    assert "bra_lit" in primary_body
    assert "ket_lit" in primary_body


def main() -> None:
    test_bralit_node_is_exported()
    print("PASS test_bralit_node_is_exported")
    test_alone_bra_parses_to_bralit()
    print("PASS test_alone_bra_parses_to_bralit")
    test_alone_bra_typechecks_as_algebra_primary()
    print("PASS test_alone_bra_typechecks_as_algebra_primary")
    test_ebnf_primary_includes_bra_lit()
    print("PASS test_ebnf_primary_includes_bra_lit")
    print("OK - LISS-0073 Slice A Phase 1 Red")


if __name__ == "__main__":
    main()
