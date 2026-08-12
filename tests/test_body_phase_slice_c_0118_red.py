"""AT-TDD Phase 1 Red: LISS-0118 Slice C — short-name policy + closeout fixtures."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def test_qualified_clean_method_not_blocked_by_tainted_peer() -> None:
    """Pure().k() must not fail merely because S.k is execution-tainted."""
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
        class Pure {
            fn init() {}
            pub fn k() -> Operator {
                return X + Z
            }
        }
        theory T {
            Operator H = Pure().k()
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


def test_qualified_tainted_method_still_rejected() -> None:
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


def test_bare_short_name_fails_closed_when_any_peer_tainted() -> None:
    """Bare k() is fail-closed if any Class.k is execution-tainted."""
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
        class Pure {
            fn init() {}
            pub fn k() -> Operator {
                return X + Z
            }
        }
        theory T {
            Operator H = k()
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


def test_bare_short_name_ok_when_only_clean_methods_exist() -> None:
    result = compile_source(
        """
        package t
        execution Run {
            n = 1000
        }
        class Pure {
            fn init() {}
            pub fn k() -> Operator {
                return X + Z
            }
        }
        theory T {
            Operator H = k()
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
    try:
        test_qualified_clean_method_not_blocked_by_tainted_peer()
        test_qualified_tainted_method_still_rejected()
        test_bare_short_name_fails_closed_when_any_peer_tainted()
        test_bare_short_name_ok_when_only_clean_methods_exist()
    except AssertionError as exc:
        print(f"FAIL: {exc}")
        raise SystemExit(1) from exc
    print("OK — body phase 0118 slice C")
