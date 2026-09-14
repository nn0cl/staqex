"""Phase 1 Red contracts for the first Evaluator decomposition seam."""

from __future__ import annotations

import importlib
import inspect
from pathlib import Path

from compiler.staqex.runtime.evaluator import Evaluator


REPOSITORY = Path(__file__).resolve().parents[1]
EVALUATOR_SOURCE = REPOSITORY / "compiler/staqex/runtime/evaluator.py"
EXTRACTION_MODULES = (
    "plans",
    "deferred",
    "measurement",
    "dynamic",
    "context",
)


def _module_available(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except ModuleNotFoundError:
        return False


def test_evaluator_extraction_modules_have_cohesive_boundaries() -> None:
    missing = [
        f"compiler.staqex.runtime.evaluation.{name}"
        for name in EXTRACTION_MODULES
        if not _module_available(f"compiler.staqex.runtime.evaluation.{name}")
    ]

    assert not missing, f"missing extraction modules: {missing}"


def test_plan_dispatch_is_extracted_from_public_evaluator_facade() -> None:
    plans = importlib.import_module("compiler.staqex.runtime.evaluation.plans")

    assert callable(getattr(plans, "dispatch_runtime_plan", None))
    assert "def _execute_runtime_plan" not in inspect.getsource(Evaluator)


def test_extracted_services_use_context_without_importing_evaluator_facade() -> None:
    context = importlib.import_module(
        "compiler.staqex.runtime.evaluation.context"
    )
    assert hasattr(context, "EvaluatorContext")

    for name in EXTRACTION_MODULES[:-1]:
        source = (
            REPOSITORY / "compiler/staqex/runtime/evaluation" / f"{name}.py"
        ).read_text(encoding="utf-8")
        assert "runtime.evaluator" not in source
        assert "from ..evaluator" not in source


def test_evaluator_remains_the_single_mutable_runtime_state_owner() -> None:
    source = EVALUATOR_SOURCE.read_text(encoding="utf-8")

    for state_name in (
        "self.rng",
        "self.scalars",
        "self.funs",
        "self.objects",
        "self.mixed_states",
        "self.povms",
    ):
        assert state_name in source

    assert "class Evaluator" in source
