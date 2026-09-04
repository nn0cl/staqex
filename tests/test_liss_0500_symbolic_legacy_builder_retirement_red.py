"""AT-TDD Phase 1 Red: LISS-0500 symbolic legacy-builder retirement."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex import symbolic_ir as symbolic_ir_module  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402


SOURCE = """
package liss0500
pub fn main() -> Unit {
    Operator H = X + Z
    State observed = Coin()
    Measure observed
}
"""


def _compiled():
    compiled = compile_source(SOURCE)
    assert compiled.unit is not None
    assert compiled.scientific_semantic_ir is not None
    return compiled


def test_symbolic_compatibility_view_does_not_call_legacy_ast_builder(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    compiled = _compiled()

    def legacy_builder_must_not_run(*args: object, **kwargs: object) -> object:
        raise AssertionError("symbolic compatibility must not rebuild from AST")

    monkeypatch.setattr(
        symbolic_ir_module, "_build_symbolic_ir_legacy", legacy_builder_must_not_run
    )
    symbolic_ir_module.build_symbolic_compatibility_view(
        compiled.scientific_semantic_ir, compiled.unit
    )


def test_symbolic_compatibility_view_conserves_canonical_identity() -> None:
    compiled = _compiled()
    view = symbolic_ir_module.build_symbolic_compatibility_view(
        compiled.scientific_semantic_ir, compiled.unit
    )

    assert view["authority"]["semantic_authority"] == "scientific_semantic_ir"
    assert view["resolved"]["canonical_source_node_ids"] == [
        node.node_id for node in compiled.scientific_semantic_ir.nodes
    ]


def test_symbolic_compatibility_view_has_no_finite_artifact() -> None:
    compiled = _compiled()
    view = symbolic_ir_module.build_symbolic_compatibility_view(
        compiled.scientific_semantic_ir, compiled.unit
    )

    assert "finite_plan" not in view["resolved"]
    assert "allocation" not in view["resolved"]


def test_explicit_legacy_api_remains_isolated() -> None:
    assert callable(symbolic_ir_module.build_symbolic_ir)
