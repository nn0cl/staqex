# LISS-0583: Evaluator static `forEach` elaboration successor

## Metadata

- Local issue ID: LISS-0583 (existing historical ID, not a new allocation)
- GitHub issue: none
- Status: review — Phase 1 test acceptance pending; separate F05 repair design started
- Phase: phase-1-red
- Type: behavior-preserving evaluator decomposition / current-base revalidation
- Priority: normal
- Initial planning size: M
- Current planning size: M
- Owner/agent: Codex host
- Related branch: `codex/liss-0583-static-foreach-phase0`
- Parent: WP-0174 rank 3
- Depends on: LISS-0582 repair/closeout, done in PR #604/#605; LISS-0584 before Green/delivery
- Blocks: static `forEach` delivery and later dependent source work

## Current authority

[Accepted current-base specification](../specs/evaluator-static-foreach-elaboration.md)
defines F01–F08, actual consumers and repair-guard disposition. Scope / Phase 0
start approved by human `Scope／Phase 0設計開始承認` on2026-10-05.
Human `Phase 0 acceptance」の承認` accepts the uniquely preceding dedicated
Issue/spec F01–F08 and bounded F08 guard disposition on2026-10-05, unchanged.
Implementation allowed: no. Post-review required: yes. Batch: N/A.
No new technology selection or ADR acceptance is proposed.

## Historical recovery, not current completion

Local `feature/liss-0583-static-foreach-successor`, tipb09e3e06, contains earlier
phase/approval/completion artifacts. Recover with
`git show b09e3e06:docs/issues/LISS-0583-evaluator-static-foreach-successor.md`.
Its base423c003b predates public-import repair; no corresponding remote branch
or PR was found. Earlier done wording describes local historical verification,
not delivery on the current repaired main. Keep that branch unchanged.
Existing AIP-0583-001 references are historical; their complete planning
details were not found in inspected artifacts, not invented here.

## AI planning record — AIP-0583-002

- Status: accepted with current-main Phase 0 on2026-10-05
- Author/environment: Codex desktop host / macOS27.0.1 arm64
- Created: 2026-10-05
- Model/reasoning as displayed: N/A, not surfaced by host
- Planning size: M, multi-file behavior-preserving split and guard reconciliation
- Intended route: host design and deterministic inventory/baseline; normal
  same_context review, empty model IDs
- Scope: current F01–F08 only; no old-branch wholesale integration
- Estimated tokens: N/A, no reliable host estimate; actual usage unavailable
- Basis: one51-line expansion body, state callbacks, public/private exports,
  unchanged adjacent authorities and reviewed snapshot-guard transition
- Assumptions: preserve current runtime order/diagnostics, not add rollback
- Confidence: medium; complete clause-to-test inventory and guard replacement
  equivalence must be checked at Phase 1 review
- Revises: historical AIP-0583-001 references; current base/repair and incomplete
  acceptance evidence require a fresh proposal, not reuse of old clearance

## Historical Phase 0 result

Actual consumer/state inventory, F01–F08 and source-budget disposition are in
the specification. Current clean-base scoped65 and adjacent41 passed; no tests
or production changes. Whole blocking suite not_run this phase.

Phase 0 acceptance received for the dedicated Issue/spec including F08 bounded
repair-guard disposition. No tests/guards changed during acceptance recording.
Phase 1 execution subsequently approved on2026-10-05 by human
`Phase 1 Red（受入テスト作成・限定guard移行）の実行承認`.
Trace/handoff: [representative trace](../collaboration/traces/2026-09-29-liss-0583-static-foreach.md).

## Phase 1 result / next decision

F01–F08 tests and the three accepted R05 guard transitions are prepared.
Focused: 89 passed / 5 failed; four structural migration gaps, one independently
discovered F05 compile mismatch (`Int i = q + 1` is accepted). Consumer/adjacent:
77 passed. All runs use a287be51 + dirty tests/docs, not final-commit evidence;
root/spec/sanity not_run, no full Green claim. Compiler remains unchanged.
Only four structural nodes are Active-Red; arithmetic is not excluded or waived.

[Phase 1 review packet](../collaboration/reviews/2026-10-05-liss-0583-phase1-review.md)
maps clauses, guard equivalence, measurements and the blocking finding.
Human `修復の設計開始承認` on2026-10-05 selects separate repair Scope / Phase 0
start, recorded in [LISS-0584](LISS-0584-opaque-foreach-wire-arithmetic-repair.md).
This is a new Green/delivery prerequisite, not retroactive revocation of0583
test execution or a cyclic repair dependency. Phase 1 test acceptance remains
pending; the failing F05 node stays unchanged and unexcluded in its current file.
Do not infer repair implementation or0583 test acceptance from design approval.
Requested approval here remains Phase 1 test review/acceptance (phase);
repair specification acceptance has its own target in0584.
Implementation allowed: no; post-review required yes, batch N/A.

## Dependency Carrier Approval — 2026-10-06

Human `はい。` approves the [named11-file carrier and three F08 guard transitions](../collaboration/reviews/2026-10-06-liss-0584-commit-scope.md)
for0584 dependency delivery and local commits. This is not wholesale0583 test
acceptance or implementation approval. Structural four exclusions unchanged;
F05 unmodified/unexcluded, fixed separately by0584. Historical refs untouched.
