"""Phase 1 Red contracts for Evaluator domain-family extraction."""

from __future__ import annotations

import importlib
import inspect
import re
from pathlib import Path

from compiler.staqex.runtime.evaluator import Evaluator


REPOSITORY = Path(__file__).resolve().parents[1]
EVALUATOR_SOURCE = REPOSITORY / "compiler/staqex/runtime/evaluator.py"
FAMILY_ENTRYPOINTS = {
    "values": "evaluate_value",
    "operators": "resolve_operator",
    "evolution": "execute_evolution",
    "calls": "bind_call",
}


def _module_source(name: str) -> str:
    path = REPOSITORY / "compiler/staqex/runtime/evaluation" / f"{name}.py"
    return path.read_text(encoding="utf-8")


def test_evaluator_domain_family_modules_expose_named_entrypoints() -> None:
    missing: list[str] = []
    for module_name, entrypoint in FAMILY_ENTRYPOINTS.items():
        try:
            module = importlib.import_module(
                f"compiler.staqex.runtime.evaluation.{module_name}"
            )
        except ModuleNotFoundError:
            missing.append(f"{module_name}.{entrypoint}")
            continue
        if not callable(getattr(module, entrypoint, None)):
            missing.append(f"{module_name}.{entrypoint}")

    assert not missing, f"missing domain-family entrypoints: {missing}"


def test_evaluator_facade_does_not_retain_domain_family_bodies() -> None:
    source = inspect.getsource(Evaluator)

    for method_name in (
        "_bind_call",
        "_hamiltonian_evolve_one_step",
        "_resolve_operator_expr",
        "_eval_value",
    ):
        assert re.search(rf"^\s+def {re.escape(method_name)}\(", source, re.MULTILINE) is None


def test_domain_family_modules_depend_on_context_not_evaluator_facade() -> None:
    context = importlib.import_module(
        "compiler.staqex.runtime.evaluation.context"
    )
    assert hasattr(context, "EvaluatorContext")

    for module_name in FAMILY_ENTRYPOINTS:
        source = _module_source(module_name)
        assert "runtime.evaluator" not in source
        assert "from ..evaluator" not in source


def test_evaluator_context_declares_domain_family_callbacks() -> None:
    context_source = _module_source("context")

    for callback_name in (
        "_evaluate_value",
        "_resolve_operator",
        "_execute_evolution",
        "_bind_call",
    ):
        assert f"def {callback_name}" in context_source
