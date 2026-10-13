"""P09 exact partial move projection; immutable b5ad7402 evidence only."""

import ast
import copy
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVALUATOR = "compiler/staqex/runtime/evaluator.py"
SUCCESSOR = "compiler/staqex/runtime/evaluation/partial_calls.py"
FIXTURE = ROOT / "tests/fixtures/liss_0587/original-partial.txt"
MODULE = "compiler.staqex.runtime.evaluator"
IMPORT = "from .evaluation.partial_calls import PartialValue, fill_partial as _fill_partial_successor"
HOOK = "_fill_partial = staticmethod(_fill_partial_successor)"


def dump(node):
    return ast.dump(node, include_attributes=False)


def original_nodes():
    source = FIXTURE.read_bytes()
    assert hashlib.sha256(source).hexdigest() == (
        "db5b998d921333b1bd5864227f239614ece3932b4fdb3425ef851e63ed75bec1"
    ), "original partial evidence changed"
    return ast.parse(source).body


def moved_function():
    function = copy.deepcopy(original_nodes()[1])
    function.name = "fill_partial"
    function.decorator_list = []
    return function


def assert_successor(source):
    """Exact dependency and body contract, not a permissive algorithm filter."""
    tree = ast.parse(source)
    if ast.get_docstring(tree) is not None:
        tree.body = tree.body[1:]
    expected = ast.parse(
        "from __future__ import annotations\n"
        "from dataclasses import dataclass\n"
        "from ...ast_nodes import Expr, Call, Var\n"
        "from .errors import KernelError\n"
    )
    expected.body.extend([original_nodes()[0], ast.parse(
        f"PartialValue.__module__ = {MODULE!r}"
    ).body[0], moved_function()])
    assert dump(tree) == dump(expected), "partial successor dependency/class/algorithm changed"


def owner(tree):
    return next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Evaluator")


def restore_partial_evaluator(tree):
    imports = [n for n in tree.body if isinstance(n, ast.ImportFrom)
               and n.module == "evaluation.partial_calls"]
    assert len(imports) <= 1, "duplicate partial import"
    cls = owner(tree)
    methods = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "_fill_partial"]
    hooks = [n for n in cls.body if isinstance(n, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == "_fill_partial" for t in n.targets)]
    types = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "PartialValue"]
    old_type, old_method = original_nodes()
    if imports:
        assert dump(imports[0]) == dump(ast.parse(IMPORT).body[0]), "wrong partial import"
        assert not methods and not types, "duplicate partial body/class"
        assert len(hooks) == 1 and dump(hooks[0]) == dump(ast.parse(HOOK).body[0]), "wrong partial static mapping"
        tree.body.remove(imports[0])
        anchor = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "MeasureResult")
        tree.body.insert(tree.body.index(anchor), old_type)
        cls.body[cls.body.index(hooks[0])] = old_method
    else:
        assert not hooks and len(methods) == len(types) == 1, "partial owner missing"
        assert dump(types[0]) == dump(old_type), "retained partial class changed"
        assert dump(methods[0]) == dump(old_method), "retained partial method changed"
    return tree


def assert_live_successor(directory):
    tree = ast.parse((directory / EVALUATOR).read_text())
    installed = any(isinstance(n, ast.ImportFrom) and n.module == "evaluation.partial_calls" for n in tree.body)
    if installed:
        assert (directory / SUCCESSOR).is_file(), "missing partial successor"
        assert_successor((directory / SUCCESSOR).read_text())


def make_shape(directory, extracted):
    """Test-only AST shape. Never installed in the actual source tree or imported."""
    tree = restore_partial_evaluator(ast.parse((directory / EVALUATOR).read_text()))
    target = directory / SUCCESSOR
    if extracted:
        old_type = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "PartialValue")
        tree.body[tree.body.index(old_type)] = ast.parse(IMPORT).body[0]
        cls = owner(tree)
        method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "_fill_partial")
        cls.body[cls.body.index(method)] = ast.parse(HOOK).body[0]
        successor = ast.parse(
            "from __future__ import annotations\n"
            "from dataclasses import dataclass\n"
            "from ...ast_nodes import Expr, Call, Var\n"
            "from .errors import KernelError\n"
        )
        successor.body.extend([copy.deepcopy(old_type), ast.parse(
            f"PartialValue.__module__ = {MODULE!r}"
        ).body[0], moved_function()])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(ast.unparse(ast.fix_missing_locations(successor)))
    elif target.exists():
        target.unlink()  # Exact copied successor under pytest's temporary directory.
    (directory / EVALUATOR).write_text(ast.unparse(ast.fix_missing_locations(tree)))


def assert_shape(directory, extracted):
    tree = ast.parse((directory / EVALUATOR).read_text())
    types = [n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "PartialValue"]
    methods = [n for n in owner(tree).body if isinstance(n, ast.FunctionDef) and n.name == "_fill_partial"]
    assert len(types) == len(methods) == (0 if extracted else 1)
    assert (directory / SUCCESSOR).is_file() == extracted
    restore_partial_evaluator(tree)
    assert_live_successor(directory)
