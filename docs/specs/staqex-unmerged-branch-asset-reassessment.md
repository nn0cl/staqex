# Staqex Unmerged Branch Asset Reassessment Specification

## Acceptance requirements

1. Every unmerged branch is identified by exact local branch name and source
   commit.
2. The inventory records whether each commit is equivalent to current `main`,
   conflicts with current files, or introduces a distinct proposal.
3. Every distinct proposal is checked against the current canonical Issue,
   Spec, WP, and ADR rather than treated as an authority.
4. A proposal passes the physicist-first check only when its source/blackboard
   meaning is preserved and machine convenience does not force a dialect shift.
5. Ideal expression, finite `Realize`/discretization, simulator execution, and
   QPU capability remain explicit separate boundaries.
6. State-first semantics, terminal `measure`, provenance, and fail-closed
   unsupported realization behavior are preserved.
7. A useful proposal is ported selectively into current design artifacts with
   a new or updated Issue/WP/Spec/ADR before implementation begins.
8. An obsolete branch is deleted only after its classification, disposition,
   source commit, and deletion gate evidence are recorded.
9. No inventory result alone grants implementation, technology, phase, merge,
   or deletion approval.

## Required evidence

- deterministic branch and worktree inventory;
- `git cherry` or equivalent duplicate-commit evidence;
- conflict/diff evidence against current `main`;
- selected review lenses and rationale;
- disposition record for every branch;
- verification of each ported design artifact.

## Explicit exclusions

No blind merge, broad cherry-pick, provider/QPU work, syntax redesign, or
reopening of settled rows without a concrete requirement and new approval.
