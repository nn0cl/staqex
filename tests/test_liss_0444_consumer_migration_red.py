"""LISS-0444 consumer-wide migration acceptance contract.

Phase 1 Red only: these tests describe the retirement boundary for the
remaining AST-derived consumers. Production paths must not be changed until
these reviewed failures receive a separate Phase 2 approval.
"""

from __future__ import annotations

from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import compiler.staqex.qpu_ir as qpu_ir_module
import compiler.staqex.backend.qasm.emitter as emitter_module
import compiler.staqex.backend.qasm.lower as lower_module
from compiler.staqex.backend.qasm.emitter import QASM3Emitter
from compiler.staqex.pipeline import compile_source


ROOT = Path(__file__).parent / "fixtures" / "semantic_core"


def _evolution_source() -> str:
    return (ROOT / "hamiltonian_evolution.sqx").read_text(encoding="utf-8")


def _binder_source() -> str:
    return """
    package t
    pub fn main() -> Unit {
        QubitRegister<3> register = system()
        Operator H = Sigma (i In 0..1) { 1.0 * Z[i] * Z[next(i)] }
        State<Int> observed = Coin()
        Measure observed
    }
    """


def test_unresolved_explicit_evolution_cannot_enter_qasm_ast_fallback(monkeypatch) -> None:
    compiled = compile_source(_evolution_source())

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("unresolved canonical evolution must not enter AST lowering")

    monkeypatch.setattr(lower_module, "lower_unit_to_circuit", fail_if_called)
    emitted = QASM3Emitter(route=False).emit_unit(compiled.unit)

    assert not emitted.ok
    assert emitted.qasm == ""
    assert not any(
        note.startswith("W_QPU_LEGACY_AST_FALLBACK:") for note in emitted.notes
    )


def test_legacy_qpu_ast_projection_helpers_are_retired() -> None:
    assert not hasattr(qpu_ir_module, "_lowering_policy_projection")
    assert not hasattr(qpu_ir_module, "_explicit_evolution_projection")


def test_qpu_diagnostics_does_not_relower_binders_from_ast(monkeypatch) -> None:
    compiled = compile_source(_binder_source())
    assert compiled.ok, compiled.diagnostics
    assert compiled.scientific_semantic_ir.binder_lowering
    assert compiled.qpu_ir["binder_lowering"] == (
        compiled.scientific_semantic_ir.binder_lowering
    )

    def fail_if_called(_unit):
        raise AssertionError("diagnostics must consume canonical binder projection")

    monkeypatch.setattr(qpu_ir_module, "lower_finite_binders", fail_if_called)
    diagnostics = qpu_ir_module.qpu_ir_diagnostics(compiled.unit)

    assert diagnostics == []


def test_canonical_compile_does_not_expose_symbolic_ir_as_live_consumer() -> None:
    compiled = compile_source(_evolution_source())

    assert compiled.scientific_semantic_ir.nodes
    assert compiled.semantic_inspection.source_node_ids == tuple(
        node.node_id for node in compiled.scientific_semantic_ir.nodes
    )
    assert compiled.symbolic_ir is None


def test_canonical_projection_is_the_live_qpu_and_inspection_consumer() -> None:
    compiled = compile_source(_evolution_source())

    assert compiled.qpu_ir["canonical_semantic_ir"] is compiled.scientific_semantic_ir
    assert compiled.quantum_semantic_ir.source_node_ids
    assert compiled.quantum_semantic_ir.source_node_ids
    assert compiled.semantic_inspection.structural_tree == compiled.scientific_semantic_ir.nodes


def test_explicit_evolution_provenance_survives_source_variable_rename() -> None:
    source = _evolution_source().replace("Operator H", "Operator generator").replace(
        "H * duration", "generator * duration"
    )
    compiled = compile_source(source)
    projection = compiled.qpu_ir["explicit_evolution"]

    assert projection["source_node_id"]
    assert projection["source_node_id"] in compiled.qpu_ir.source_node_ids
    assert projection["provenance"]["source_node_id"] == projection["source_node_id"]
