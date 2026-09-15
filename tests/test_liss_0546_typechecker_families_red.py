"""Phase 1 Red contracts for TypeChecker family extraction."""

from __future__ import annotations

import importlib
import inspect
import re
from pathlib import Path

from compiler.staqex.typecheck import TypeChecker


REPOSITORY = Path(__file__).resolve().parents[1]
TYPECHECK_SOURCE = REPOSITORY / "compiler/staqex/typecheck.py"
FAMILY_ENTRYPOINTS = {
    "declarations": "check_declaration",
    "operators": "check_operator_expr",
    "dimensions": "check_assignment",
    "inference": "infer_expression",
    "evolution": "check_evolution",
}


def _module_source(name: str) -> str:
    path = REPOSITORY / "compiler/staqex/typechecking" / f"{name}.py"
    return path.read_text(encoding="utf-8")


def test_typechecker_family_modules_expose_named_entrypoints() -> None:
    missing: list[str] = []
    for module_name, entrypoint in FAMILY_ENTRYPOINTS.items():
        try:
            module = importlib.import_module(
                f"compiler.staqex.typechecking.{module_name}"
            )
        except ModuleNotFoundError:
            missing.append(f"{module_name}.{entrypoint}")
            continue
        if not callable(getattr(module, entrypoint, None)):
            missing.append(f"{module_name}.{entrypoint}")

    assert not missing, f"missing typechecker entrypoints: {missing}"


def test_typechecker_facade_does_not_retain_family_bodies() -> None:
    source = inspect.getsource(TypeChecker)

    for method_name in (
        "_check_operator_expr",
        "_infer_inner",
        "_infer_call",
        "_infer_evolve",
        "_check_function_body",
    ):
        assert re.search(
            rf"^\s+def {re.escape(method_name)}\(",
            source,
            re.MULTILINE,
        ) is None


def test_typechecker_family_modules_depend_on_context_not_facade() -> None:
    context = importlib.import_module("compiler.staqex.typechecking.context")
    assert hasattr(context, "TypeCheckContext")

    for module_name in FAMILY_ENTRYPOINTS:
        source = _module_source(module_name)
        assert "staqex.typecheck" not in source
        assert "from ..typecheck" not in source


def test_typecheck_context_declares_family_callbacks() -> None:
    context_source = _module_source("context")

    for callback_name in (
        "_check_declaration",
        "_check_operator",
        "_check_dimensions",
        "_infer_expression",
        "_check_evolution",
    ):
        assert f"def {callback_name}" in context_source

