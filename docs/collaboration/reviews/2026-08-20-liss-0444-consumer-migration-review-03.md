# LISS-0444 consumer migration review 03

## Scope

- Approved batch: canonical QPU projection for ForEach gates, terminal
  measurement, QFT/CQFT decomposition, logical shape, resource rejection, and
  source provenance.
- Excluded: `lowering_policy`, `explicit_evolution`, `binder_lowering`,
  Symbolic IR retirement, evaluator migration, provider SDK, live QPU, and S02
  numerical migration.
- Independent context: fresh read-only review; no approval or implementation
  authority.

## Verdict

- Representative QPU projection batch: `READY`.
- WP-0107 consumer-wide migration: remains open.

## Evidence

- CQFT canonical operation preserves `logical_qubits=4`, `control=0`, and
  `target_offset=1`; emitted controlled interactions use `CX(0, 1)` and the
  target register wires after the control.
- Oversized registers produce `E_QPU_RESOURCE_UNSUPPORTED`, no instructions,
  and empty QASM without entering the legacy fallback.
- Every decomposed instruction receives the operation's canonical
  `source_node_id` directly; emitter validates membership and body fingerprint.
- Bounded regression: `47 passed` before the final CQFT assertion correction;
  `32 passed` after the final targeted correction.
- Full regression after the final correction: `1630 passed in 293.09s`.
- `git diff --check`: passed.

## Remaining work

The reviewer confirmed that these AST-derived consumer paths remain and are
now explicitly listed in WP-0107 and the Phase 3 trace:

- `lowering_policy` / Suzuki policy projection
- `explicit_evolution` projection
- `binder_lowering` projection
- routing and finite-lowering helpers
- QASM fallback retirement and Symbolic IR/evaluator migration

These are not silently treated as complete and require a subsequent bounded
approval.

## Terminal state

- Review loop: `COMPLETE` for this approved batch.
- Next condition: a new bounded scope and approval before migrating the
  remaining policy/evolution/binder consumers.
