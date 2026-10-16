"""S07 expected ownership Red; S08 independent immutable Git preservation."""

import ast
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from compiler.staqex.runtime.evaluator import Evaluator
from tests import liss_0589_guard_support as capture


def successor():
    assert (capture.ROOT / capture.SUCCESSOR).is_file(), 'scalar capture successor not implemented'
    return importlib.import_module('compiler.staqex.runtime.evaluation.classical_scalars')


def test_s07_successor_owns_exact_algorithm_protocol_and_dependencies():
    module = successor()
    capture.assert_successor(Path(module.__file__).read_text())
    assert module.maybe_capture_classical_scalar.__module__ == module.__name__


def test_s07_old_body_absent_and_exact_class_assignment():
    tree = ast.parse((capture.ROOT / capture.EVALUATOR).read_text())
    assert not any(isinstance(n, ast.FunctionDef) and n.name == '_maybe_capture_classical_scalar'
                   for n in capture.owner(tree).body), 'old scalar capture body remains'
    capture.restore_capture_evaluator(tree)


def test_s07_actual_class_and_bound_instance_identity():
    function = successor().maybe_capture_classical_scalar
    assert Evaluator._maybe_capture_classical_scalar is function
    instance = Evaluator.__new__(Evaluator)
    assert instance._maybe_capture_classical_scalar.__func__ is function
    assert instance._maybe_capture_classical_scalar.__self__ is instance
    assert not isinstance(Evaluator.__dict__['_maybe_capture_classical_scalar'], (staticmethod, classmethod))


def test_s07_both_cold_requested_import_orders_and_actual_consumer_imports():
    successor()
    facade = 'compiler.staqex.runtime.evaluator'
    moved = 'compiler.staqex.runtime.evaluation.classical_scalars'
    for order in [(facade, moved), (moved, facade)]:
        code = (
            'import importlib\n'
            f'a=importlib.import_module({order[0]!r}); b=importlib.import_module({order[1]!r})\n'
            f'e=importlib.import_module({facade!r}); s=importlib.import_module({moved!r})\n'
            'assert e.Evaluator._maybe_capture_classical_scalar is s.maybe_capture_classical_scalar\n'
            'from compiler.staqex.runtime.evaluation import execution,observation\n'
            'from compiler.staqex.runtime.joint import Joint\n'
            'o=e.Evaluator.__new__(e.Evaluator); o.scalars={}\n'
            'assert o._maybe_capture_classical_scalar.__self__ is o\n'
            'assert o._maybe_capture_classical_scalar(Joint.unit().bind_const("x",2),"x") is None\n'
            'assert o.scalars=={"x":2.0}\n'
        )
        result = subprocess.run([sys.executable, '-c', code], cwd=capture.ROOT,
                                capture_output=True, text=True, timeout=30)
        assert result.returncode == 0, result.stdout + result.stderr


def evidence():
    fixture = capture.FIXTURE.parent / 'readonly-boundary.json'
    assert hashlib.sha256(fixture.read_bytes()).hexdigest() == (
        'e8ad62914008d2ad725c5f3f2aee04b6364ebb0dd658c55039ac4c331eeb9fe3'
    ), 'scalar readonly evidence changed'
    return json.loads(fixture.read_text())


def test_s08_original_whole_method_and_unaffected_evaluator_ast():
    recorded = evidence()
    assert recorded['base'] == 'f14a332c8f8e6aa9e6bc7b01403f5f89da6b6044'
    original = capture.original_method()
    assert hashlib.sha256(capture.dump(original).encode()).hexdigest() == recorded['original_ast_sha256']
    tree = capture.restore_capture_evaluator(ast.parse((capture.ROOT / capture.EVALUATOR).read_text()))
    assert hashlib.sha256(capture.dump(tree).encode()).hexdigest() == recorded['evaluator_ast_sha256']


def test_s08_all_39_readonly_sources_tests_and_fixtures():
    recorded = evidence()
    assert len(recorded['readonly_sha256']) == 39
    for path, expected in recorded['readonly_sha256'].items():
        assert hashlib.sha256((capture.ROOT / path).read_bytes()).hexdigest() == expected, path


@pytest.mark.parametrize('mutation', ['other-method', 'new-import', 'extra-state'])
def test_s08_whole_evaluator_guard_rejects_unrelated_changes(mutation):
    tree = ast.parse((capture.ROOT / capture.EVALUATOR).read_text())
    if mutation == 'other-method':
        fn = next(n for n in capture.owner(tree).body if isinstance(n, ast.FunctionDef) and n.name == '_lit')
        fn.body = [ast.Pass()]
    elif mutation == 'new-import':
        tree.body.append(ast.parse('import math').body[0])
    else:
        capture.owner(tree).body.append(ast.parse('extra_state = {}').body[0])
    restored = capture.restore_capture_evaluator(tree)
    assert hashlib.sha256(capture.dump(restored).encode()).hexdigest() != evidence()['evaluator_ast_sha256']
