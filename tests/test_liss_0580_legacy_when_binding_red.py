"""Phase 1 Red contracts for extracting the legacy `when` binder."""

from __future__ import annotations

import ast
import importlib
import importlib.util
import inspect
import io
from pathlib import Path
import sys

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex.host import run_source  # noqa: E402
from compiler.staqex.runtime.evaluation import orchestration  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402


SUCCESSOR_MODULE = (
    "compiler.staqex.runtime.evaluation.legacy_control_binding"
)


def _successor():
    spec = importlib.util.find_spec(SUCCESSOR_MODULE)
    assert spec is not None, (
        "legacy control binding successor module has not been extracted"
    )
    return importlib.import_module(SUCCESSOR_MODULE)


def test_successor_module_owns_legacy_binding_algorithm() -> None:
    successor = _successor()
    assert callable(successor.bind_when)
    assert successor.bind_when.__module__ == SUCCESSOR_MODULE

    source = inspect.getsource(successor)
    tree = ast.parse(source)
    owned_helpers = {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert {"_ctrl_masses", "_pat_match"} <= owned_helpers
    assert "runtime.evaluator" not in source
    assert "Evaluator(" not in source


def test_evaluator_has_no_duplicate_legacy_when_implementation() -> None:
    evaluator_source = inspect.getsource(Evaluator)
    evaluator_tree = ast.parse(evaluator_source)
    evaluator_class = next(
        node
        for node in evaluator_tree.body
        if isinstance(node, ast.ClassDef) and node.name == "Evaluator"
    )
    class_methods = {
        node.name
        for node in evaluator_class.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert "_bind_when" not in class_methods
    assert "_ctrl_masses" not in class_methods

    module_source = inspect.getsource(importlib.import_module(
        "compiler.staqex.runtime.evaluator"
    ))
    module_tree = ast.parse(module_source)
    facade_helpers = {
        node.name
        for node in module_tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert "_pat_match" not in facade_helpers


def test_compatibility_installs_successor_and_live_hook_identity() -> None:
    compatibility = importlib.import_module(
        "compiler.staqex.runtime.evaluation.compatibility"
    )
    compatibility_tree = ast.parse(inspect.getsource(compatibility))
    installer = next(
        (
            node
            for node in compatibility_tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "install_legacy_control_binding_compatibility"
        ),
        None,
    )
    assert installer is not None, "legacy control binding installer is missing"
    assignments = [
        node
        for node in ast.walk(installer)
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Attribute)
            and target.attr == "_bind_when"
            and isinstance(target.value, ast.Name)
            and target.value.id == "evaluator_type"
            for target in node.targets
        )
    ]
    assert len(assignments) == 1
    assert isinstance(assignments[0].value, ast.Name)
    assert assignments[0].value.id == "bind_when"

    evaluator_module = importlib.import_module(
        "compiler.staqex.runtime.evaluator"
    )
    evaluator_tree = ast.parse(inspect.getsource(evaluator_module))
    imports_installer = any(
        isinstance(node, ast.ImportFrom)
        and any(
            alias.name == "install_legacy_control_binding_compatibility"
            and alias.asname == "_install_legacy_control_binding_compatibility"
            for alias in node.names
        )
        for node in evaluator_tree.body
    )
    assert imports_installer, "Evaluator does not import the dedicated installer"
    setup_calls = [
        node
        for node in ast.walk(evaluator_tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_install_legacy_control_binding_compatibility"
        and len(node.args) == 1
        and isinstance(node.args[0], ast.Name)
        and node.args[0].id == "Evaluator"
    ]
    assert len(setup_calls) == 1, "Evaluator setup must install the hook once"

    successor = _successor()
    assert Evaluator._bind_when is successor.bind_when


def test_canonical_control_mixture_fallback_reaches_legacy_when_binding(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Existing enum+Inspect shape is canonical but outside deferred eligibility."""
    source = """
package liss0580
namespace N {
    pub enum S { Open, Blocked }
}
pub fn main() -> Unit {
    N.S selected = N.S.Open
    State result = Mix (selected) {
        Open -> |1>,
        else -> |0>,
    }
    State peeked = expect(Z, result)
    State viewed = Inspect(peeked)
    Measure result
}
"""
    legacy_calls: list[int] = []
    when_calls: list[int] = []
    mixture_plan_families: list[str] = []
    mixture_executor_eligibility: list[list[bool]] = []
    mixture_executor_legacy_calls: list[int] = []
    deferred_eligibility_events: list[bool] = []
    legacy_original = Evaluator._run_legacy_ast_body
    when_original = Evaluator._bind_when
    control_mixture_original = orchestration.execute_control_mixture_plan
    deferred_eligibility_original = Evaluator._main_deferred_eligible

    def observe_legacy(self, unit, *, stdout=None):
        legacy_calls.append(1)
        return legacy_original(self, unit, stdout=stdout)

    def observe_when(self, joint, name, expr):
        when_calls.append(1)
        return when_original(self, joint, name, expr)

    def observe_control_mixture(context, plan, unit, *, stdout=None):
        mixture_plan_families.append(plan.family)
        eligibility_start = len(deferred_eligibility_events)
        legacy_start = len(legacy_calls)
        result = control_mixture_original(context, plan, unit, stdout=stdout)
        mixture_executor_eligibility.append(
            deferred_eligibility_events[eligibility_start:]
        )
        mixture_executor_legacy_calls.append(len(legacy_calls) - legacy_start)
        return result

    def observe_deferred_eligibility(statements):
        eligible = deferred_eligibility_original(statements)
        deferred_eligibility_events.append(eligible)
        return eligible

    monkeypatch.setattr(Evaluator, "_run_legacy_ast_body", observe_legacy)
    monkeypatch.setattr(Evaluator, "_bind_when", observe_when)
    monkeypatch.setattr(
        orchestration, "execute_control_mixture_plan", observe_control_mixture
    )
    monkeypatch.setattr(
        Evaluator,
        "_main_deferred_eligible",
        staticmethod(observe_deferred_eligibility),
    )

    result = run_source(
        source,
        settings={"target": "local", "seed": 0},
        stdout=io.StringIO(),
    )

    assert result.status == "succeeded", result.diagnostics
    assert mixture_plan_families == ["control_mixture"]
    assert len(mixture_executor_eligibility) == 1
    assert mixture_executor_eligibility[0]
    assert not any(mixture_executor_eligibility[0])
    assert mixture_executor_legacy_calls == [1]
    assert legacy_calls == [1]
    assert when_calls
