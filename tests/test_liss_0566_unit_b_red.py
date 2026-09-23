"""Phase 1 Red contracts for WP-0163 / LISS-0566-B Unit B."""

from __future__ import annotations

import ast
import importlib
import inspect
from pathlib import Path

from compiler.staqex.host import run_source


ROOT = Path(__file__).resolve().parents[1]
EVALUATOR = ROOT / "compiler/staqex/runtime/evaluator.py"
PACKAGE = "compiler.staqex.runtime.evaluation"

UNIT_B_IMPLEMENTATION_METHODS = {
    "_evolution_legacy_resolve_unitary_matrix",
    "_evolution_legacy_qft_family_matrix",
    "_evolution_legacy_bind_apply",
    "_split_capply_args",
    "_evolution_legacy_bind_capply",
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


def test_unit_b_module_exposes_gate_entrypoints() -> None:
    evolution = importlib.import_module(f"{PACKAGE}.evolution")

    for name in (
        "resolve_unitary_matrix",
        "qft_family_matrix",
        "bind_apply",
        "split_capply_args",
        "bind_capply",
    ):
        assert callable(getattr(evolution, name, None)), name


def test_unit_b_implementation_bodies_leave_evaluator_facade() -> None:
    remaining = _evaluator_method_names() & UNIT_B_IMPLEMENTATION_METHODS
    assert not remaining, (
        "Unit B implementation bodies remain on Evaluator: "
        f"{sorted(remaining)}"
    )


def test_unit_b_context_declares_narrow_gate_callbacks() -> None:
    context = inspect.getsource(importlib.import_module(f"{PACKAGE}.context"))
    for callback in (
        "_unitary_operator_definition",
        "_scalar_environment",
        "_static_register_size",
        "_stateful_evolution_context",
    ):
        assert f"def {callback}" in context


def test_unit_b_compatibility_wiring_uses_extracted_gate_functions() -> None:
    compatibility = inspect.getsource(
        importlib.import_module(f"{PACKAGE}.compatibility")
    )
    expected_assignments = (
        "evaluator_type._resolve_unitary_matrix = resolve_unitary_matrix",
        "evaluator_type._qft_family_matrix = qft_family_matrix",
        "evaluator_type._bind_apply = bind_apply",
        "evaluator_type._split_capply_args = split_capply_args",
        "evaluator_type._bind_capply = bind_capply",
    )
    for assignment in expected_assignments:
        assert assignment in compatibility


def test_unit_b_extracted_module_has_no_public_facade_dependency() -> None:
    source = inspect.getsource(importlib.import_module(f"{PACKAGE}.evolution"))
    assert "runtime.evaluator" not in source
    assert "from ..evaluator" not in source
    assert "Evaluator(" not in source
    assert "self.operators" not in source
    assert "self.static_register_sizes" not in source


def test_unit_b_qft_characterization_remains_available() -> None:
    result = run_source(
        """
package t
pub fn main() -> Unit {
  QubitRegister<2> reg = system()
  Operator F = qft(reg)
  Operator Fi = iqft(reg)
  State a = |0>
  State b = |1>
  State (a, b) = apply(F, a, b)
  State (a, b) = apply(Fi, a, b)
  Measure b
}
""",
        settings={"seed": 0},
    )
    assert result.status == "succeeded", result.diagnostics


def test_unit_b_controlled_gate_characterization_remains_available() -> None:
    result = run_source(
        """
package t
pub fn main() -> Unit {
  State control = |1>
  State target = |0>
  State target = capply(control, X, target)
  Measure target
}
""",
        settings={"seed": 0},
    )
    assert result.status == "succeeded", result.diagnostics
