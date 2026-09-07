# LISS-0511: Product/Tensor Meaning Preservation

| Field | Value |
|---|---|
| Status | **proposed — design intake; Phase 1 Red not approved** |
| Type / priority | architecture / P0 |
| WorkPlan | [WP-0128](../work-plans/WP-0128-product-tensor-meaning-preservation.md) |
| Specification | [Product/Tensor Meaning Preservation](../specs/staqex-semantic-ir-product-tensor-preservation.md) |
| Parent | [WP-0113](../work-plans/WP-0113-semantic-ir-meaning-preservation.md) |
| Authority | ADR 0211; ADR 0212 |

## Objective

Define and verify a canonical Scientific Semantic IR boundary that preserves
operator products, tensor products, grouping, factor order, carrier/dimension
information, and non-unitary mathematical meaning before any target projection.

## Approved design scope

This design separates three meanings that must not be collapsed:

- operator multiplication and its source grouping;
- tensor products and their ordered factors;
- ideal non-unitary products that may be inspectable but not QPU-executable.

The scope does not authorize implementation. Phase 1 Red requires a separate
typed approval after the Spec/WP review.

## Acceptance boundary

- Real source is the authority for operand identity and grouping.
- Canonical IR is the authority for semantic product/tensor structure.
- Simulator/inspection may consume ideal meaning without finiteization.
- Unsupported finite/QPU projection fails closed before allocation and emits no
  artifact.
- Provenance, exactness, carrier, dimensions, role, and source node identity
  survive every accepted projection.

## Exclusions

Provider SDKs, live QPU execution, AWS credentials/network, Rust migration,
solver work, tensor-network storage, numerical approximation, syntax redesign,
and gate synthesis are excluded.

## Required review questions

1. Does the proposed contract distinguish operator and tensor products without
   making either a compatibility DTO authoritative?
2. Is source grouping preserved, or is every normalization rule explicit and
   testable?
3. Are tensor factor order and dimensions retained through the canonical IR?
4. Can ideal non-unitary products be inspected without a finite/QPU artifact?
5. Are rejection and provenance atomic when a target cannot realize the product?

## Gate

Request: Architecture/Scope approval for the design, followed separately by
Phase 1 Red approval. Implementation permission: none. Post-review:
independent review must return READY before any Phase 2 Green request.

