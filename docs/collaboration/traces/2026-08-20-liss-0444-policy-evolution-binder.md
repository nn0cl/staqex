# LISS-0444/WP-0107 — policy/evolution/binder projection trace

## Scope and approval

The user approved the bounded Phase 3 continuation for `lowering_policy`,
`explicit_evolution`, and `binder_lowering`. Provider SDKs, live QPU submit,
S02 numerical migration, solver expansion, and consumer-wide legacy retirement
were excluded.

## Work performed

- Added source-derived canonical fields and provenance to
  `ScientificSemanticIR`.
- Projected those fields into `QpuProgram` from canonical IR.
- Added semantic and executable-projection fingerprint validation; QASM rejects
  mutated or provenance-incomplete programs without emitting artifacts.
- Added positive and negative acceptance tests for policy, explicit evolution,
  binder projection, and instruction mutation.

## Verification

- Targeted suites: **45 passed**.
- Full `.venv/bin/pytest -q`: **1636 passed**.
- `git diff --check`: passed.
- Independent review:
  [`2026-08-20-liss-0444-policy-evolution-binder-review-02.md`](../reviews/2026-08-20-liss-0444-policy-evolution-binder-review-02.md)
  returned `READY` for this bounded batch.

## Remaining boundary

The old AST helper definitions, diagnostic-time binder re-lowering, QASM AST
fallback, and parallel `symbolic_ir` path remain explicitly deferred. This
trace closes the bounded review loop only; it does not mark WP-0107 or the
consumer-wide migration complete.
