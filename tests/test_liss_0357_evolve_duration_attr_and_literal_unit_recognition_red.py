"""AT-TDD: LISS-0357 -- Evolve's fail-closed duration check recognizes
struct-field and inline-literal durations, not just a bare Var.

Design decision: docs/issues/LISS-0357-Evolve-duration-attr-and-literal-unit-recognition.md
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex import run_source  # noqa: E402


def _hard(diags: list[dict]) -> list[dict]:
    return [
        d
        for d in diags
        if not str(d.get("code", "")).startswith("QSEM_")
        and d.get("code") != "MULTI_REGISTER_INDEX_AMBIGUOUS"
    ]


def test_struct_field_access_duration_is_accepted() -> None:
    src = """
    package p
    struct Config { val duration: Time }

    pub fn main() -> Unit {
        Config config = Config(0.25.fs)
        State s = |+>
        State s = Evolve { s under Z for config.duration }.run()
        Measure s
    }
    """
    result = run_source(src, settings={"target": "local", "seed": 0})
    hard = _hard(result.diagnostics)
    assert result.status == "succeeded" and not hard, (result.status, hard)


def test_inline_unit_suffixed_literal_duration_is_accepted() -> None:
    src = """
    package p
    pub fn main() -> Unit {
        State s = |+>
        State s = Evolve { s under Z for 0.25.fs }.run()
        Measure s
    }
    """
    result = run_source(src, settings={"target": "local", "seed": 0})
    hard = _hard(result.diagnostics)
    assert result.status == "succeeded" and not hard, (result.status, hard)


def test_genuinely_dimensionless_duration_is_still_rejected() -> None:
    """ADR 0195's fail-closed check must remain fail-closed."""
    src = """
    package p
    pub fn main() -> Unit {
        Float t = 1.0
        State s = |+>
        State s = Evolve { s under Z for t }.run()
        Measure s
    }
    """
    result = run_source(src, settings={"target": "local", "seed": 0})
    codes = {d.get("code") for d in result.diagnostics}
    assert result.status == "failed"
    assert "EVOLVE_UNRESOLVED_UNIT_ERROR" in codes
