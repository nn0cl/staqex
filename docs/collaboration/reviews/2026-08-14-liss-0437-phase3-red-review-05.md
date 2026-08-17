# LISS-0437 Phase 3 Red Review 05 — late-result disposition

## Trigger and scope

- Trigger: continuation after review-04 `ABORT`; late result from its fresh
  independent reviewer was received.
- Scope: Phase 3 Red acceptance artifacts and the approved existing Phase 2 /
  first target-realization boundaries.
- Branch: `codex/wp-0100-explicit-evolution-surface`.
- Allowed changes: Red test and review/trace documentation only. No new
  binder, provenance, allocation, `Limit`, or S02 Green implementation.

## Independent review result

The reviewer returned `NOT READY` with these findings:

1. P1 alleged that the current explicit Suzuki lowering exceeded the latest
   minimal `register_mapping` approval.
2. P1 observed that mapping and budget rejection are not implemented in the
   current residual target slice.
3. P1 observed that typed provenance and no-allocation fields are not present
   for the residual Red cases.
4. P2 stated that the phase gate remains stopped.

## Disposition

### Finding 1 — existing approved implementation boundary

- Disposition: `rejected`.
- Authority: primary agent under the delegated review policy.
- Evidence: LISS-0437 records Phase 2 Green approval; the Phase 2 independent
  implementation review records the explicit runtime path and QPU rejection
  boundary; the ADR records the bounded first target-realization slice as
  independently READY. The current diff adds only the typed profile field;
  the existing Suzuki path is not a new implementation in this correction.
- Rationale: the finding conflates the residual Phase 3 Red approval trace
  with the already approved earlier slices. Removing the existing path would
  violate the accepted implementation history and is outside this review.
- Design deviation: no.

### Finding 2 — mapping/budget behavior is not yet implemented

- Disposition: `rejected` as a Red-readiness defect; retained as an expected
  future Green gap.
- Authority: primary agent under the delegated review policy.
- Evidence: the tests intentionally fail while requiring distinct future
  capability decisions; the trace and WP state that binder-aware lowering is
  a later Phase 3 workstream. No Green implementation is authorized here.
- Correction: the budget Red fixture was corrected to use the same finite
  `Sigma (i In 0..7) { Z[i] }` binder as its typed mapping.
- Design deviation: no.

### Finding 3 — typed provenance/no-allocation fields are not present

- Disposition: `rejected` as a Red-readiness defect; retained as an expected
  future Green gap.
- Authority: primary agent under the delegated review policy.
- Evidence: the Red runner reports the three expected assertion failures;
  the tests are the acceptance contract for the not-yet-approved residual
  implementation. Adding these production fields now would be Phase 3 Green,
  not a correction to the Red phase.
- Design deviation: no.

### Finding 4 — gate remains stopped

- Disposition: `accepted`.
- Authority: primary agent under the delegated review policy.
- Rationale: the latest residual Red workstream has not received a READY
  independent review verdict and no Phase 3 Green approval is inferred.
- Design deviation: no.

## Verification

- `python3 tests/test_liss_0437_phase3_red.py`: `RED`, 3/5 failing as expected.
- `python3 -m py_compile compiler/staqex/backend/qasm/lower.py tests/test_liss_0437_phase3_red.py`: passed.
- `git diff --check`: passed.

## Terminal status

- Status: `COMPLETE` for this review/correction iteration.
- Basis: the one actionable Red-fixture mismatch was corrected; remaining
  findings are either context-conflicting or intentionally represent the
  unimplemented residual Green scope. Phase transition remains blocked by its
  separate approval gate.
- Reusable lenses: approval-to-diff history, Red-versus-Green distinction,
  orthogonality of mapping and budget rejection, typed provenance across
  rejection, and no-allocation invariants.
