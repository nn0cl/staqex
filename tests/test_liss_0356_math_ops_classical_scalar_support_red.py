"""AT-TDD: LISS-0356 -- add classical-scalar execution support for
MATH_OPS (abs/sin/cos/exp/sqrt/log/tan) -- closes LISS-0338's last
documented gap.

Design decision: docs/issues/LISS-0356-math-ops-classical-scalar-support.md
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

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


@pytest.mark.parametrize("op", ["sin", "cos", "exp", "sqrt", "abs", "log", "tan"])
def test_math_op_usable_as_classical_scalar(op: str) -> None:
    src = f"""
    fn use_op(x: Float) -> Float {{
        return {op}(x)
    }}

    pub fn main() -> Unit {{
        Float x = 1.0
        Float y = use_op(x)
        State s = |0>
        Measure s
    }}
    """
    compiled = compile_source(src)
    hard = _hard(compiled.diagnostics)
    assert compiled.ok and not hard, hard
    result = run_source(src, settings={"target": "local", "seed": 0})
    hard_run = _hard(result.diagnostics)
    assert result.status == "succeeded" and not hard_run, (result.status, hard_run)


def test_abs_computes_the_correct_value() -> None:
    src = """
    fn abs_val(x: Float) -> Float {
        return abs(x)
    }

    pub fn main() -> Unit {
        Float x = -3.0
        Float y = abs_val(x)
        Bool ok = y == 3.0
        State s = Dirac(ok)
        Measure s
    }
    """
    compiled = compile_source(src)
    hard = _hard(compiled.diagnostics)
    assert compiled.ok and not hard, hard
    result = run_source(src, settings={"target": "local", "seed": 0})
    hard_run = _hard(result.diagnostics)
    assert result.status == "succeeded" and not hard_run, (result.status, hard_run)
    assert result.measurements[0].value == 1.0
