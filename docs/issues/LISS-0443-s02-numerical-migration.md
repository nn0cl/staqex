# LISS-0443: S02 numerical migration after explicit evolution reconciliation

| Field | Value |
|---|---|
| Status/phase | **Phase 2 Green evidence complete — final re-review pending** |
| WorkPlan | [WP-0106](../work-plans/WP-0106-s02-numerical-migration.md) |
| Specification | [S02 numerical migration](../specs/staqex-s02-numerical-migration.md) |
| Related inventory | [LISS-0442](LISS-0442-s02-corpus-migration-inventory.md) / [WP-0105](../work-plans/WP-0105-s02-corpus-migration-inventory.md) |
| Related implementation | [LISS-0438](LISS-0438-explicit-evolution-residual-reconciliation.md) / [WP-0104](../work-plans/WP-0104-explicit-evolution-residual-reconciliation.md) |
| Approval status | Phase 2 Green approved; independent review pending; Phase 3 not approved |
| Phase 1 trace | [2026-08-19 Phase 1 Red](../collaboration/traces/2026-08-19-liss-0443-phase1-red.md) |
| Phase 2 review | [2026-08-19 Phase 2 Green review](../collaboration/reviews/2026-08-19-liss-0443-phase2-green-review.md) |
| Phase 2 re-review | [2026-08-19 Phase 2 re-review](../collaboration/reviews/2026-08-19-liss-0443-phase2-rereview-01.md) |

## Objective

Define the next S02 numerical comparison as a separate, reviewable task after
the explicit exact/formal/finite evolution boundaries have been reconciled.
The task must determine whether the numerical lane can be migrated while
preserving the frozen pre-migration baseline and keeping exact local output
distinct from a finite target plan.

## In scope for the future task

- freeze the input, seed, duration, weights, shots, and baseline identity;
- specify exact-local versus finite-target comparison outputs;
- specify numerical tolerances and provenance for any changed metric;
- add or update regression tests only after a separate Phase 1 approval;
- preserve fail-closed capability rejection and no-partial-artifact behavior.

## Explicit exclusions

- no implementation or numerical rerun is authorized by this planning record;
- no automatic finiteization or hidden `Limit` conversion;
- no Provider SDK, credentials, network, or live QPU submission;
- no change to ADR 0210 or the explicit `Realize` boundary;
- no retuning of the benchmark to make a result pass.

## Exit conditions

- an independently reviewed acceptance specification exists;
- the baseline and comparison contract are approved;
- a typed Phase 1 Red approval names the tests and allowed paths;
- numerical changes, if any, are explained with reproducible evidence;
- a later independent review confirms exact/finite provenance and rejection
  boundaries remain visible.

## Phase 1 Red result

The reviewed Red suite is recorded at
`tests/test_liss_0443_s02_numerical_migration_red.py`. R1 initially failed
because the report did not expose `source_sha256` and `base_seed` in its
numeric result record; R2 and R3 preserved the already-shipped realization and
atomic-rejection evidence.

Phase 2 Green added only `source_sha256` and `base_seed` to the S02 numeric
result metadata, including the failed-result path. The source meaning,
realization policy, baseline, and scoring logic were not changed.

The independent Phase 2 review returned `NOT READY`. The composite numeric
identity finding was accepted and corrected after user approval. The full
LISS-0403 regression evidence gap was then closed using the repository
`.venv`: 4 pytest tests passed in 184.57s. Final independent re-review remains
pending before Phase 3 or closeout.
