# LISS-0449: Ideal Expression and Finite Realization Boundary

| Field | Value |
|---|---|
| Status | **open** |
| Phase | **phase-2-green** |
| Type / priority | architecture / P0 |
| Initial size | XL |
| Current size | XL |
| WorkPlan | [WP-0112](../work-plans/WP-0112-ideal-expression-realization-boundary-review.md) |
| Specification | [Ideal Expression and Finite Realization Boundary](../specs/staqex-ideal-expression-realization-boundary.md) |
| Related authority | ADR 0209, ADR 0210, ADR 0211, [ADR 0212](../architecture/adr/0212-ideal-meaning-and-finite-realization-boundary.md) |
| Dependencies | none |
| Implementation approval | granted for Phase 2 Green; Phase 3 not granted |

## Objective

Define a boundary in which ideal blackboard expressions are representable and
source-owned, while finite QPU realization remains explicit.

## Acceptance direction

- `Limit`, exact exponentials, and ideal `Evolve` retain semantic meaning when
  the target cannot execute them.
- `Realize` marks the explicit transition to finite target realization.
- QPU rejection does not erase or replace the ideal semantic representation.
- Exactness, approximation method, order, steps, error budget, and provenance
  are observable.
- Any conflict with ADR 0209/0210/0211 is resolved by a new accepted ADR.

## Exclusions

Provider SDK, live QPU, S02 numerical migration, solver, syntax rewrite, and
production implementation are excluded.

## Approval boundary

Phase 1 Red is complete. The user approved Phase 2 Green for the bounded
implementation and regression tests recorded in the work trace. Phase 3,
merge/push, and any provider/live-QPU work remain unapproved.

Approval evidence: `docs/collaboration/traces/2026-08-20-liss-0449-0451-phase2-green.md`.
