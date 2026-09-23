"""Phase 1 Red contracts for the LISS-0566-C operator successor."""

from __future__ import annotations

import importlib
import inspect

from canonical_execution import run_canonical

from compiler.staqex.backend.qasm.emitter import QASM3Emitter
from compiler.staqex.pipeline import compile_source
from compiler.staqex.runtime.evaluator import Evaluator
from compiler.staqex.runtime.hamiltonian import compile_hamiltonian


PACKAGE = "compiler.staqex.runtime.evaluation"
UNIT_C_METHODS = {
    "_operator_legacy_operator_name",
    "_operator_legacy_looks_like_operator_rhs",
    "_operator_legacy_resolve_operator",
    "_operator_legacy_array_context",
    "_operator_legacy_resolve_op_call",
    "_operator_legacy_resolve_operator_tree",
    "_operator_legacy_lookup_set_comprehension_value",
    "_operator_legacy_lower_operator_value",
    "_operator_legacy_resolve_operator_factory_call",
    "_operator_legacy_resolve_operator_method_call",
    "_operator_legacy_bind_second_quantized",
}


def _evaluator_method_names() -> set[str]:
    source = inspect.getsource(Evaluator)
    return {
        line.split("def ", 1)[1].split("(", 1)[0]
        for line in source.splitlines()
        if line.lstrip().startswith("def ")
    }


def _run(source: str):
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    return run_canonical(compiled, Evaluator(seed=0))


def test_unit_c_operator_module_exposes_successor_entrypoints() -> None:
    operators = importlib.import_module(f"{PACKAGE}.operators")
    assert callable(operators.resolve_operator)
    assert callable(operators.resolve_operator_tree)
    assert callable(operators.lower_operator_value)
    assert callable(operators.resolve_operator_factory_call)
    assert callable(operators.resolve_operator_method_call)


def test_unit_c_implementation_bodies_leave_evaluator_facade() -> None:
    remaining = _evaluator_method_names() & UNIT_C_METHODS
    assert not remaining, (
        "Unit C implementation bodies remain on Evaluator: "
        f"{sorted(remaining)}"
    )


def test_unit_c_context_declares_only_explicit_operator_callbacks() -> None:
    context = inspect.getsource(importlib.import_module(f"{PACKAGE}.context"))
    for callback in (
        "_operator_environment",
        "_grid_hamiltonian_environment",
        "_scalar_environment",
        "_object_environment",
        "_class_environment",
        "_struct_environment",
        "_enum_environment",
        "_second_quantized_environment",
        "_operator_array_context",
        "_evaluate_value",
        "_evaluate_set_comprehension",
        "_resolve_receiver_instance",
        "_execute_assignment",
    ):
        assert f"def {callback}" in context


def test_unit_c_compatibility_hooks_point_to_extracted_operators() -> None:
    operators = importlib.import_module(f"{PACKAGE}.operators")
    assert Evaluator._legacy_resolve_operator is operators.resolve_operator
    assert Evaluator._resolve_operator_tree is operators.resolve_operator_tree
    assert Evaluator._lower_operator_value is operators.lower_operator_value
    assert Evaluator._resolve_operator_factory_call is operators.resolve_operator_factory_call
    assert Evaluator._resolve_operator_method_call is operators.resolve_operator_method_call
    assert Evaluator._bind_second_quantized is operators.bind_second_quantized


def test_unit_c_extracted_module_has_no_public_facade_or_state_copy() -> None:
    source = inspect.getsource(importlib.import_module(f"{PACKAGE}.operators"))
    assert "runtime.evaluator" not in source
    assert "from ..evaluator" not in source
    assert "Evaluator(" not in source
    for forbidden in (
        "self.operators",
        "self.scalars",
        "self.objects",
        "self.classes",
        "self._this",
        "self.second_quantized_operators",
    ):
        assert forbidden not in source


def test_nested_operator_factory_call_keeps_existing_runtime_meaning() -> None:
    source = """
    package t
    struct W { a: Float }
    fn f(w: W) -> Operator { return w.a * Z[0] }
    pub fn main() -> Unit {
        W weights = W(0.5)
        Energy scale = 1.0.eV to J
        Operator H = scale * f(weights)
        State q = |0>
        Time dur = 0.6.fs
        State q = Evolve { q under H for dur }.run()
        Measure q
    }
    """
    result = _run(source)
    assert result.measure is not None
    assert result.measure.vacuum is False


def test_factory_finite_binder_keeps_parameterized_array_materialization() -> None:
    source = """
    package t
    fn f(n: Int, weights: Float[2]) -> Operator {
        return Sigma (i In 0..n-1) { weights[i] * Z[i] }
    }
    pub fn main() -> Unit {
        Float[2] weights = [1.0, 2.0]
        Int n = 2
        Energy scale = 1.0.eV to J
        Operator H = scale * f(n, weights)
        State q0 = |0>
        State q1 = |0>
        State (q0, q1) = Evolve { (q0, q1) under H for 0.1.fs }.run()
        Measure q0 tracing_out q1
    }
    """
    result = _run(source)
    assert result.measure is not None


def test_operator_method_receiver_resolution_keeps_existing_contract() -> None:
    source = """
    package t
    class Model {
        pub fn hamiltonian() -> Operator { return Z[0] + X[0] }
    }
    pub fn main() -> Unit {
        Model model = Model()
        Operator H = model.hamiltonian()
        State q = |0>
        State q = apply(H, q)
        Measure q
    }
    """
    result = _run(source)
    assert result.measure is not None


def test_operator_characterization_preserves_qasm_emission_boundary() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        QubitRegister<1> register = system()
        Operator H = Z[0]
        State q = |0>
        State q = apply(H, q)
        Measure q
    }
    """
    compiled = compile_source(source)
    assert compiled.ok, compiled.diagnostics
    emitted = QASM3Emitter(route=False).emit_unit(
        compiled.unit, semantic_ir=compiled.scientific_semantic_ir
    )
    assert emitted.ok, emitted.notes
    assert "h q[0];" in emitted.qasm


def test_operator_tree_set_projector_lowering_keeps_existing_contract() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        Int n = 2
        Set F = { x In {0,1}^n : x[0] == 1 }
        Operator P_F = Sigma (x In F) { |x><x| }
        State a = |0>
        Measure a
    }
    """
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    evaluator = Evaluator(seed=0)
    run_canonical(compiled, evaluator)
    matrix = compile_hamiltonian(evaluator.operators["P_F"], env={}, n_qubits=2)
    assert [round(matrix[i][i].real, 6) for i in range(4)] == [0.0, 0.0, 1.0, 1.0]


def test_second_quantized_mapping_keeps_operator_bind_contract() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        FermionOperator<Orbitals> H_fermion = 1.0 * create[0] * annihilate[0]
        QubitOperator<Qubits> H_raw = map(H_fermion, JordanWigner)
        Energy scale = 1.0.eV to J
        Operator H = scale * H_raw
        State a = |0>
        State a = Evolve { a under H for 0.5.fs }.run()
        Measure a
    }
    """
    result = _run(source)
    assert result.measure is not None
