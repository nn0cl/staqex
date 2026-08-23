# LISS-0448 Post-Green Review Correction Trace

## Trigger and scope

- Trigger: accepted findings from Post-Green Independent Context Review 01.
- User decision: separately accept the canonical projection Spec on
  2026-08-23, preserving the blackboard-first and explicit QPU-boundary rule.
- Scope: provenance correction, Spec acceptance record, competing-path
  disposition, and reproducible verification evidence.
- Excluded: provider integration, hidden finiteization, unitary fallback, and
  broad AST-lowerer migration.

## Corrections

- QASM rejection provenance now records `source_node_id`,
  `branch_source_node_ids`, and `source_span` in addition to reason and the
  null target plan.
- The accepted Spec records the semantic authority and the legacy AST lowerer
  disposition: retained only as a fail-closed compatibility boundary, with
  future retirement after caller inventory.
- The review record now records the user's separate Spec acceptance and moves
  the loop to `RE_REVIEW`.

## Exact verification

```text
.venv/bin/python -m pytest -q \
  tests/test_liss_0448_coin_mix_semantic_red.py \
  tests/test_liss_0450_semantic_ir_meaning_red.py \
  tests/test_liss_0445_consumer_migration_red.py \
  tests/test_scientific_semantic_core_red.py \
  tests/test_liss_0446_qasm_public_entry_red.py \
  tests/test_liss_0447_residual_semantic_consumers_red.py
```

- Focused and related tests: **73 passed**.
- `.venv/bin/python tests/spec_verification/run_all.py`: **161/161 passed**.
- Python compilation: passed.
- `git diff --check`: passed.
- Reviewed tests changed only to pin the accepted provenance fields.

## Re-review result

- Fresh Post-Green Review 02 returned **NOT READY**.
- Review record: `docs/collaboration/reviews/2026-08-23-liss-0448-post-green-review-02.md`.
- Review loop state: **ABORT pending Architecture/User decision**.
- New blockers: canonical branch-pattern/control/mixture-rule preservation,
  fail-closed or explicit retirement of the legacy `CX` path, and authority
  chain resolution for the proposed QPU rejection contract.
