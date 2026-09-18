"""Phase 1 Red contracts for LISS-0560's orchestration boundary.

These tests intentionally fail until the first evaluator orchestration
extraction is implemented.  They describe structure and dispatch coverage;
they do not change runtime behavior or introduce a new public API.
"""

from __future__ import annotations

import ast
import importlib
import inspect
from pathlib import Path

from compiler.staqex.runtime.evaluator import Evaluator


ROOT = Path(__file__).resolve().parents[1]
EVALUATOR = ROOT / "compiler/staqex/runtime/evaluator.py"
ORCHESTRATION_IMPORT = "compiler.staqex.runtime.evaluation.orchestration"
PLAN_FAMILIES = (
    "evolution",
    "control_mixture",
    "pure_transformation",
    "binder",
    "callable",
    "dynamic_lane",
)


def _class_method_names() -> set[str]:
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


def test_first_orchestration_boundary_has_a_dedicated_internal_module() -> None:
    """Plan selection must have an internal home separate from the facade."""

    orchestration = importlib.import_module(ORCHESTRATION_IMPORT)

    assert callable(getattr(orchestration, "dispatch_runtime_plan", None))
    assert "runtime.evaluator" not in inspect.getsource(orchestration)


def test_plan_family_executor_methods_leave_the_evaluator_facade() -> None:
    """The first extraction owns family dispatch, not Evaluator's state maps."""

    remaining = _class_method_names() & {
        "_execute_evolution_plan",
        "_execute_control_mixture_plan",
        "_execute_pure_transformation_plan",
        "_execute_binder_plan",
        "_execute_callable_plan",
        "_execute_dynamic_lane_plan",
    }

    assert not remaining, f"plan dispatch methods remain on Evaluator: {sorted(remaining)}"


def test_canonical_entrypoint_is_a_thin_orchestration_delegator() -> None:
    """Canonical IR authority stays visible while execution selection moves out."""

    source = inspect.getsource(Evaluator.run_canonical_unit)

    assert "build_runtime_execution_plan" not in source
    assert "dispatch_runtime_plan" not in source
    assert "orchestration" in source


def test_runtime_plan_family_manifest_covers_all_first_boundary_cases() -> None:
    """The extraction must preserve every currently characterized family."""

    plans = importlib.import_module("compiler.staqex.runtime.evaluation.plans")
    source = inspect.getsource(plans.dispatch_runtime_plan)

    for family in PLAN_FAMILIES:
        assert f'"{family}"' in source

