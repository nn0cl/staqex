"""G01–G07: exercise the real repair guard, not a replacement checker."""

import ast
import copy
import json
from pathlib import Path
import tomllib

import pytest

from tests import liss_0583_guard_support as support
from tests import test_liss_0584_repair_boundary_red as repair

ROOT = Path(__file__).resolve().parents[1]
EVALUATOR = "compiler/staqex/runtime/evaluator.py"
COMPATIBILITY = "compiler/staqex/runtime/evaluation/compatibility.py"
CONTEXT = "compiler/staqex/runtime/evaluation/context.py"
BYTE_PATHS = (
    "compiler/staqex/pipeline_legacy.py",
    "docs/testing/refactor-baseline.json",
    "scripts/capture-refactor-baseline.py",
    "tests/test_liss_0583_static_foreach_successor_red.py",
    "tests/test_liss_0583_static_foreach_behavior_red.py",
)


@pytest.fixture
def guarded_tree(tmp_path, monkeypatch):
    """Only ROOT changes; the real immutable fixture and checker remain in use."""
    evidence = repair.boundary()
    assert set(evidence["readonly_sha256"]) == {
        EVALUATOR, COMPATIBILITY, CONTEXT, *BYTE_PATHS,
    }
    for name in evidence["readonly_sha256"]:
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / name).read_bytes())
    monkeypatch.setattr(repair, "ROOT", tmp_path)
    return tmp_path


def check():
    repair.test_existing_f05_owner_and_readonly_dependencies_are_preserved()


def baseline_shape(directory):
    """Recover the old executable shape, not old bytes; no test-time Git use."""
    successor = ast.parse(
        (ROOT / "compiler/staqex/runtime/evaluation/static_foreach.py").read_text()
    )
    method = copy.deepcopy(next(n for n in successor.body if isinstance(n, ast.FunctionDef)))
    method.name = "_run_foreach"
    method.args.args[0] = ast.arg(arg="self")
    method.body[0] = ast.Expr(ast.Constant(
        "Expand a static register loop into compiler-internal wire names."
    ))

    class OriginalReceiver(ast.NodeTransformer):
        def visit_Name(self, node):
            if node.id == "context":
                node.id = "self"
            return node

    method = OriginalReceiver().visit(method)
    assert support.digest(method) == support.baseline()["old_foreach_ast"]
    evaluator = support.evaluator_projection((directory / EVALUATOR).read_text())
    owner = next(n for n in evaluator.body if isinstance(n, ast.ClassDef) and n.name == "Evaluator")
    owner.body.append(method)
    evaluator_source = ast.unparse(ast.fix_missing_locations(evaluator))
    support.assert_evaluator_preserved(evaluator_source)
    (directory / EVALUATOR).write_text(evaluator_source)
    compatibility = support.compatibility_projection((directory / COMPATIBILITY).read_text())
    (directory / COMPATIBILITY).write_text(ast.unparse(compatibility))
    context = support.context_projection((directory / CONTEXT).read_text())
    (directory / CONTEXT).write_text(ast.unparse(context))


@pytest.mark.parametrize("shape", ["extracted", "baseline-ast"])
def test_real_guard_accepts_only_reviewed_positive_shapes(guarded_tree, shape):
    if shape == "baseline-ast":
        baseline_shape(guarded_tree)
    check()


def test_real_guard_delegates_to_existing_f08_projections(guarded_tree, monkeypatch):
    calls = []
    for name in ("assert_evaluator_preserved", "assert_compatibility_preserved", "context_projection"):
        original = getattr(support, name)

        def record(*args, _name=name, _original=original, **kwargs):
            calls.append((_name, kwargs))
            return _original(*args, **kwargs)

        # The old guard has no such imports. Inject spies without modifying its
        # function: a missing delegation is Red, not a fixture import failure.
        monkeypatch.setattr(repair, name, record, raising=False)
    check()
    assert ("assert_evaluator_preserved", {"imports_only": True}) in calls
    assert ("assert_evaluator_preserved", {}) in calls
    assert ("assert_compatibility_preserved", {}) in calls
    assert ("context_projection", {}) in calls


@pytest.mark.parametrize("path", BYTE_PATHS)
def test_each_persistent_byte_dependency_still_rejects_change(guarded_tree, path):
    target = guarded_tree / path
    target.write_bytes(target.read_bytes() + b"\n# forbidden byte change\n")
    with pytest.raises(AssertionError):
        check()


