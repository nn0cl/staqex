"""LISS-0479 / WP-0120 Phase 1 Red coverage contracts."""

from __future__ import annotations

from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex.codegen_qasm import OpenQASM3Generator
from compiler.staqex.pipeline import compile_path


SPEC = REPO / "docs/specs/staqex-real-qpu-readiness-acceptance.md"
ISSUE = REPO / "docs/issues/LISS-0479-residual-semantic-family-matrix.md"
PRODUCT = REPO / "tests/fixtures/semantic_meaning/mixture_and_product.sqx"
INTERFERENCE = REPO / "tests/fixtures/semantic_meaning/interfer_phase_branch.sqx"
DYNAMIC = REPO / "tests/fixtures/semantic_core/dynamic_measurement.sqx"


def test_every_matrix_row_has_required_readiness_fields() -> None:
    text = SPEC.read_text(encoding="utf-8") + ISSUE.read_text(encoding="utf-8")
    for required in (
        "Product/tensor",
        "Continuous/open-system",
        "Terminal measurement",
        "Dynamic measurement",
        "Interfer/phase/branch",
        "Observation projection",
        "Semantic role",
        "Finite boundary",
        "Rejection code",
        "Exit evidence",
        "ready",
        "reject",
        "defer",
    ):
        assert required in text


def test_deferred_product_family_retains_meaning_and_emits_no_artifact() -> None:
    compiled = compile_path(PRODUCT)
    assert compiled.scientific_semantic_ir is not None
    emitted = OpenQASM3Generator(route=False).generate_detailed(
        compiled.unit,
        semantic_ir=compiled.scientific_semantic_ir,
    )
    assert not emitted.ok
    assert emitted.circuit is not None
    assert emitted.circuit.reject_code == "E_QPU_CANONICAL_PROJECTION_UNAVAILABLE"
    assert emitted.qasm == ""
    assert emitted.circuit.gates == []
    assert emitted.circuit.allocation_started is False


def test_deferred_interference_family_remains_inspectable() -> None:
    compiled = compile_path(INTERFERENCE)
    assert compiled.semantic_inspection is not None
    assert compiled.semantic_inspection.structural_tree
    assert compiled.scientific_semantic_ir is not None
    assert any(
        node.meaning_kind in {"phase", "interference"}
        for node in compiled.scientific_semantic_ir.nodes
    )


def test_terminal_and_dynamic_measurement_are_distinct_rows() -> None:
    matrix = SPEC.read_text(encoding="utf-8").lower()
    dynamic = compile_path(DYNAMIC)
    assert "terminal measurement" in matrix
    assert "dynamic measurement" in matrix
    assert dynamic.scientific_semantic_ir is not None
    assert dynamic.semantic_inspection is not None


def test_observation_projection_row_has_a_reachable_fixture() -> None:
    fixture = REPO / "tests/fixtures/semantic_meaning/observation_projection.sqx"
    assert fixture.is_file()
