"""AT-TDD: LISS-0352 -- fix Classical relational comparisons mistyped
as Classical<Float> in typecheck.py (LISS-0338's documented, deferred
"Related, not blocking" gap).

Design decision: docs/issues/LISS-0352-typecheck-classical-relational-bool-fix.md
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


def test_classical_greater_than_type_checks_and_runs_as_bool() -> None:
    src = """
    fn is_greater(a: Float, b: Float) -> Bool {
        return a > b
    }

    pub fn main() -> Unit {
        Float a = 1.0
        Float b = 2.0
        Bool c = is_greater(a, b)
        State s = |0>
        measure s
    }
    """
    compiled = compile_source(src)
    hard = _hard(compiled.diagnostics)
    assert compiled.ok and not hard, hard

    result = run_source(src, settings={"target": "local", "seed": 0})
    hard_run = _hard(result.diagnostics)
    assert result.status == "succeeded" and not hard_run, (result.status, hard_run)
