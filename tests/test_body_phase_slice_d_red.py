"""AT-TDD Phase 1 Red: LISS-0076 Slice D — call / method phase leaks."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def test_theory_call_argument_must_not_name_execution_symbol() -> None:
    """Direct leak: Call/BinOp args inside a Theory body name Execution symbols."""
    result = compile_source(
        """
        package t
        execution Run {
            n = 1000
        }
        pub fn scale(x: Operator) -> Operator {
            return x
        }
        theory T {
            Operator H = scale(n * X)
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


def test_theory_must_not_call_fn_that_uses_execution_symbol() -> None:
    """Indirect leak: Theory invokes a fn whose body names an Execution symbol."""
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


def test_theory_must_not_call_method_that_uses_execution_symbol() -> None:
    result = compile_source(
        """
        package t
        execution Run {
            n = 1000
        }
        class S {
            fn init() {}
            pub fn k() -> Operator {
                Operator H = n * X
                return H
            }
        }
        theory T {
            Operator H = S().k()
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


def test_main_may_call_fn_that_uses_execution_symbol() -> None:
    """Kernel/main is not a blocked scientific phase for this slice."""
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
            Operator H = X + Z
        }
        pub fn main() -> Unit {
            Operator H = leak()
            State<Int> q = Coin()
            Measure q
        }
        """
    )

    codes = {diagnostic.get("code", "") for diagnostic in result.diagnostics}
    assert "PHASE_TYPE_VISIBILITY_ERROR" not in codes
    assert result.ok, result.diagnostics


def test_theory_may_call_pure_operator_fn() -> None:
    result = compile_source(
        """
        package t
        execution Run {
            n = 1000
        }
        pub fn scale(x: Operator) -> Operator {
            return x
        }
        theory T {
            Operator H = scale(X)
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
    test_theory_call_argument_must_not_name_execution_symbol()
    test_theory_must_not_call_fn_that_uses_execution_symbol()
    test_theory_must_not_call_method_that_uses_execution_symbol()
    test_main_may_call_fn_that_uses_execution_symbol()
    test_theory_may_call_pure_operator_fn()
    print("OK — body phase slice D")
