"""AT-TDD Phase 1 Red: LISS-0118 Slice B — Report ↔ Execution visibility."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def test_report_may_reference_execution_symbol() -> None:
    """Report depends on execution results; Execution-bound names are visible."""
    result = compile_source(
        """
        package t
        execution Run {
            n = 1000
        }
        report R {
            Classical x = n
        }
        pub fn main() -> Unit {
            State<Int> q = Coin()
            Measure q
        }
        """
    )

    codes = {diagnostic.get("code", "") for diagnostic in result.diagnostics}
    assert "PHASE_TYPE_VISIBILITY_ERROR" not in codes
    assert result.ok, result.diagnostics


def test_theory_must_not_see_report_symbol() -> None:
    """Report symbols must not leak upward into Theory bodies."""
    result = compile_source(
        """
        package t
        execution Run {
            n = 1000
        }
        report R {
            Classical out = n
        }
        theory T {
            Operator H = out * X
        }
        pub fn main() -> Unit {
            State<Int> q = Coin()
            Measure q
        }
        """
    )

    codes = {diagnostic.get("code", "") for diagnostic in result.diagnostics}
    assert "PHASE_TYPE_VISIBILITY_ERROR" in codes
    assert result.ok is False


def test_experiment_must_not_see_report_symbol() -> None:
    result = compile_source(
        """
        package t
        theory T { Operator H = X }
        execution Run {
            n = 1000
        }
        report R {
            Classical out = n
        }
        experiment E {
            theory = T
            Classical x = out
        }
        pub fn main() -> Unit {
            State<Int> q = Coin()
            Measure q
        }
        """
    )

    codes = {diagnostic.get("code", "") for diagnostic in result.diagnostics}
    assert "PHASE_TYPE_VISIBILITY_ERROR" in codes
    assert result.ok is False


if __name__ == "__main__":
    test_report_may_reference_execution_symbol()
    test_theory_must_not_see_report_symbol()
    test_experiment_must_not_see_report_symbol()
    print("OK — body phase 0118 slice B")
