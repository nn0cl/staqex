# LISS-0444 consumer-wide migration — Phase 2 Green trace

## Approved scope

The user approved Phase 2 Green for the reviewed Red contract. The slice
covers explicit-evolution fallback suppression, old QPU helper removal,
diagnostic binder authority, and the explicit-evolution `symbolic_ir`
boundary. Provider SDK, live QPU, S02, solver work, and full legacy retirement
were excluded.

## Implementation

- Explicit evolution without an executable canonical projection now rejects
  with an empty QASM artifact before AST lowering.
- `_lowering_policy_projection` and `_explicit_evolution_projection` were
  removed from `qpu_ir.py`.
- `qpu_ir_diagnostics()` consumes canonical projection errors and no longer
  directly calls `lower_finite_binders()`.
- Explicit-evolution compilation no longer publishes `symbolic_ir`; other
  un-migrated symbolic consumers retain a compatibility projection.
- Existing finite Suzuki/binder compatibility lowering and diagnostic codes
  were preserved.

## Verification

- Bounded target suites: **98 passed**.
- Full `.venv/bin/pytest -q`: **1642 passed**.
- `git diff --check`: passed.
- Independent review:
  [`2026-08-20-liss-0444-consumer-migration-phase2-green-review-01.md`](../reviews/2026-08-20-liss-0444-consumer-migration-phase2-green-review-01.md)
  returned `READY` for this bounded slice.

## Remaining boundary

Finite Suzuki/binder canonical instruction projection, non-explicit
`symbolic_ir` retirement, general QASM fallback retirement, and residual
AST-derived diagnostics remain deferred to future approved phases.
