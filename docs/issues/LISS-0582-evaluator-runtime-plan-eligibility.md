# LISS-0582: Evaluator runtime-plan eligibility successor

## Metadata

- Local issue ID: LISS-0582
- GitHub issue: none
- Status: in_progress — repair provisionally verified; post-commit checks and Phase 3 approval pending
- Phase: phase-2-green
- Type: behavior-preserving evaluator decomposition
- Priority: normal
- Initial planning size: M
- Current planning size: M
- Owner/agent: Codex host agent
- Related branch: `codex/liss-0582-public-import-repair-design` (design); PR #604 on original feature branch
- Parent: WP-0174
- Depends on: none; rank-2 scope approved 2026-09-29

## Summary

Current action 2026-10-05: repair provisionally verified; post-commit checks and Phase 3 approval pending. Original completion
below is historical, not current CI clearance. Canonical supplement:
[R01–R07 accepted repair specification](../specs/evaluator-public-import-compatibility-repair.md).

Investigate and, after separate phase approvals, extract the cohesive runtime
execution eligibility/projection policy that remains on `Evaluator`. The slice
covers callable eligibility, Operator-attribute walking, minimal-evolution and
first-family checks, and the small runtime-unit projections used by existing
canonical/legacy routing. It must preserve the compile-owned
`ScientificSemanticIR` authority, the single mutable-state owner, private
compatibility hooks, diagnostics, and established fallback behavior.

## Design authority

The proposed acceptance boundary is [the Phase 0 specification](../specs/evaluator-runtime-plan-eligibility.md).
Existing authority and compatibility boundaries include ADR 0211, ADR 0225,
ADR 0227, and the completed LISS-0544/LISS-0560 orchestration slices. No new
ADR is accepted by this Issue yet.

## Design Check

- Scope: Phase 0 consumer and authority investigation for WP-0174 rank 2.
- Implementation permission: none. Phase 1 Red, Phase 2 Green, and Phase 3
  require separate typed approval.
- Accepted successor candidate: stateless
  `compiler/staqex/runtime/evaluation/plan_eligibility.py`; membership is
  constrained by the accepted Phase 0 specification.
- Out of scope: new runtime-plan families, semantic IR meaning changes,
  implicit realization, provider/QPU integration, Rust, public API retirement,
  and rank 3–6 residual candidates.

## AI planning record — AIP-0582-001

- Status: proposed
- Created by: Codex desktop, local repository worktree
- Model/reasoning as displayed: N/A; not surfaced by host
- Created: 2026-09-29
- Planning size: M
- Intended route: strong reasoning host analysis for the cross-module boundary;
  deterministic search/AST/import checks for evidence; same-context review if
  a review packet is required by live routing.
- Scope: one runtime-plan eligibility/projection family, its compatibility
  hooks, and direct consumers only.
- Estimated token range: 8,000–14,000; midpoint 11,000; planning estimate,
  not actual usage.
- Basis: residual evaluator policy helpers, existing orchestration seam,
  private consumers, and authority/fallback boundaries across runtime modules.
- Assumptions: accepted runtime-plan family semantics remain unchanged; no
  second mutable state owner is introduced; static search is only a lower bound
  for consumer discovery.
- Confidence: medium; `_main_deferred_eligible` membership and the boundary
  between semantic projection and evaluator eligibility require review.
- Revises/supersedes: none.

## Phase 0 result

The Phase 0 design and initial consumer inventory are recorded in the linked
specification. Phase 0 acceptance is recorded in the [review packet](../collaboration/reviews/2026-09-29-liss-0582-phase0-acceptance.md).
Phase 1 Red tests are recorded in the linked review packet. The Phase 2 Green
implementation is recorded in the Phase 2 review packet; the accepted Red
tests remain unchanged.

## Phase 1 Red scope

Phase 1 adds only
`tests/test_liss_0582_runtime_plan_eligibility_red.py` and its active-Red
registry entry. Existing LISS-0493–0498 runtime-plan suites remain the
behavioral authority and are not duplicated here. No production source,
public API, or semantic-plan builder is changed.

The five Red tests cover:

1. successor module and pure exported policy functions;
2. removal of candidate bodies from the Evaluator facade;
3. absence of copied mutable evaluator state;
4. orchestration imports and calls through the successor;
5. runtime compatibility-hook identity.

## Phase 1 Red result

The reviewed Red contract is accepted in the [Phase 1 Red review packet](../collaboration/reviews/2026-09-29-liss-0582-phase1-red-review.md).
The bounded suite remains intentionally Red with five structural failures; no
production source was changed.

## Phase 2 Green result

Implementation approval was received in the thread on 2026-09-29:
`Phase 2 Green／実装承認`. The minimum successor boundary is implemented and
verified with focused, consumer/adjacent, lifecycle, and all-blocking suites.
Phase 3 refactor/review is recorded in the Phase 3 review packet.

## Historical final verification

The human Adjudicator approved final verification on 2026-09-29 with
`Phase 3 review passed; final verification承認`. On final commit
`7620eb8c7b6843de4d821f4100c1d029e0a8b572`, the all-blocking suite passed
with 2,285 tests; lifecycle validation passed and the tree was clean.

