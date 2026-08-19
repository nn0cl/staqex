# Staqex S02 numerical migration

| Field | Value |
|---|---|
| Status | **Phase 3 refactor complete — final review pending** |
| Issue | [LISS-0443](../issues/LISS-0443-s02-numerical-migration.md) |
| WorkPlan | [WP-0106](../work-plans/WP-0106-s02-numerical-migration.md) |
| Predecessor inventory | [LISS-0442](../issues/LISS-0442-s02-corpus-migration-inventory.md) |
| Authority | ADR 0210, explicit evolution surface, and the frozen S02 baseline |

## Purpose

Specify how S02 numerical behavior may be compared after the source-visible
exact/formal/finite evolution separation is complete. This document is a
planning boundary, not permission to change source, tests, or benchmark data.

## Frozen boundaries

1. `U_t` remains the exact local evolution lane.
2. Formal `Limit` remains mathematical source meaning and is not submitted.
3. `Realize(...)` is the only explicit finite-target boundary.
4. Unsupported finite lowering rejects before allocation and leaves no partial
   program, qubit assignment, or target provenance.
5. The pre-migration fixed-seed baseline remains reference evidence; it is not
   silently rewritten to match a new implementation.
6. Host inputs and classical scoring remain outside Kernel quantum state
   semantics.

## Future acceptance outline

- Given frozen S02 inputs and seed, the exact-local lane produces a reproducible
  comparison record with a deterministic `numeric_identity` containing the
  source hash, Host-input digest, seed schedule, baseline identity, and
  realization policy.
- Given the same source meaning, a finite target lane is either explicitly
  realized with recorded policy fields or explicitly capability-rejected.
- When a numerical metric changes, the record identifies the source hash,
  policy, Host-input digest, baseline identity, inputs, seed, tolerance, and
  provenance. Success and failure records use the same identity shape.
- A rejected finite lane produces diagnostics only and no partial execution
  artifacts.
- No provider-specific submission is required for this task.

The concrete Red scenarios, allowed files, and tolerances must be reviewed
before Phase 1 begins. They are intentionally not invented in this planning
split.
