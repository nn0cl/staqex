"""AT-TDD contract tests for the LISS-0027/0028/0029 boundary slices.

The filename preserves the Phase 1 origin; the reviewed assertions now serve
as regression coverage for the implemented type and capability boundaries.
Provider submission and dynamic execution remain out of scope.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compile_source(source).diagnostics}


def test_qubit_register_is_a_type_level_static_shape() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            QubitRegister<3> reg = system()
            ForEach q in reg {
                apply(H, q)
            }
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert compiled.ok, compiled.diagnostics


def test_param_angle_is_allowed_only_as_a_gate_argument() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            QubitRegister<1> reg = system()
            Param<Angle> theta = parameter("theta")
            ForEach q in reg {
                apply(Rz(theta), q)
            }
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert compiled.ok, compiled.diagnostics


def test_param_cannot_control_static_register_shape() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            Param<Int> n = parameter("n")
            ForEach q in register(n) {
                apply(H, q)
            }
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert "PARAMETER_CONTROL_ERROR" in codes


def test_dynamic_lane_requires_explicit_capability_and_mid_measurement_rule() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            dynamic qpu {
                State<Int> flag = Coin()
                Measure flag
                apply(X, flag)
            }
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert "DYNAMIC_CAPABILITY_REQUIRED_ERROR" in codes


def test_dynamic_lane_does_not_fall_back_to_host_execution() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            dynamic qpu {
                State<Int> flag = Coin()
                Measure flag
            }
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert "DYNAMIC_UNSUPPORTED_FEATURE_ERROR" in codes


if __name__ == "__main__":
    tests = [
        test_qubit_register_is_a_type_level_static_shape,
        test_param_angle_is_allowed_only_as_a_gate_argument,
        test_param_cannot_control_static_register_shape,
        test_dynamic_lane_requires_explicit_capability_and_mid_measurement_rule,
        test_dynamic_lane_does_not_fall_back_to_host_execution,
    ]
    for test in tests:
        test()
    print("OK — static/parametric/dynamic boundary tests")
