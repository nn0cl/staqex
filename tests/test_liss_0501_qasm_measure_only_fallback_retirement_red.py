"""AT-TDD Phase 1 Red: LISS-0501 QASM fallback retirement proof."""

from __future__ import annotations

from pathlib import Path
import inspect
import sys

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import compiler.staqex.backend.qasm.emitter as emitter_module  # noqa: E402
import compiler.staqex.backend.qasm.lower as lower_module  # noqa: E402
from compiler.staqex.backend.qasm.emitter import QASM3Emitter  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402


SOURCE = """
package liss0501
pub fn main() -> Unit {
    State psi = |0>
    Measure psi
}
"""


def _compiled():
    compiled = compile_source(SOURCE)
    assert compiled.unit is not None
    assert compiled.scientific_semantic_ir is not None
    return compiled


def test_canonical_qasm_entry_has_no_direct_ast_fallback_branch() -> None:
    source = inspect.getsource(QASM3Emitter.emit_unit)

    assert "lower_unit_to_circuit" not in source


def test_measure_only_qasm_uses_canonical_measure_projection() -> None:
    compiled = _compiled()
    emitted = QASM3Emitter(route=False).emit_unit(
        compiled.unit, semantic_ir=compiled.scientific_semantic_ir
    )

    assert emitted.ok
    assert "h q" not in emitted.qasm.lower()


def test_measure_only_qasm_keeps_canonical_source_evidence() -> None:
    compiled = _compiled()
    emitted = QASM3Emitter(route=False).emit_unit(
        compiled.unit, semantic_ir=compiled.scientific_semantic_ir
    )

    assert emitted.ok
    assert "measure" in emitted.qasm.lower()


def test_qasm_emitter_legacy_lowerer_remains_an_explicit_compatibility_symbol() -> None:
    assert callable(lower_module.lower_unit_to_circuit)
