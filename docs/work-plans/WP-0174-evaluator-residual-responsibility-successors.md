# WP-0174: Evaluator residual responsibility successors

| Field | Value |
|---|---|
| Status | active — LISS-0582 done; residual candidates require separate intake |
| Size | M |
| Parent | WP-0160 / core module decomposition |
| Scope approval | Evaluator residual-responsibility Architecture Path Phase 0 investigation approved 2026-09-28 |
| Completed candidate | LISS-0581 — coordinate liveness and Trace-Out successor; architecture accepted by ADR 0228 |
| Current Next Issue | LISS-0584 Phase 2 C verification passed; record-head final rerun, then Phase 3 approval; LISS-0583 feature acceptance separate |

## Goal

Continue reducing Evaluator-owned implementation bodies by selecting cohesive
successors from current consumer/state evidence, not by line count alone.
Preserve source meaning, public/private compatibility, diagnostics, and
Evaluator's unique mutable-state ownership.

## Inventory and order proposal

| Rank | Residual responsibility | Evidence | Disposition |
|---:|---|---|---|
| 1 | Coordinate liveness and Trace-Out: five Evaluator helpers and duplicate frame helpers | Shared consumers in frames, pipes, evolution, execution, observation; tied to existing ADR 0138/0142/0153/0158 behavior | LISS-0581 done; implementation commit passed 2,280 tests; PR delivery pending GitHub CI and merge |
| 2 | Runtime-plan eligibility/projection: callable eligibility, Operator-attribute walk, unit projection, first-family checks | Extracted policy retained; ten public imports restored | LISS-0582 done; PR #604 merged at 458fcbe6, PR/main CI and merge-result local checks passed; no retirement waiver |
| 3 | Static `forEach` expansion | 51-line evaluator body, actual execution dispatch and live binding callbacks; historical local implementation predates repair | LISS-0583 test acceptance pending; LISS-0584 minimal guard implemented, all-blocking sanity gap; no old-branch wholesale integration |
| 4 | Tensor binding | 45-line evaluator body; owns `Joint` transformation and dispatch dependency | Separate binding/algebra slice; not an external-resource adapter and not automatically part of `binding.py` |
| 5 | Host coefficient-array resolution | 42-line body crosses HostInputPort, finite binder and scientific input validation/provenance | Treat as resource/input-boundary design, not generic evaluator helper extraction |
| 6 | Partial-call filling and small classical-state helpers | `_fill_partial` 31 lines; `_is_closed` 28; `_maybe_capture_classical_scalar` 23 | Keep separate until actual consumers, state writes, and feature ownership show a cohesive unit |
| Excluded | `_eval_set_comprehension` | Explicitly retained as dispatch/consumer in accepted classical Operator-evaluation spec | Do not reopen in this WP absent a new scope decision |

Ranks express investigation priority, not a committed roadmap. Only LISS-0581
has a Phase 0 proposal here. Lower-ranked candidates require their own
consumer/architecture intake and do not become authorized by this Work Plan.

## Issue Graph

| Issue | Status | Initial size | Current size | Planning record | Depends on | Blocks | Branch |
|---|---|---|---|---|---|---|---|
| [LISS-0581](../issues/LISS-0581-evaluator-coordinate-liveness-successor.md) | done — PR #603 merged and CI passed | M | M | AIP-0581-001 | ADR 0228 accepted | - | `feature/liss-0581-red` (deleted after merge) |
| [LISS-0582](../issues/LISS-0582-evaluator-runtime-plan-eligibility.md) | done — PR #604 merged; repaired-head and main CI passed | M | M | AIP-0582-002 | extraction retained; no later dependency | later dependency delivery still separately gated | `codex/liss-0582-repair-closeout` (documentation only) |
| [LISS-0583](../issues/LISS-0583-evaluator-static-foreach-successor.md) | review — Phase 1 test acceptance pending; separate repair design started | M | M | AIP-0583-002 | LISS-0582 done; LISS-0584 before Green/delivery | static foreach/later dependent delivery | `codex/liss-0583-static-foreach-phase0` |
| [LISS-0584](../issues/LISS-0584-opaque-foreach-wire-arithmetic-repair.md) | review — Phase 2 C all checks passed; record-head rerun and Phase 3 approval | M | M | AIP-0584-001 | LISS-0582 done; A carrier a14ab3af | LISS-0583 Green/delivery | `codex/liss-0584-opaque-wire-arithmetic-phase0` |

