# Review Summary: LISS-0554 Phase 2 Architecture Conflict

## Finding

The approved LISS-0554 design requires `semantic_ir=None` to reject before any
IR construction. The existing accepted LISS-0446 public-entry contract
requires a unit-only compatibility call to build one invocation-local
canonical projection and emit QASM. Applying the LISS-0554 guard makes the
former pass but the latter fail.

## Disposition

The Adjudicator approved the layered resolution: direct `QASM3Emitter` calls
require explicit canonical IR, while the public unit-only facade may perform
one invocation-local build and pass it explicitly. The guard was previously
removed, so no conflicting production implementation remains.

## Evidence

- LISS-0554 exact Red contract: passes with the guard.
- LISS-0446 unit-only compatibility regression: fails with the guard,
  specifically `test_unit_only_compatibility_builds_at_most_once`.
- The current branch has no emitter source diff from the attempted guard.

## Decision recorded

Preserve LISS-0446 unit-only compatibility while enforcing the strict
canonical-input requirement at the direct emitter boundary. LISS-0554's Red
test is narrowed to direct `QASM3Emitter.emit_unit()` calls.

Isolation used: `same_context`, weaker than `separate_context`.
