"""LISS-0445 consumer-wide migration — Phase 1 Red contract.

These tests intentionally describe migration gaps. They may fail until a
separately approved Green slice changes production consumers.
"""

from __future__ import annotations

from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import compiler.staqex.backend.qasm.emitter as emitter_module
import compiler.staqex.finite_binder as finite_binder_module
import compiler.staqex.scientific_semantic_ir as semantic_ir_module
import compiler.staqex.qpu_ir as qpu_ir_module
from compiler.staqex.backend.qasm.emitter import QASM3Emitter
from compiler.staqex.pipeline import compile_path, compile_source
from compiler.staqex.qpu_ir import build_qpu_ir


SPEC = REPO / "docs/specs/staqex-scientific-semantic-consumer-migration.md"
ORDINARY_GATE = REPO / "tests/fixtures/semantic_consumer_migration/ordinary_gate.sqx"
EVOLUTION = REPO / "tests/fixtures/semantic_core/hamiltonian_evolution.sqx"


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


def test_consumer_inventory_is_explicit_and_complete() -> None:
    text = SPEC.read_text(encoding="utf-8")
    for required in (
        "physics_ir",
        "physics_equation",
        "EquationNode",
        "OpExpr",
        "AlgorithmPlanModule",
        "H1 compiler early-return",
        "symbolic_ir",
        "QASM fallback boundary",
        "Atomic rejection matrix",
    ):
        assert required in text


def test_caller_equation_dto_is_not_a_canonical_source_authority() -> None:
    from compiler.staqex.hir import build_hir
    from compiler.staqex.physics_equation import Coefficient, EquationNode, Unit
    from compiler.staqex.physics_ir import SourceOrigin
    from compiler.staqex.physics_ir_lower import lower_hir_to_physics_ir

    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Operator H = X + Z
            State psi = |0>
            Measure psi
        }
        """
    )
    assert compiled.ok, compiled.diagnostics
    origin = SourceOrigin(source_id="caller.sqx", line=1, col=1)
    unit = Unit(symbol="J", dimensions=(1, 1, -2), origin=origin)
    injected = EquationNode(
        kind="equality",
        left="H",
        right="omega * N",
        coefficients=(Coefficient(expression="omega", unit=unit, origin=origin),),
        origin=origin,
    )
    hir = build_hir(compiled.checker, unit=compiled.unit)
    lowered = lower_hir_to_physics_ir(
        hir,
        unit=compiled.unit,
        equations=(injected,),
    )

    assert injected in lowered.nodes
    assert injected not in compiled.scientific_semantic_ir.nodes


def test_string_equation_dto_is_rejected_without_coercion() -> None:
    from compiler.staqex.hir import build_hir
    from compiler.staqex.physics_ir_lower import lower_hir_to_physics_ir

    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State psi = |0>
            Measure psi
        }
        """
    )
    assert compiled.ok, compiled.diagnostics
    hir = build_hir(compiled.checker, unit=compiled.unit)

    try:
        lower_hir_to_physics_ir(
            hir,
            unit=compiled.unit,
            equations=("H = omega * N",),
        )
    except TypeError as exc:
        assert "EquationNode" in str(exc)
    else:
        raise AssertionError("string equation payload must not be silently coerced")


def test_binder_diagnostics_reuse_compile_owned_canonical_projection(monkeypatch) -> None:
    compiled = compile_source(_binder_source())
    assert compiled.ok, compiled.diagnostics
    canonical = compiled.scientific_semantic_ir

    calls: list[str] = []

    def record_qpu_lowerer(*args, **kwargs):
        calls.append("qpu")
        return qpu_original(*args, **kwargs)

    def record_semantic_lowerer(*args, **kwargs):
        calls.append("semantic")
        return semantic_original(*args, **kwargs)

    def record_operator_lowerer(*args, **kwargs):
        calls.append("operator")
        return operator_original(*args, **kwargs)

    qpu_original = qpu_ir_module.lower_finite_binders
    semantic_original = semantic_ir_module.lower_finite_binders
    operator_original = semantic_ir_module.lower_finite_binder_operators
    finite_original = finite_binder_module.lower_finite_binders
    finite_operator_original = finite_binder_module.lower_finite_binder_operators
    monkeypatch.setattr(qpu_ir_module, "lower_finite_binders", record_qpu_lowerer)
    monkeypatch.setattr(semantic_ir_module, "lower_finite_binders", record_semantic_lowerer)
    monkeypatch.setattr(
        semantic_ir_module, "lower_finite_binder_operators", record_operator_lowerer
    )
    monkeypatch.setattr(finite_binder_module, "lower_finite_binders", record_qpu_lowerer)
    monkeypatch.setattr(
        finite_binder_module, "lower_finite_binder_operators", record_operator_lowerer
    )
    build_qpu_ir(compiled.unit, canonical)
    assert calls == [], "QPU projection must consume the compile-owned canonical IR"
    calls.clear()
    diagnostics = qpu_ir_module.qpu_ir_diagnostics(compiled.unit, canonical)

    assert diagnostics == []
    assert calls == [], "diagnostics must not rebuild the canonical binder projection"
    assert compiled.scientific_semantic_ir is canonical