## Current rank-3 design gate — 2026-10-05

Current2026-10-06: approved A/B/C locally committed, C=6517c208 all checks pass,
including formerly failing copy smoke. Synchronization-head rerun evidence is
external under `/private/tmp/liss0584-final-*`; then request separate Phase3.
Earlier pending scopes/sanity failures below are historical, no delivery claimed.

Human `Scope／Phase 0設計開始承認` approves design/inventory only. Existing
local LISS-0583 tipb09e3e06 and its historical approvals are retained, not
treated as current repaired-main delivery or new phase authorization. The
[current accepted specification](../specs/evaluator-static-foreach-elaboration.md)
records F01–F08, twelve public imports missing from the old tip, complete
behavior-test requirements and bounded repair-guard disposition. Scoped65 and
adjacent41 baseline tests passed at a287be51; historical scoped evidence, not a
fresh run during acceptance sync. Human `Phase 0 acceptance」の承認` accepts
the dedicated Issue/spec F01–F08 and bounded guard disposition unchanged.
Phase 1 Red execution / limited guard migration separately approved. New tests:
89 passed / 5 failed (four structural, one F05 arithmetic contract mismatch);
consumer/adjacent77 passed on a287be51 + dirty tests/docs. Compiler unchanged.
Next: [test review / F05 disposition](../collaboration/reviews/2026-10-05-liss-0583-phase1-review.md);
implementation allowed no. No automatic deferral or test waiver.

Human `修復の設計開始承認` selects separate repair design on2026-10-05.
LISS-0584 accepted R01–R07 covers inferred-Wire numeric binary validation,
alias/nesting detection and positive neighbors. Existing failing F05 test is
retained, not weakened/excluded. Fresh repair design baseline:1expected failure,
adjacent21passed / numeric12passed; scoped only, no full Green. Human
`専用Issue/spec R01–R07 と Phase 0 acceptance` accepts the dedicated target
unchanged on2026-10-05. Subsequent explicit Phase 1 execution prepares48 cases:
24 expected Red/24 passed; consumer/adjacent74 passed, no source changes.
Human `LISS-0584 Phase 1 Red テストレビュー／acceptance` accepts the
[0584 packet](../collaboration/reviews/2026-10-05-liss-0584-phase1-review.md)
unchanged2026-10-06. Subsequent explicit Phase 2 implementation approval executes
the12-line numeric guard: focused48, consumer/adjacent74 and spec161 pass.
Sanity copy smoke rejects the pre-existing uncommitted0583 spec; full Green
not established. [Current584 verification/handoff](../collaboration/reviews/2026-10-06-liss-0584-phase2-verification.md)
requests reviewed dependency/document separation and commit permission, not
Phase 3 or delivery approval.
Human `はい。整理して` authorizes scope organization2026-10-06;
[A/B/C proposal](../collaboration/reviews/2026-10-06-liss-0584-commit-scope.md)
is prepared (11/4/8 files), not executed. Carrier guard disposition/local
commit permission remain pending; all-blocking sanity gap is not waived.
Phase 2 root2419 pass (4 approved0583 deselections); spec161 pass; sanity fails
copy smoke. Committed test dependency separation remains open.0583 Phase 1
test acceptance remains separate.0583 implementation and a new ADR are not authorized.

## Current repair closeout — 2026-10-05

Separate human delivery approval executed: PR #604 merged at
`458fcbe69b9161be21c2b8f92c8cd2838539e6f9` after all repaired-head PR CI
checks passed. All actual merge-result local blocking checks and main CI also
passed. Subsequent `続けて` authorizes documentation-only synchronization,
not rank 3–6 implementation or later dependency propagation. LISS-0582's
completion process review is recorded in its Issue; WP-0174 remains active.
See the [current trace](../collaboration/traces/2026-09-29-liss-0582-runtime-plan-eligibility.md)
for exact SHAs, environments, CI links and verification boundaries.

## Historical repair gates — 2026-10-05

