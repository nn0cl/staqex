# WP-0128: Product/Tensor Meaning Preservation

| Field | Value |
|---|---|
| Status | **proposed — Architecture Path design intake** |
| Size | M for Phase 1 Red; larger follow-up if realization is requested |
| Issue | [LISS-0511](../issues/LISS-0511-product-tensor-meaning-preservation.md) |
| Specification | [Product/Tensor Meaning Preservation](../specs/staqex-semantic-ir-product-tensor-preservation.md) |
| Parent | [WP-0113](WP-0113-semantic-ir-meaning-preservation.md) |

## Goal

Make product/tensor meaning independently reviewable in the canonical
Scientific Semantic IR without widening the existing Coin/Mix or interfer
meaning slices and without implying finite or provider execution.

## Work units

| Unit | Scope | Exit evidence |
|---|---|---|
| U1 inventory | Map source forms, AST/HIR nodes, current semantic fields, and consumers | disposition matrix with authority/retire/retain decision |
| U2 source retention | Confirm grouping, operand identity, tensor factor order, carrier, and dimensions | real-source structural fixture and parser/HIR assertions |
| U3 canonical meaning | Define product/tensor role and provenance requirements without production types | reviewed Spec/ADR disposition |
| U4 fail-closed projection | Define ideal inspection versus unsupported finite/QPU result | no-artifact rejection scenarios |
| U5 Phase 1 Red | Add only fixtures and failing acceptance tests after typed approval | focused Red result and independent review |

## Phase 1 Red allowed paths

- `tests/fixtures/semantic_meaning/product_tensor.sqx`;
- `tests/test_liss_0511_product_tensor_meaning_red.py`;
- this WP, LISS-0511, the Spec, and review/trace records.

No production code, deletion, fallback change, provider, network, numerical
approximation, or QPU execution is allowed in Phase 1.

## Phase 2/3 gate

Phase 2 may implement only the minimum accepted canonical semantic projection
after a reviewed Red result and typed implementation approval. Phase 3 may
refactor or retire a duplicate path only after independent review, unchanged-
neighbor regression, provenance/fingerprint checks, and a no-bypass proof.

## Dependencies and stop conditions

Depends on ADR 0211/0212 and WP-0113's common meaning contract. Stop if the
slice requires a new IR authority, syntax decision, storage engine, unitary
interpretation of a non-unitary product, or a change to explicit `Realize`.

