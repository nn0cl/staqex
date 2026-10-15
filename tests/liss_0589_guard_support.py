"""S09 exact test-only reconstruction; never a production implementation."""

import ast
import copy
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATOR = 'compiler/staqex/runtime/evaluator.py'
SUCCESSOR = 'compiler/staqex/runtime/evaluation/classical_scalars.py'
FIXTURE = ROOT / 'tests/fixtures/liss_0589/original-capture.txt'
IMPORT = 'from .evaluation.classical_scalars import maybe_capture_classical_scalar as _capture_classical_scalar_successor'
HOOK = '_maybe_capture_classical_scalar = _capture_classical_scalar_successor'
HEADER = '''from __future__ import annotations
from fractions import Fraction
from typing import MutableMapping, Protocol
from ..joint import Joint

class ClassicalScalarContext(Protocol):
    scalars: MutableMapping[str, float | Fraction]
'''


def dump(node):
    return ast.dump(node, include_attributes=False)


def original_method():
    source = FIXTURE.read_bytes()
    assert hashlib.sha256(source).hexdigest() == (
        '5f0baa2b3f721b87f4887c5e97e48f39c4c01a3e4e256f41e318f350a5a9f816'
    ), 'original scalar capture evidence changed'
    return ast.parse('class Evaluator:\n' + source.decode()).body[0].body[0]


def proposed_tree():
    tree = ast.parse(HEADER)
    method = copy.deepcopy(original_method())
    method.name = 'maybe_capture_classical_scalar'
    method.args.args[0] = ast.arg(
        arg='context', annotation=ast.Name(id='ClassicalScalarContext', ctx=ast.Load())
    )

    class Receiver(ast.NodeTransformer):
        def visit_Name(self, node):
            if node.id == 'self':
                node.id = 'context'
            return node

    tree.body.append(Receiver().visit(method))
    return ast.fix_missing_locations(tree)


def assert_successor(source):
    tree = ast.parse(source)
    if ast.get_docstring(tree) is not None:
        tree.body = tree.body[1:]
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and ast.get_docstring(node) is not None:
            node.body = node.body[1:]
    assert dump(tree) == dump(proposed_tree()), 'scalar capture algorithm/protocol/dependency changed'


def owner(tree):
    return next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Evaluator')


def restore_capture_evaluator(tree):
    imports = [n for n in tree.body if isinstance(n, ast.ImportFrom)
               and n.module == 'evaluation.classical_scalars']
    cls = owner(tree)
    methods = [n for n in cls.body if isinstance(n, ast.FunctionDef)
               and n.name == '_maybe_capture_classical_scalar']
    hooks = [n for n in cls.body if isinstance(n, (ast.Assign, ast.AnnAssign))
             and any(isinstance(t, ast.Name) and t.id == '_maybe_capture_classical_scalar'
                     for t in (n.targets if isinstance(n, ast.Assign) else [n.target]))]
    assert len(imports) <= 1, 'duplicate scalar capture import'
    if imports:
        assert dump(imports[0]) == dump(ast.parse(IMPORT).body[0]), 'wrong scalar capture import'
        assert not methods, 'duplicate scalar capture body'
        assert len(hooks) == 1 and dump(hooks[0]) == dump(ast.parse(HOOK).body[0]), 'wrong scalar capture hook'
        tree.body.remove(imports[0])
        cls.body[cls.body.index(hooks[0])] = original_method()
    else:
        assert not hooks and len(methods) == 1, 'scalar capture owner missing'
        assert dump(methods[0]) == dump(original_method()), 'retained scalar capture changed'
    return tree


def assert_live_successor(directory):
    tree = ast.parse((directory / EVALUATOR).read_text())
    installed = any(isinstance(n, ast.ImportFrom) and n.module == 'evaluation.classical_scalars'
                    for n in tree.body)
    if installed:
        assert (directory / SUCCESSOR).is_file(), 'missing scalar capture successor'
        assert_successor((directory / SUCCESSOR).read_text())


def make_shape(directory, extracted):
    """Only AST proposals in explicit pytest copies; never import this proposal."""
    assert directory.resolve() != ROOT.resolve(), 'temporary roots only'
    tree = restore_capture_evaluator(ast.parse((directory / EVALUATOR).read_text()))
    target = directory / SUCCESSOR
    if extracted:
        tree.body.insert(1, ast.parse(IMPORT).body[0])
        cls = owner(tree)
        method = next(n for n in cls.body if isinstance(n, ast.FunctionDef)
                      and n.name == '_maybe_capture_classical_scalar')
        cls.body[cls.body.index(method)] = ast.parse(HOOK).body[0]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(ast.unparse(proposed_tree()))
    elif target.exists():
        target.unlink()  # Exact file in the pytest temporary copy only.
    (directory / EVALUATOR).write_text(ast.unparse(ast.fix_missing_locations(tree)))


def assert_shape(directory, extracted):
    tree = ast.parse((directory / EVALUATOR).read_text())
    methods = [n for n in owner(tree).body if isinstance(n, ast.FunctionDef)
               and n.name == '_maybe_capture_classical_scalar']
    assert len(methods) == (0 if extracted else 1)
    assert (directory / SUCCESSOR).is_file() == extracted
    restore_capture_evaluator(tree)
    assert_live_successor(directory)
