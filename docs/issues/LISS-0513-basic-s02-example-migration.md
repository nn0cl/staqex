# LISS-0513: Move the current S02 boundary sample into Basics

| Field | Value |
|---|---|
| Status | **done** |
| Phase | phase-3-refactor-complete |
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

Phase 3 requires review of the Green result and explicit refactor/final-review
approval.

## Phase 2 Green result

- User approval: `Feature Path / Phase 2 Green / 現行S02のBasic移管 実装承認`, 2026-09-07.
- Moved the runnable boundary sample to `examples/basics/B19_constrained_selection/`.
- Simplified the source and README to remove drug-discovery framing while
  preserving State, Projector, exact evolution, finite `Realize`, and terminal
  `measure` boundaries.
- Updated current tests, baseline identity, Host paths, and the Basics catalog;
  historical evidence documents were not rewritten.
- Verification: migration and boundary suites **42 passed**; S02 execution and
  baseline suites **14 passed**.

## Phase 3 Refactor result

- Re-read the canonical source, README, migration tests, current references,
  and historical evidence as a same-context reviewer.
- Confirmed that the migration preserves the language boundary and keeps the
  finite target plan explicit without implying live QPU execution.
- No additional behavior-preserving code refactor was necessary; readability
  and separation of concerns are preserved by the Basic source/README split.
- Verification: focused suites **56 passed**; spec verification **161/161**;
  `compileall` and `git diff --check` passed.
- Review packet: [LISS-0513 Phase 3 review](../collaboration/reviews/2026-09-07-liss-0513-phase3-review.md).

## Completion

- Final approval: `Feature Path / Phase 3 最終レビュー 承認`, 2026-09-07.
- Process review: no operating-contract deviation or operational problem found.
- The future realistic S02 remains a separate, not-yet-defined work item.
