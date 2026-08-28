"""LISS-0456 Phase 1 Red: canonical semantic ownership at QASM entry points."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import compiler.staqex.backend.qasm.emitter as emitter_module
from compiler.staqex.backend.qasm import emit_openqasm3
from compiler.staqex.pipeline import compile_source


def _measure_only_source() -> str:
    return """
    package canonical_entry
    pub fn main() -> Unit {
        State q = |0>
        Measure q
    }
    """


def test_canonical_measure_projection_does_not_fallback_to_ast_lowering(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A canonical projection must be sufficient for the public QASM entry."""
    compiled = compile_source(_measure_only_source())
    assert compiled.ok, compiled.diagnostics
    assert compiled.unit is not None
    assert compiled.scientific_semantic_ir is not None
    assert compiled.scientific_semantic_ir.qpu_projection is not None

    def fail_ast_fallback(*_args, **_kwargs):
        raise AssertionError(
            "canonical QASM entry must not reconstruct meaning through AST/DAG"
        )

    monkeypatch.setattr(emitter_module, "lower_unit_to_circuit", fail_ast_fallback)

    emitted = emit_openqasm3(
        compiled.unit,
        semantic_ir=compiled.scientific_semantic_ir,
        route=False,
    )

    assert emitted.ok, emitted.notes
    assert "measure q[0]" in emitted.qasm
    assert emitted.circuit is not None
    assert emitted.circuit.gates[-1].name == "measure"


def test_canonical_measure_projection_retains_terminal_measure_provenance() -> None:
    """The public entry must expose terminal Measure, not an AST-only result."""
    compiled = compile_source(_measure_only_source())
    assert compiled.ok, compiled.diagnostics
    assert compiled.unit is not None
    semantic_ir = compiled.scientific_semantic_ir
    assert semantic_ir is not None
    measurement_nodes = [node for node in semantic_ir.nodes if node.kind == "Measure"]
    assert len(measurement_nodes) == 1
    measure_node = measurement_nodes[0]
    assert measure_node.role_lane == "terminal_classical"
    assert measure_node.intent == "measurement"

    emitted = emit_openqasm3(compiled.unit, semantic_ir=semantic_ir, route=False)

    assert emitted.ok, emitted.notes
    assert emitted.circuit is not None
    assert emitted.circuit.gates[-1].name == "measure"
    assert emitted.circuit.gates[-1].comment == "terminal measure"
