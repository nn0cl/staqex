"""Phase 1 Red contracts for LISS-0562.

These tests pin the extraction boundary before production code is moved.  The
runtime behavior checks are characterization evidence; the ownership checks
are intentionally Red until the approved extraction is implemented.
"""

from __future__ import annotations

import importlib
import inspect
from pathlib import Path

from compiler.staqex.backend.qasm.emitter import QASM3Emitter
from compiler.staqex.pipeline import compile_source
from compiler.staqex.runtime.evaluator import Evaluator


ROOT = Path(__file__).resolve().parents[1]
EVALUATOR_SOURCE = ROOT / "compiler/staqex/runtime/evaluator.py"
PACKAGE = "compiler.staqex.runtime.evaluation"

EVOLUTION_METHODS = {
    "_bind_evolve",
    "_bind_explicit_evolve",
    "_explicit_propagator",
    "_eval_max_steps",
    "_eval_until_predicate",
    "_joint_l2_distance",
    "_bind_evolve_hamiltonian",
    "_legacy_hamiltonian_evolve_one_step",
    "_hamiltonian_evolve_tuple_coordinate",
    "_evolve_precomputed_grid",
    "_resolve_unitary_matrix",
    "_qft_family_matrix",
    "_bind_apply",
    "_bind_apply_multi",
    "_bind_capply",
    "_bind_cnot_multi",
}

OPERATOR_METHODS = {
    "_operator_name",
    "_looks_like_operator_rhs",
    "_legacy_resolve_operator",
    "_operator_array_context",
    "_op_expr_arg_to_source_expr",
    "_resolve_op_call",
    "_resolve_operator_tree",
    "_lookup_set_comprehension_value",
    "_build_projector_sum_operator",
    "_lower_operator_value",
    "_resolve_operator_factory_call",
    "_resolve_operator_method_call",
    "_bind_second_quantized",
}


def _evaluator_method_names() -> set[str]:
    source = inspect.getsource(Evaluator)
    return {
        line.split("def ", 1)[1].split("(", 1)[0]
        for line in source.splitlines()
        if line.lstrip().startswith("def ")
    }


def test_evolution_and_operator_modules_expose_named_entrypoints() -> None:
    evolution = importlib.import_module(f"{PACKAGE}.evolution")
    operators = importlib.import_module(f"{PACKAGE}.operators")

    assert callable(evolution.execute_evolution)
    assert callable(operators.resolve_operator)


def test_evolution_and_operator_methods_leave_the_evaluator_facade() -> None:
    remaining = _evaluator_method_names() & (EVOLUTION_METHODS | OPERATOR_METHODS)
    assert not remaining, (
        "evolution/operator methods remain on Evaluator: "
        f"{sorted(remaining)}"
    )


def test_extracted_families_depend_on_context_not_the_public_facade() -> None:
    for name in ("evolution", "operators"):
        source = inspect.getsource(importlib.import_module(f"{PACKAGE}.{name}"))
        assert "runtime.evaluator" not in source
        assert "from ..evaluator" not in source
        assert "Evaluator(" not in source
        assert "self.operators" not in source
        assert "self.rng" not in source


def test_context_declares_evolution_and_operator_callbacks() -> None:
    context = inspect.getsource(importlib.import_module(f"{PACKAGE}.context"))
    for callback in (
        "_execute_evolution",
        "_legacy_hamiltonian_evolve_one_step",
        "_resolve_operator",
        "_legacy_resolve_operator",
    ):
        assert f"def {callback}" in context


def test_explicit_evolution_qasm_characterization_is_preserved() -> None:
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


def test_operator_binder_projection_characterization_is_preserved() -> None:
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
