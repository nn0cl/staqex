"""H09: exact Host transition through actual inherited guards and fixture copies."""

import ast
import copy
from pathlib import Path

import pytest

from tests import liss_0583_guard_support as shared
from tests import liss_0585_guard_support as tensor
from tests import liss_0586_guard_support as host
from tests import test_liss_0583_repair_boundary_migration_red as foreach_tests
from tests import test_liss_0584_repair_boundary_red as repair
from tests import test_liss_0585_tensor_guard_migration_red as tensor_tests

ROOT = Path(__file__).resolve().parents[1]
EVALUATOR = "compiler/staqex/runtime/evaluator.py"
COMPATIBILITY = "compiler/staqex/runtime/evaluation/compatibility.py"


def write_tree(directory, path, tree):
    (directory / path).write_text(ast.unparse(ast.fix_missing_locations(tree)))


def make_shape(directory, extracted):
    evaluator = host.restore_host_evaluator(ast.parse((directory / EVALUATOR).read_text()))
    compatibility = host.restore_host_compatibility(ast.parse((directory / COMPATIBILITY).read_text()))
    if extracted:
        owner = next(n for n in evaluator.body if isinstance(n, ast.ClassDef) and n.name == "Evaluator")
        method = next(n for n in owner.body if isinstance(n, ast.FunctionDef) and n.name == host.METHOD)
        assert host.dump(method) == host.dump(host.original_method())
        owner.body.remove(method)
        evaluator.body.extend(ast.parse(
            f"from .evaluation.compatibility import {host.INSTALLER} as {host.PRIVATE}\n"
            f"{host.PRIVATE}(Evaluator)\n"
        ).body)
        compatibility.body.extend(ast.parse(
            f"from .host_coefficients import {host.FUNCTION}\n"
            f"def {host.INSTALLER}(evaluator_type: type[Any]) -> None:\n"
            f"    evaluator_type.{host.METHOD} = {host.FUNCTION}\n"
        ).body)
        method = copy.deepcopy(method)
        method.name = host.FUNCTION
        method.args.args[0].arg = "context"
        class Move(ast.NodeTransformer):
            def visit_Name(self, node):
                if node.id == "self":
                    node.id = "context"
                return node
            def visit_ImportFrom(self, node):
                if node.module in ("finite_binder", "scientific_input"):
                    node.level = 3
                return node
        successor = ast.parse(
            '"""Temporary AST proposal; never imported or production implementation."""\n'
            "from typing import Any, Protocol\n"
            "from ...host_input_port import HostInputPort\n"
            "from ...ast_nodes import CompilationUnit\n"
            "from .errors import KernelDiagnosticError\n"
            "class HostCoefficientContext(Protocol):\n"
            "    host_input: HostInputPort | None\n"
        )
        successor.body.append(Move().visit(method))
        target = directory / host.SUCCESSOR
        target.parent.mkdir(parents=True, exist_ok=True)
        write_tree(directory, host.SUCCESSOR, successor)
    else:
        target = directory / host.SUCCESSOR
        if target.exists():
            target.unlink()  # Only this copied file under pytest's temporary root.
    write_tree(directory, EVALUATOR, evaluator)
    write_tree(directory, COMPATIBILITY, compatibility)


def assert_shape(directory, extracted):
    tree = ast.parse((directory / EVALUATOR).read_text())
    owner = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Evaluator")
    methods = [n for n in owner.body if isinstance(n, ast.FunctionDef) and n.name == host.METHOD]
    setups = [n for n in tree.body if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
              and isinstance(n.value.func, ast.Name) and n.value.func.id == host.PRIVATE]
    assert len(methods) == (0 if extracted else 1)
    assert len(setups) == (1 if extracted else 0)
    assert (directory / host.SUCCESSOR).is_file() == extracted


def check(directory, monkeypatch):
    monkeypatch.setattr(repair, "ROOT", directory)
    repair.test_existing_f05_owner_and_readonly_dependencies_are_preserved()
    source = (directory / EVALUATOR).read_text()
    shared.assert_evaluator_preserved(source, imports_only=True)
    shared.assert_evaluator_preserved(source)
    shared.assert_compatibility_preserved((directory / COMPATIBILITY).read_text())
    tree = ast.parse(source)
    installed = any(isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
                    and isinstance(n.value.func, ast.Name) and n.value.func.id == host.PRIVATE
                    for n in tree.body)
    if installed:
        assert (directory / host.SUCCESSOR).is_file(), "missing Host successor"
        host.assert_successor_algorithm((directory / host.SUCCESSOR).read_text())


@pytest.fixture
def guarded(tmp_path):
    tensor_tests.copy_guarded_dependencies(ROOT, tmp_path)
    path = "compiler/staqex/runtime/evaluation/static_foreach.py"
    (tmp_path / path).write_bytes((ROOT / path).read_bytes())
    return tmp_path


