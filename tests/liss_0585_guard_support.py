"""T09 test-only exact Tensor extraction projection; no future-move exemption.

Original method evidence: main a349a5b720c59f3a0e288c4751dd012c25514843,
compiler/staqex/runtime/evaluator.py:502–546, dedented, newline-terminated.
Historical 0583/0584 fixtures remain the authority for all unaffected AST/bytes.
"""

import ast
import copy
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/liss_0585/original-tensor-method.txt"
INSTALLER = "install_tensor_binding_compatibility"
PRIVATE = "_install_tensor_binding_compatibility"


def original_method():
    source = FIXTURE.read_bytes()
    assert hashlib.sha256(source).hexdigest() == (
        "8fc41a4cfb69c3dfca1c6f5b29a9eef8f764dc862d65ed32f74173a9ade0cb0f"
    ), "original tensor evidence changed"
    return ast.parse(source).body[0]


def remove_exact_import(tree, module, name, alias):
    found = []
    for node in list(tree.body):
        if not isinstance(node, ast.ImportFrom):
            continue
        for item in list(node.names):
            if item.name != name:
                continue
            assert (node.module, node.level, item.asname) == (module, 1, alias)
            found.append(item)
            node.names.remove(item)
        if not node.names:
            tree.body.remove(node)
    assert len(found) <= 1, "duplicate tensor import"
    return bool(found)


def restore_tensor_evaluator(tree):
    imported = remove_exact_import(tree, "evaluation.compatibility", INSTALLER, PRIVATE)
    calls = [n for n in tree.body if isinstance(n, ast.Expr)
             and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name)
             and n.value.func.id == PRIVATE]
    assert len(calls) <= 1, "duplicate tensor setup"
    for call in calls:
        assert ast.dump(call, include_attributes=False) == ast.dump(
            ast.parse(f"{PRIVATE}(Evaluator)").body[0], include_attributes=False
        ), "wrong tensor setup"
        tree.body.remove(call)
    assert imported == bool(calls), "incomplete tensor wiring"
    owner = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Evaluator")
    methods = [n for n in owner.body if isinstance(n, ast.FunctionDef) and n.name == "_bind_tensor"]
    assert len(methods) <= 1, "duplicate tensor body"
    if imported:
        assert not methods, "reintroduced tensor body"
        anchor = next(n for n in owner.body if isinstance(n, ast.FunctionDef) and n.name == "_eval_times")
        owner.body.insert(owner.body.index(anchor), original_method())
    else:
        assert len(methods) == 1, "tensor body removed without wiring"
    return tree


def restore_tensor_compatibility(tree):
    imported = remove_exact_import(tree, "tensor_binding", "bind_tensor", None)
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == INSTALLER]
    assert len(functions) <= 1, "duplicate tensor installer"
    expected = ast.parse(
        f"def {INSTALLER}(evaluator_type: type[Any]) -> None:\n"
        "    evaluator_type._bind_tensor = bind_tensor\n"
    ).body[0]
    for function in functions:
        candidate = copy.deepcopy(function)
        if ast.get_docstring(candidate) is not None:
            candidate.body = candidate.body[1:]
        assert ast.dump(candidate, include_attributes=False) == ast.dump(
            expected, include_attributes=False
        ), "wrong tensor mapping"
        tree.body.remove(function)
    assert imported == bool(functions), "incomplete tensor installer"
    return tree


def canonical_algorithm(function, receiver):
    """Only receiver spelling, docstring and relative Joint import may differ."""
    body = copy.deepcopy(function.body)
    if isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
        assert isinstance(body[0].value.value, str)
        body = body[1:]

    class Receiver(ast.NodeTransformer):
        def visit_Name(self, node):
            if node.id == receiver:
                node.id = "self"
            return node

        def visit_ImportFrom(self, node):
            if node.module == "joint":
                assert node.level in (1, 2)
                node.level = 1
            return node

    return ast.dump(Receiver().visit(ast.Module(body=body, type_ignores=[])),
                    include_attributes=False)


def assert_successor_algorithm(source):
    tree = ast.parse(source)
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "bind_tensor"]
    assert len(functions) == 1, "missing/duplicate tensor successor"
    function = functions[0]
    assert [a.arg for a in function.args.args] == ["context", "joint", "names", "expr"]
    assert not function.decorator_list
    assert canonical_algorithm(function, "context") == canonical_algorithm(original_method(), "self")
    assert not any(isinstance(n, ast.ClassDef) for n in tree.body)
    assert not any(isinstance(n, (ast.Assign, ast.AnnAssign)) for n in tree.body)
