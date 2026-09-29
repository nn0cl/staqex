"""Phase 1 Red contracts for LISS-0582 runtime-plan eligibility.

These tests intentionally fail until the approved stateless eligibility
successor exists.  Existing runtime-plan family suites remain the behavioral
authority; this file covers the new ownership, compatibility, and orchestration
boundary only.
"""

from __future__ import annotations

import ast
import importlib
import inspect
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from compiler.staqex.runtime.evaluator import Evaluator


EVALUATOR = ROOT / "compiler/staqex/runtime/evaluator.py"
ORCHESTRATION = ROOT / "compiler/staqex/runtime/evaluation/orchestration.py"
SUCCESSOR_IMPORT = "compiler.staqex.runtime.evaluation.plan_eligibility"

CANDIDATE_METHODS = {
    "_is_deferred_callable_eligible",
    "_operator_expr_contains_attr",
    "_is_minimal_local_evolution",
    "_is_first_runtime_family",
    "_unit_without_operator_declarations",
    "_evolution_runtime_unit",
    "_binder_runtime_unit",
}

SUCCESSOR_SYMBOLS = {
    "is_deferred_callable_eligible",
    "operator_expr_contains_attr",
    "is_minimal_local_evolution",
    "is_first_runtime_family",
    "project_runtime_unit",
}


def _evaluator_method_names() -> set[str]:
    tree = ast.parse(EVALUATOR.read_text(encoding="utf-8"))
    evaluator = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "Evaluator"
    )
    return {
        node.name
        for node in evaluator.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def test_plan_eligibility_has_a_dedicated_stateless_successor() -> None:
    successor = importlib.import_module(SUCCESSOR_IMPORT)

    for symbol in SUCCESSOR_SYMBOLS:
        assert callable(getattr(successor, symbol, None)), (
            f"successor must export pure policy function {symbol}"
        )
    source = inspect.getsource(successor)
    assert "runtime.evaluator" not in source
    assert "Evaluator(" not in source


def test_eligibility_and_unit_projection_bodies_leave_evaluator_facade() -> None:
    remaining = _evaluator_method_names() & CANDIDATE_METHODS

    assert not remaining, (
        "runtime-plan eligibility/projection bodies remain on Evaluator: "
        f"{sorted(remaining)}"
    )


def test_successor_does_not_copy_mutable_evaluator_state() -> None:
    successor = importlib.import_module(SUCCESSOR_IMPORT)
    source = inspect.getsource(successor)

    for forbidden in (
        "self.rng",
        "self.operators",
        "self.scalars",
        "self.objects",
        "self.mixed_states",
        "self.semantic_ir",
    ):
        assert forbidden not in source


def test_orchestration_calls_successor_policy_instead_of_facade_methods() -> None:
    tree = ast.parse(ORCHESTRATION.read_text(encoding="utf-8"))
    imported_successor = any(
        isinstance(node, (ast.Import, ast.ImportFrom))
        and "plan_eligibility" in ast.unparse(node)
        for node in tree.body
    )
    called_symbols = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    called_symbols |= {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }

    assert imported_successor
    for symbol in (
        "is_deferred_callable_eligible",
        "is_minimal_local_evolution",
        "is_first_runtime_family",
        "project_runtime_unit",
    ):
        assert symbol in called_symbols


def test_compatibility_hooks_preserve_successor_callable_identity() -> None:
    successor = importlib.import_module(SUCCESSOR_IMPORT)

    assert Evaluator._is_deferred_callable_eligible is successor.is_deferred_callable_eligible
    assert Evaluator._is_minimal_local_evolution is successor.is_minimal_local_evolution
    assert Evaluator._is_first_runtime_family is successor.is_first_runtime_family
