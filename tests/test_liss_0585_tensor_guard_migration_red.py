"""T09: exact accepted Tensor shape through inherited real preservation guards."""

import ast
import copy
import hashlib
from pathlib import Path

import pytest

from tests import liss_0583_guard_support as shared
from tests import liss_0585_guard_support as tensor
from tests import test_liss_0584_repair_boundary_red as repair
from tests.test_liss_0583_repair_boundary_migration_red import BYTE_PATHS

ROOT = Path(__file__).resolve().parents[1]
EVALUATOR = "compiler/staqex/runtime/evaluator.py"
COMPATIBILITY = "compiler/staqex/runtime/evaluation/compatibility.py"
SUCCESSOR = "compiler/staqex/runtime/evaluation/tensor_binding.py"


def copy_guarded_dependencies(origin, destination):
    """Preserve the historical manifest and separately copy a live successor."""
    for path in repair.boundary()["readonly_sha256"]:
        target = destination / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((origin / path).read_bytes())
    successor = origin / SUCCESSOR
    if successor.is_file():
        target = destination / SUCCESSOR
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(successor.read_bytes())


@pytest.fixture(name="guarded")
def guarded_tree(tmp_path, monkeypatch):
    copy_guarded_dependencies(ROOT, tmp_path)
    monkeypatch.setattr(repair, "ROOT", tmp_path)
    return tmp_path


def extracted_shape(directory):
    """Construct only a temporary test proposal, never production implementation."""
    tree = tensor.restore_tensor_evaluator(ast.parse((directory / EVALUATOR).read_text()))
    owner = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Evaluator")
    method = next(n for n in owner.body if isinstance(n, ast.FunctionDef) and n.name == "_bind_tensor")
    assert ast.dump(method, include_attributes=False) == ast.dump(tensor.original_method(), include_attributes=False)
    owner.body.remove(method)
    tree.body.extend(ast.parse(
        "from .evaluation.compatibility import install_tensor_binding_compatibility as _install_tensor_binding_compatibility\n"
        "_install_tensor_binding_compatibility(Evaluator)\n"
    ).body)
    (directory / EVALUATOR).write_text(ast.unparse(tree))
    compatibility = tensor.restore_tensor_compatibility(ast.parse((directory / COMPATIBILITY).read_text()))
    compatibility.body.extend(ast.parse(
        "from .tensor_binding import bind_tensor\n"
        "def install_tensor_binding_compatibility(evaluator_type: type[Any]) -> None:\n"
        "    evaluator_type._bind_tensor = bind_tensor\n"
    ).body)
    (directory / COMPATIBILITY).write_text(ast.unparse(compatibility))
    method = copy.deepcopy(method)
    method.name = "bind_tensor"
    method.args.args[0].arg = "context"

    class Receiver(ast.NodeTransformer):
        def visit_Name(self, node):
            if node.id == "self":
                node.id = "context"
            return node

        def visit_ImportFrom(self, node):
            if node.module == "joint":
                node.level = 2
            return node

    successor = ast.Module(body=[Receiver().visit(method)], type_ignores=[])
    (directory / SUCCESSOR).write_text(ast.unparse(ast.fix_missing_locations(successor)))


def check(directory):
    evaluator_source = (directory / EVALUATOR).read_text()
    shared.assert_evaluator_preserved(evaluator_source, imports_only=True)
    shared.assert_evaluator_preserved(evaluator_source)
    shared.assert_compatibility_preserved((directory / COMPATIBILITY).read_text())
    repair.test_existing_f05_owner_and_readonly_dependencies_are_preserved()
    tree = ast.parse(evaluator_source)
    installed = any(isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
                    and isinstance(n.value.func, ast.Name) and n.value.func.id == tensor.PRIVATE
                    for n in tree.body)
    if installed:
        assert (directory / SUCCESSOR).is_file(), "missing tensor implementation"
        tensor.assert_successor_algorithm((directory / SUCCESSOR).read_text())


@pytest.mark.parametrize("shape", ["current", "tensor-extracted"])
def test_t09_real_shared_and_readonly_guards_accept_authorized_shapes(guarded, shape):
    if shape == "tensor-extracted":
        extracted_shape(guarded)
    check(guarded)


@pytest.mark.parametrize("path,old,new", [
    (EVALUATOR, "_install_tensor_binding_compatibility(Evaluator)", "_install_tensor_binding_compatibility(object)"),
    (EVALUATOR, "_install_tensor_binding_compatibility(Evaluator)", "_install_tensor_binding_compatibility(Evaluator)\n_install_tensor_binding_compatibility(Evaluator)"),
    (EVALUATOR, "return self.static_register_sizes.get(name)", "return 99"),
    (EVALUATOR, "class Evaluator:", "class Evaluator:\n    new_state = {}"),
    (EVALUATOR, "_install_static_foreach_compatibility(Evaluator)", "_install_static_foreach_compatibility(object)"),
    (EVALUATOR, "replace", "replace as lost"),
    (COMPATIBILITY, "evaluator_type._bind_tensor = bind_tensor", "evaluator_type._bind_tensor = bind_call"),
    (COMPATIBILITY, "evaluator_type._bind_tensor = bind_tensor", "evaluator_type._bind_tensor = bind_tensor\n    evaluator_type.state = {}"),
    (COMPATIBILITY, "evaluator_type._run_foreach = execute_static_foreach", "evaluator_type._run_foreach = bind_call"),
    (COMPATIBILITY, "evaluator_type._bind_call = bind_call", "evaluator_type._bind_call = None"),
    (SUCCESSOR, "return Joint.empty()", "return Joint.unit()"),
])
def test_t09_real_guards_reject_wiring_export_state_and_algorithm_mutations(guarded, path, old, new):
    extracted_shape(guarded)
    target = guarded / path
    source = target.read_text()
    assert source.count(old) == 1
    target.write_text(source.replace(old, new, 1))
    with pytest.raises(AssertionError):
        check(guarded)


