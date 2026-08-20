# LISS-0447 AlgorithmPlan Phase 2 Green Trace

- Approval: user typed `承認` for the AlgorithmPlan subcontract Phase 2 Green.
- Scope: `scientific_semantic_ir.py`, `algorithm_plan_ir.py`, `qpu_ir.py`,
  AlgorithmPlan-focused tests, and this trace/review evidence only.
- Excluded: H1 delivery, ordinary QASM fallback, provider/live QPU, S02,
  solver, syntax, and LISS-0446 changes.

## Implementation

- Added source-owned `realize_source_node_id` and
  `FiniteRealizationRecord` to `ScientificSemanticIR`.
- Built one `AlgorithmPlanModule` from that canonical record, preserving the
  existing provenance view for callers without retaining a second executable
  plan authority.
- Added deterministic `E_ALGORITHM_PLAN_CANONICAL_PROVENANCE` reasons for
  missing/multiple Realize owners and missing finite records.
- Extended QPU diagnostic routing to preserve the exact code/reason.

## Verification

- LISS-0447 focused: **5 passed / 4 failed**; the four failures are the
  intentionally unimplemented H1 and ordinary-QASM subcontract cases.
- AlgorithmPlan integrated and related regression command:
  `.venv/bin/pytest -q tests/test_algorithm_plan_ir_integrated_red.py
  tests/test_liss_0445_consumer_migration_red.py -k 'algorithm_plan or provenance'`
  **12 passed, 10 deselected**.
- `git diff --check`: passed.

Phase 2 Green review was required before this subcontract could close. No later
subcontract is approved by this trace.

Final independent review: **READY**. AlgorithmPlan subcontract is complete;
H1 and ordinary-QASM batches remain separately gated.
