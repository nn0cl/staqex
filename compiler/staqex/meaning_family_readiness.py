"""Small, provider-neutral meaning-family readiness boundary.

This module implements only the reviewed Product/Tensor rejection slice for
LISS-0457.  Other meaning families remain explicitly outside this Green
increment until their own contracts are approved.
"""

from __future__ import annotations

from dataclasses import dataclass

from .pipeline import compile_source


@dataclass(frozen=True, slots=True)
class MeaningFamilyDecision:
    """Observable, artifact-free result of a QPU readiness classification."""

    family: str
    semantic_role: str
    status: str
    code: str | None
    reason: str
    source_id: str
    artifact: object | None
    rewritten_as_unitary: bool
    numerical_method: str | None
    provider_mapping: str | None
    qasm: str | None
    terminal_measurement_is_not_dynamic: bool


def _contains_non_unitary_product(source: str) -> bool:
    """Read the product meaning from the canonical Scientific Semantic IR."""

    compiled = compile_source(source)
    if not compiled.ok or compiled.scientific_semantic_ir is None:
        return False

    nodes = {
        node.node_id: node for node in compiled.scientific_semantic_ir.nodes
    }
    for node in nodes.values():
        if node.meaning_kind != "mathematical_product":
            continue
        child_kinds = {
            nodes[child_id].kind
            for child_id in node.children
            if child_id in nodes
        }
        if {"OpLit", "OpPauli"}.issubset(child_kinds):
            return True
    return False


def _non_unitary_product_rejection(source_id: str) -> MeaningFamilyDecision:
    """Build the stable, artifact-free rejection for this bounded slice."""

    return MeaningFamilyDecision(
        family="product/tensor",
        semantic_role="product/tensor",
        status="rejected",
        code="E_QPU_UNSUPPORTED_CAPABILITY",
        reason="non_unitary_target",
        source_id=source_id,
        artifact=None,
        rewritten_as_unitary=False,
        numerical_method=None,
        provider_mapping=None,
        qasm=None,
        terminal_measurement_is_not_dynamic=True,
    )


def classify_for_qpu(source: str, *, source_id: str) -> MeaningFamilyDecision:
    """Classify the currently accepted non-unitary Product/Tensor boundary.

    The source text is compiled only to obtain the canonical Scientific
    Semantic IR; classification is based on its meaning and node structure.
    No target artifact or provider operation is created by this function.
    """

    if _contains_non_unitary_product(source):
        return _non_unitary_product_rejection(source_id)

    raise ValueError("unsupported meaning family")