Process review: no operating-contract deviation or operational problem found.

## Historical completion

LISS-0582 is done. The Phase 1 Active-Red registration is retired. Lower-ranked
WP-0174 candidates require separate design intake and approval.

## Repair planning — AIP-0582-002

- Status: accepted with R01–R07 and Phase 0 on 2026-10-05
- Author: Codex desktop host; macOS 27.0.1 arm64
- Initial/current issue size: M unchanged; multiple evidence/test/import files
  and review phases despite small production correction
- Model/reasoning displayed: N/A, reliable display unavailable
- Estimated token range/midpoint/metric: N/A, reliable estimate unavailable
- Intended route: Architecture Path Phase 0 host; later host/same_context, empty IDs
- Basis: ten frozen public names, identity, failed CI, bounded area/propagation
- Assumptions/confidence: high on ten-name cause; later branch compatibility unverified
- Revises: AIP-0582-001 for reopened scope; original estimate retained as historical

## Historical Phase 0 repair / review target

Human `互換性修復の Scope／Phase 0 設計開始` authorizes investigation/design only.
PR #604 head 423c003b fails public baseline; root/spec CI successes do not waive it.
Fresh capture: ten removed evaluator names; other manifests/cases identical;
adjacent 52 pass. Earlier review missed public re-exports; no retirement waiver.
Use existing Issue, not a competing bug owner. Accepted extraction retained;
no later task dependency. Blocks PR #604 and dependency delivery through LISS-0602.

- Artifact: R01–R07 repair spec / trace / WP-0174
- Current phase: Architecture Path / Phase 0 design
- Requested approval: Phase 1 Red execution (phase), accepted R01–R07 only
- Approved scope: ten original-object re-exports, frozen baseline/ownership
- Implementation allowed: no; tests/source and baseline unchanged
- Post-review required: yes; separate Red, review, implementation and final gates
- Execution batch: N/A
- No commit/push/merge this design phase; PR still blocked by failed CI

Human `修復仕様 R01–R07 と Phase 0 acceptance` received 2026-10-05.
Repair requirements, boundary and planning record accepted without changes.
No Phase 1 execution, test review, implementation or later-phase permission
inferred. Earlier 52-case/capture evidence is historical, not a fresh run.
Next: request Phase 1 Red; implementation permission remains no, post-review yes.

## Historical repair Phase 1 Red / review target

Human `Phase 1 Red（受入テスト作成）承認` received 2026-10-05.
Feature Path readiness satisfied by accepted R01–R07 and observable import,
identity and frozen-baseline outcomes. Added only new repair tests and scoped
active-Red metadata, with documentation/status synchronization.

- Result: 37 focused cases, 14 expected failures / 23 passes, no errors/skips.
- Consumer/baseline-generator regression: 8 pass; adjacent/ownership: 52 pass.
- Requested approval: Phase 2 Green execution / implementation (phase and implementation); Red accepted.
- Implementation allowed: no; Phase 2 requires separate explicit approval.
- Post-review required: yes; batch N/A; no commit/push/merge.
- Evidence and R01–R07 matrix: [Red acceptance request](../collaboration/reviews/2026-10-05-liss-0582-repair-red-acceptance.md).

User `Phase 1 Red テストレビュー／acceptance` received as review request.
Fresh same-context review reproduces exactly14 expected failures/23 passes,
consumer8 and adjacent52 pass; no acceptance blocker. Test/production/baseline
unchanged. Human `Phase 1 Red acceptance を承認` received 2026-10-05 accepts
the reviewed tests without changes. Separate Phase 2 Green execution and
implementation approval remain pending; no later permission inferred from
test acceptance. New test SHA256 remains
`88c949852d81846a5ff28b90a7fd226f25017f0aba69bd0a94a3381e48036a8f`.
No source/test/baseline/lifecycle edits or commit/push/merge in acceptance sync;
earlier scoped test results are historical, not rerun in this step.

## Current repair Phase 2 Green

Human `Phase 2 Green／implementation` received 2026-10-05 as approval of
the uniquely requested phase and implementation target. Red acceptance
already recorded; no later approval inferred. Accepted design/tests committed
separately as c7c726978de8d8e1228b49982c2caf8987ec4603.

Production changes only: nine AST facade imports and dataclasses.replace,
with compatibility comments. Executable evaluator AST, successor,
orchestration/installer, tests and baseline artifacts unchanged. Fresh
focused37 / consumer8 / adjacent52 pass; spec161 pass; capture/cmp byte-equal.
All five active-Red entries retired; no exclusions. Full root2322 passed;
evidence is provisional until rerun at the implementation commit.

- Current phase: Phase 2 Green; implementation allowed yes within R01–R05 only.
- Next approval: Phase 3 Refactor/review (phase), after blocking verification.
- Post-review required: yes; batch N/A; no push/merge or issue completion.
- R06/R07 final approval, remote CI and downstream delivery still gated.
