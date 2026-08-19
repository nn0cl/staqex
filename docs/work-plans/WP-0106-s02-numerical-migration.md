# WP-0106: S02 numerical migration

| Field | Value |
|---|---|
| Status | **planned — awaiting independent design review and phase approval** |
| Local Issue | [LISS-0443](../issues/LISS-0443-s02-numerical-migration.md) |
| Specification | [S02 numerical migration](../specs/staqex-s02-numerical-migration.md) |
| Predecessor | [WP-0105](WP-0105-s02-corpus-migration-inventory.md) |
| Implementation permission | **No** |

## [DESIGN CHECK]

- **Scope and expected behavior:** Define a reproducible numerical comparison
  for S02 after the explicit evolution reconciliation, without changing the
  source meaning or silently converting the formal lane.
- **Specifications and files inspected:** LISS-0442/WP-0105, LISS-0438/WP-0104,
  ADR 0210, the S02 acceptance/design documents, current source/Host/baseline,
  and the independent-review perspectives ledger.
- **Component boundaries:** Future S02 source/Host/test evidence only; no
  provider adapter, SDK, live submission, or new Kernel boundary is proposed.
- **Applicable constraints:** frozen baseline, exact/finite provenance,
  fail-closed rejection, terminal measurement, and explicit approval gates.
- **Independent review lenses:** contract completeness; source fidelity;
  realization/fail-closed behavior; migration/regression safety; evidence
  hygiene; phase discipline; architecture boundaries; type/validity closure;
  and state/physics safety.
- **Verification:** future frozen-input comparison, direct compile/run,
  provenance/rejection assertions, full regression, and diff inspection.

## Planned work units

1. Freeze the numerical input, seed, source identity, and baseline contract.
2. Define exact-local and finite-target comparison records and tolerances.
3. Create reviewed Phase 1 Red tests only after the scenarios and paths are
   approved.
4. Request separate Phase 2 implementation approval.
5. Re-run numerical and full regression evidence, then request independent
   review.

## Exclusions

- S02 numerical execution before phase approval;
- automatic finiteization or hidden `Limit` conversion;
- Provider SDK, credentials, network, and live QPU submission;
- benchmark retuning or baseline replacement;
- unrelated example or compiler redesign.

WP-0105 closes with the inventory and evidence needed to make this task
reviewable. It does not authorize any work unit above.
