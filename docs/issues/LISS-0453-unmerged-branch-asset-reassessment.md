# LISS-0453: Unmerged Branch Asset Reassessment

- Status/phase: **design intake**
- Type / priority: architecture / P1
- WorkPlan: [WP-0116](../work-plans/WP-0116-unmerged-branch-asset-reassessment.md)
- Specification: [Unmerged Branch Asset Reassessment](../specs/staqex-unmerged-branch-asset-reassessment.md)
- Proposed authority: [ADR 0214](../architecture/adr/0214-unmerged-branch-asset-reassessment-policy.md)

## Objective

Define a safe, physicist-first process for re-evaluating unmerged local branch
work before cleanup. A branch is not merged merely because it contains useful
ideas, and it is not discarded merely because its original implementation is
stale.

## Scope

- inventory unmerged branch commits and worktree ownership;
- compare each proposal with current Issue, Spec, WP, ADR, and `main`;
- classify each branch as duplicate, historical reference, redesign candidate,
  or discardable;
- selectively port accepted design evidence into current artifacts;
- delete the old branch only after its disposition and source commit are
  recorded.

## Non-goals

- direct merge or blind cherry-pick of stale branches;
- reviving settled work without a concrete requirement;
- implementation, provider selection, or QPU submission;
- changing Staqex syntax or semantics during the inventory phase.

## Current boundary

The remaining unmerged branches are local-only and several are stale relative
to current canonical documents. They are evidence sources, not authorities.
The blackboard expression remains primary; ideal meaning must remain distinct
from finite realization and QPU capability.

## Gate

Architecture review and acceptance of ADR 0214/Spec are required before any
policy change or implementation-oriented port. Each redesign candidate then
requires its own Issue/WP/Spec and typed phase approval.
