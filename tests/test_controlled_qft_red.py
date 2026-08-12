"""AT-TDD: LISS-0151 controlled exact QFT (ADR 0120)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402

_BASIC_QPU_OPCODES = {"H", "X", "Y", "Z", "CX", "RX", "RY", "RZ", "Measure"}


def _codes(source: str) -> set[str]:
    return {d.get("code", "") for d in compile_source(source).diagnostics}


def test_cqft_lowers_to_basic_opcodes() -> None:
    result = compile_source(
        """
        package t
        pub fn main() -> Unit {
            QubitRegister<1> ctrl = system()
            QubitRegister<2> reg = system()
            Operator CF = cqft(ctrl, reg)
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )
    assert result.ok, result.diagnostics
    instructions = result.qpu_ir["instructions"]
    assert instructions
    assert {i.opcode for i in instructions} <= _BASIC_QPU_OPCODES
    assert "CPHASE" not in {i.opcode for i in instructions}
    assert "CCX" not in {i.opcode for i in instructions}
    assert result.qpu_ir["qft"]["wire_order"] == "logical"
    assert any(op["operation"] == "cqft" for op in result.qpu_ir["qft"]["operations"])


def test_ciqft_preserves_inverse_provenance() -> None:
    result = compile_source(
        """
        package t
        pub fn main() -> Unit {
            QubitRegister<1> ctrl = system()
            QubitRegister<2> reg = system()
            Operator CI = ciqft(ctrl, reg)
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )
    assert result.ok, result.diagnostics
    assert {i.opcode for i in result.qpu_ir["instructions"]} <= _BASIC_QPU_OPCODES
    assert any(op["operation"] == "ciqft" for op in result.qpu_ir["qft"]["operations"])


def test_cqft_rejects_non_register_control() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            QubitRegister<2> reg = system()
            State<Int> n = Coin()
            Operator CF = cqft(n, reg)
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )
    assert "QFT_REGISTER_TYPE_ERROR" in codes


if __name__ == "__main__":
    test_cqft_lowers_to_basic_opcodes()
    print("PASS test_cqft_lowers_to_basic_opcodes")
    test_ciqft_preserves_inverse_provenance()
    print("PASS test_ciqft_preserves_inverse_provenance")
    test_cqft_rejects_non_register_control()
    print("PASS test_cqft_rejects_non_register_control")
