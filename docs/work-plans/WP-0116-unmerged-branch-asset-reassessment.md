# WP-0116: Unmerged Branch Asset Reassessment

| Field | Value |
|---|---|
| Status | **design intake** |
| Issue | [LISS-0453](../issues/LISS-0453-unmerged-branch-asset-reassessment.md) |
| Specification | [Unmerged Branch Asset Reassessment](../specs/staqex-unmerged-branch-asset-reassessment.md) |
| Proposed authority | [ADR 0214](../architecture/adr/0214-unmerged-branch-asset-reassessment-policy.md) |
| Path | Architecture Path |

## Work units

1. Build a branch inventory: source commit, unique/equivalent commits,
   `main` divergence, conflict state, worktree ownership, and affected files.
2. Apply the physicist-first review: blackboard fidelity, ideal meaning,
   explicit finite realization, QPU boundary, State/Measure safety, and
   provenance.
3. Classify each branch as `duplicate`, `reference`, `redesign-candidate`, or
   `discard` with evidence and disposition authority.
4. For redesign candidates, create or update the current Issue/WP/Spec/ADR;
   do not import stale implementation mechanically.
5. Re-verify the ported design and record the original commit hash before
   deleting the obsolete branch.

## Deletion gate

An old branch may be deleted only when its disposition is recorded, any useful
design has been ported, no worktree or uncommitted work depends on it, and the
source commit remains recoverable from the trace or an accepted archival
reference.

## Approval boundary

This WP authorizes design inventory only after Architecture approval. It does
not authorize implementation, phase transition, ADR acceptance, or deletion
of an unmerged branch before its disposition is recorded.
