"""Phase 1 Red contracts for Scientific Semantic IR decomposition."""

from __future__ import annotations

import ast
from importlib.util import find_spec
from pathlib import Path


ROOT = Path(__file__).parents[1]
PACKAGE = ROOT / "compiler" / "staqex" / "scientific_semantic"
FACADE = ROOT / "compiler" / "staqex" / "scientific_semantic_ir.py"


def test_scientific_semantic_families_expose_named_owners() -> None:
    expected = {
        "model": (
            "ScientificSemanticIR",
            "SemanticNode",
            "SemanticRelation",
            "CanonicalQpuProjection",
            "FiniteRealizationRecord",
        ),
        "fingerprint": ("semantic_fingerprint",),
        "builder": (
            "build_scientific_semantic_ir",
            "build_inspection",
            "build_rejection",
        ),
        "runtime_plan": ("build_runtime_execution_plan",),
        "qpu_projection": (
            "build_qpu_projection",
            "build_lowering_policy",
            "build_explicit_evolution",
        ),
        "realization": (
            "build_algorithm_plan",
            "build_finite_realization_record",
        ),
    }

    missing: list[str] = []
    for module_name, symbols in expected.items():
        module_path = PACKAGE / f"{module_name}.py"
        if find_spec(f"compiler.staqex.scientific_semantic.{module_name}") is None:
            missing.append(f"{module_name}:module")
            continue
        source = module_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        declared = {
            node.name
            for node in tree.body
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
        }
        missing.extend(
            f"{module_name}:{symbol}"
            for symbol in symbols
            if symbol not in declared
        )
    assert not missing, f"missing Scientific Semantic IR owners: {missing}"


def test_scientific_semantic_facade_does_not_retain_family_implementations() -> None:
    tree = ast.parse(FACADE.read_text(encoding="utf-8"))
    declarations = {
        node.name
        for node in tree.body
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
    }
    retained = declarations & {
        "CanonicalQpuOperation",
        "CanonicalQpuProjection",
        "SemanticProvenance",
        "SemanticNode",
        "SemanticRelation",
        "ScientificSemanticIR",
        "semantic_fingerprint",
        "build_scientific_semantic_ir",
        "build_runtime_execution_plan",
        "build_algorithm_plan",
    }
    assert not retained, f"facade retains implementation declarations: {sorted(retained)}"


def test_scientific_semantic_families_do_not_import_the_public_facade() -> None:
    if not PACKAGE.exists():
        offenders = ["<missing package>"]
    else:
        offenders = []
        for path in sorted(PACKAGE.glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module == "..scientific_semantic_ir":
                    offenders.append(path.name)
                if isinstance(node, ast.Import) and any(
                    alias.name == "compiler.staqex.scientific_semantic_ir"
                    for alias in node.names
                ):
                    offenders.append(path.name)
    assert not offenders, f"internal semantic modules import the facade: {offenders}"


def test_canonical_build_and_projection_ownership_is_explicit() -> None:
    expected_sources = {
        "builder.py": ("build_scientific_semantic_ir",),
        "runtime_plan.py": ("build_runtime_execution_plan",),
        "qpu_projection.py": ("build_qpu_projection",),
        "realization.py": ("build_finite_realization_record",),
    }
    missing: list[str] = []
    for filename, symbols in expected_sources.items():
        source = (
            (PACKAGE / filename).read_text(encoding="utf-8")
            if (PACKAGE / filename).exists()
            else ""
        )
        for symbol in symbols:
            if f"def {symbol}" not in source:
                missing.append(f"{filename}:{symbol}")
    assert not missing, f"canonical ownership is not explicit: {missing}"
