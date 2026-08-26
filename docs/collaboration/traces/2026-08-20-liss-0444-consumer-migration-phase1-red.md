# LISS-0444 consumer-wide migration — Phase 1 Red trace

## Design check

- Scope: acceptance tests only for the remaining AST-derived consumer paths.
- Included: QASM fallback suppression, old QPU helper retirement, duplicate
  binder lowering removal from diagnostics, `symbolic_ir` retirement boundary,
  and AST dependency evidence.
- Omitted: production code, helper deletion, QASM behavior changes, provider
  SDK, live QPU, S02 migration, solver work, and Phase 2 Green.
- Applicable lenses: canonical authority, projection conservation, realization
  and fail-closed behavior, migration/regression safety, and phase discipline.
- Evidence contract: each test names an observable failure and the production
  path it protects; no hidden model reasoning is used.

## Red tests

File: `tests/test_liss_0444_consumer_migration_red.py`

The six tests define the Red contract; four fail against the current
implementation and two preserve positive canonical-connection evidence:

1. unresolved explicit evolution still emits the legacy-fallback warning;
2. old `_lowering_policy_projection` and `_explicit_evolution_projection`
   helpers still exist;
3. `qpu_ir_diagnostics()` still calls `lower_finite_binders()` directly;
4. canonical compilation still exposes a live `symbolic_ir` projection;
5. the diagnostics function still contains the AST binder-lowering call.
6. canonical QPU/inspection consumers remain connected and renamed-source
   provenance remains structurally valid; the corresponding retirement test
   still fails until `symbolic_ir` is removed.

Verification: `.venv/bin/pytest -q tests/test_liss_0444_consumer_migration_red.py`
returned **4 failed, 2 passed**, with no collection errors.

## Gate

This is Phase 1 Red only. Phase 2 Green requires explicit approval after the
independent review of this test contract. No production implementation was
performed.

## Independent review

The final independent review is
[`2026-08-20-liss-0444-consumer-migration-phase1-red-review-01.md`](../reviews/2026-08-20-liss-0444-consumer-migration-phase1-red-review-01.md).
It returned `READY` for Phase 1 Red. The review loop terminal state is
`COMPLETE`; Phase 2 remains unapproved.
