# LISS-0511: Product/Tensor Meaning Preservation

| Field | Value |
|---|---|
| Status | **Phase 2 Green bounded slice complete — Phase 3 not approved** |
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

## Phase 1 Red result

- Added `tests/fixtures/semantic_meaning/product_tensor.sqx` with grouped
  operator multiplication and a two-factor state tensor.
- Added `tests/test_liss_0511_product_tensor_meaning_red.py` with four
  acceptance contracts for distinct meanings, factor identity/dimensions,
  source grouping, and atomic unsupported projection.
- Verification: **4 failed, 0 passed**, no collection errors; `py_compile`
  and `git diff --check` passed.
- The failures are intentional migration gaps: `OpBin` is still classified as
  `mathematical_product`, `TensorExpr` lacks direct factor identity/dimension
  metadata, grouped product structure is not exposed as a canonical contract,
  and the fixture still reaches a QPU circuit instead of failing closed.
- No production code, fallback, lowering, provider, network, or QPU execution
  was changed.

## Gate

Phase 1 Red approval: granted by user on 2026-09-07. Implementation permission:
granted by user on 2026-09-07 for the bounded slice below. Phase 3 refactor,
broader product/tensor realization, and provider work are not approved.
Post-review: independent review must return READY before Phase 3 or any
broader consumer migration request.

## Phase 2 Green result

- `ScientificSemanticIR.SemanticNode` now records `product_kind` separately
  from the existing `meaning_kind`, preserving the compatibility value
  `mathematical_product` while distinguishing `operator_product` and
  `tensor_product`.
- Operator and tensor nodes retain direct child source IDs; tensor nodes expose
  an honest structural dimension marker until resolved dimensions are available.
- Canonical projection errors reject the bounded scalar/operator non-unitary
  product before QPU artifact instructions are emitted.
- Focused LISS-0511 suite: **4 passed**. Related product/semantic/QPU suites:
  **39 passed**. Spec verification: **161/161**. Syntax and diff checks passed.
- Full pytest was not a clean completion: it was stopped in the repository's
  long documentation-compression phase after **1169 passed and 9 failures**;
  the failures were outside LISS-0511's focused and related suites.
- No provider SDK, network, credentials, or real QPU execution was used.
