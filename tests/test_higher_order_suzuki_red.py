"""AT-TDD Phase 1 Red: LISS-0017 higher-order Suzuki syntax contract."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compile_source(source).diagnostics}


def test_suzuki_s2_steps_policy_is_accepted() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            State psi = dirac(0)
            State evolved = evolve { psi under X for 1.0.s using Suzuki(order = 2, steps = 8) }.run()
            measure evolved
        }
        """
    )

    assert "SUZUKI_ORDER_ERROR" not in codes
    assert "SUZUKI_POLICY_ERROR" not in codes


def test_suzuki_tolerance_policy_requires_explicit_error_mode() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            State psi = dirac(0)
            State evolved = evolve { psi under X for 1.0.s using Suzuki(order = 2, tolerance = 1e-4, error = EmpiricalEstimate) }.run()
            measure evolved
        }
        """
    )

    assert "SUZUKI_ORDER_ERROR" not in codes
    assert "SUZUKI_POLICY_ERROR" not in codes


def test_suzuki_s4_steps_policy_is_accepted() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            State psi = dirac(0)
            State evolved = evolve { psi under X for 1.0.s using Suzuki(order = 4, steps = 4) }.run()
            measure evolved
        }
        """
    )

    assert "SUZUKI_ORDER_ERROR" not in codes
    assert "SUZUKI_POLICY_ERROR" not in codes


def test_suzuki_order_three_is_rejected() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            State psi = dirac(0)
            State evolved = evolve { psi under X for 1.0.s using Suzuki(order = 3, steps = 8) }.run()
            measure evolved
        }
        """
    )

    assert "SUZUKI_ORDER_ERROR" in codes


def test_steps_and_tolerance_are_mutually_exclusive() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            State psi = dirac(0)
            State evolved = evolve { psi under X for 1.0.s using Suzuki(order = 2, steps = 8, tolerance = 1e-4) }.run()
            measure evolved
        }
        """
    )

    assert "SUZUKI_POLICY_ERROR" in codes


def test_tolerance_requires_error_mode_and_steps_forbid_it() -> None:
    missing_mode = _codes(
        """
        package t
        pub fn main() -> Unit {
            State psi = dirac(0)
            State evolved = evolve { psi under X for 1.0.s using Suzuki(order = 2, tolerance = 1e-4) }.run()
            measure evolved
        }
        """
    )
    steps_with_mode = _codes(
        """
        package t
        pub fn main() -> Unit {
            State psi = dirac(0)
            State evolved = evolve { psi under X for 1.0.s using Suzuki(order = 2, steps = 8, error = Bound) }.run()
            measure evolved
        }
        """
    )

    assert "SUZUKI_POLICY_ERROR" in missing_mode
    assert "SUZUKI_POLICY_ERROR" in steps_with_mode


if __name__ == "__main__":
    for test in (
        test_suzuki_s2_steps_policy_is_accepted,
        test_suzuki_tolerance_policy_requires_explicit_error_mode,
        test_suzuki_s4_steps_policy_is_accepted,
        test_suzuki_order_three_is_rejected,
        test_steps_and_tolerance_are_mutually_exclusive,
        test_tolerance_requires_error_mode_and_steps_forbid_it,
    ):
        test()
    print("OK — higher-order Suzuki Red tests")
