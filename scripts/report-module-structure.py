#!/usr/bin/env python3
"""Print an advisory source-size and import-cycle inventory.

This report is intentionally advisory. It does not make a line-count threshold
blocking and does not replace the project's architectural review.
"""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).parents[1]


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    result: set[str] = set()
    module = "compiler." + ".".join(path.relative_to(ROOT / "compiler").with_suffix("").parts)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                package = module.split(".")[:-1]
                package = package[: -(node.level - 1)] if node.level > 1 else package
                imported = ".".join((*package, *(node.module or "").split(".")))
                result.add(imported.rstrip("."))
            elif node.module:
                result.add(node.module)
    return result


def _cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    cycles: list[list[str]] = []
    visiting: list[str] = []
    active: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in active:
            start = visiting.index(node)
            cycles.append([*visiting[start:], node])
            return
        if node in visited:
            return
        active.add(node)
        visiting.append(node)
        for dependency in sorted(graph.get(node, ())):
            if dependency in graph:
                visit(dependency)
        visiting.pop()
        active.remove(node)
        visited.add(node)

    for node in sorted(graph):
        visit(node)
    return cycles


def main() -> int:
    paths = sorted((ROOT / "compiler").rglob("*.py"))
    graph = {
        "compiler." + ".".join(path.relative_to(ROOT / "compiler").with_suffix("").parts):
        _imports(path)
        for path in paths
    }
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        classes = sum(isinstance(node, ast.ClassDef) for node in ast.walk(tree))
        functions = sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            for node in ast.walk(tree)
        )
        lines = len(path.read_text(encoding="utf-8").splitlines())
        print(f"{path.relative_to(ROOT)} lines={lines} classes={classes} functions={functions}")
    cycles = _cycles(graph)
    print("advisory import cycle inventory:")
    if not cycles:
        print("  cycles=none")
    else:
        for cycle in cycles:
            print("  cycle=" + " -> ".join(cycle))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
