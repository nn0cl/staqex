# WP-0128: Product/Tensor Meaning Preservation

| Field | Value |
|---|---|
| Status | **Phase 1 Red complete — Phase 2 Green not approved** |
| Size | M for Phase 1 Red; larger follow-up if realization is requested |
| Issue | [LISS-0511](../issues/LISS-0511-product-tensor-meaning-preservation.md) |
| Specification | [Product/Tensor Meaning Preservation](../specs/staqex-semantic-ir-product-tensor-preservation.md) |
| Parent | [WP-0113](WP-0113-semantic-ir-meaning-preservation.md) |

## Goal

Make product/tensor meaning independently reviewable in the canonical
Scientific Semantic IR without widening the existing Coin/Mix or interfer
meaning slices and without implying finite or provider execution.

## U1 implementation-reality inventory

| Path | Current evidence | Authority disposition | Required follow-up |
|---|---|---|---|
| State tensor source (`*|*`, `tensor(a, b)`) | `parser.py` creates `TensorExpr`; `ast_nodes.py` retains only `left`, `right`, and span | source structure exists; canonical product/tensor meaning is not yet separately classified | Red must assert factor order, child identity, and dimensions from real source |
| Operator product (`*`) | OpDSL creates `OpBin`; the Scientific Semantic IR currently maps `OpBin`/`BinOp` generically to `mathematical_product` | product meaning exists but operator product and tensor product are not distinct canonical kinds | decide and test grouping, operand role, carrier, and normalization boundaries |
| Non-unitary product | `meaning_family_readiness.py` reads canonical `mathematical_product` nodes and rejects a bounded scalar/Pauli case | rejection path is a readiness consumer, not a complete product/tensor semantic contract | preserve ideal inspection and prove atomic no-artifact behavior for broader products |
| Quantum semantic lowering | `quantum_semantic_ir.py` validates acting-space tensor factors and total dimensions | target-oriented validation; not the authority for source meaning | consume canonical product/tensor meaning without re-reading AST meaning |
| QPU projection | `qpu_ir.py` consumes `ScientificSemanticIR`, but unsupported product/tensor cases remain family-specific | canonical consumer boundary exists; coverage is incomplete | add negative projection cases only after Phase 1 approval |
| Existing fixture | `tests/fixtures/semantic_meaning/mixture_and_product.sqx` covers scalar/operator product and mixture, not explicit tensor factor order | useful neighbor fixture, not sufficient for this Issue | add a dedicated product/tensor fixture in Phase 1 |

The inventory confirms a bounded design gap rather than an implementation
permission: `OpBin` and `TensorExpr` are currently separate AST forms, while
the canonical semantic classification is not yet equally explicit for both.
This Issue therefore starts with source/IR contract tests and does not alter
the existing readiness classifier or lowering paths during Phase 1.

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

## Phase 1 Red result

- User approval: `LISS-0511 Phase 1 Red承認`, 2026-09-07.
- Added the dedicated product/tensor fixture and four fixed acceptance tests.
- Verification: **4 failed, 0 passed**, no collection errors; Python syntax and
  `git diff --check` passed.
- Red evidence identifies four bounded gaps: distinct canonical meaning kinds,
  direct tensor factor identity/dimensions, grouped operator-product
  structure, and atomic rejection of unsupported non-unitary projection.
- Production implementation, deletion, fallback changes, provider/network
  access, and real QPU execution were not performed.

## Dependencies and stop conditions

Depends on ADR 0211/0212 and WP-0113's common meaning contract. Stop if the
slice requires a new IR authority, syntax decision, storage engine, unitary
interpretation of a non-unitary product, or a change to explicit `Realize`.
