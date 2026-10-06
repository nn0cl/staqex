"""F08: positive migration and mutation-negative equivalence checks."""

import ast
import hashlib
from pathlib import Path

import pytest

from tests.liss_0583_guard_support import (
    assert_compatibility_preserved, assert_evaluator_preserved, baseline,
    compatibility_projection, context_projection, digest, evaluator_projection,
)

ROOT = Path(__file__).resolve().parents[1]
EVALUATOR = ROOT / "compiler/staqex/runtime/evaluator.py"
COMPATIBILITY = ROOT / "compiler/staqex/runtime/evaluation/compatibility.py"


def test_fixture_provenance_and_original_guard_audit():
    evidence = baseline()
    assert evidence["base_sha"] == "a287be51da358eed195f836afa21b07286128940"
    assert evidence["repair_base_sha"] == "423c003b0b39c292731f6a8c7456a0b40cbd03f2"
    assert evidence["old_repair_import_digest"] == "1fbcee4ff01ad715a09074c5d1f3232e083e89cd23f212df6e5147cb33b6d959"
    assert evidence["old_repair_executable_digest"] == "a745686bf2fb7930b56e950aa2bbc3bc485db08cca494bdb2351a0ca80a2a25d"
    assert evidence["compatibility_source_sha256"] == "f3792eb9c7c8636e1395e74a9faf0d539a7b170549a22ad70a1dc2a944cc2c4a"


def test_evaluator_projection_accepts_only_body_removal_and_private_setup():
    tree = evaluator_projection(EVALUATOR.read_text())
    added = ast.parse(
        "from .evaluation.compatibility import install_static_foreach_compatibility as _install_static_foreach_compatibility\n"
        "_install_static_foreach_compatibility(Evaluator)\n"
    ).body
    tree.body.extend(added)
    source = ast.unparse(tree)
    assert_evaluator_preserved(source)
    assert_evaluator_preserved(source, imports_only=True)


@pytest.mark.parametrize("old,new", [
    ("return self.static_register_sizes.get(name)", "return 99"),
    ("class Evaluator:", "class Evaluator:\n    unexpected = 1"),
    ("    ForEachStmt,", ""),
    ("from ..static_hilbert import MVP_MAX_LOGICAL_QUBITS", "from ..static_hilbert import MVP_MAX_LOGICAL_QUBITS as lost"),
    ("from dataclasses import dataclass, field, replace", "from dataclasses import dataclass, field"),
])
def test_evaluator_guard_detects_unapproved_mutations(old, new):
    source = EVALUATOR.read_text()
    assert old in source
    with pytest.raises(AssertionError):
        assert_evaluator_preserved(source.replace(old, new, 1))


def test_evaluator_guard_rejects_changed_or_reintroduced_foreach_body():
    tree = ast.parse(EVALUATOR.read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Evaluator")
    method = next((n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "_run_foreach"), None)
    if method is not None:
        method.body = ast.parse("return 99").body
    else:
        cls.body.extend(ast.parse("def _run_foreach(self, joint, stmt):\n    return 99\n").body)
    with pytest.raises(AssertionError, match="retained foreach body changed"):
        assert_evaluator_preserved(ast.unparse(tree))


def installer_source(target="execute_static_foreach"):
    return (
        "\nfrom .static_foreach import execute_static_foreach\n"
        "def install_static_foreach_compatibility(evaluator_type: type[Any]) -> None:\n"
        f"    evaluator_type._run_foreach = {target}\n"
    )


def test_compatibility_projection_accepts_only_exact_new_mapping():
    source = ast.unparse(compatibility_projection(COMPATIBILITY.read_text()))
    assert_compatibility_preserved(source + installer_source())


@pytest.mark.parametrize("mutation", ["wrong-target", "existing-hook", "extra-state", "duplicate"])
def test_compatibility_guard_detects_mapping_or_unrelated_changes(mutation):
    source = ast.unparse(compatibility_projection(COMPATIBILITY.read_text()))
    if mutation == "wrong-target":
        source += installer_source("bind_call")
    elif mutation == "existing-hook":
        source = source.replace("evaluator_type._bind_call = bind_call", "evaluator_type._bind_call = None")
    elif mutation == "extra-state":
        source += installer_source() + "    evaluator_type.shared_state = {}\n"
    else:
        source += installer_source() * 2
    with pytest.raises(AssertionError):
        assert_compatibility_preserved(source)


def test_context_and_adjacent_owners_remain_preserved():
    # No exclusions for execution/calls/pipes bodies. Context may add only
    # the two specifically typed protocol declarations, not implementations.
    directory = ROOT / "compiler/staqex/runtime/evaluation"
    expected = baseline()["adjacent_sha256"]
    for name, value in expected.items():
        assert hashlib.sha256((directory / name).read_bytes()).hexdigest() == value
    assert digest(context_projection((directory / "context.py").read_text())) == baseline()["context_ast"]


def test_context_projection_accepts_only_the_two_typed_declarations():
    tree = context_projection((ROOT / "compiler/staqex/runtime/evaluation/context.py").read_text())
    protocol = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "EvaluatorContext")
    protocol.body.extend(ast.parse(
        "static_register_sizes: Mapping[str, int]\n"
        "def _run_foreach(self, joint: Any, stmt: Any) -> Any: ...\n"
    ).body)
    assert digest(context_projection(ast.unparse(tree))) == baseline()["context_ast"]


@pytest.mark.parametrize("declaration", [
    "static_register_sizes: dict[str, int]",
    "def _run_foreach(self, joint: Any, stmt: Any) -> Any: return joint",
])
def test_context_projection_rejects_unapproved_declarations(declaration):
    tree = context_projection((ROOT / "compiler/staqex/runtime/evaluation/context.py").read_text())
    protocol = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "EvaluatorContext")
    protocol.body.extend(ast.parse(declaration).body)
    with pytest.raises(AssertionError, match="context addition is not a declaration"):
        context_projection(ast.unparse(tree))
