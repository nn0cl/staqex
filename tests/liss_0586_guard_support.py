"""H09 exact Host projection. Original a661fb17 evaluator:421–462."""

import ast
import copy
import hashlib
from pathlib import Path

from tests.liss_0585_guard_support import remove_exact_import

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/liss_0586/original-host-method.txt"
INSTALLER = "install_host_coefficient_compatibility"
PRIVATE = "_install_host_coefficient_compatibility"
FUNCTION = "resolve_host_coefficient_arrays"
METHOD = "_resolve_host_coefficient_arrays"
SUCCESSOR = "compiler/staqex/runtime/evaluation/host_coefficients.py"


def dump(node):
    return ast.dump(node, include_attributes=False)


def original_method():
    source = FIXTURE.read_bytes()
    assert hashlib.sha256(source).hexdigest() == (
        "db4ab0b67131655cc42649fcbce5f8cf6cd8870bcba14a83ae9695aa70008ad8"
    ), "original Host evidence changed"
    method = ast.parse(source).body[0]
    # Dedenting the source removed four spaces inside the multiline docstring.
    # Restore that literal's original bytes for the historical whole-AST guard.
    method.body[0].value.value = method.body[0].value.value.replace("\n", "\n    ")
    return method


def restore_host_evaluator(tree):
    imported = remove_exact_import(tree, "evaluation.compatibility", INSTALLER, PRIVATE)
    calls = [n for n in tree.body if isinstance(n, ast.Expr)
             and isinstance(n.value, ast.Call) and isinstance(n.value.func, ast.Name)
             and n.value.func.id == PRIVATE]
    assert len(calls) <= 1, "duplicate Host setup"
    for call in calls:
        assert dump(call) == dump(ast.parse(f"{PRIVATE}(Evaluator)").body[0]), "wrong Host setup"
        tree.body.remove(call)
    assert imported == bool(calls), "incomplete Host setup"
    owner = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Evaluator")
    methods = [n for n in owner.body if isinstance(n, ast.FunctionDef) and n.name == METHOD]
    assert len(methods) <= 1, "duplicate Host body"
    if imported:
        assert not methods, "reintroduced Host body"
        anchor = next(n for n in owner.body if isinstance(n, ast.FunctionDef)
                      and n.name == "_require_uncompute_zero")
        owner.body.insert(owner.body.index(anchor), original_method())
    else:
        assert len(methods) == 1, "Host body missing without setup"
        assert dump(methods[0]) == dump(original_method()), "retained Host body changed"
    return tree


def restore_host_compatibility(tree):
    imported = remove_exact_import(tree, "host_coefficients", FUNCTION, None)
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == INSTALLER]
    assert len(functions) <= 1, "duplicate Host installer"
    expected = ast.parse(
        f"def {INSTALLER}(evaluator_type: type[Any]) -> None:\n"
        f"    evaluator_type.{METHOD} = {FUNCTION}\n"
    ).body[0]
    for function in functions:
        candidate = copy.deepcopy(function)
        if ast.get_docstring(candidate) is not None:
            candidate.body = candidate.body[1:]
        assert dump(candidate) == dump(expected), "wrong Host mapping"
        tree.body.remove(function)
    assert imported == bool(functions), "incomplete Host installer"
    return tree


def canonical_algorithm(function, receiver, *, moved):
    body = copy.deepcopy(function.body)
    if ast.get_docstring(function) is not None:
        body = body[1:]

    class Ownership(ast.NodeTransformer):
        def visit_Name(self, node):
            if node.id == receiver:
                node.id = "self"
            return node

        def visit_ImportFrom(self, node):
            if node.module in ("finite_binder", "scientific_input"):
                assert node.level == (3 if moved else 2), "wrong Host dependency location"
                node.level = 2
            return node

    return dump(Ownership().visit(ast.Module(body=body, type_ignores=[])))


def assert_successor_algorithm(source):
    tree = ast.parse(source)
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
    assert len(functions) == 1 and functions[0].name == FUNCTION, "wrong Host owner"
    function = functions[0]
    assert [a.arg for a in function.args.args] == ["context", "unit"]
    assert not function.decorator_list and not function.args.defaults
    assert not function.args.kwonlyargs and function.args.vararg is None and function.args.kwarg is None
    assert canonical_algorithm(function, "context", moved=True) == canonical_algorithm(
        original_method(), "self", moved=False
    ), "Host algorithm changed"
    protocols = [n for n in tree.body if isinstance(n, ast.ClassDef)]
    assert len(protocols) == 1 and protocols[0].name == "HostCoefficientContext"
    protocol = copy.deepcopy(protocols[0])
    if ast.get_docstring(protocol) is not None:
        protocol.body = protocol.body[1:]
    assert dump(protocol) == dump(ast.parse(
        "class HostCoefficientContext(Protocol):\n"
        "    host_input: HostInputPort | None\n"
    ).body[0]), "Host context must be declaration-only"
    assert not any(isinstance(n, (ast.Assign, ast.AnnAssign)) for n in tree.body)
    errors = [n for n in tree.body if isinstance(n, ast.ImportFrom)
              and any(a.name == "KernelDiagnosticError" for a in n.names)]
    assert len(errors) == 1 and dump(errors[0]) == dump(ast.parse(
        "from .errors import KernelDiagnosticError"
    ).body[0]), "Host diagnostic type must remain the shared error"
    assert all(isinstance(n, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.ClassDef))
               or isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)
               and isinstance(n.value.value, str) for n in tree.body)
    assert not any(isinstance(n, ast.ImportFrom) and (n.module or "").endswith("evaluator")
                   or isinstance(n, ast.Import) and any(a.name.endswith("evaluator") for a in n.names)
                   for n in ast.walk(tree)), "facade dependency cycle"
