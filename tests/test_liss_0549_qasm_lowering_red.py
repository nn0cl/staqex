"""Phase 1 Red contracts for QASM lowering decomposition."""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).parents[1]
PACKAGE = ROOT / "compiler" / "staqex" / "backend" / "qasm" / "lowering"
FACADE = ROOT / "compiler" / "staqex" / "backend" / "qasm" / "lower.py"


def _declared(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {
        node.name
        for node in tree.body
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
    }


def test_qasm_lowering_families_expose_named_owners() -> None:
    expected = {
        "profiles.py": ("EvolutionTargetProfile",),
        "preflight.py": (
            "qudit_capability_reject",
            "explicit_evolution_capability_reject",
            "formal_limit_capability_reject",
        ),
        "semantic.py": ("lower_semantic_to_circuit",),
        "ast_compat.py": ("lower_ast_compat",),
        "evolution.py": (
            "lower_explicit_evolve",
            "lower_formal_limit",
            "lower_evolve_under",
        ),
        "resources.py": ("register_resource_budget_reject",),
    }
    missing: list[str] = []
    for filename, symbols in expected.items():
        declared = _declared(PACKAGE / filename)
        missing.extend(f"{filename}:{symbol}" for symbol in symbols if symbol not in declared)
    assert not missing, f"missing QASM lowering owners: {missing}"


def test_qasm_lower_facade_does_not_retain_family_implementations() -> None:
    retained = _declared(FACADE) & {
        "qudit_capability_reject",
        "explicit_evolution_capability_reject",
        "formal_limit_capability_reject",
        "lower_unit_to_circuit",
        "lower_formal_limit",
        "lower_explicit_evolve",
        "register_resource_budget_reject",
        "_from_ast_patterns",
        "_from_dag",
    }
    assert not retained, f"lower facade retains implementation declarations: {sorted(retained)}"


def test_qasm_lowering_families_do_not_import_the_public_facade() -> None:
    offenders: list[str] = []
    if not PACKAGE.exists():
        offenders.append("<missing package>")
    for path in sorted(PACKAGE.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.level >= 3 and node.module == "lower":
                offenders.append(path.name)
            if isinstance(node, ast.Import) and any(
                alias.name == "compiler.staqex.backend.qasm.lower" for alias in node.names
            ):
                offenders.append(path.name)
    assert not offenders, f"internal lowering modules import the facade: {offenders}"


def test_canonical_lowering_precedes_allocation_and_ast_compatibility() -> None:
    preflight = (PACKAGE / "preflight.py").read_text(encoding="utf-8") if (PACKAGE / "preflight.py").is_file() else ""
    semantic = (PACKAGE / "semantic.py").read_text(encoding="utf-8") if (PACKAGE / "semantic.py").is_file() else ""
    ast_compat = (PACKAGE / "ast_compat.py").read_text(encoding="utf-8") if (PACKAGE / "ast_compat.py").is_file() else ""
    resources = (PACKAGE / "resources.py").read_text(encoding="utf-8") if (PACKAGE / "resources.py").is_file() else ""
    assert "def preflight" in preflight
    assert "ScientificSemanticIR" in semantic
    assert "diagnostic" in ast_compat.lower()
    assert "allocate" not in preflight.lower()
    assert "def register_resource_budget_reject" in resources
