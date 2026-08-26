"""WP-0117 Phase 1 Red: executable projection boundary contract.

These tests intentionally fail until the canonical byte serialization contract
from ``staqex-blackboard-boundary-deployment-matrix.md`` is implemented. They
must remain test-only in Phase 1: no production fallback or serializer is added
here.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex.qpu_ir import QpuInstruction, instruction_fingerprint  # noqa: E402


def _instruction(parameter: str | float | None) -> QpuInstruction:
    return QpuInstruction(
        opcode="RZ",
        qubits=(0,),
        parameter=parameter,
        provenance={
            "source_node_id": "semantic:operator:0",
            "role": "evolution",
            "type": "State",
            "dimensions": "dimensionless",
            "exactness": "finite-realized",
            "intent": "Hamiltonian evolution",
        },
    )


def test_fingerprint_uses_unicode_nfc_for_string_fields() -> None:
    composed = (_instruction("é"),)
    decomposed = (_instruction("e\u0301"),)

    assert instruction_fingerprint(composed) == instruction_fingerprint(decomposed)


def test_fingerprint_rejects_non_finite_numeric_values() -> None:
    with pytest.raises(ValueError, match="finite"):
        instruction_fingerprint((_instruction(math.nan),))

    with pytest.raises(ValueError, match="finite"):
        instruction_fingerprint((_instruction(math.inf),))


def test_fingerprint_preserves_instruction_order_and_duplicates() -> None:
    first = _instruction(0.25)
    second = _instruction(0.5)

    ordered = instruction_fingerprint((first, second, first))
    reordered = instruction_fingerprint((second, first, first))
    deduplicated = instruction_fingerprint((first, second))

    assert ordered != reordered
    assert ordered != deduplicated


if __name__ == "__main__":
    test_fingerprint_uses_unicode_nfc_for_string_fields()
    test_fingerprint_rejects_non_finite_numeric_values()
    test_fingerprint_preserves_instruction_order_and_duplicates()
