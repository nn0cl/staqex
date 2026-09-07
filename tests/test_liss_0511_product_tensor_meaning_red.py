"""Phase 1 Red contracts for product/tensor meaning preservation."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex.backend.qasm.emitter import QASM3Emitter  # noqa: E402
from compiler.staqex.pipeline import compile_path  # noqa: E402


FIXTURE = REPO / "tests/fixtures/semantic_meaning/product_tensor.sqx"


def _compile_fixture():
    compiled = compile_path(FIXTURE)
    assert compiled.unit is not None, compiled.diagnostics
    assert compiled.scientific_semantic_ir is not None
    return compiled


def test_operator_and_tensor_have_distinct_canonical_meanings() -> None:
    compiled = _compile_fixture()
    nodes = compiled.scientific_semantic_ir.nodes
    operator_product = next(node for node in nodes if node.kind == "OpBin")
    tensor_product = next(node for node in nodes if node.kind == "TensorExpr")
    assert operator_product.meaning_kind == "mathematical_product"
    assert operator_product.product_kind == "operator_product"
    assert tensor_product.product_kind == "tensor_product"
    assert operator_product.product_kind != tensor_product.product_kind


def test_tensor_preserves_factor_order_identity_and_dimensions() -> None:
    compiled = _compile_fixture()
    tensor_product = next(
        node for node in compiled.scientific_semantic_ir.nodes if node.kind == "TensorExpr"
    )
    assert len(tensor_product.child_source_node_ids) == 2
    assert tensor_product.child_source_node_ids == tensor_product.children
    assert tensor_product.dimensions != "unknown"
    assert tensor_product.provenance.source_node_id == tensor_product.node_id


def test_nested_operator_product_preserves_source_grouping() -> None:
    compiled = _compile_fixture()
    products = [
        node
        for node in compiled.scientific_semantic_ir.nodes
        if node.kind == "OpBin" and node.product_kind == "operator_product"
    ]
    assert len(products) >= 2
    product_ids = {node.node_id for node in products}
    outer = next(node for node in products if any(child in product_ids for child in node.children))
    assert len(outer.child_source_node_ids) == 2
    assert any(child_id in {node.node_id for node in products} for child_id in outer.children)


def test_unsupported_non_unitary_product_projection_is_atomic() -> None:
    compiled = _compile_fixture()
    emitted = QASM3Emitter(route=False).emit_unit(
        compiled.unit, semantic_ir=compiled.scientific_semantic_ir
    )
    assert emitted.ok is False
    assert emitted.qasm == ""
    assert emitted.circuit is not None
    assert emitted.circuit.gates == []
    assert emitted.circuit.allocation_started is False


if __name__ == "__main__":
    for test in (
        test_operator_and_tensor_have_distinct_canonical_meanings,
        test_tensor_preserves_factor_order_identity_and_dimensions,
        test_nested_operator_product_preserves_source_grouping,
        test_unsupported_non_unitary_product_projection_is_atomic,
    ):
        test()
