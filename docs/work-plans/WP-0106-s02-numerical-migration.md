# WP-0106: S02 numerical migration

| Field | Value |
|---|---|
| Status | **final-review-ready — Phase 3 refactor complete; final review pending** |
| Local Issue | [LISS-0443](../issues/LISS-0443-s02-numerical-migration.md) |
| Specification | [S02 numerical migration](../specs/staqex-s02-numerical-migration.md) |
| Predecessor | [WP-0105](WP-0105-s02-corpus-migration-inventory.md) |
| Implementation permission | **Phase 3 refactor completed; final review pending** |
| Phase 1 trace | [2026-08-19 Phase 1 Red](../collaboration/traces/2026-08-19-liss-0443-phase1-red.md) |
| Phase 2 review | [2026-08-19 Phase 2 Green review](../collaboration/reviews/2026-08-19-liss-0443-phase2-green-review.md) |
| Phase 2 re-review | [2026-08-19 Phase 2 re-review](../collaboration/reviews/2026-08-19-liss-0443-phase2-rereview-01.md) |
| Final review | [2026-08-19 final Phase 2 review](../collaboration/reviews/2026-08-19-liss-0443-phase2-rereview-02.md) |

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
3. Create reviewed Phase 1 Red tests for source identity, actual realization
   policy, and atomic finite-lane rejection.
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

Phase 1 Red is complete. After typed approval, the minimum Phase 2 Green
implementation records the composite `numeric_identity` in S02 numeric result
metadata without changing numerical behavior. The repository `.venv` resolved
the evidence path: LISS-0403 pytest completed 4/4 in 188.66s after the Phase 3
refactor. Phase 3 improves helper naming, responsibility separation, and test
readability without changing assertions or behavior. The WP is
`final-review-ready`; final review is pending.
