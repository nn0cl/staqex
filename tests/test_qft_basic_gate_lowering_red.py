"""AT-TDD Phase 1 Red: LISS-0042 / ADR 0086 QFT basic-gate lowering."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


_BASIC_QPU_OPCODES = {"H", "X", "Y", "Z", "CX", "RX", "RY", "RZ", "Measure"}


def _compile(operation: str):
    result = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            QubitRegister<3> reg = system()
            Operator F = {operation}(reg)
            State<Int> observed = Coin()
            Measure observed
        }}
        """
    )
    assert result.ok, result.diagnostics
    return result


def test_qft_lowering_emits_only_basic_qpu_opcodes() -> None:
    result = _compile("qft")
    instructions = result.qpu_ir["instructions"]
    assert instructions
    assert {instruction.opcode for instruction in instructions} <= _BASIC_QPU_OPCODES
    assert "CPHASE" not in {instruction.opcode for instruction in instructions}
    assert "CRZ" not in {instruction.opcode for instruction in instructions}
    assert "SWAP" not in {instruction.opcode for instruction in instructions}
    assert "H" in {instruction.opcode for instruction in instructions}
    assert "RZ" in {instruction.opcode for instruction in instructions}


def test_qft_register_reversal_is_three_cx_decomposed_at_the_end() -> None:
    result = _compile("qft")
    instructions = result.qpu_ir["instructions"]
    gate_instructions = [instruction for instruction in instructions if instruction.opcode != "Measure"]
    assert [instruction.opcode for instruction in gate_instructions[-3:]] == ["CX"] * 3


def test_iqft_lowering_preserves_inverse_provenance_and_basic_vocabulary() -> None:
    result = _compile("iqft")
    instructions = result.qpu_ir["instructions"]
    assert instructions
    assert {instruction.opcode for instruction in instructions} <= _BASIC_QPU_OPCODES
    assert result.qpu_ir["qft"]["inverse_of"] == "qft"
    assert result.qpu_ir["qft"]["wire_order"] == "logical"