@pytest.mark.parametrize("mutation", ["duplicate-mapping", "duplicate-import", "reintroduced-body", "missing-successor"])
def test_t09_real_guards_reject_duplicate_or_missing_ownership(guarded, mutation):
    extracted_shape(guarded)
    if mutation == "missing-successor":
        # Delete only the explicitly created temporary test file.
        (guarded / SUCCESSOR).unlink()
    elif mutation == "reintroduced-body":
        tree = ast.parse((guarded / EVALUATOR).read_text())
        owner = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Evaluator")
        owner.body.append(tensor.original_method())
        (guarded / EVALUATOR).write_text(ast.unparse(tree))
    else:
        tree = ast.parse((guarded / COMPATIBILITY).read_text())
        node = next(n for n in tree.body if (
            isinstance(n, ast.FunctionDef) and n.name == tensor.INSTALLER
            if mutation == "duplicate-mapping" else
            isinstance(n, ast.ImportFrom) and n.module == "tensor_binding"
        ))
        tree.body.append(copy.deepcopy(node))
        (guarded / COMPATIBILITY).write_text(ast.unparse(tree))
    with pytest.raises(AssertionError):
        check(guarded)


def test_t09_changed_original_method_is_not_an_allowed_projection(guarded):
    # Recover historical shape even when the current checkout is extracted.
    target = guarded / EVALUATOR
    tree = tensor.restore_tensor_evaluator(ast.parse(target.read_text()))
    target.write_text(ast.unparse(tree))
    compatibility = guarded / COMPATIBILITY
    compatibility.write_text(ast.unparse(tensor.restore_tensor_compatibility(
        ast.parse(compatibility.read_text())
    )))
    check(guarded)  # Authorized reconstruction must pass before mutation.
    source = target.read_text()
    assert "left = _amps_indep(expr.left)" in source
    target.write_text(source.replace("left = _amps_indep(expr.left)", "left = []", 1))
    with pytest.raises(AssertionError):
        check(guarded)


@pytest.mark.parametrize("root_shape", ["unextracted", "tensor-extracted"])
def test_t09_guard_fixture_and_old_body_mutation_work_before_and_after_extraction(guarded, monkeypatch, root_shape):
    if root_shape == "tensor-extracted":
        extracted_shape(guarded)
    copied = guarded / "fixture-copy"
    # Invoke the real pytest fixture against both possible checkout shapes.
    monkeypatch.setitem(globals(), "ROOT", guarded)
    fixture = guarded_tree.__wrapped__(copied, monkeypatch)
    assert (fixture / SUCCESSOR).is_file() == (guarded / SUCCESSOR).is_file()
    test_t09_real_shared_and_readonly_guards_accept_authorized_shapes(fixture, "current")
    test_t09_changed_original_method_is_not_an_allowed_projection(fixture)


@pytest.mark.parametrize("path", BYTE_PATHS)
def test_t09_all_five_repair_byte_dependencies_remain_frozen(guarded, path):
    target = guarded / path
    target.write_bytes(target.read_bytes() + b"\n# mutation\n")
    with pytest.raises(AssertionError):
        check(guarded)


def test_t09_original_tensor_fixture_is_immutable(tmp_path, monkeypatch):
    original = tensor.original_method()
    fixture = tmp_path / "changed.txt"
    fixture.write_text(ast.unparse(original))
    monkeypatch.setattr(tensor, "FIXTURE", fixture)
    with pytest.raises(AssertionError, match="evidence changed"):
        tensor.original_method()


@pytest.mark.parametrize("path,expected", [
    ("compiler/staqex/runtime/evaluation/binding.py", "c00bdd49bcf326a40b733042b74275c7f4fbfc50ba9a585385f6ba9a77d8dcc5"),
    ("compiler/staqex/runtime/evaluation/context.py", "0f11c9a59026dff24d29666c7597380aa82a82a73aa116f8c66ccdbc97a33f77"),
    ("tests/fixtures/liss_0583/guard-baseline.json", "9cca28c93d06df68081ea2a3c01a54d07a9222aa2dcb002d3948c44325b66dd0"),
    ("tests/fixtures/liss_0584/repair-boundary.json", "d0d2c74d0552fd31a6894ea7d2908e4ea506fd639e5d986c2ed40423f3fc4bd3"),
])
def test_t09_adjacent_dispatch_context_and_original_evidence_bytes_are_frozen(path, expected):
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected
