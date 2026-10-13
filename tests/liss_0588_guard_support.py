"""C09 test-only exact restoration; immutable main AST, never a runtime owner."""

import ast
import copy
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATOR = 'compiler/staqex/runtime/evaluator.py'
SUCCESSOR = 'compiler/staqex/runtime/evaluation/closed_expressions.py'
FIXTURE = ROOT / 'tests/fixtures/liss_0588/original-closed.txt'
IMPORT = 'from .evaluation.closed_expressions import is_closed as _is_closed_successor'
HOOK = '_is_closed = _is_closed_successor'
HEADER = '''from __future__ import annotations
from typing import Any, Mapping, Protocol
from ...ast_nodes import Expr, LitInt, LitFloat, LitBool, LitString, Var, Attr, UnitConvert, BinOp

class ClosedExpressionContext(Protocol):
    scalars: Mapping[str, Any]
    objects: Mapping[str, Any]
    def _is_closed(self, expr: Expr) -> bool: ...
'''


def dump(node):
    return ast.dump(node, include_attributes=False)


def original_method():
    source = FIXTURE.read_bytes()
    assert hashlib.sha256(source).hexdigest() == (
        '44f5bbc8d79d11b3618f910da60e8172b2480c836d6572191f3df838db03625a'
    ), 'original closed evidence changed'
    return ast.parse(source).body[0]


def moved_function():
    method = copy.deepcopy(original_method())
    method.name = 'is_closed'
    method.args.args[0] = ast.arg(arg='context', annotation=ast.Name(id='ClosedExpressionContext', ctx=ast.Load()))

    class Move(ast.NodeTransformer):
        def visit_Name(self, node):
            if node.id == 'self':
                node.id = 'context'
            return node

        def visit_ImportFrom(self, node):
            assert node.module == 'dimensions' and node.level == 2
            node.level = 3
            return node

    return Move().visit(method)


def proposed_tree():
    tree = ast.parse(HEADER)
    tree.body.append(moved_function())
    return ast.fix_missing_locations(tree)


def assert_successor(source):
    tree = ast.parse(source)
    if ast.get_docstring(tree) is not None:
        tree.body = tree.body[1:]
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and ast.get_docstring(node) is not None:
            node.body = node.body[1:]
    assert dump(tree) == dump(proposed_tree()), 'closed successor algorithm/protocol/dependency changed'


def owner(tree):
    return next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Evaluator')


def restore_closed_evaluator(tree):
    imports = [n for n in tree.body if isinstance(n, ast.ImportFrom) and n.module == 'evaluation.closed_expressions']
    cls = owner(tree)
    methods = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == '_is_closed']
    hooks = [n for n in cls.body if isinstance(n, (ast.Assign, ast.AnnAssign))
             and any(isinstance(t, ast.Name) and t.id == '_is_closed'
                     for t in (n.targets if isinstance(n, ast.Assign) else [n.target]))]
    assert len(imports) <= 1, 'duplicate closed import'
    if imports:
        assert dump(imports[0]) == dump(ast.parse(IMPORT).body[0]), 'wrong closed import'
        assert not methods, 'duplicate closed body'
        assert len(hooks) == 1 and dump(hooks[0]) == dump(ast.parse(HOOK).body[0]), 'wrong closed hook'
        tree.body.remove(imports[0])
        cls.body[cls.body.index(hooks[0])] = original_method()
    else:
        assert not hooks and len(methods) == 1, 'closed owner missing'
        assert dump(methods[0]) == dump(original_method()), 'retained closed method changed'
    return tree


def assert_live_successor(directory):
    tree = ast.parse((directory / EVALUATOR).read_text())
    installed = any(isinstance(n, ast.ImportFrom) and n.module == 'evaluation.closed_expressions' for n in tree.body)
    if installed:
        assert (directory / SUCCESSOR).is_file(), 'missing closed successor'
        assert_successor((directory / SUCCESSOR).read_text())


def make_shape(directory, extracted):
    """AST-only proposal in copied pytest root; never imported or installed."""
    assert directory.resolve() != ROOT.resolve(), 'temporary roots only'
    tree = restore_closed_evaluator(ast.parse((directory / EVALUATOR).read_text()))
    target = directory / SUCCESSOR
    if extracted:
        tree.body.insert(1, ast.parse(IMPORT).body[0])
        cls = owner(tree)
        method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == '_is_closed')
        cls.body[cls.body.index(method)] = ast.parse(HOOK).body[0]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(ast.unparse(proposed_tree()))
    elif target.exists():
        target.unlink()  # Exact copied file in this pytest temporary root.
    (directory / EVALUATOR).write_text(ast.unparse(ast.fix_missing_locations(tree)))


def assert_shape(directory, extracted):
    tree = ast.parse((directory / EVALUATOR).read_text())
    methods = [n for n in owner(tree).body if isinstance(n, ast.FunctionDef) and n.name == '_is_closed']
    assert len(methods) == (0 if extracted else 1)
    assert (directory / SUCCESSOR).is_file() == extracted
    restore_closed_evaluator(tree)
    assert_live_successor(directory)
