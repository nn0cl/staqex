# LISS-0443: S02 numerical migration after explicit evolution reconciliation

| Field | Value |
|---|---|
| Status/phase | **Phase 1 Red complete — Phase 2 Green not approved** |
| WorkPlan | [WP-0106](../work-plans/WP-0106-s02-numerical-migration.md) |
| Specification | [S02 numerical migration](../specs/staqex-s02-numerical-migration.md) |
| Related inventory | [LISS-0442](LISS-0442-s02-corpus-migration-inventory.md) / [WP-0105](../work-plans/WP-0105-s02-corpus-migration-inventory.md) |
| Related implementation | [LISS-0438](LISS-0438-explicit-evolution-residual-reconciliation.md) / [WP-0104](../work-plans/WP-0104-explicit-evolution-residual-reconciliation.md) |
| Approval status | Scope/documentation split approved; separate phase and implementation approval required |
| Phase 1 trace | [2026-08-19 Phase 1 Red](../collaboration/traces/2026-08-19-liss-0443-phase1-red.md) |

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
`tests/test_liss_0443_s02_numerical_migration_red.py`. R1 currently fails
because the report does not expose `source_sha256` and `base_seed` in its
numeric result record; R2 and R3 preserve the already-shipped realization and
atomic-rejection evidence. Phase 2 Green remains unapproved.