Scope/Phase 0 start and unchanged [R01–R07 specification](../specs/evaluator-public-import-compatibility-repair.md)
accepted 2026-10-05; human `修復仕様 R01–R07 と Phase 0 acceptance` received.
Restore original-object re-exports, not old bodies or a weakened baseline.
Phase 1 execution separately approved; new repair tests: 14 expected failures /
23 passes. Consumer regression 8 pass; adjacent 52 pass. No production or frozen
baseline edits, commit/push/merge. Same-context review passed on unchanged tests;
human `Phase 1 Red acceptance を承認` received 2026-10-05.
Separate `Phase 2 Green／implementation` approved 2026-10-05. Import-only
repair passes focused37 / consumer8 / adjacent52 and spec161; capture/cmp
byte-equal. Full root2322 passed provisionally, no exclusions. Next: Phase 3
Refactor/review separately approved 2026-10-05; code review passed, no source
or test refactor required. Phase 2 final-SHA checks passed at93c1c86a; review
record commit checks passed atc2112a4f. Human final local verification/review
approved 2026-10-05; no source/test change, final status-commit checks required.
Next: separate delivery authorization, then repaired-head CI; no Issue/WP done
before R06/R07 and completion process review. See the
[review packet](../collaboration/reviews/2026-10-05-liss-0582-repair-phase3-review.md).
Red execution/review/implementation remain separately gated. Prior completion
is historical; delivery approval is not a CI waiver.

## Verification and approval gates

- Phase 0 was a static AST/consumer/spec inventory; it authorized no tests or
  source edits at that time.
- Before Phase 1: accept the successor boundary and Phase 0 packet; inspect
  lifecycle state of existing `_red.py` tests; confirm the exact phase path
  matrix; and obtain separate Phase 1 Red approval. The acceptance inventory
  identifies two coverage gaps: eligible post-call live-out retention and
  Snapshot exclusion, plus structural ownership/delegate assertions.
- Before Phase 2: reviewed Red, separate Phase 2 Green/Implementation approval.
- Before Phase 3: separate Phase 3 approval; inspect body ownership behind any
  compatibility hook and run actual consumers/adjacent suites.
- LISS-0581 Phase 2: implementation and all-blocking tests passed on the dirty
  worktree; see the [verification record](../collaboration/reviews/2026-09-28-liss-0581-phase2-verification.md).
  This is provisional evidence, not final-commit verification. The 131-line
  free-variable walker was moved intact; any readability restructuring belongs
  to the separately approved Phase 3 review, not an assumed Phase 2 expansion.
- Completion: deterministic verification tied to final commit SHA, all
  blocking suites rerun after final commit, status synchronized, process review.
- LISS-0581 Phase 3: `expr_free_vars` is decomposed into named binder, operator,
  and expression-node walkers without changing tests or intended traversal
  behavior. See the [Phase 3 review packet](../collaboration/reviews/2026-09-28-liss-0581-phase3-refactor-review.md).
  Human final review is approved; commit and post-commit verification remain
  pending.

## Applicable process lessons

The detailed application is recorded in LISS-0581 and its proposed spec:
state ownership; private-consumer inventory; narrow callbacks; true successor
ownership; compatibility identity/export rules; clause-to-test reconciliation;
and status drift prevention.

## Planning record

### AIP-0581-001

- Status: proposed
- Created by: Codex desktop, local repository worktree
- Model/reasoning as displayed: N/A; not surfaced by host
- Created: 2026-09-28
- Planning size: M
- Intended route: host agent for bounded stateless decomposition; same-context
  review if the runtime-routing policy requires an agent review packet;
  deterministic AST/import checks and runtime suites for verification.
- Scope: one cross-module liveness family, its compatibility hooks and direct
  consumers; no semantic expansion.
- Estimated context tokens: 8,000–14,000; midpoint 11,000 (planning estimate,
  not actual usage).
- Basis: five small evaluator methods, duplicate frame helpers, reuse by five
  runtime services, existing liveness AST hooks, and direct characterization
  consumers. Verification requires behavior suites across four established
  Trace-Out paths and broad blocking tests.
- Assumptions: approved semantics remain unchanged; existing tests can be
  mapped/reused; no new shared mutable state.
- Confidence: medium; AST walker ownership and live `_red.py` status require
  Phase 0 acceptance reconciliation.
- Revises/supersedes: none.
