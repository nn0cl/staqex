# LISS-0556: POVM rejection evidence regression

## Metadata

- Local issue ID: LISS-0556
- GitHub issue: none
- Status: done
- Phase: done
- Type: compiler result regression
- Priority: P0
- Initial/current planning size: M / M
- Owner/agent: host implementation; same-context review
- Related branch: `codex/liss-0556-povm-rejection`

## Summary

Restore the accepted `CompileResult.povm_observation_rejections` evidence
surface for a domain-mismatched POVM request without implementing POVM math.

## Acceptance Notes

- Preserve rejection reason, request/effect identity, source provenance,
  non-repair, and non-fabrication fields.
- A rejection creates no sampled outcome, post-state, finite target, or provider
  artifact.
- Existing computational-basis behavior remains unchanged.

## Dependencies

- Parent: WP-0161
- Depends on: none
- Blocks: none
- Related: LISS-0485, LISS-0084, WP-0092

## Adjudicator Decision Points

- Approve [ADR 0224](../architecture/adr/0224-povm-rejection-evidence-projection.md)
  and the Phase 0 acceptance boundary. The existing failing node is the
  regression authority; general POVM effect mathematics remains excluded.

## Phase 0 acceptance / Architecture review

- Review packet: [LISS-0556 Phase 0 architecture review](../collaboration/reviews/2026-09-14-liss-0556-phase0-architecture-review.md)
- Proposed ADR: [ADR 0224](../architecture/adr/0224-povm-rejection-evidence-projection.md)
- Current evidence: the exact active-Red node fails with
  `AttributeError: 'CompileResult' object has no attribute
  'povm_observation_rejections'` after `compiled.ok` is correctly false.
- Existing `POVM_DOMAIN_MISMATCH` diagnostics already preserve the rejection
  code, source span, requested effect-set identity, and source state domain.
- Decision boundary: Phase 2 may project those fields into
  `CompileResult.povm_observation_rejections`, with explicit
  `repaired=False` and `fabricated_outcome=False`. The projection must not
  evaluate effects, repair a domain mismatch, create an outcome/post-state,
  or create finite-target/provider artifacts.
- No implementation or test changes are authorized by this Phase 0 record.
- Adjudicator approval: `ADR 0224 Architecture / LISS-0556 Phase 0 acceptance
  承認`, received 2026-09-14. ADR 0224 is now accepted.
- Next gate: `LISS-0556 Phase 1 Red 承認`.

## Phase 1 Red result

- Adjudicator approval: `LISS-0556 Phase 1 Red 承認`, received 2026-09-14.
- The existing LISS-0485 test already expresses the approved regression
  contract; no test weakening or duplicate test was added.
- Direct verification of the complete LISS-0485 bridge file: **2 passed, 1
  failed**. The two valid/request evidence tests pass; the rejection test fails
  only because `CompileResult.povm_observation_rejections` is absent.
- No production implementation changed.
- Next gate: `LISS-0556 Phase 1 Red テストレビュー承認`.

## Phase 1 Red review result

- Adjudicator approval: `LISS-0556 Phase 1 Red テストレビュー承認`, received
  2026-09-14.
- The existing test is accepted as the single regression authority. Its
  rejection, reason, request identity, state domain, non-repair, and
  non-fabrication assertions are retained.
- The two neighboring valid bridge assertions remain passing; the missing
  result projection remains the sole Red failure.
- Next gate: `LISS-0556 Phase 2 Green / Implementation 承認`.

## Phase 2 Green / Implementation result

- Adjudicator approval: `LISS-0556 Phase 2 Green / Implementation 承認`,
  received 2026-09-14.
- Added `CompileResult.povm_observation_rejections` as a compiler-owned
  diagnostic projection for POVM rejection codes.
- The projection preserves code, source span, message, requested effect-set
  identity, and state domain, and adds explicit false non-repair and
  non-fabrication flags.
- No POVM effect evaluation, repair, sampled outcome, post-state, finite
  target, provider artifact, or valid measurement behavior was added or
  changed.
- Verification: LISS-0485 bridge suite **3 passed**; nearby POVM/mixed-dispatch
  regression suites **7 passed**; measurement-family aggregate **25 passed**;
  py_compile, lifecycle, coverage, and diff checks passed.
- Next gate: `LISS-0556 Phase 3 Refactor 承認`.

## Phase 3 Refactor result

- Adjudicator approval: `LISS-0556 Phase 3 Refactor 承認`, received
  2026-09-14.
- Consolidated the `dataclasses` import and rechecked the projection helper's
  placement and responsibility boundary. No behavior or assertion semantics
  changed.
- Verification: measurement-family aggregate **25 passed**; py_compile,
  document lifecycle, test lifecycle, coverage-ledger consistency, and diff
  check passed.
- Next gate: `LISS-0556 Phase 3 最終レビュー 承認`.

## Final review and completion

- Adjudicator approval: `LISS-0556 Phase 3 最終レビュー 承認`, received
  2026-09-14.
- The compiler result now exposes the accepted POVM rejection evidence without
  repair, fabricated outcomes, or provider artifacts.
- The active-Red node is removed from the manifest. LISS-0556 is complete.

Process review: no operating-contract deviation or operational problem found.

## Verification

One active rejection node, the complete LISS-0485 bridge suite, source
provenance, and no fabricated measurement/artifact evidence.

## AI Planning Record — AIP-0556-001

- Status/date/size: proposed, 2026-09-11, M
- Route/scope: host; CompileResult rejection projection only
- Estimate: N/A; compatible metric unavailable
- Basis/confidence: accepted field is absent from current DTO; high confidence

## Process Review

- Outcome: not yet
- Lesson written: not yet
- Template-feedback path: none
