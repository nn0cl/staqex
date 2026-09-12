# LISS-0551: Current source fixture conformance

## Metadata

- Local issue ID: LISS-0551
- GitHub issue: none
- Status: ready
- Phase: phase-0-design
- Type: test fixture migration
- Priority: P0
- Initial/current planning size: M / M
- Owner/agent: host implementation; same-context review
- Related branch: `codex/liss-0551-fixture-conformance`

## Summary

Reconcile eight tests whose source setup contains same-scope duplicate `State`
declarations after the lowercase-`state` corpus migration. Preserve the
evolve-until, empty identity, Dirac sugar, operator, and pipeline assertions.

## Acceptance Notes

- Move helper-only replacement declarations into an explicit nested scope or
  remove them only when the measured value already satisfies current syntax.
- Do not permit same-scope redeclaration; LISS-0510 shadowing remains lexical.
- Do not change expected semantic values or diagnostics to silence failures.
- After fixture repair, transfer any residual QSEM/finiteization failure to
  LISS-0552 with exact diagnostics and source.

## Dependencies

- Parent: WP-0161
- Depends on: none
- Blocks: LISS-0552
- Related: LISS-0012, 0013, 0031, 0056, 0234, 0418, 0510

## Adjudicator Decision Points

- Approve fixture-only Phase 1 changes and the exact eight-node batch.
- Review each removal/nested-scope edit against its original assertion.
- WP-0161 Architecture approved 2026-09-12; no Phase 1 permission is inferred.

## Context and Verification

- Included: five test files and current lexical/scope specifications.
- Omitted: compiler implementation and QPU lowering changes.
- Verify eight direct nodes, duplicate-declaration absence, unchanged
  assertions, nearest scope tests, and residual diagnostic inventory.

## AI Planning Record — AIP-0551-001

- Status/date/size: proposed, 2026-09-11, M
- Route/scope: host; eight fixture nodes only
- Estimate: N/A; compatible metric unavailable
- Basis/assumption/confidence: git history shows the setup survived a mechanical
  lowercase-to-Type-First migration; high confidence for fixture drift, medium
  for residual projection behavior

## Process Review

- Outcome: not yet
- Lesson written: not yet
- Template-feedback path: none
