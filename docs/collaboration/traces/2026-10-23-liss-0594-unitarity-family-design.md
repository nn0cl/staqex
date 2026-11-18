# 2026-10-23 — LISS-0594 Unitarity family Phase 0 design

## Request

- Date: 2026-10-23 Asia/Tokyo
- User request: continue after closing LISS-0593; prepare the next source
  decomposition candidate.
- Current phase: Phase 0 design proposal only.
- Canonical issue: [LISS-0594](../../issues/LISS-0594-unitarity-check-family-separation.md)
- Specification: [proposed U01–U10](../../specs/unitarity-check-family-separation.md)
- AI planning record: AIP-0594-001, proposed in the issue.

## Context and routing

- Included: accepted WP-0175 inventory, target implementation, pipeline
  caller, direct/inherited tests, relevant LISS-0411/LISS-0436 safeguards,
  local issue/spec conventions, verification and structure policies, runtime
  routing, and process lessons already applied in the design-intake context.
- Omitted: unrelated implementation families, broad historical deletion
  audit, full root test execution, dynamic external-consumer claims, and all
  test/source edits.
- Assumption: “continue” after the prior closeout authorizes only the next
  candidate's Phase 0 investigation/design; it does not accept a new spec or
  authorize Red/implementation.
- Open decisions: exact module grouping; disposition of classical
  measurement eligibility and shared `_children`; later human acceptance of
  U01–U10.
- Route: Codex host; deterministic repository inspection; implementation not
  requested. Runtime review isolation is `same_context`; implementation is
  `host`, but no implementation phase is authorized.
- Privacy: repository-local source and test evidence only; no external/private
  payload.

## Attempt 1

- Environment: local macOS desktop repository, branch
  `codex/liss-0594-unitarity-family-design`, base
  `93a2548ae168a70a3c3340bf79533de95828dc39`.
- Model/reasoning as displayed: N/A; not exposed in task context.
- Scope: map the current responsibility and consumer boundary and prepare a
  dedicated Phase 0 acceptance proposal.
- Result: prepared proposed issue/spec and this trace; no test or production
  changes and no execution verification claimed.
- Decision boundary: U01–U10 and the bounded responsibility proposal are
  accepted; Phase 1 still needs distinct approval.
- Adjudicator decision: explicitly accepted LISS-0594 Phase 0 U01–U10 on
  2026-10-23. This does not authorize Phase 1 Red.
- Token use: N/A; unavailable to the agent.

## Verification / next safe action

- Checks: `git status`, branch and HEAD inspection; source/caller/test search;
  manual cross-check of issue/spec links and approval wording.
- Result: design evidence only. No tests run because no code/tests were
  changed or authorized.
- Changed files: issue, proposed spec, trace, and WP-0175 status pointer.
- Next: [LISS-0594 Phase 1 Red execution approval](../../issues/LISS-0594-unitarity-check-family-separation.md)
  was received 2026-10-25; test-only cohort and lifecycle registration are now
  underway. The authored cohort has one expected structural Red and 23 focused
  passes, but six inherited exact-path guard nodes fail because they reject the
  new test module as an undeclared path. No predecessor guard was modified.
  A bounded compatibility-supplement design decision is required before
  modifying the accepted path contracts; Phase 1 review/acceptance remains
  pending.

## Phase 1 execution record — 2026-10-25

- Current tree: dirty, HEAD `93a2548ae168a70a3c3340bf79533de95828dc39`;
  macOS 27.0.1 arm64, CPython 3.12.6, pytest 9.0.3.
- Focused new plus direct/adjacent consumers: 23 passed / 1 expected Red.
- Spec verification: 161/161 PASS; active-Red lifecycle: one entry, PASS.
- Broad pytest excluding only the new active-Red module: 3,583 passed / 6
  failed. All failures share the predecessor guard's exact new-test-path
  assertion (LISS-0591 P10, LISS-0592 R06, LISS-0593 F09 pre/post and G07
  pre/post); they are induced by this new path. No prior equivalent root run
  was captured, so no unrelated baseline comparison is claimed.
- No implementation or prior guard changes. `git diff --check` PASS.
