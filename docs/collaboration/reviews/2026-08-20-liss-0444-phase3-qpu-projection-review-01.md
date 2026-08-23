# LISS-0444 Phase 3 QPU projection review 01

## Trigger and boundary

- Trigger: user-approved Phase 3 representative QPU IR/QASM projection slice.
- Date: 2026-08-20.
- Issue / Spec / WP / ADR: LISS-0444 / scientific semantic core / WP-0107 /
  ADR 0211.
- Branch: `codex/liss-0438-residual-reconciliation`.
- Reviewer context: fresh independent read-only context.
- Allowed review paths: `compiler/staqex/qpu_ir.py`,
  `compiler/staqex/pipeline.py`, `compiler/staqex/backend/qasm/emitter.py`,
  the bounded semantic-core tests, and related design/traces.
- Excluded actions: edits, approval, provider SDK, live QPU, S02 migration,
  and solver expansion.

## Lenses

- Canonical authority and implementation reality
- Projection conservation and authority reachability
- Source-to-domain fidelity
- Realization and fail-closed behavior
- Migration/regression safety
- Phase and approval discipline

## Finding summary

The reviewer returned `NOT READY` for a complete consumer-wide Phase 3
migration. The representative slice is implemented and verified, but the
following remain visible in the current implementation:

1. QPU instruction/shape/lowering helpers still read the AST directly, so the
   canonical IR currently supplies provenance and entry authority but not all
   semantic fields.
2. QASM retains a legacy `lower_unit_to_circuit()` fallback.
3. `symbolic_ir` remains a parallel compatibility projection.
4. Instruction-level provenance is not linked to canonical node IDs.
5. Direct `QpuProgram` emission does not validate canonical consistency.
6. Consumer-wiring tests do not yet exercise all of those negative boundaries.

Evidence: reviewer cited `qpu_ir.py:171-265,611-643`,
`backend/qasm/emitter.py:82-100,102-167`, `pipeline.py:218,850-900`, and
`tests/test_scientific_semantic_core_red.py:170-176`.

## Disposition

| ID | Disposition | Authority | Rationale |
|---|---|---|---|
| P3-QPU-01..06 | `deferred` | primary agent under accepted WP boundary | These are valid migration findings, but resolving them changes the consumer set, retirement behavior, and provenance contract beyond the approved representative projection slice. They are recorded as the next bounded migration scope, not silently implemented. |
| P3-QPU-07 | `accepted` | primary agent under accepted WP boundary | The review exposed stale approval/status records. WP-0107, LISS-0444, open-work register, and the Phase 3 trace now record the user's 2026-08-20 representative-slice approval and the remaining migration boundary. |

No finding changes ADR 0211, the accepted semantic authority, or the explicit
exclusions. No user/Adjudicator decision is required to record the current
partial status; a new implementation batch is required before resolving the
deferred migration findings.

## Verification and terminal state

- Bounded regression: `32 passed`.
- Full regression: `1621 passed in 280.31s`.
- `git diff --check`: required before handoff.
- Review terminal state: `ABORT` for the broader migration review because the
  deferred findings require a new bounded implementation decision; the
  approved representative slice itself is verified.
- User/Adjudicator decision required: approve or reject a separately bounded
  consumer-wide migration slice before implementation continues.
- Next review condition: after that decision and any approved implementation,
  run a fresh review against current artifacts.
