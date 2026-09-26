"""Phase 1 Red contracts for WP-0172 / LISS-0579.

Structural ownership checks are intentionally expected to fail until the
projection successor is implemented. Runtime cases characterize current
projection behavior and are reported separately from those structural Reds.
"""

from __future__ import annotations

import ast
import importlib
from pathlib import Path
import sys

import pytest

from canonical_execution import run_canonical


ROOT = Path(__file__).resolve().parents[1]
COMPILER = ROOT / "compiler"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(COMPILER) not in sys.path:
    sys.path.insert(0, str(COMPILER))

EVALUATOR = ROOT / "compiler/staqex/runtime/evaluator.py"
COMPATIBILITY = ROOT / "compiler/staqex/runtime/evaluation/compatibility.py"
SUCCESSOR = ROOT / "compiler/staqex/runtime/evaluation/operator_projection.py"

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator, KernelError  # noqa: E402
from compiler.staqex.runtime.joint import Joint, World  # noqa: E402


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


def _projection_installer_assignments() -> list[tuple[str, str]]:
    tree = ast.parse(COMPATIBILITY.read_text(encoding="utf-8"))
    assignments: list[tuple[str, str]] = []
    for function in tree.body:
        if not isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for statement in ast.walk(function):
            if not isinstance(statement, ast.Assign) or len(statement.targets) != 1:
                continue
            target = statement.targets[0]
            value = statement.value
            if (
                isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Name)
                and target.value.id == "evaluator_type"
                and target.attr == "_project_onto_operator"
                and isinstance(value, ast.Name)
            ):
                assignments.append((function.name, value.id))
    return assignments


def _run(source: str):
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    return run_canonical(compiled, Evaluator(seed=0))


def _evaluator_with_zero_projector() -> Evaluator:
    source = """
    package t
    pub fn main() -> Unit {
        Set F = { x In {0,1}^1 : x[0] == 0 }
        Operator P = Sigma (x In F) { |x><x| }
        State psi = |0>
        Measure psi
    }
    """
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    evaluator = Evaluator(seed=0)
    run_canonical(compiled, evaluator)
    assert "P" in evaluator.operators
    return evaluator


def test_projection_successor_owns_the_algorithm_without_evaluator_state() -> None:
    assert SUCCESSOR.is_file(), "missing operator_projection.py successor"
    source = SUCCESSOR.read_text(encoding="utf-8")
    tree = ast.parse(source)
    functions = {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert "project_onto_operator" in functions
    imported_evaluator = any(
        isinstance(node, ast.ImportFrom)
        and node.module in {"runtime.evaluator", "..evaluator", "evaluator"}
        for node in tree.body
    )
    assert not imported_evaluator
    assert not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "Evaluator"
        for node in ast.walk(tree)
    )


def test_projection_algorithm_body_leaves_evaluator_facade() -> None:
    assert "_project_onto_operator" not in _evaluator_method_names()


def test_projection_compatibility_hook_maps_to_successor_function() -> None:
    assert _projection_installer_assignments() == [
        ("install_operator_projection_compatibility", "project_onto_operator")
    ]


def test_projection_compatibility_installer_is_imported_and_invoked() -> None:
    installers = {
        installer
        for installer, target in _projection_installer_assignments()
        if target == "project_onto_operator"
    }
    assert installers, "projection compatibility installer is missing"
    tree = ast.parse(EVALUATOR.read_text(encoding="utf-8"))
    imported = {
        alias.asname or alias.name
        for node in tree.body
        if isinstance(node, ast.ImportFrom)
        and node.module == "evaluation.compatibility"
        for alias in node.names
        if alias.name in installers
    }
    invoked = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert imported & invoked, "Evaluator setup must invoke the installer"


def test_live_projection_hook_is_the_successor_function() -> None:
    assert SUCCESSOR.is_file(), "missing operator_projection.py successor"
    evaluator_module = importlib.import_module("staqex.runtime.evaluator")
    successor = importlib.import_module("staqex.runtime.evaluation.operator_projection")
    assert (
        evaluator_module.Evaluator._project_onto_operator
        is successor.project_onto_operator
    )


def test_genuinely_non_diagonal_operator_is_rejected_for_tuple_coordinate() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        Int n = 2
        Operator H = X[0]
        State psi = Sigma (x In {0,1}^n) { |x> }
        State projected = project psi onto H
        Measure projected
    }
    """
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    with pytest.raises(KernelError, match="supports diagonal projectors only"):
        run_canonical(compiled, Evaluator(seed=0))


def test_operator_projection_rejects_scalar_coordinate_independently() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        Operator H = Z[0]
        State psi = |0>
        State projected = project psi onto H
        Measure projected
    }
    """
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    with pytest.raises(KernelError, match="requires a tuple-valued coordinate"):
        run_canonical(compiled, Evaluator(seed=0))


def test_operator_projection_reports_unknown_operator_through_compatibility_hook() -> None:
    evaluator = Evaluator(seed=0)
    with pytest.raises(KernelError, match="unknown Operator"):
        evaluator._project_onto_operator(Joint.empty(), "q", "missing")


def test_operator_projection_returns_empty_joint_when_every_world_is_pruned() -> None:
    evaluator = _evaluator_with_zero_projector()
    source = Joint(worlds=[World(assign={"q": (1,)}, amp=1 + 0j)])

    projected = evaluator._project_onto_operator(source, "q", "P")

    assert projected.worlds == []


def test_operator_projection_copies_phase_data_and_coalesces_equal_worlds() -> None:
    evaluator = _evaluator_with_zero_projector()
    original_phase = {"q": 1j}
    source = Joint(
        worlds=[
            World(assign={"q": (0,)}, amp=1 + 0j, coord_phase=original_phase),
            World(assign={"q": (0,)}, amp=2 + 0j, coord_phase=original_phase),
            World(assign={"q": (0,)}, amp=4 + 0j, coord_phase={"q": -1j}),
        ]
    )

    projected = evaluator._project_onto_operator(source, "q", "P")

    by_phase = {world.coord_phase["q"]: world for world in projected.worlds}
    assert len(projected.worlds) == 2
    assert by_phase[1j].amp == 3 + 0j
    assert by_phase[-1j].amp == 4 + 0j
    assert by_phase[1j].coord_phase is not original_phase
    original_phase["q"] = 1 + 0j
    assert by_phase[1j].coord_phase["q"] == 1j


def test_operator_projection_reuses_compiled_matrix_for_same_name_and_width(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    evaluator = _evaluator_with_zero_projector()
    from compiler.staqex.runtime.evaluation import operator_projection

    original_compile = operator_projection.compile_hamiltonian
    compile_calls = 0

    def counted_compile(*args, **kwargs):
        nonlocal compile_calls
        compile_calls += 1
        return original_compile(*args, **kwargs)

    monkeypatch.setattr(operator_projection, "compile_hamiltonian", counted_compile)
    source = Joint(worlds=[World(assign={"q": (0,)}, amp=1 + 0j)])

    evaluator._project_onto_operator(source, "q", "P")
    first_cached_matrix = evaluator._compiled_operator_cache[("P", 1)]
    evaluator._project_onto_operator(source, "q", "P")

    assert compile_calls == 1
    assert evaluator._compiled_operator_cache[("P", 1)] is first_cached_matrix


if __name__ == "__main__":
    for test_name, test_fn in list(globals().items()):
        if test_name.startswith("test_") and callable(test_fn):
            test_fn()
            print(f"PASS {test_name}")
    print("OK - LISS-0579 Phase 1 Red")
