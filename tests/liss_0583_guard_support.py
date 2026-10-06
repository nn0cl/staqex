"""Test-only F08 projection: permit exactly the reviewed foreach extraction."""

import ast
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/liss_0583/guard-baseline.json"
INSTALLER = "install_static_foreach_compatibility"
PRIVATE_INSTALLER = "_install_static_foreach_compatibility"


def digest(node: ast.AST) -> str:
    return hashlib.sha256(ast.dump(node, include_attributes=False).encode()).hexdigest()


def baseline() -> dict:
    assert hashlib.sha256(FIXTURE.read_bytes()).hexdigest() == (
        "9cca28c93d06df68081ea2a3c01a54d07a9222aa2dcb002d3948c44325b66dd0"
    ), "Phase 1 baseline fixture changed"
    return json.loads(FIXTURE.read_text())


def _remove_import(tree: ast.Module, module: str, level: int, name: str, alias: str | None) -> None:
    removed = 0
    for node in list(tree.body):
        if not isinstance(node, ast.ImportFrom):
            continue
        for item in list(node.names):
            if item.name != name:
                continue
            assert (node.module, node.level, item.asname) == (module, level, alias)
            removed += 1
            node.names.remove(item)
        if not node.names:
            tree.body.remove(node)
    assert removed <= 1, "duplicate foreach import"


def evaluator_projection(source: str, *, imports_only: bool = False) -> ast.Module:
    tree = ast.parse(source)
    _remove_import(tree, "evaluation.compatibility", 1, INSTALLER, PRIVATE_INSTALLER)
    if imports_only:
        tree.body = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
        return tree
    evaluator = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Evaluator")
    methods = [n for n in evaluator.body if isinstance(n, ast.FunctionDef) and n.name == "_run_foreach"]
    assert len(methods) <= 1
    for method in methods:
        assert digest(method) == baseline()["old_foreach_ast"], "retained foreach body changed"
        evaluator.body.remove(method)
    calls = [n for n in tree.body if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
             and isinstance(n.value.func, ast.Name) and n.value.func.id == PRIVATE_INSTALLER]
    assert len(calls) <= 1
    expected = ast.parse(f"{PRIVATE_INSTALLER}(Evaluator)").body[0]
    for call in calls:
        assert digest(call) == digest(expected), "invalid foreach installer setup"
        tree.body.remove(call)
    return tree


def compatibility_projection(source: str) -> ast.Module:
    tree = ast.parse(source)
    _remove_import(tree, "static_foreach", 1, "execute_static_foreach", None)
    installers = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == INSTALLER]
    assert len(installers) <= 1
    expected = ast.parse(
        f"def {INSTALLER}(evaluator_type: type[Any]) -> None:\n"
        "    evaluator_type._run_foreach = execute_static_foreach\n"
    ).body[0]
    for installer in installers:
        candidate = copy.deepcopy(installer)
        if ast.get_docstring(candidate) is not None:
            candidate.body = candidate.body[1:]
        assert digest(candidate) == digest(expected), "invalid foreach hook mapping"
        tree.body.remove(installer)
    return tree


def assert_evaluator_preserved(source: str, *, imports_only: bool = False) -> None:
    key = "evaluator_imports" if imports_only else "evaluator_unaffected_ast"
    assert digest(evaluator_projection(source, imports_only=imports_only)) == baseline()[key]


def assert_compatibility_preserved(source: str) -> None:
    assert digest(compatibility_projection(source)) == baseline()["compatibility_unaffected_ast"]


def context_projection(source: str) -> ast.Module:
    tree = ast.parse(source)
    protocol = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "EvaluatorContext")
    allowed = ast.parse(
        "static_register_sizes: Mapping[str, int]\n"
        "def _run_foreach(self, joint: Any, stmt: Any) -> Any: ...\n"
    ).body
    counts = {"static_register_sizes": 0, "_run_foreach": 0}
    for node in list(protocol.body):
        name = node.name if isinstance(node, ast.FunctionDef) else (
            node.target.id if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) else None
        )
        if name not in counts:
            continue
        expected = allowed[0 if name == "static_register_sizes" else 1]
        assert digest(node) == digest(expected), "context addition is not a declaration"
        counts[name] += 1
        protocol.body.remove(node)
    assert all(count <= 1 for count in counts.values())
    return tree
