# LISS-0444 finite instruction projection — Phase 2 Green trace

## Gate and scope

- User approval: bounded Phase 2 Green implementation approved 2026-08-20.
- Included: source-derived finite Suzuki/binder gate projection, canonical
  QPU instruction/QASM consumption, fail-closed invalid order handling,
  provenance/instruction integrity tests.
- Excluded: consumer-wide AST fallback retirement, provider SDK, live QPU,
  S02 numerical migration, solver expansion, and implicit finiteization.
- Formal `Realize`/`Limit` source boundary remains unchanged.

## Implementation result

- Valid finite `using Suzuki(...)` and finite binder paths emit canonical QPU
  instructions with opcode, wires, parameter, Suzuki step/order comments,
  source-node identity, and provenance preserved.
- Projection errors are atomic: QPU instructions and QASM are empty, including
  terminal Measure, and no default order/policy is synthesized.
- QASM validates canonical finite gates and Measure operations against the
  source-derived projection. Recomputed fingerprints cannot authorize
  instruction mutation.
- Non-finite and not-yet-migrated compatibility paths retain their documented
  fallback boundary; no claim of consumer-wide migration is made.

## Review loop

- Independent contexts reviewed the Red contract, implementation, fail-closed
  behavior, partial-artifact behavior, projection symmetry, and evidence.
- Findings were accepted/rejected/deferred within the approved phase boundary;
  accepted findings were corrected and fresh contexts re-reviewed the current
  artifacts.
- Final independent review: **READY / COMPLETE**.

## Verification

- Related suite: **26 passed**.
- Full regression: **1650 passed**.
- `git diff --check`: passed.
