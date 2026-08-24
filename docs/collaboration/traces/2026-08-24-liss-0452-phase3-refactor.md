# LISS-0452 Phase 3 Refactor Closeout

## [DESIGN CHECK]

- Scope and expected behavior: close Phase 3 for the bounded S02
  documentation boundary slice without changing program or runtime behavior.
- Specifications and files inspected: LISS-0452, WP-0115, the proposed S02
  boundary specification, the Phase 0 audit/reviews, the Red test file, and
  the README/source pair.
- Component boundaries, ports/adapters, and VO/DTO candidates: none added;
  the README documents existing source, host-report, and target-boundary
  contracts.
- Applicable constraints: preserve blackboard spelling, exact-local versus
  finite-realization separation, fail-closed QPU scope, terminal measurement,
  and the no-provider/no-numerical-migration boundary.
- Decisions, assumptions, and unresolved ambiguities: no refactor of runtime
  or language code is justified by this slice. The example remains partial and
  SIM-only; additional S02 numerical or provider work remains separate.
- Included and omitted AI context: included the bounded Issue/WP/spec, audit,
  reviews, README/source, host report, and focused tests; omitted unrelated
  examples, providers, and numerical migration implementation.
- Task routing: deterministic documentation inspection and local tests; no
  AI-generated runtime data is consumed.
- Independent review lenses selected and why: source-to-domain fidelity,
  realization/fail-closed behavior, contract completeness, readability,
  migration safety, and phase/approval discipline.
- Verification plan: rerun the focused Red/regression suite, source compile
  check, and `git diff --check`; independent Phase 3 review is required before
  completion PR status can advance.

## Phase 3 approval

- Approval type: Phase 3 Refactor.
- Approved by user: current task message.
- Implementation permission: limited to the bounded documentation/readability
  slice; no runtime or language implementation permission inferred.
- Post-review: required.

## Refactor result

The README's boundary inventory was organized into four explicit researcher-
facing stages: blackboard equation, ideal Staqex expression, explicit finite
realization, and QPU/QASM projection. It records the partial classification,
the deterministic `QASM_TROTTER_UNSUPPORTED_H` rejection, the absence of a
partial program/target provenance, and the absence of live QPU submission.
The state names now match `main_selection.sqx` (`psi_0`, `psi_sel`,
`psi_final`). No tests or production code were changed in Phase 3.

## Verification

```text
./.venv/bin/python -m pytest \
  tests/test_liss_0452_s02_example_boundary_red.py \
  tests/test_liss_0438_residual_reconciliation_red.py -q
9 passed in 0.13s

./.venv/bin/python -m compiler.staqex check \
  examples/showcase/S02_drug_discovery/main_selection.sqx
ok — no hard compile diagnostics

git diff --check
passed
```

## Reviewer empathy summary

- A physicist can recover the equation, ideal meaning, explicit finite method,
  and target limitation without mistaking QPU rejection for loss of meaning.
- A programmer can find the exact rejection code and atomic no-artifact result
  without inferring provider behavior from the example.
- A future maintainer can see that this is a partial, SIM-only example and
  that numerical migration and provider integration remain separate tasks.

## Independent Phase 3 review outcome

- Review: `docs/collaboration/reviews/2026-08-24-liss-0452-phase3-review-01.md`.
- Verdict: **NOT READY**; terminal state **ABORT**.
- P1 unresolved decision: direct finite-target rejection currently reports an
  empty gate/program envelope but `n_qubits=1` and no provenance, while the
  generic QPU rejection contract expects zero qubits and provenance-bearing
  rejection. Whether the one-qubit shell is intentional or must be removed is
  an unresolved contract decision; no implementation change is inferred.
- Additional P2 observations: source and host realization parameters are
  duplicated without a comparison assertion; WP branch wording still says
  “Phase 0 corpus audit”. These are not corrected while the P1 contract
  decision remains unresolved.

## User decision and accepted correction

- User decision: choose the generic fail-closed rejection contract (option 2).
- Correction commit: `6f65e6cd` (`fix: make S02 target rejection fail closed`).
- Changed lowering rejection envelopes to `n_qubits=0`, `n_bits=0`, empty
  gates, no allocation, no allocated qubits, no partial program, and
  rejection provenance containing the code and `target_plan=None`.
- Updated the S02 host report so rejection provenance cannot be interpreted as
  successful target-plan provenance.
- Added a direct S02 lowering contract test covering the complete envelope.

## Independent Phase 3 re-review outcome

- Review: `docs/collaboration/reviews/2026-08-24-liss-0452-phase3-review-02.md`.
- Verdict: **READY** for Phase 3 closeout / final Adjudicator review.
- Terminal state: **COMPLETE** for the independent review loop.
- P1 blocker: resolved. Remaining P2 observations are explicitly deferred and
  are not blockers for this bounded S02 boundary slice.
- Verification: focused suites 16 passed, additional boundary suites 53
  passed, and the full `.venv` suite 1712 passed.

## Remaining gate

Issue and WorkPlan are synchronized to `final-review-ready`. Completion PR and
final Adjudicator review remain. This trace does not mark the Issue complete and
does not approve Phase 1 for any new S02 behavior.
