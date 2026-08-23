# WP-0110: Residual Semantic Consumer Reconciliation

| Field | Value |
|---|---|
| Status | **Phase 3 Refactor final-review-ready** |
| Issue | [LISS-0447](../issues/LISS-0447-residual-semantic-consumer-reconciliation.md) |
| Specification | [Residual Semantic Consumer Reconciliation](../specs/staqex-residual-semantic-consumer-reconciliation.md) |
| Parent | [WP-0108](WP-0108-scientific-semantic-consumer-migration.md) |
| Authority | [ADR 0211](../architecture/adr/0211-scientific-semantic-core-and-ir-authority.md) |

## Recommended execution order

1. Independently review this Issue/Spec/WP and the three-subcontract impact
   inventory.
2. Phase 1 Red: add tests/fixtures only; no production changes.
3. Phase 2 Green: implement one subcontract per approved batch, starting with
   AlgorithmPlan projection because it is the smallest authority mismatch.
4. Phase 3 Refactor: remove temporary representations or fallback only after
   all replacement and regression evidence is complete.

## Phase 1 Red scope

- `tests/test_liss_0447_residual_semantic_consumers_red.py`;
- fixed fixtures under `tests/fixtures/residual_semantic_consumers/`;
- this Issue/Spec/WP and review/trace records;
- no production implementation, deletion, provider, network, S02, or solver.

## Candidate production scope for later Green batches

- `compiler/staqex/algorithm_plan_ir.py`;
- `compiler/staqex/scientific_semantic_ir.py`;
- `compiler/staqex/pipeline.py`;
- `compiler/staqex/h1_authoring.py` only if the reviewed H1 boundary requires it;
- `compiler/staqex/backend/qasm/emitter.py` and related tests for ordinary QASM
  fallback retirement only.

## Stop conditions

Stop for Architecture/User judgment if a subcontract requires changing ADR
0211, language syntax, State/Measure semantics, explicit Realize/Limit policy,
provider technology, or the completed LISS-0446 public-entry contract.

## Verification

- `.venv/bin/pytest` targeted Red/Green suites;
- canonical object identity and source provenance;
- no-bypass and atomic rejection tests;
- spec verification and full regression;
- independent review after each approved Green batch;
- `git diff --check`.

## Fixed Phase 1 Red cases

The Red suite must contain separate cases for each subcontract:

- `test_algorithm_plan_projection_preserves_canonical_fields`;
- `test_algorithm_plan_projection_rejects_mismatched_or_incomplete_authority`;
- `test_algorithm_plan_projection_rejects_mismatched_pair`;
- `test_algorithm_plan_rejects_multiple_realize_owners`;
- `test_algorithm_plan_rejects_missing_finite_record`;
- `test_h1_compile_exposes_canonical_semantic_ir`;
- `test_h1_diagnostics_remain_without_parallel_executable_authority`;
- `test_ordinary_qasm_canonical_fixture_never_calls_ast_fallback`;
- `test_ordinary_qasm_unsupported_input_rejects_atomically`.

Phase 1 Red must create these required fixtures/inputs: `explicit_realize_plan.sqx`,
`missing_realize_policy.sqx`, `h1_canonical_dispatch.sqx`, the existing
`semantic_consumer_migration/ordinary_gate.sqx`, and one inline unresolved
ordinary-QASM source. The first two cases must prove that
`ScientificSemanticIR.realize_source_node_id` and
`finite_realization_record` are source-owned, not inferred by the consumer.
Missing/multiple Realize owners and missing finite records all use
`E_ALGORITHM_PLAN_CANONICAL_PROVENANCE` with the deterministic reason values
specified by the Spec.

Each negative case asserts the exact rejection code and the complete empty
artifact envelope: no plan/result/QASM, no gates or QPU instructions, no
allocation, empty allocated qubits, and no partial program.

Phase 1 Red is complete: **7 failed, 0 passed, no collection errors**.
The failures are the intended missing canonical fields/H1 authority/fallback
contracts. AlgorithmPlan Phase 2 Green implementation is now complete under its
separate approval; H1 and ordinary-QASM Phase 2 Green batches are complete
after their independent reviews.

AlgorithmPlan Phase 2 Green passed independent review and is complete. H1
Phase 2 Green is complete after its independent review. Ordinary-QASM Phase 2
Green implementation passed independent review and is complete. Phase 3
Refactor removed the obsolete ordinary AST fallback and is ready for final
review.
