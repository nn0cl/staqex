# ADR 0214: Unmerged Branch Asset Reassessment Policy

| Field | Value |
|---|---|
| Status | **Accepted** (Architecture approval 2026-08-25) |
| Scope | Project operation and design-asset lifecycle |
| Issue | [LISS-0453](../../issues/LISS-0453-unmerged-branch-asset-reassessment.md) |
| WorkPlan | [WP-0116](../../work-plans/WP-0116-unmerged-branch-asset-reassessment.md) |

## Context

Unmerged branches can contain useful physics/design reasoning, duplicate
commits, obsolete implementations, or unresolved architectural proposals.
Direct merging is unsafe when current canonical documents, language axioms,
or realization boundaries have moved on.

## Decision proposed

Treat an unmerged branch as evidence, never as current authority. Reassess it
against the current `main` using the blackboard-first and ideal/realization
separation rules. Port only accepted design content into current artifacts.
Delete the old branch only after disposition, source-commit preservation, and
worktree safety are recorded.

## Consequences

- useful historical reasoning remains recoverable and reviewable;
- stale implementation cannot silently revive old semantics;
- new work receives current Issue/WP/Spec/ADR boundaries;
- cleanup is delayed until evidence and disposition are complete;
- inventory and disposition records add modest process overhead.

## Rejected alternatives

- **Merge every unmerged branch:** violates current authority and can revive
  stale physics or architecture.
- **Delete every unmerged branch:** loses potentially useful design evidence.
- **Cherry-pick by commit age or file overlap:** does not establish semantic or
  acceptance compatibility.

## Approval boundary

Architecture approval accepts this process boundary only. It does not approve
any branch content, implementation, technology, phase, merge, or deletion.
Each redesign candidate still requires its own current Issue/WP/Spec and typed
phase approval.
