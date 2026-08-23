"""LISS-0447 / WP-0110 Phase 1 Red contracts.

These tests intentionally expose the three residual consumer gaps. They add no
production implementation and must fail until an individually approved Green
subcontract is implemented.
"""

from __future__ import annotations

from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import compiler.staqex.backend.qasm.emitter as emitter_module
from compiler.staqex.algorithm_plan_ir import ConsumerProjection, project_algorithm_plan
from compiler.staqex.backend.qasm import emit_openqasm3
from compiler.staqex.codegen_qasm import OpenQASM3Generator
from compiler.staqex.pipeline import compile_path, compile_source


EXPLICIT_REALIZE = REPO / "tests/fixtures/residual_semantic_consumers/explicit_realize_plan.sqx"
MISSING_POLICY = REPO / "tests/fixtures/residual_semantic_consumers/missing_realize_policy.sqx"
H1_SOURCE = (REPO / "tests/fixtures/residual_semantic_consumers/h1_canonical_dispatch.sqx").read_text(
    encoding="utf-8"
)
ORDINARY_GATE = REPO / "tests/fixtures/semantic_consumer_migration/ordinary_gate.sqx"


def _assert_empty_rejection(emitted, code: str) -> None:
    assert not emitted.ok
    assert emitted.circuit is not None
    assert emitted.circuit.reject_code == code
    assert emitted.qasm == ""
    assert emitted.circuit.gates == []
    assert emitted.circuit.allocation_started is False
    assert emitted.circuit.allocated_qubits == ()
    assert emitted.circuit.partial_program is None


def test_algorithm_plan_projection_preserves_canonical_fields() -> None:
    compiled = compile_path(EXPLICIT_REALIZE)
    assert compiled.scientific_semantic_ir is not None
    canonical = compiled.scientific_semantic_ir
    assert canonical.realize_source_node_id
    record = canonical.finite_realization_record
    assert record is not None
    assert record.source_name == "U_formal"
    assert record.realized_name == "U_qpu"
    assert record.method == "suzuki"
    assert record.order == 2
    assert record.steps == 8
    assert record.error_budget == 1e-6
    assert dict(record.provenance)["source_node_id"] == record.source_node_id
    assert compiled.algorithm_plan is not None
    projection = ConsumerProjection(
        consumer="finite-qpu",
        plan_id=canonical.realize_source_node_id,
        requested_fields=("source_identity", "realization_policy"),
    )
    assert project_algorithm_plan(compiled.algorithm_plan, projection) == projection


def test_algorithm_plan_projection_rejects_mismatched_or_incomplete_authority() -> None:
    compiled = compile_path(MISSING_POLICY)
    assert compiled.scientific_semantic_ir is not None
    assert compiled.scientific_semantic_ir.realize_source_node_id is None
    assert compiled.algorithm_plan is None
    assert any(
        diagnostic.get("code") == "E_ALGORITHM_PLAN_CANONICAL_PROVENANCE"
        and diagnostic.get("reason") == "missing_realize_owner"
        for diagnostic in compiled.diagnostics
    )


def test_algorithm_plan_projection_rejects_mismatched_pair() -> None:
    compiled = compile_path(EXPLICIT_REALIZE)
    assert compiled.algorithm_plan is not None
    projection = ConsumerProjection(
        consumer="finite-qpu",
        plan_id="ssc:mismatched-source",
        requested_fields=("source_identity",),
    )
    try:
        project_algorithm_plan(compiled.algorithm_plan, projection)
    except ValueError:
        return
    raise AssertionError("mismatched plan/projection pair must reject explicitly")


def test_algorithm_plan_rejects_multiple_realize_owners() -> None:
    source = """
    package residual.multiple_realize
    pub fn main() -> Unit {
        Operator U_formal = Limit N -> Infinity { (I - i * X / N) ^ N }
        Operator U_a = Realize(source = U_formal, method = "suzuki", order = 2, steps = 4, error_budget = 1e-3)
        Operator U_b = Realize(source = U_formal, method = "suzuki", order = 2, steps = 8, error_budget = 1e-4)
        Measure |0>
    }
    """
    compiled = compile_source(source)
    assert any(
        diagnostic.get("code") == "E_ALGORITHM_PLAN_CANONICAL_PROVENANCE"
        and diagnostic.get("reason") == "multiple_realize_owners"
        for diagnostic in compiled.diagnostics
    )


def test_algorithm_plan_rejects_missing_finite_record() -> None:
    source = """
    package residual.missing_record
    pub fn main() -> Unit {
        Operator U_formal = Limit N -> Infinity { (I - i * X / N) ^ N }
        Operator U_qpu = Realize(source = U_formal, method = "suzuki", order = 2)
        Measure |0>
    }
    """
    compiled = compile_source(source)
    assert any(
        diagnostic.get("code") == "E_ALGORITHM_PLAN_CANONICAL_PROVENANCE"
        and diagnostic.get("reason") == "missing_finite_realization_record"
        for diagnostic in compiled.diagnostics
    )


def test_h1_compile_exposes_canonical_semantic_ir() -> None:
    compiled = compile_source(H1_SOURCE)
    assert compiled.ok, compiled.diagnostics
    assert compiled.scientific_semantic_ir is not None
    assert compiled.execution_authority == "scientific_semantic_ir"
    assert compiled.semantic_inspection is not None
    assert compiled.semantic_snapshot is not None
    assert compiled.semantic_inspection.source_node_ids == tuple(
        node.node_id for node in compiled.scientific_semantic_ir.nodes
    )
    assert compiled.semantic_snapshot.structural_tree == compiled.scientific_semantic_ir.nodes


def test_h1_diagnostics_remain_without_parallel_executable_authority() -> None:
    compiled = compile_source(H1_SOURCE)
    assert compiled.ok, compiled.diagnostics
    assert compiled.scientific_semantic_ir is not None
    assert compiled.symbolic_ir is None
    assert compiled.physics_ir is not None
    assert compiled.state_transform_plan is not None


def test_ordinary_qasm_canonical_fixture_never_calls_ast_fallback(monkeypatch) -> None:
    compiled = compile_path(ORDINARY_GATE)
    assert compiled.ok, compiled.diagnostics

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("ordinary canonical QASM must not call AST fallback")

    monkeypatch.setattr(emitter_module, "lower_unit_to_circuit", fail_if_called)
    emitted = emit_openqasm3(
        compiled.unit,
        semantic_ir=compiled.scientific_semantic_ir,
        route=False,
    )
    assert emitted.ok, emitted.notes
    assert "OPENQASM 3.0;" in emitted.qasm


def test_ordinary_qasm_unsupported_input_rejects_atomically() -> None:
    source = """
    package residual.unsupported
    pub fn main() -> Unit {
        Operator H = X
        State psi = |0>
        State result = Evolve() { H * psi }.run()
        Measure result
    }
    """
    compiled = compile_source(source)
    assert compiled.unit is not None
    emitted = OpenQASM3Generator(route=False).generate_detailed(
        compiled.unit,
        semantic_ir=compiled.scientific_semantic_ir,
    )
    _assert_empty_rejection(emitted, "E_QPU_CANONICAL_PROVENANCE")
