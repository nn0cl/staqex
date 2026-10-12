"""P06/P07 four independent ownership gaps; P08 unaffected preservation."""

import ast
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from compiler.staqex.runtime.evaluator import Evaluator, PartialValue
from tests import liss_0583_guard_support as shared
from tests import liss_0587_guard_support as partial

ROOT = Path(__file__).resolve().parents[1]


def successor():
    assert (ROOT / partial.SUCCESSOR).is_file(), "partial successor not implemented"
    return importlib.import_module("compiler.staqex.runtime.evaluation.partial_calls")


def test_p07_successor_owns_exact_class_and_algorithm():
    module = successor()
    partial.assert_successor(Path(module.__file__).read_text())
    assert module.fill_partial.__module__ == module.__name__


def test_p07_old_class_and_method_bodies_absent():
    tree = ast.parse((ROOT / partial.EVALUATOR).read_text())
    assert not any(isinstance(n, ast.ClassDef) and n.name == "PartialValue" for n in tree.body)
    assert not any(isinstance(n, ast.FunctionDef) and n.name == "_fill_partial" for n in partial.owner(tree).body)


def test_p06_exact_reexport_and_static_successor_identity():
    module = successor()
    assert PartialValue is module.PartialValue
    assert Evaluator._fill_partial is module.fill_partial
    assert Evaluator.__new__(Evaluator)._fill_partial is module.fill_partial
    assert isinstance(Evaluator.__dict__["_fill_partial"], staticmethod)
    partial.restore_partial_evaluator(ast.parse((ROOT / partial.EVALUATOR).read_text()))


def test_p07_both_cold_import_orders_have_single_class_and_hook():
    successor()  # Missing owner is an assertion Red, not collection failure.
    facade = "compiler.staqex.runtime.evaluator"
    moved = "compiler.staqex.runtime.evaluation.partial_calls"
    for order in ((facade, moved), (moved, facade)):
        code = (
            "import importlib,pickle\n"
            f"a=importlib.import_module({order[0]!r}); b=importlib.import_module({order[1]!r})\n"
            f"e=importlib.import_module({facade!r}); p=importlib.import_module({moved!r})\n"
            "assert e.PartialValue is p.PartialValue\n"
            "assert e.Evaluator._fill_partial is p.fill_partial\n"
            "v=p.PartialValue('f',[None]); assert type(pickle.loads(pickle.dumps(v))) is p.PartialValue\n"
        )
        result = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True, timeout=30)
        assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("imports_only", [False, True])
def test_p08_unaffected_evaluator_ast_and_imports_stay_protected(imports_only):
    shared.assert_evaluator_preserved((ROOT / partial.EVALUATOR).read_text(), imports_only=imports_only)


def test_p05_p08_consumers_behavior_tests_and_unrelated_owners_are_readonly():
    fixture = partial.FIXTURE.parent / "readonly-boundary.json"
    assert hashlib.sha256(fixture.read_bytes()).hexdigest() == (
        "666be68bafa1b27611f59877c7fb47778e00838c5534760118d54f86c13ccc1d"
    ), "readonly evidence changed"
    evidence = json.loads(fixture.read_text())
    assert evidence["base"] == "b5ad7402c184a3a79440271e02dd423c53d8bc36"
    assert len(evidence["readonly_sha256"]) == 22
    for path, digest in evidence["readonly_sha256"].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
