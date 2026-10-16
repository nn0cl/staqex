"""C07 structural Red and C08 immutable unrelated ownership evidence."""

import ast
from tests.liss_0590_guard_support import readonly_bytes
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from compiler.staqex.runtime.evaluator import Evaluator
from tests import liss_0583_guard_support as shared
from tests import liss_0588_guard_support as closed


def successor():
    assert (closed.ROOT / closed.SUCCESSOR).is_file(), 'closed successor not implemented'
    return importlib.import_module('compiler.staqex.runtime.evaluation.closed_expressions')


def test_c07_successor_owns_exact_algorithm_and_protocol():
    module = successor()
    closed.assert_successor(Path(module.__file__).read_text())
    assert module.is_closed.__module__ == module.__name__


def test_c07_old_algorithm_absent_and_exact_class_assignment():
    tree = ast.parse((closed.ROOT / closed.EVALUATOR).read_text())
    assert not any(isinstance(n, ast.FunctionDef) and n.name == '_is_closed' for n in closed.owner(tree).body)
    closed.restore_closed_evaluator(tree)


def test_c07_runtime_class_and_bound_instance_identity():
    module = successor()
    assert Evaluator._is_closed is module.is_closed
    owner = Evaluator.__new__(Evaluator)
    assert owner._is_closed.__func__ is module.is_closed
    assert owner._is_closed.__self__ is owner
    assert not isinstance(Evaluator.__dict__['_is_closed'], (staticmethod, classmethod))


def test_c07_both_cold_requested_import_orders_and_actual_consumers():
    successor()
    facade = 'compiler.staqex.runtime.evaluator'
    moved = 'compiler.staqex.runtime.evaluation.closed_expressions'
    for order in [(facade, moved), (moved, facade)]:
        code = (
            'import importlib\n'
            f'a=importlib.import_module({order[0]!r}); b=importlib.import_module({order[1]!r})\n'
            f'e=importlib.import_module({facade!r}); s=importlib.import_module({moved!r})\n'
            "assert e.Evaluator._is_closed is s.is_closed\n"
            "o=e.Evaluator.__new__(e.Evaluator); assert o._is_closed.__func__ is s.is_closed\n"
            "from compiler.staqex.runtime.evaluation import execution,binding,operators,context\n"
            "from compiler.staqex.ast_nodes import LitInt,Span\n"
            "assert o._is_closed(LitInt(1,Span(1,1))) is True\n"
        )
        result = subprocess.run([sys.executable, '-c', code], cwd=closed.ROOT, capture_output=True, text=True, timeout=30)
        assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize('imports_only', [False, True])
def test_c08_unaffected_evaluator_ast_and_exports_still_protected(imports_only):
    shared.assert_evaluator_preserved((closed.ROOT / closed.EVALUATOR).read_text(), imports_only=imports_only)


def test_c08_readonly_sources_adjacent_tests_and_prior_fixtures():
    fixture = closed.FIXTURE.parent / 'readonly-boundary.json'
    assert hashlib.sha256(fixture.read_bytes()).hexdigest() == '9155dadf4440560188e58a29ae7a44b6009b2241fb6f71b3658f5748543e6bdf'
    evidence = json.loads(fixture.read_text())
    assert evidence['base'] == 'a19cc974a4e0200d74ae012c9b76d2a8f4d18b0a'
    assert hashlib.sha256(closed.dump(closed.original_method()).encode()).hexdigest() == evidence['original_ast_sha256']
    for path, expected in evidence['readonly_sha256'].items():
        assert hashlib.sha256(readonly_bytes(closed.ROOT, path)).hexdigest() == expected, path
