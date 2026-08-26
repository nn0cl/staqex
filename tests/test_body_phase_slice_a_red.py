"""AT-TDD Phase 1 Red: LISS-0076 Slice A — Theory body vs Execution symbols."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def test_theory_body_must_not_see_execution_symbol() -> None:
    """Theory expression referencing an Execution-bound name is a phase leak.

    Must not rely on the fixed lexeme set (shots/backend/retry/Host); those
    remain PHASE_SCOPE_DEPENDENCY_ERROR in test_scientific_scopes_red.py.
    """
    result = compile_source(
        """
        package t
        execution Run {
            n = 1000
        }
        theory T {
            Operator H = n * X
        }
        pub fn main() -> Unit {
            State<Int> q = Coin()
            Measure q
        }
        """
    )

    codes = {diagnostic.get("code", "") for diagnostic in result.diagnostics}
    assert "PHASE_TYPE_VISIBILITY_ERROR" in codes
    assert "PHASE_SCOPE_DEPENDENCY_ERROR" not in codes
    assert result.ok is False


def test_theory_body_without_execution_symbol_still_compiles() -> None:
    result = compile_source(
        """
        package t
        execution Run {
            shots = 1000
        }
        theory T {
            Operator H = X + Z
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
    test_theory_body_must_not_see_execution_symbol()
    test_theory_body_without_execution_symbol_still_compiles()
    print("OK — body phase slice A")
