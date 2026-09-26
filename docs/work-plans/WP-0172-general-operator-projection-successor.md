# Work Plan: General Operator projection successor

## Goal

Separate general-Operator projection from the Evaluator facade without
changing the existing source meaning, numerical behavior, error contract,
cache lifetime, or single-owner runtime-state boundary.

## Scope

- In: `project ψ onto P` when `P` resolves to an Operator; compilation/cache
  access boundary; diagonal eligibility check; tuple-index mapping; Joint/world
  transformation; private consumer inventory; behavioral and structural
  acceptance evidence.
- Out: non-diagonal/Lüders projection, normalization changes, stronger
  mathematical projector validation, generic Operator lowering, parser or
  typechecker changes, QPU/provider behavior, unrelated evaluator families.

## Issue Graph

| Issue | Status | Initial size | Current size | Planning record | Depends on | Blocks | Branch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [LISS-0579](../issues/LISS-0579-general-operator-projection-successor.md) | review — Phase 2 verified on dirty worktree; commit-level template-copy smoke pending | M | M | AIP-0579-001 | WP-0171 / LISS-0578 (done, PR #600) | - | `codex/liss-0579-operator-projection-successor` |

## Recommended Order

1. Phase 0 boundary and acceptance specification were approved on 2026-09-27.
   The open cache/numerical edge questions remain explicitly deferred; no
   semantic expansion is included.
2. Phase 1 Red is complete; review structural Red failures separately from
   passing behavior characterization. The initial invalid tuple fixture was
   corrected and rerun. No production implementation was changed.
3. The Adjudicator accepted the Phase 1 Red test review on 2026-09-27; the
   active-Red entry remains until Phase 2 Green passes.
4. A spec-to-test cross-check found missing explicit characterization for
   unknown Operator, empty output, copied phase metadata, coalescing, and cache
   reuse. Phase 2 code is present but uncommitted; Green acceptance is withheld.
5. The Adjudicator approved the bounded Phase 1 correction and its test review.
   Phase 2 focused/adjacent tests (31), root tests (2,271), and spec verifier
   (161/161) pass. Template-copy smoke is unavailable on the uncommitted tree;
   run all blocking checks after commit before closing Phase 2 or requesting
   Phase 3.

## Current Next Issue

- Issue: LISS-0579 commit-level Phase 2 verification.
- Adjudicator approval needed: separate Phase 3 approval only after the
  committed tree passes all blocking checks. No Phase 3 work has started.

## Risks

- The existing non-diagonal test does not exercise its named condition; test
  evidence must distinguish Operator off-diagonality from tuple-shape failure.
- General Operator projection combines matrix compilation, numerical policy,
  and state transformation; extracting it must not expand semantics or move
  mutable-map ownership.
- Cache lifecycle appears tied to execution setup and name/width; rebinding or
  alternate execution lanes must be inspected before relying on cache safety.
- The live routing TOML does not configure `[source_structure]`; no quantitative
  structure-budget claim is currently supported.
- Prior local documentation branch `codex/docs-evaluator-integration-closeout`
  remains separate and unpushed; this plan is based on current `main`.

## Verification Plan

- Phase 0: static inventory only; no test execution.
- Phase 1: issue-owned structural suite and behavior characterization reported
  separately; focused runtime consumers include LISS-0430/0431.
- Phase 2/3: per verification policy, report focused and all-blocking suites
  separately, identify tested SHA/environment, compare failures, and rerun all
  blocking suites after final commit. Splits require actual-consumer inventory,
  private-import checks, consumer smoke, adjacent regressions, and source
  structure disposition including implementation bodies behind facades.

## AI Planning Records

### AIP-0579-001

- Status: proposed
- Created by:
  - Agent/environment: Codex desktop, local repository worktree
  - Model as displayed: N/A
  - Reasoning setting as displayed: N/A
  - N/A reason: not surfaced by host
- Created at: 2026-09-27
- Planning size: M
- Intended execution route: host agent for architecture design and later
  implementation; same-context review when a review packet is required, per
  live routing.
- Intended scope: one projection successor, explicit state boundary,
  structural/behavioral tests, and directly adjacent consumer verification.
- Estimated token range: 8,000–14,000
- Estimated token midpoint: 11,000
- Token metric: planning/execution context tokens, estimate only
- Estimation basis: one 74-line body with numerical behavior and cache ownership,
  existing characterization correction, compatibility/consumer inventory,
  and focused plus blocking verification; no language semantic expansion.
- Assumptions: no API/syntax change and no separate semantic bug fix is
  approved; adjacent tests are sufficient to characterize current behavior.
- Confidence: medium
- Revises: none
- Revision reason: none
- Superseded by: none

## Applicable Process Lessons

See the canonical application list in LISS-0579. The design honors state
ownership, private consumer discovery, callback boundaries, source ownership,
separated Red contracts, compatibility identity, branch-preserving refactor,
and canonical status synchronization.

## Process Review

- Outcome: not yet — contract correction/review and Phase 2 acceptance remain;
  Phase 3 is unauthorized.
- Lesson written: not applicable.
- Template-feedback path: none.
