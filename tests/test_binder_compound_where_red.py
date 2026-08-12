"""AT-TDD: LISS-0141 compound binder where (&&)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.finite_binder import lower_finite_binder_operators  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {d.get("code", "") for d in compile_source(source).diagnostics}


def test_compound_where_and_lowers_filtered_terms() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        QubitRegister<3> register = system()
        Operator H = sum (i in Index<0..2>, j in Index<0..2>) where i < j && j < 2 {
            Z[i] * Z[j]
        }
        State a = |0>
        Measure a
    }
    """
    codes = _codes(source)
    assert "PARSE_ERROR" not in codes
    assert "LEX_ERROR" not in codes
    assert "BINDER_GUARD_UNSUPPORTED" not in codes
    assert "BINDER_DOMAIN_ERROR" not in codes
    compiled = compile_source(source)
    assert compiled.unit is not None
    lowered, diags = lower_finite_binder_operators(compiled.unit)
    assert not diags, diags
    assert "H" in lowered


def test_classical_ampersand_on_non_bool_operands_rejects_at_typecheck() -> None:
    """ADR 0196: `&&` is now a general-expression operator (total pushforward,
    Bool-only) -- `Float && Float` correctly *parses* and is rejected at
    typecheck (TYPE_MISMATCH), not at the lexer/parser stage. Renamed from
    `test_classical_ampersand_outside_where_still_errors`, which asserted the
    pre-ADR-0196 behavior (a parse-level rejection) that this ADR
    superseded."""
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            Float x = 1.0
            Float y = 2.0
            Float z = x && y
            Measure z
        }
        """
    )
    assert "LEX_ERROR" not in codes
    assert "PARSE_ERROR" not in codes
    assert "TYPE_MISMATCH" in codes


if __name__ == "__main__":
    test_compound_where_and_lowers_filtered_terms()
    print("PASS test_compound_where_and_lowers_filtered_terms")
    test_classical_ampersand_on_non_bool_operands_rejects_at_typecheck()
    print("PASS test_classical_ampersand_on_non_bool_operands_rejects_at_typecheck")
