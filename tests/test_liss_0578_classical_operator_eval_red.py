"""Phase 1 Red structural contract for WP-0171 / LISS-0578.

Existing language-behavior characterizations stay in the LISS-0424/0427/0428/
0429 suites; this file asserts only successor ownership and compatibility
structure so expected Red gaps remain distinct from behavior regressions.
"""

from __future__ import annotations

import ast
import importlib
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
COMPILER = ROOT / "compiler"
if str(COMPILER) not in sys.path:
    sys.path.insert(0, str(COMPILER))
EVALUATOR = ROOT / "compiler/staqex/runtime/evaluator.py"
SUCCESSOR = ROOT / "compiler/staqex/runtime/evaluation/classical_operator_eval.py"
COMPATIBILITY = ROOT / "compiler/staqex/runtime/evaluation/compatibility.py"
EVALUATOR_MODULE = ROOT / "compiler/staqex/runtime/evaluator.py"


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


def _installer_assignments(function_name: str) -> dict[str, str]:
    tree = ast.parse(COMPATIBILITY.read_text(encoding="utf-8"))
    function = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == function_name
    )
    assignments: dict[str, str] = {}
    for statement in function.body:
        if not isinstance(statement, ast.Assign):
            continue
        if len(statement.targets) != 1:
            continue
        target = statement.targets[0]
        value = statement.value
        if (
            isinstance(target, ast.Attribute)
            and isinstance(target.value, ast.Name)
            and target.value.id == "evaluator_type"
            and isinstance(value, ast.Name)
        ):
            assignments[target.attr] = value.id
    return assignments


def test_classical_operator_successor_owns_both_algorithms() -> None:
    assert SUCCESSOR.is_file(), "missing classical_operator_eval.py successor"
    source = SUCCESSOR.read_text(encoding="utf-8")
    tree = ast.parse(source)
    functions = {
        node.name for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert {
        "eval_classical_op_binder",
        "eval_op_expr_classical",
    } <= functions
    assert "runtime.evaluator" not in source
    assert "from ..evaluator" not in source
    assert "Evaluator(" not in source
    assert "self.scalars" not in source
    assert "self.operators" not in source


def test_classical_operator_implementation_bodies_leave_evaluator_facade() -> None:
    remaining = _evaluator_method_names() & {
        "_eval_classical_op_binder",
        "_eval_op_expr_classical",
    }
    assert not remaining, sorted(remaining)


def test_classical_operator_compatibility_hooks_target_successor_functions() -> None:
    expected = {
        "_eval_classical_op_binder": "eval_classical_op_binder",
        "_eval_op_expr_classical": "eval_op_expr_classical",
    }
    actual = _installer_assignments("install_classical_compatibility")
    hooks = set(expected)
    assert {hook: actual.get(hook) for hook in hooks} == expected


def test_classical_operator_compatibility_installer_is_invoked_by_evaluator_setup() -> None:
    tree = ast.parse(EVALUATOR_MODULE.read_text(encoding="utf-8"))
    imported_installers = {
        alias.asname or alias.name
        for node in tree.body
        if isinstance(node, ast.ImportFrom)
        and node.module == "evaluation.compatibility"
        for alias in node.names
        if alias.name == "install_classical_compatibility"
    }
    assert imported_installers, "Evaluator setup must import the compatibility installer"

    invoked = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert imported_installers & invoked, "Evaluator setup must invoke the installer"


def test_live_classical_operator_hooks_are_successor_function_identities() -> None:
    assert SUCCESSOR.is_file(), "missing classical_operator_eval.py successor"
    evaluator_module = importlib.import_module("staqex.runtime.evaluator")
    successor = importlib.import_module(
        "staqex.runtime.evaluation.classical_operator_eval"
    )
    evaluator_type = evaluator_module.Evaluator
    assert evaluator_type._eval_classical_op_binder is successor.eval_classical_op_binder
    assert evaluator_type._eval_op_expr_classical is successor.eval_op_expr_classical
