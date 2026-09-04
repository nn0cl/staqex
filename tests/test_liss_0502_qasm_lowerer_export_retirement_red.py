"""AT-TDD Phase 1 Red: LISS-0502 QASM lowerer export retirement."""

from __future__ import annotations

import inspect
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import compiler.staqex.backend.qasm.emitter as emitter_module  # noqa: E402
from compiler.staqex.backend.qasm.emitter import QASM3Emitter  # noqa: E402
from compiler.staqex.backend.qasm.lower import lower_unit_to_circuit  # noqa: E402


def test_qasm_emitter_does_not_reexport_legacy_lowerer() -> None:
    assert not hasattr(emitter_module, "lower_unit_to_circuit")


def test_canonical_qasm_entry_does_not_reference_legacy_lowerer() -> None:
    assert "lower_unit_to_circuit" not in inspect.getsource(QASM3Emitter.emit_unit)


def test_legacy_lowerer_remains_available_at_its_explicit_module_boundary() -> None:
    assert callable(lower_unit_to_circuit)


def test_qasm_emitter_has_no_provider_sdk_dependency() -> None:
    assert all(
        token not in inspect.getsource(emitter_module).lower()
        for token in ("braket", "qiskit", "cirq", "pennylane")
    )