@pytest.mark.parametrize("extracted", [False, True], ids=["pre-host", "post-host"])
@pytest.mark.parametrize("tensor_shape", ["current", "historical"])
def test_h09_real_guards_and_actual_fixture_copies_in_distinct_shapes(guarded, monkeypatch, extracted, tensor_shape):
    if tensor_shape == "historical":
        write_tree(guarded, EVALUATOR, tensor.restore_tensor_evaluator(ast.parse((guarded / EVALUATOR).read_text())))
        write_tree(guarded, COMPATIBILITY, tensor.restore_tensor_compatibility(ast.parse((guarded / COMPATIBILITY).read_text())))
    make_shape(guarded, extracted)
    assert_shape(guarded, extracted)
    check(guarded, monkeypatch)
    for suite in (foreach_tests, tensor_tests):
        monkeypatch.setattr(suite, "ROOT", guarded)
        copied = guarded / suite.__name__.split(".")[-1]
        fixture = suite.guarded_tree.__wrapped__(copied, monkeypatch)
        assert_shape(fixture, extracted)
        check(fixture, monkeypatch)
        if suite is foreach_tests:
            historical = guarded / "historical-foreach"
            historical_fixture = suite.guarded_tree.__wrapped__(historical, monkeypatch)
            suite.baseline_shape(historical_fixture)
            successor = historical_fixture / host.SUCCESSOR
            if successor.exists():
                successor.unlink()  # Only the dependency copy in this temporary shape.
            assert_shape(historical_fixture, False)
            check(historical_fixture, monkeypatch)
        if extracted:
            (fixture / host.SUCCESSOR).unlink()
            with pytest.raises(AssertionError, match="missing Host successor"):
                check(fixture, monkeypatch)


@pytest.mark.parametrize("path,old,new", [
    (EVALUATOR, f"{host.PRIVATE}(Evaluator)", f"{host.PRIVATE}(object)"),
    (EVALUATOR, f"{host.PRIVATE}(Evaluator)", f"{host.PRIVATE}(Evaluator)\n{host.PRIVATE}(Evaluator)"),
    (EVALUATOR, "return self.static_register_sizes.get(name)", "return 99"),
    (EVALUATOR, "replace", "replace as lost"),
    (COMPATIBILITY, f"evaluator_type.{host.METHOD} = {host.FUNCTION}", f"evaluator_type.{host.METHOD} = bind_tensor"),
    (COMPATIBILITY, f"evaluator_type.{host.METHOD} = {host.FUNCTION}", f"evaluator_type.{host.METHOD} = {host.FUNCTION}\n    evaluator_type.state = {{}}"),
    (COMPATIBILITY, "evaluator_type._bind_tensor = bind_tensor", "evaluator_type._bind_tensor = bind_call"),
    (host.SUCCESSOR, "return arrays", "return {}"),
    (host.SUCCESSOR, "host_input: HostInputPort | None", "host_input: HostInputPort | None = None"),
    (host.SUCCESSOR, "from ...finite_binder", "from ..finite_binder"),
    (host.SUCCESSOR, "from .errors import KernelDiagnosticError", "from .values import KernelDiagnosticError"),
])
def test_h09_rejects_algorithm_export_state_and_wiring_mutations(guarded, monkeypatch, path, old, new):
    make_shape(guarded, True)
    check(guarded, monkeypatch)
    target = guarded / path
    source = target.read_text()
    assert source.count(old) == 1
    target.write_text(source.replace(old, new, 1))
    with pytest.raises(AssertionError):
        check(guarded, monkeypatch)


@pytest.mark.parametrize("mutation", ["missing-successor", "old-body", "duplicate-import", "duplicate-installer"])
def test_h09_rejects_missing_or_duplicate_ownership(guarded, monkeypatch, mutation):
    make_shape(guarded, True)
    check(guarded, monkeypatch)
    if mutation == "missing-successor":
        (guarded / host.SUCCESSOR).unlink()
    elif mutation == "old-body":
        tree = ast.parse((guarded / EVALUATOR).read_text())
        next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Evaluator").body.append(host.original_method())
        write_tree(guarded, EVALUATOR, tree)
    else:
        tree = ast.parse((guarded / COMPATIBILITY).read_text())
        node = next(n for n in tree.body if (
            isinstance(n, ast.ImportFrom) and n.module == "host_coefficients"
            if mutation == "duplicate-import" else isinstance(n, ast.FunctionDef) and n.name == host.INSTALLER
        ))
        tree.body.append(copy.deepcopy(node))
        write_tree(guarded, COMPATIBILITY, tree)
    with pytest.raises(AssertionError):
        check(guarded, monkeypatch)


def test_h09_old_body_change_rejected_before_and_after_move(guarded, monkeypatch):
    for extracted in (False, True):
        make_shape(guarded, extracted)
        check(guarded, monkeypatch)
        make_shape(guarded, False)
        target = guarded / EVALUATOR
        source = target.read_text()
        assert "return arrays" in source
        target.write_text(source.replace("return arrays", "return {}", 1))
        with pytest.raises(AssertionError):
            check(guarded, monkeypatch)
        tree = ast.parse(source)
        write_tree(guarded, EVALUATOR, tree)


def test_h09_original_host_fixture_is_immutable(tmp_path, monkeypatch):
    fixture = tmp_path / "changed.txt"
    fixture.write_bytes(host.FIXTURE.read_bytes() + b"\n")
    monkeypatch.setattr(host, "FIXTURE", fixture)
    with pytest.raises(AssertionError, match="evidence changed"):
        host.original_method()


@pytest.mark.parametrize("path", foreach_tests.BYTE_PATHS)
def test_h09_five_persistent_byte_dependencies_remain_protected(guarded, monkeypatch, path):
    make_shape(guarded, True)
    check(guarded, monkeypatch)
    target = guarded / path
    target.write_bytes(target.read_bytes() + b"\n# forbidden change\n")
    with pytest.raises(AssertionError):
        check(guarded, monkeypatch)
