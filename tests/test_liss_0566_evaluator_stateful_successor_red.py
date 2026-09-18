"""Phase 1 Red contracts for the LISS-0566 stateful successor."""

from __future__ import annotations

import ast
import importlib
import inspect
from pathlib import Path

from compiler.staqex.backend.qasm.emitter import QASM3Emitter
from compiler.staqex.pipeline import compile_source


ROOT = Path(__file__).resolve().parents[1]
EVALUATOR = ROOT / "compiler/staqex/runtime/evaluator.py"
PACKAGE = "compiler.staqex.runtime.evaluation"

EVOLUTION_IMPLEMENTATION_METHODS = {
    "_evolution_legacy_bind_apply_multi",
    "_evolution_legacy_bind_cnot_multi",
    "_evolution_legacy_bind_evolve",
    "_evolution_legacy_bind_explicit_evolve",
    "_evolution_legacy_eval_max_steps",
    "_evolution_legacy_eval_until_predicate",
    "_evolution_legacy_bind_evolve_hamiltonian",
    "_evolution_legacy_hamiltonian_evolve_one_step",
    "_evolution_legacy_hamiltonian_evolve_tuple_coordinate",
    "_evolution_legacy_evolve_precomputed_grid",
}


def _evaluator_method_names() -> set[str]:
    tree = ast.parse(EVALUATOR.read_text(encoding="utf-8"))
    evaluator = next(
        node for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "Evaluator"
    )
    return {
        node.name for node in evaluator.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def test_stateful_successor_module_exposes_evolution_unit() -> None:
    evolution = importlib.import_module(f"{PACKAGE}.evolution")

    assert callable(evolution.execute_stateful_evolution)


def test_stateful_implementation_bodies_leave_evaluator_facade() -> None:
    remaining = _evaluator_method_names() & EVOLUTION_IMPLEMENTATION_METHODS
    assert not remaining, (
        "stateful evolution implementation bodies remain on Evaluator: "
        f"{sorted(remaining)}"
    )


def test_successor_context_declares_narrow_stateful_callbacks() -> None:
    context = inspect.getsource(importlib.import_module(f"{PACKAGE}.context"))
    assert "def _stateful_evolution_context" in context


def test_extracted_stateful_modules_do_not_import_or_rebuild_evaluator() -> None:
    source = inspect.getsource(importlib.import_module(f"{PACKAGE}.evolution"))
    assert "runtime.evaluator" not in source
    assert "from ..evaluator" not in source
    assert "Evaluator(" not in source
    assert "self.operators" not in source
    assert "self.rng" not in source


def test_explicit_suzuki_qasm_characterization_is_preserved() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        QubitRegister<1> register = system()
        Operator H = Z[0]
        State a = |+>
        State a = Evolve { a under H for 0.1 using Suzuki(order = 2, steps = 3) }.run()
        Measure a
    }
    """
    compiled = compile_source(source)
    assert compiled.ok, compiled.diagnostics
    assert compiled.unit is not None
    emitted = QASM3Emitter(route=False).emit_unit(
        compiled.unit, semantic_ir=compiled.scientific_semantic_ir
    )
    assert emitted.ok, emitted.notes
    assert emitted.qasm.count("rz(") == 3


def test_operator_projection_characterization_remains_canonical() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        QubitRegister<3> register = system()
        Operator H = Sigma (i In 0..1) { 1.0 * Z[i] * Z[next(i)] }
        State<Int> observed = Coin()
        Measure observed
    }
    """
    compiled = compile_source(source)
    assert compiled.ok, compiled.diagnostics
    assert compiled.scientific_semantic_ir is not None
    assert compiled.qpu_ir["binder_lowering"] == (
        compiled.scientific_semantic_ir.binder_lowering
    )
