# WP-0174: Evaluator residual responsibility successors

| Field | Value |
|---|---|
| Status | active — LISS-0581 complete; next residual candidate requires separate intake |
| Size | M |
| Parent | WP-0160 / core module decomposition |
| Scope approval | Evaluator residual-responsibility Architecture Path Phase 0 investigation approved 2026-09-28 |
| Completed candidate | LISS-0581 — coordinate liveness and Trace-Out successor; architecture accepted by ADR 0228 |
| Current Next Issue | [LISS-0582](../issues/LISS-0582-evaluator-runtime-plan-eligibility.md) — Phase 2 Green implemented; Phase 3 review pending |

## Goal

Continue reducing Evaluator-owned implementation bodies by selecting cohesive
successors from current consumer/state evidence, not by line count alone.
Preserve source meaning, public/private compatibility, diagnostics, and
Evaluator's unique mutable-state ownership.

## Inventory and order proposal

| Rank | Residual responsibility | Evidence | Disposition |
|---:|---|---|---|
| 1 | Coordinate liveness and Trace-Out: five Evaluator helpers and duplicate frame helpers | Shared consumers in frames, pipes, evolution, execution, observation; tied to existing ADR 0138/0142/0153/0158 behavior | LISS-0581 done; implementation commit passed 2,280 tests; PR delivery pending GitHub CI and merge |
| 2 | Runtime-plan eligibility/projection: callable eligibility, Operator-attribute walk, unit projection, first-family checks | Partly routed by `evaluation/orchestration.py`; close to semantic-plan eligibility and existing canonical/legacy boundaries | LISS-0582 Phase 1 Red accepted; Phase 2 Green approval pending; do not combine with liveness |
| 3 | Static `forEach` expansion | 51-line evaluator body, calls binding dispatch for each expanded wire | Separate execution/loop boundary study; avoid enlarging `execution.py` without line/body budget review |
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
| [LISS-0582](../issues/LISS-0582-evaluator-runtime-plan-eligibility.md) | in progress — Phase 2 Green implemented; Phase 3 review pending | M | M | AIP-0582-001 | none | - | `feature/liss-0582-runtime-plan-eligibility` |

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
