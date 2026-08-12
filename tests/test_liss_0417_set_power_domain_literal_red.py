"""AT-TDD Phase 1 Red -> Green: `{0,1}^n` set-power domain literal.

Target: docs/issues/LISS-0417-set-power-domain-literal.md.

Reserved ahead of its consumer (LISS-0420's `Sigma`/`Pi` binder domain) --
this Issue only makes `{0,1}^n` parse and typecheck, matching LISS-0416's
own "reserve ahead of use" pattern. No runtime evaluation path exists yet.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _hard(diags: list[dict]) -> list[dict]:
    return [d for d in diags if not str(d.get("code", "")).startswith("QSEM_")]


def test_bit_domain_literal_parses_and_typechecks() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        d = {0,1}^8
        state a = |0>
        measure a
    }
    """
    compiled = compile_source(src)
    hard = _hard(compiled.diagnostics)
    assert compiled.unit is not None, compiled.diagnostics
    assert not hard, hard


def test_qudit_domain_literal_parses_for_free() -> None:
    """{0,1,2}^n is not hardcoded to two labels."""
    src = """
    package t
    pub fn main() -> Unit {
        d = {0,1,2}^4
        state a = |0>
        measure a
    }
    """
    compiled = compile_source(src)
    hard = _hard(compiled.diagnostics)
    assert compiled.unit is not None, compiled.diagnostics
    assert not hard, hard


def test_variable_width_parses() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        Int n = 8
        d = {0,1}^n
        state a = |0>
        measure a
    }
    """
    compiled = compile_source(src)
    hard = _hard(compiled.diagnostics)
    assert compiled.unit is not None, compiled.diagnostics
    assert not hard, hard


def test_dimensioned_width_is_rejected() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        Time dur = 1.0.s
        d = {0,1}^dur
        state a = |0>
        measure a
    }
    """
    compiled = compile_source(src)
    codes = {d.get("code") for d in compiled.diagnostics}
    assert "TYPE_MISMATCH" in codes, compiled.diagnostics


def test_anticommutator_braces_are_unaffected() -> None:
    """Regression guard: `{A, B}` (Slice F anticommutator) must still
    disambiguate correctly from `{0,1}^n` on the same LBRACE token -- a
    real collision found and fixed during this Issue's own Green phase."""
    src = """
    package t
    pub fn main() -> Unit {
        Operator C = {X, Y}
        State observed = coin()
        measure observed
    }
    """
    compiled = compile_source(src)
    hard = _hard(compiled.diagnostics)
    assert compiled.unit is not None, compiled.diagnostics
    assert not hard, hard


def test_brace_in_expression_position_was_previously_a_parse_error() -> None:
    """Regression/precedent guard: confirms this is purely additive -- `{`
    in expression position had no prior meaning."""
    src = """
    package t
    pub fn main() -> Unit {
        d = {
        state a = |0>
        measure a
    }
    """
    compiled = compile_source(src)
    codes = {d.get("code") for d in compiled.diagnostics}
    assert "PARSE_ERROR" in codes, compiled.diagnostics
