"""Phase 1 Red contracts for LISS-0576 shadowed Evaluator bodies."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
EVALUATOR_SOURCE = ROOT / "compiler/staqex/runtime/evaluator.py"


def _evaluator_method_names() -> set[str]:
    tree = ast.parse(EVALUATOR_SOURCE.read_text(encoding="utf-8"))
    evaluator = next(
        node for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "Evaluator"
    )
    return {
        node.name for node in evaluator.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


@pytest.mark.parametrize(
    "method_name",
    [
        "_bind_finiteize",
        "_bind_finiteize_continuous",
        "_bind_field_from_host",
        "_bind_continuous_compose",
    ],
)
def test_shadowed_continuous_method_bodies_are_absent(method_name: str) -> None:
    assert method_name not in _evaluator_method_names()


def test_recursive_assignment_stub_is_absent() -> None:
    assert "_execute_assignment" not in _evaluator_method_names()
