# LISS-0580: Extract legacy `when` binding from Evaluator

## Metadata

- Local issue ID: LISS-0580
- GitHub issue: none
- Status: in-progress — final review approved; commit and final-SHA verification pending
- Phase: final-verification
- Type: Architecture Path structural decomposition
- Priority: normal
- Initial planning size: M
- Current planning size: M
- Reclassification reason: none
- Owner/agent: Codex host agent
- Related branch: `test/liss-0580-legacy-when-binding-red`

## Summary

Extract the legacy AST `WhenExpr` binding implementation from the Evaluator
facade while preserving the canonical control-mixture fallback, current
control/branch behavior, and Evaluator's sole ownership of mutable runtime
state. This is a file split only; retiring the fallback or changing semantics
is not included.

## Design Note

- Target behavior: Structural ownership moves to
  `runtime/evaluation/legacy_control_binding.py`; runtime behavior remains
  unchanged.
- Requested phase: Phase 3 Refactor (executed); final review approved.
- Proposed next phase: commit and final-SHA verification.
- Adjudicator decision: Phase 3 Refactor approved 2026-09-27.
- Requested approval type: phase.
- Approved scope: Architecture Path investigation and design for legacy
  `when` consumer/fallback disposition.
- Architecture approval: ADR 0227 boundary approved 2026-09-27.
- Implementation allowed: no further Phase 3 edits without renewed direction;
  final review and tested-final-commit verification remain.
- Post-review required: yes; commit and tested-final-commit verification.

## Acceptance Notes

The canonical `control_mixture` executor selects the legacy AST body when the
main body is outside deferred State/Measure eligibility. The binder dispatcher
then calls `_bind_when`. That path is reachable and must be retained. The
accepted architecture choice is extraction, not retirement.

Phase 0 acceptance: `LISS-0580 Phase 0 acceptance` approved 2026-09-27.
The linked specification is accepted for this bounded Issue. Phase 1 Red was
separately approved 2026-09-27. The initial test review finding has been
corrected: the fallback characterization now proves `control_mixture` plan
dispatch, deferred ineligibility, legacy body entry by that executor, and the
`_bind_when` callback. Same-context re-review found no remaining blockers.
Adjudicator accepted `LISS-0580 Phase 1 Red テストレビュー承認` on
2026-09-27. Phase 2 Green/Implementation was separately approved and executed;
verification results are recorded below. See the
[review summary](../collaboration/reviews/2026-09-27-liss-0580-phase1-red-review.md).

## Dependencies

- Parent: WP-0173
- Depends on: none
- Blocks: none
- Related: LISS-0495, LISS-0560, LISS-0571

## Adjudicator Decision Points

1. Commit the reviewed changes when authorized.
2. Rerun all blocking suites against that commit before closure.

## Context

- Included: ADR 0227, LISS-0495 control-mixture design/evidence,
  `Evaluator._bind_when`, canonical orchestration fallback, binder dispatch,
  compatibility wiring, and relevant existing tests.
- Omitted: language semantic changes, nested/dynamic-control changes, target
  lowering, provider work, and unrelated Evaluator bodies.
- Assumptions: established `_bind_when` behavior is the compatibility
  contract; tests may characterize it but must not broaden it.

## AI Planning Records

### AIP-0580-001

- Status: proposed
- Created by:
  - Agent/environment: Codex desktop, local repository worktree
  - Model as displayed: N/A
  - Reasoning setting as displayed: N/A
  - N/A reason: not surfaced by host
- Created at: 2026-09-27
- Planning size: M
- Intended execution route: host agent for bounded extraction; deterministic
  AST/import tools and pytest for verification; same-context review per routing.
- Intended scope: extract legacy control binding helpers behind the existing
  callback and preserve canonical fallback behavior.
- Estimated token range: 7,000–12,000
- Estimated token midpoint: 9,500
- Token metric: planning/execution context tokens, estimate only
- Estimation basis: one runtime method family, compatibility wiring, private
  consumer inventory, existing characterization reconciliation, and focused
  plus all-blocking verification.
- Assumptions: no semantic changes, and a valid canonical fallback fixture
  can be expressed using existing AST/source test helpers.
- Confidence: medium
- Revises: none
- Revision reason: none
- Superseded by: none

## Verification

Phase 0 was static only. Phase 1 added only the approved Red tests and
active-Red lifecycle entries; no production code changed. Focused result:
3 expected structural failures, 1 passing fallback characterization. Existing
LISS-0495/0225/0138/0375 consumers: 11 passed. Combined: 3 failed, 12 passed.
Tested base SHA `98d71df0f553bc3c0b8173d7aeb2310fa40c7184`, dirty working tree,
macOS 27.0.0 arm64, Python 3.14.6. Lifecycle, `py_compile`, and diff checks
passed. Ruff was unavailable. The initial Phase 1 test-review finding was
corrected and the same-context re-review found no remaining test-contract
blocker. The Adjudicator accepted the test review on 2026-09-27. At that
historical point Phase 2 had not yet been authorized; separate Phase 2 approval
was subsequently granted and its result is recorded below.

## Process Review

- Outcome: not yet
- Lesson written: active-Red status wording and lifecycle substring matching
- Template-feedback path: none

## Phase 2 Green Result

- Approval: Phase 2 Green/Implementation, Adjudicator, 2026-09-27.
- Focused plus adjacent consumers: 15 passed. All 2,275 collected pytest
  cases passed across the initial 863-pass run before interruption, the
  isolated slow test (1 pass), and a continuation run (1,411 pass).
- Lifecycle, syntax, coverage-ledger consistency, and whitespace checks
  passed. Ruff was unavailable.
- Successor is 140 physical lines; `evaluator.py` is 1,305 lines. No
  quantitative source-structure budget is configured.
- Evidence SHA `98d71df0f553bc3c0b8173d7aeb2310fa40c7184`, dirty tree;
  macOS 27.0.0 arm64, Python 3.14.6, pytest 9.1.1.
- Phase 3 Refactor approval received 2026-09-27; the Phase 3 final review is
  accepted. Issue remains open until commit and final-SHA verification.

## Phase 3 Refactor Result

- Reviewer-empathy inspection found the extracted binder readable and
  responsibility-focused. Added a short comment that makes the precedence of
  matching arms over `else` explicit; no assertions or behavior changed.
- Repeated private consumer inventory found only the binder dispatcher,
  `EvaluatorContext` callback, compatibility installation, and approved tests.
- Focused/adjacent consumers: 15 passed. Full blocking pytest suite: 2,275
  passed in 314.44s. Lifecycle, coverage ledger, and whitespace checks passed.
- Tested base SHA `98d71df0f553bc3c0b8173d7aeb2310fa40c7184`; worktree dirty;
  macOS 27.0.0 arm64, Python 3.14.6, pytest 9.1.1. Final committed-SHA rerun
  is still required; Ruff unavailable.
- Same-context review found no blocker; final Adjudicator review was approved
  on 2026-09-27.
- Adjudicator approved the Phase 3 final review on 2026-09-27. Commit and
  tested-final-commit evidence remain outstanding.
