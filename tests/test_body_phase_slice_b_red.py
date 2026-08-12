"""AT-TDD Phase 1 Red: LISS-0076 Slice B — Experiment/Workflow vs Execution."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compile_source(source).diagnostics}


def test_experiment_body_must_not_see_execution_symbol() -> None:
    result = compile_source(
        """
        package t
        theory T { Operator H = X }
        execution Run {
            n = 1000
        }
        experiment E {
            theory = T
            Classical x = n
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


def test_experiment_field_rhs_must_not_see_execution_symbol() -> None:
    """Idiomatic `observable = n` (not Type-First) must still phase-fail."""
    result = compile_source(
        """
        package t
        theory T { Operator H = X }
        execution Run {
            n = 1000
        }
        experiment E {
            theory = T
            observable = n
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


def test_workflow_body_must_not_see_execution_symbol() -> None:
    result = compile_source(
        """
        package t
        theory T { Operator H = X }
        experiment E { theory = T }
        execution Run {
            n = 1000
        }
        workflow W {
            experiment = E
            Classical x = n
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


def test_experiment_may_reference_theory_symbol() -> None:
    codes = _codes(
        """
        package t
        theory T { Operator H = X + Z }
        experiment E {
            theory = T
            observable = H
        }
        execution Run {
            experiment = E
            shots = 1000
        }
        pub fn main() -> Unit {
            State<Int> q = Coin()
            Measure q
        }
        """
    )

    assert "PHASE_TYPE_VISIBILITY_ERROR" not in codes


def test_execution_may_reference_theory_operator() -> None:
    """Downward dependency remains allowed (execution -> … -> theory)."""
    result = compile_source(
        """
        package t
        theory T { Operator H = X }
        execution Run {
            Operator Bad = H
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


if __name__ == "__main__":
    test_experiment_body_must_not_see_execution_symbol()
    test_experiment_field_rhs_must_not_see_execution_symbol()
    test_workflow_body_must_not_see_execution_symbol()
    test_experiment_may_reference_theory_symbol()
    test_execution_may_reference_theory_operator()
    print("OK — body phase slice B")
