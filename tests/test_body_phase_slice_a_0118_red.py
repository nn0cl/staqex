"""AT-TDD Phase 1 Red: LISS-0118 Slice A — transitive call taint."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def test_theory_must_not_call_transitively_tainted_fn() -> None:
    """Theory→mid()→leak() where leak names Execution symbol must phase-fail."""
    result = compile_source(
        """
        package t
        execution Run {
            n = 1000
        }
        pub fn leak() -> Operator {
            Operator H = n * X
            return H
        }
        pub fn mid() -> Operator {
            return leak()
        }
        theory T {
            Operator H = mid()
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


def test_one_hop_taint_still_rejected() -> None:
    result = compile_source(
        """
        package t
        execution Run {
            n = 1000
        }
        pub fn leak() -> Operator {
            Operator H = n * X
            return H
        }
        theory T {
            Operator H = leak()
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


def test_main_may_call_transitively_tainted_fn() -> None:
    result = compile_source(
        """
        package t
        execution Run {
            n = 1000
        }
        pub fn leak() -> Operator {
            Operator H = n * X
            return H
        }
        pub fn mid() -> Operator {
            return leak()
        }
        theory T {
            Operator H = X
        }
        pub fn main() -> Unit {
            Operator H = mid()
            State<Int> q = Coin()
            Measure q
        }
        """
    )

    codes = {diagnostic.get("code", "") for diagnostic in result.diagnostics}
    assert "PHASE_TYPE_VISIBILITY_ERROR" not in codes
    assert result.ok, result.diagnostics


if __name__ == "__main__":
    test_theory_must_not_call_transitively_tainted_fn()
    test_one_hop_taint_still_rejected()
    test_main_may_call_transitively_tainted_fn()
    print("OK — body phase 0118 slice A")
