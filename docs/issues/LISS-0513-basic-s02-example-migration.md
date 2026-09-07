# LISS-0513: Move the current S02 boundary sample into Basics

| Field | Value |
|---|---|
| Status | **phase-1-red** |
| Phase | phase-1-red |
| Type / priority | documentation/example migration / P1 |
| WorkPlan | [WP-0130](../work-plans/WP-0130-basic-s02-example-migration.md) |
| Specification | [S02 acceptance specification](../specs/staqex-v1-s02-drug-discovery-benchmark.md), limited to the current language-boundary behavior |
| Branch | `feature/basic-s02-migration-red` |
| Depends on | none; current S02 contracts are the migration baseline |
| Blocks | future replacement S02 creation |

## Scope

Move the current candidate-selection language-boundary sample out of the
showcase namespace and into `examples/basics/B19_constrained_selection/`.
Simplify its vocabulary and documentation without changing the demonstrated
Staqex semantics.

The future realistic quantum-drug-discovery S02 is explicitly out of scope.

## Acceptance scenarios

- The canonical Basic sample exists under `examples/basics/B19_constrained_selection/`.
- The Basic source demonstrates finite State preparation, projection,
  Hamiltonian evolution, and terminal measurement.
- The Basic source and README do not present synthetic candidate scoring as a
  drug-discovery claim.
- The Basic sample remains runnable locally without provider credentials or a
  live QPU.
- Current historical Issue, Trace, and Review evidence is not rewritten as if
  the old path had never existed.

## Phase 1 Red result

- Added `tests/test_liss_0513_basic_s02_example_migration_red.py`.
- Verification: **3 failed, 0 passed**, with no collection errors.
- The failures identify the absent Basic canonical artifacts and the absent
  non-drug boundary source/README contract.
- No example move, source simplification, reference update, or compiler change
  was performed.

## Next gate

Phase 2 requires review of the Red result and explicit implementation approval.
