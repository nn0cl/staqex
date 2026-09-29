# LISS-0582: Evaluator runtime-plan eligibility successor

## Metadata

- Local issue ID: LISS-0582
- GitHub issue: none
- Status: in progress — Phase 2 Green implemented; Phase 3 review pending
- Phase: phase-1-red
- Type: behavior-preserving evaluator decomposition
- Priority: normal
- Initial planning size: M
- Current planning size: M
- Owner/agent: Codex host agent
- Related branch: `feature/liss-0582-runtime-plan-eligibility`
- Parent: WP-0174
- Depends on: none; rank-2 scope approved 2026-09-29

## Summary

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
Phase 3 refactor/review remains separate.

## Next gate

Request separate **Phase 3 Refactor/review approval**, if needed. Do not mark
the issue complete until final-commit verification and process review are
recorded.