@pytest.mark.parametrize("field,value", [
    ("base_sha", "wrong-base"),
    ("adopted_owner", "wrong-owner"),
    ("adopted_node", "tests/other.py::different_node"),
])
def test_real_guard_keeps_adoption_metadata(guarded_tree, monkeypatch, field, value):
    # Isolate metadata assertions from the separately tested fixture digest.
    evidence = copy.deepcopy(repair.boundary())
    evidence[field] = value
    monkeypatch.setattr(repair, "boundary", lambda: evidence)
    with pytest.raises(AssertionError):
        check()


def test_original_fixture_cannot_be_rewritten(guarded_tree, monkeypatch, tmp_path):
    candidate = tmp_path / "altered-boundary.json"
    evidence = json.loads(repair.FIXTURE.read_text())
    evidence["readonly_sha256"][EVALUATOR] = "0" * 64
    candidate.write_text(json.dumps(evidence))
    monkeypatch.setattr(repair, "FIXTURE", candidate)
    with pytest.raises(AssertionError):
        check()


SOURCE_MUTATIONS = (
    (EVALUATOR, "    ForEachStmt,", "", "removed-public-import"),
    (EVALUATOR, "from dataclasses import dataclass, field, replace",
     "from dataclasses import dataclass, field, replace as lost", "rebound-public-import"),
    (EVALUATOR, "return self.static_register_sizes.get(name)", "return 99", "unrelated-body"),
    (EVALUATOR, "class Evaluator:",
     "class Evaluator:\n    def _run_foreach(self, joint, stmt):\n        return 99\n", "reintroduced-body"),
    (EVALUATOR, "_install_static_foreach_compatibility(Evaluator)",
     "_install_static_foreach_compatibility(object)", "wrong-setup"),
    (EVALUATOR, "_install_static_foreach_compatibility(Evaluator)",
     "_install_static_foreach_compatibility(Evaluator)\n_install_static_foreach_compatibility(Evaluator)", "duplicate-setup"),
    (COMPATIBILITY, "evaluator_type._run_foreach = execute_static_foreach",
     "evaluator_type._run_foreach = bind_call", "wrong-installer"),
    (COMPATIBILITY, "evaluator_type._bind_call = bind_call",
     "evaluator_type._bind_call = None", "changed-existing-hook"),
    (COMPATIBILITY, "evaluator_type._run_foreach = execute_static_foreach",
     "evaluator_type._run_foreach = execute_static_foreach\n    evaluator_type.shared_state = {}", "extra-state"),
    (CONTEXT, "static_register_sizes: Mapping[str, int]",
     "static_register_sizes: dict[str, int]", "wrong-context-type"),
    (CONTEXT, "def _run_foreach(self, joint: Any, stmt: Any) -> Any: ...",
     "def _run_foreach(self, joint: Any, stmt: Any) -> Any: return joint", "context-implementation"),
    (CONTEXT, "funs: Mapping[str, Any]", "funs: Mapping[str, int]", "unrelated-context"),
)


@pytest.mark.parametrize("path,old,new,label", SOURCE_MUTATIONS, ids=[m[3] for m in SOURCE_MUTATIONS])
def test_real_guard_rejects_unapproved_source_mutations(guarded_tree, path, old, new, label):
    target = guarded_tree / path
    source = target.read_text()
    assert source.count(old) == 1, label
    target.write_text(source.replace(old, new, 1))
    with pytest.raises(AssertionError):
        check()


def test_real_guard_rejects_duplicate_installer(guarded_tree):
    target = guarded_tree / COMPATIBILITY
    tree = ast.parse(target.read_text())
    installer = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                     and n.name == "install_static_foreach_compatibility")
    tree.body.append(copy.deepcopy(installer))
    target.write_text(ast.unparse(tree))
    with pytest.raises(AssertionError):
        check()


def test_real_guard_rejects_changed_retained_old_body(guarded_tree):
    baseline_shape(guarded_tree)
    target = guarded_tree / EVALUATOR
    tree = ast.parse(target.read_text())
    method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "_run_foreach")
    method.body = ast.parse("return 99").body
    target.write_text(ast.unparse(tree))
    with pytest.raises(AssertionError):
        check()


def test_original_guard_is_not_excluded_from_blocking_root():
    data = tomllib.loads((ROOT / "docs/testing/active-red-tests.toml").read_text())
    node = "tests/test_liss_0584_repair_boundary_red.py::test_existing_f05_owner_and_readonly_dependencies_are_preserved"
    assert not any(entry["test"] == node for entry in data.get("active_red", []))