def test_binder_canonical_build_occurs_once_per_compile(monkeypatch) -> None:
    calls = {"binders": 0, "operators": 0}
    original_binders = semantic_ir_module.lower_finite_binders
    original_operators = semantic_ir_module.lower_finite_binder_operators

    def count_binders(*args, **kwargs):
        calls["binders"] += 1
        return original_binders(*args, **kwargs)

    def count_operators(*args, **kwargs):
        calls["operators"] += 1
        return original_operators(*args, **kwargs)

    monkeypatch.setattr(semantic_ir_module, "lower_finite_binders", count_binders)
    monkeypatch.setattr(
        semantic_ir_module, "lower_finite_binder_operators", count_operators
    )
    compiled = compile_source(_binder_source())

    assert compiled.ok, compiled.diagnostics
    assert calls == {"binders": 1, "operators": 1}


def test_algorithm_plan_has_one_canonical_authority() -> None:
    from compiler.staqex.algorithm_plan_ir import ConsumerProjection, project_algorithm_plan

    compiled = compile_path(REPO / "tests/fixtures/semantic_core/explicit_realize.sqx")
    assert compiled.algorithm_plan is not None
    projection = ConsumerProjection(
        consumer="finite-qpu",
        plan_id=compiled.algorithm_plan.provenance.realize_source_node_id,
        requested_fields=("source_identity", "realization_policy"),
    )
    try:
        project_algorithm_plan(compiled.algorithm_plan, projection)
    except (AttributeError, TypeError, ValueError) as exc:
        raise AssertionError(
            "the compile-owned AlgorithmPlan must be consumable through the "
            "single plan projection boundary"
        ) from exc


def test_h1_early_return_is_canonical_dispatch() -> None:
    source = """
    theory Ising {
      parameter J: Energy
      parameter h: Energy
      operator H(J, h) = -J * (Z[0] * Z[1]) - h * (X[0] + X[1])
    }
    experiment run(J = 1.0, h = 0.5) {
      State psi = |+>
      psi |> Evolve under Ising.H(J, h) for 0.7
      observable energy = expect(Ising.H, psi)
      Measure psi
    }
    """
    compiled = compile_source(source)
    assert compiled.ok, compiled.diagnostics
    assert compiled.scientific_semantic_ir is not None


def test_ordinary_qasm_fixture_has_no_ast_fallback(monkeypatch) -> None:
    source = ORDINARY_GATE.read_text(encoding="utf-8")
    compiled = compile_source(source)
    assert compiled.ok, compiled.diagnostics

    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("ordinary canonical QASM must not call AST fallback")

    monkeypatch.setattr(emitter_module, "lower_unit_to_circuit", fail_if_called)
    monkeypatch.setattr(
        emitter_module,
        "build_scientific_semantic_ir",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("QASM must consume the compile-owned semantic IR")
        ),
    )
    emitted = QASM3Emitter(route=False).emit_unit(
        compiled.unit,
        semantic_ir=compiled.scientific_semantic_ir,
    )

    assert emitted.ok, emitted.notes
    assert emitted.qasm.startswith("OPENQASM 3.0;")
    assert "h q[0]" in emitted.qasm
    assert "measure" in emitted.qasm
    assert not any("AST_FALLBACK" in note for note in emitted.notes)


def test_rejection_matrix_names_all_artifacts() -> None:
    text = SPEC.read_text(encoding="utf-8")
    for required in (
        "qasm ==",
        "instructions == ()",
        "algorithm_plan is None",
        "no allocation",
        "terminal `Measure`",
    ):
        assert required in text


def test_unresolved_evolution_rejects_without_consumer_artifacts() -> None:
    compiled = compile_source(EVOLUTION.read_text(encoding="utf-8"))
    emitted = QASM3Emitter(route=False).emit_unit(compiled.unit)

    assert not emitted.ok
    assert emitted.qasm == ""
    assert emitted.circuit is not None
    assert emitted.circuit.gates == []
    assert not hasattr(emitted.circuit, "allocation_record")
    assert compiled.qpu_ir["instructions"] == ()
    assert "allocation_record" not in compiled.qpu_ir
    assert compiled.algorithm_plan is None


def test_limit_and_realize_execution_boundaries_are_observable() -> None:
    bare = compile_source(
        (REPO / "tests/fixtures/semantic_core/invalid_boundaries.sqx").read_text(
            encoding="utf-8"
        )
    )
    realized = compile_source(
        (REPO / "tests/fixtures/semantic_core/explicit_realize.sqx").read_text(
            encoding="utf-8"
        )
    )

    assert bare.semantic_rejection is not None
    assert bare.algorithm_plan is None
    assert bare.qpu_ir["instructions"] == ()
    assert realized.algorithm_plan is not None
    assert realized.algorithm_plan.provenance.realize_source_node_id


def test_state_and_terminal_measurement_provenance_survive_projection() -> None:
    compiled = compile_source(ORDINARY_GATE.read_text(encoding="utf-8"))
    quantum_nodes = [
        node for node in compiled.scientific_semantic_ir.nodes if node.role_lane == "quantum"
    ]
    measure = [
        instruction
        for instruction in compiled.qpu_ir["instructions"]
        if instruction.opcode == "Measure"
    ]

    assert quantum_nodes
    assert all(node.type == "State<T>" for node in quantum_nodes)
    assert measure
    assert measure[-1].provenance["source_node_id"] in compiled.qpu_ir.source_node_ids
    assert compiled.qpu_ir["instructions"][-1].opcode == "Measure"
    assert all(
        instruction.opcode != "Measure"
        for instruction in compiled.qpu_ir["instructions"][:-1]
    )
