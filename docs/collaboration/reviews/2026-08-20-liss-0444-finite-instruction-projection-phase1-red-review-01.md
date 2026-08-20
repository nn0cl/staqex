# Independent Context Review — finite instruction projection Phase 1 Red

| Field | Value |
|---|---|
| Trigger | User-approved Phase 1 Red for finite Suzuki/binder canonical instructions |
| Scope | Red tests, finite fallback boundary, provenance, state safety, Realize boundary |
| Excluded | Phase 2 implementation, provider/live QPU, S02, solver work |
| Verdict | **READY for Phase 1 Red; Phase 2 remains unapproved** |
| Verification | 4 failed; no collection errors; `git diff --check` passed |

## Findings and disposition

| Priority | Finding | Disposition |
|---|---|---|
| P1 | Positive tests initially checked only non-empty instructions and used an invalid binder fixture | accepted / resolved; gate opcode/wire/provenance checks and existing linear fixture applied |
| P1 | Direct `using Suzuki(...)` boundary needed explicit documentation | accepted / resolved; identified as the existing explicit finite surface, not new implicit finiteization |
| P2 | Binder opcode allow-list assertion could be strengthened | deferred; current wire/provenance assertion is sufficient for Red and Green can add exact gate vocabulary |

## Evidence

- `tests/test_liss_0444_finite_instruction_projection_red.py` has four
  intentional failures: missing canonical gate instructions and both
  compatibility fallback calls.
- The Suzuki test verifies non-Measure opcode, wires, and source node
  provenance; the binder test verifies wires and provenance with a linear-safe
  existing fixture.
- WP and trace explicitly preserve source-visible `Realize` as the formal-limit
  conversion boundary and treat direct `using Suzuki(...)` as the already
  accepted finite surface being migrated.

## Reusable perspectives

Contract completeness; source-to-domain fidelity; state and physics safety;
realization/fail-closed behavior; canonical authority; projection conservation;
executable projection integrity; migration safety; phase discipline.

## Terminal state

`COMPLETE` for the Phase 1 Red review loop. Phase 2 Green requires separate
typed user approval.
