"""Phase 1 Red contracts for LISS-0550 secondary module decomposition."""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).parents[1]
COMPILER = ROOT / "compiler" / "staqex"
TARGETS = (
    COMPILER / "quantum_semantic_ir.py",
    COMPILER / "hir.py",
    COMPILER / "finite_binder.py",
    COMPILER / "ast_nodes.py",
    COMPILER / "pipeline.py",
)


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def test_secondary_public_facades_are_reviewably_small() -> None:
    """Each public compatibility module must be a thin facade, not a second implementation."""

    oversized = {
        str(path.relative_to(ROOT)): len(path.read_text(encoding="utf-8").splitlines())
        for path in TARGETS
        if len(path.read_text(encoding="utf-8").splitlines()) > 600
    }
    assert not oversized, f"oversized public facades remain: {oversized}"


def test_public_facades_do_not_define_model_families() -> None:
    """DTO and verifier classes must be owned by extracted internal modules."""

    class_owners = {
        str(path.relative_to(ROOT)): [node.name for node in _tree(path).body if isinstance(node, ast.ClassDef)]
        for path in TARGETS
    }
    assert not any(class_owners.values()), f"public modules still own classes: {class_owners}"


def test_pipeline_facade_does_not_own_compilation_orchestration() -> None:
    """Compilation sequencing belongs behind pipeline.py's public facade."""

    pipeline = _tree(COMPILER / "pipeline.py")
    owned = {
        node.name
        for node in pipeline.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name in {"compile_source", "compile_path"}
    }
    assert not owned, f"pipeline facade still owns orchestration: {sorted(owned)}"


def test_advisory_structure_report_is_available() -> None:
    """The decomposition must ship a deterministic, initially advisory report."""

    report = ROOT / "scripts" / "report-module-structure.py"
    assert report.is_file(), "missing advisory module-structure report"
    text = report.read_text(encoding="utf-8")
    assert "advisory" in text.lower()
    assert "import" in text.lower() and "cycle" in text.lower()
