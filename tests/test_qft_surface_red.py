"""AT-TDD Phase 1 Red: LISS-0010 exact Kernel QFT/IQFT surface."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compile_source(source).diagnostics}


def test_qft_and_iqft_are_operator_values_over_a_static_register() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            QubitRegister<3> reg = system()
            Operator F = qft(reg)
            Operator G = iqft(reg)
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert compiled.ok, compiled.diagnostics
    assert compiled.qpu_ir is not None
    assert compiled.qpu_ir["qft"]["inverse_of"] == "qft"
    assert compiled.qpu_ir["qft"]["wire_order"] == "logical"


def test_qft_rejects_non_register_inputs() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            State<Int> n = Coin()
            Operator F = qft(n)
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert "QFT_REGISTER_TYPE_ERROR" in codes


def test_qft_rejects_unsupported_static_resource_size() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            QubitRegister<1000000> reg = system()
            Operator F = qft(reg)
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert "QFT_RESOURCE_ERROR" in codes


if __name__ == "__main__":
    for test in (
        test_qft_and_iqft_are_operator_values_over_a_static_register,
        test_qft_rejects_non_register_inputs,
        test_qft_rejects_unsupported_static_resource_size,
    ):
        test()
    print("OK — QFT surface Red tests")
