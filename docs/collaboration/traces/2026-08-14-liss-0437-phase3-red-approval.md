# LISS-0437 Phase 3 Red approval and execution record

## Approval

- Date: 2026-08-14
- Approved scope: all three Phase 3 Red workstreams
  1. formal `Limit`
  2. binder-aware QPU realization
  3. S02 numerical/source migration boundary
- Authorized operations: create and execute reviewed Red acceptance tests;
  record failures and review findings
- Not authorized: Green implementation, QPU implementation, finite `Limit`
  realization, S02 numerical migration, broad corpus rewrite, or closeout
- Architecture amendment approved: the target profile exposes typed
  `register_mapping`; this updates the contract only and does not authorize
  Green implementation.
- Phase 3 Green minimal implementation approval: **Approved by user** for the
  `EvolutionTargetProfile.register_mapping` field and profile-boundary
  plumbing only. Binder lowering, QPU circuit generation, S02 migration, and
  formal `Limit` execution remain unapproved.

## Red suite

Test file: `tests/test_liss_0437_phase3_red.py`

The suite contains five tests across the three approved workstreams. The two
S02/expanded-Limit tests are explicitly boundary-protection tests: they may
pass before Green because they protect source fidelity and non-rewrite
semantics rather than asserting an unimplemented runtime capability.

The suite asserts:

- typed provenance survives the formal `Limit` AST before realization;
- binder-aware QPU rejection retains provenance, resource estimate, and budget;
  the missing-mapping case passes `register_mapping={}` for
  `Sigma (i In 0..7) { Z[i] }` and expects
  `binder_register_mapping_missing`; the budget case passes the complete
  `{"Sigma": "q[0..7]"}` mapping with a zero-qubit budget and expects
  `resource_budget_exceeded`. Both cases require no allocation or partial
  circuit.
- S02 contains the canonical executable `exp` form and `U_t * psi_sel` before
  numerical migration. The expanded `Limit` form is an optional
  source-fidelity fixture and must not be silently rewritten.
- expanded `Limit` remains a `Limit` boundary and is not silently rewritten.

## Execution

- Command: `python3 tests/test_liss_0437_phase3_red.py`
- Result: **RED**, as required; the runner executes all five tests and reports
  each failure without stopping at the first assertion.
- The approved minimal Green plumbing is present: the target profile now
  accepts typed `register_mapping`. No binder lowering, QPU circuit
  generation, `Limit` realization, or S02 migration Green implementation was
  performed.
- First failing acceptance: formal `Limit` typed provenance is not yet
  present in the current implementation.
- This is an expected pre-Green failure, not an implementation defect to fix
  in this phase.

## Next gate

Each workstream requires independent review of its Red result and a separate
Phase 3 Green implementation approval. A finite executable `Limit` also
requires a separate Architecture decision.

## Independent review loop status

- Review record: `docs/collaboration/reviews/2026-08-14-liss-0437-phase3-red-review-03.md`
- Latest loop terminal state: **ABORT**.
- Reason: the fresh read-only reviewer did not return prioritized findings,
  evidence paths, or a readiness verdict after bounded waiting and an
  interrupt request. No design conclusion or phase approval was inferred.
- Next condition: a fresh user-triggered independent review may resume the
  loop; the current scope remains bounded to Red readiness and the approved
  `register_mapping` field plumbing.

## Review continuation status

- Continuation record:
  `docs/collaboration/reviews/2026-08-14-liss-0437-phase3-red-review-04.md`
- Result: **ABORT** again because the fresh reviewer returned no usable
  findings, evidence, or readiness verdict after bounded waiting and an
  interrupt request.
- No READY conclusion, phase transition, or implementation approval was
  inferred from the missing reviewer output.

## Late review result and disposition

- The delayed reviewer result was received after the review-04 record had
  been written; disposition is recorded in
  `docs/collaboration/reviews/2026-08-14-liss-0437-phase3-red-review-05.md`.
- The only actionable Red-fixture issue was corrected: the budget case now
  uses the same finite `Sigma` binder described by its `register_mapping`.
- Existing explicit Suzuki/runtime and first target-realization code was not
  removed because it is covered by earlier Phase 2/target-realization
  approvals; this residual review does not reopen those accepted slices.
- Typed provenance, distinct mapping/budget rejection, and no-allocation
  metadata remain future Green acceptance conditions. They were not
  implemented under this correction.

## Final re-review

- Review record:
  `docs/collaboration/reviews/2026-08-14-liss-0437-phase3-red-review-06.md`
- Verdict: **READY — Phase 3 Red acceptance artifacts only**.
- The Red loop is complete. This verdict does not approve Phase 3 Green,
  QPU implementation, formal `Limit` implementation, or S02 numerical
  migration.

## Phase 3 Green bounded implementation and review

- Implementation scope approved by user on 2026-08-15: typed mapping
  validation, distinct mapping/budget rejection, common target-rejection
  provenance, and allocation-before-rejection safety.
- Implementation result: complete for the bounded slice.
- Review record:
  `docs/collaboration/reviews/2026-08-15-liss-0437-phase3-green-review-01.md`
- Review verdict: **READY for the approved bounded slice**.
- Verification: Red runner reports 1/6 failing (formal `Limit` provenance only);
  explicit-evolution surface and evolve-until regression checks passed;
  compilation and diff checks passed.
- Remaining gates: formal `Limit` implementation, S02 numerical migration,
  live QPU deployment, and broader Phase 3 closeout remain separate.

## Formal Limit provenance bounded implementation

- User approval: 2026-08-15 for source-preserving rejection provenance only.
- Implementation: `CompileResult.evolution_provenance` now retains the typed
  envelope; target lowering rejects formal `Limit` with
  `EVOLUTION_REALIZATION_REQUIRED` before allocation and does not rewrite it
  to `exp`.
- Review record:
  `docs/collaboration/reviews/2026-08-15-liss-0437-limit-provenance-review-02.md`
- Verdict: **READY for the approved limited scope**.
- Finite `Limit` execution remains unimplemented and requires a separate
  architecture/implementation approval.

## ADR 0210 architecture approval

- User approval received: 2026-08-15.
- ADR 0210 status: **Accepted**.
- Accepted boundary: finite `Limit` realization requires explicit target
  method, order/steps, and error budget; no silent `exp` rewrite or compiler-
  selected `N`.
- Implementation permission: not granted by ADR acceptance. Phase 1 Red and
  subsequent implementation approvals remain separate.
