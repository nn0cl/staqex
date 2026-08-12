"""AT-TDD Phase 1 Red: classical Float power (`^`).

Target: docs/issues/LISS-0415-classical-float-power.md.

`^` (CARET) was Operator-DSL-only before this Issue (`OpPow`, integer
exponent, matrix-power semantics) -- unreachable from the general/classical
expression grammar at all. This Issue adds a classical `^` producing plain
numeric exponentiation, reusing the existing `BinOp` AST node.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex import compile_source, run_source  # noqa: E402


def _hard(diags: list[dict]) -> list[dict]:
    return [
        d
        for d in diags
        if not str(d.get("code", "")).startswith("QSEM_")
        and d.get("code") != "MULTI_REGISTER_INDEX_AMBIGUOUS"
    ]


def test_float_power_with_int_literal_exponent() -> None:
    src = """
    fn f() -> Float {
        return 2.0 ^ 8
    }
    pub fn main() -> Unit {
        Float x = f()
        Bool ok = x == 256.0
        state s = dirac(ok)
        measure s
    }
    """
    compiled = compile_source(src)
    hard = _hard(compiled.diagnostics)
    assert compiled.ok and not hard, hard
    result = run_source(src, settings={"target": "local", "seed": 0})
    hard_run = _hard(result.diagnostics)
    assert result.status == "succeeded" and not hard_run, (result.status, hard_run)
    assert result.measurements[0].value == 1.0


def test_float_power_with_int_variable_exponent() -> None:
    src = """
    fn f(n: Int) -> Float {
        return 2.0 ^ n
    }
    pub fn main() -> Unit {
        Int n = 8
        Float x = f(n)
        Bool ok = x == 256.0
        state s = dirac(ok)
        measure s
    }
    """
    compiled = compile_source(src)
    hard = _hard(compiled.diagnostics)
    assert compiled.ok and not hard, hard
    result = run_source(src, settings={"target": "local", "seed": 0})
    hard_run = _hard(result.diagnostics)
    assert result.status == "succeeded" and not hard_run, (result.status, hard_run)
    assert result.measurements[0].value == 1.0


def test_sigma_coefficient_style_expression_evaluates_correctly() -> None:
    """The actual target use case: `1.0 / sqrt(2.0 ^ n)`, the equal-
    superposition normalization coefficient, as a sub-expression (not a
    bare top-level bind, which is a separate, pre-existing math_ops-as-map
    design, not a bug -- see this Issue's own docs for the correction)."""
    expected = 1.0 / (2.0**8) ** 0.5
    src = f"""
    fn coeff(n: Int) -> Float {{
        return 1.0 / sqrt(2.0 ^ n)
    }}
    pub fn main() -> Unit {{
        Int n = 8
        Float c = coeff(n)
        Bool ok = c == {expected!r}
        state s = dirac(ok)
        measure s
    }}
    """
    compiled = compile_source(src)
    hard = _hard(compiled.diagnostics)
    assert compiled.ok and not hard, hard
    result = run_source(src, settings={"target": "local", "seed": 0})
    hard_run = _hard(result.diagnostics)
    assert result.status == "succeeded" and not hard_run, (result.status, hard_run)
    assert result.measurements[0].value == 1.0


def test_dimensioned_base_power_is_rejected_with_clear_diagnostic() -> None:
    src = """
    pub fn main() -> Unit {
        Energy scale = 1.0.eV to J
        Float bad = scale ^ 2
        state a = |0>
        measure a
    }
    """
    compiled = compile_source(src)
    codes = {d.get("code") for d in compiled.diagnostics}
    assert "TYPE_MISMATCH" in codes, compiled.diagnostics


def test_operator_dsl_power_is_unaffected() -> None:
    """Regression guard: existing Operator-DSL `^` (OpPow, matrix power)
    must be completely unaffected by adding classical `^`."""
    src = """
    pub fn main() -> Unit {
        Energy scale = 1.0.eV to J
        Operator H_raw = Z ^ 2
        Operator H = scale * H_raw
        state a = |0>
        state a = evolve { a under H for 0.1.fs }.run()
        measure a
    }
    """
    compiled = compile_source(src)
    hard = _hard(compiled.diagnostics)
    assert compiled.ok and not hard, hard
    result = run_source(src, settings={"target": "local", "seed": 0})
    hard_run = _hard(result.diagnostics)
    assert result.status == "succeeded" and not hard_run, (result.status, hard_run)
