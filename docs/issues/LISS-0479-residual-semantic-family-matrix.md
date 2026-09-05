# LISS-0479: Residual semantic-family coverage matrix

| Field | Value |
|---|---|
| Status | **done — Phase 3 refactor and review complete** |
| Phase | phase-3-refactor-complete |
| Parent | WP-0120 |
| Design authority | [Real-QPU readiness acceptance](../specs/staqex-real-qpu-readiness-acceptance.md#liss-0479--residual-semantic-family-coverage) |
| Depends on | LISS-0457, LISS-0471, LISS-0472 |
| Implementation permission | Granted only for the bounded Phase 2 classifier slice |
| Next approval | None for this Issue; broader family support requires a new Issue/phase approval |

## Scope

Reconcile every remaining source construct against the completed Product/
Tensor, Measurement, and Continuous/Open-system bounded rows. Record source
fixture, semantic role, finite boundary, target status, rejection code, owner,
and exit evidence.

## Acceptance scenarios

- Every inventoried construct has ready, reject, or defer status.
- Deferred/unsupported rows retain meaning and emit no artifact.
- Static terminal measurement and dynamic measurement remain distinct.
- No row silently expands an existing family’s completion claim.

## Exclusions and stop conditions

No provider capability, new numerical method, syntax change, or family-wide
implementation. Stop when a row needs an ADR or technology selection.

## Phase 1 candidate files

Coverage matrix, source-reachability fixtures, inventory assertions, and
negative tests only.

## Phase 1 Red execution record

- Typed approval: user message `` `LISS-0479 Phase 1 Red 承認` ``,
  2026-09-04.
- Added `tests/test_liss_0479_residual_semantic_family_matrix_red.py`.
- The packet defines three bounded residual rows: ideal-limit,
  observation, and interference. Each row requires source identity, family,
  semantic role, finite boundary, ready/reject/defer status, diagnostic/reason,
  and artifact/provider absence for non-ready rows.
- Existing terminal/dynamic measurement behavior is asserted as an unchanged
  neighboring family; unknown constructs must fail closed.
- Red verification: **1 passed, 6 failed**, with no collection errors. The
  failures are expected because the Phase 2 classifier module does not yet
  exist. No production implementation or artifact behavior was changed.
- `git diff --check` passed.

Phase 2 Green requires a separate approval and remains limited to the reviewed
matrix contract. Provider capability, new numerical methods, syntax changes,
and real-QPU execution remain excluded.

## Phase 2 Green execution record

- Typed approval: user message `承認`, 2026-09-04.
- Added `compiler/staqex/residual_semantic_family_readiness.py`.
- The classifier consumes canonical Scientific Semantic IR and exposes the
  complete disposition record for ideal-limit, observation, and interference.
  It delegates the already-accepted measurement boundary and preserves its
  terminal/dynamic distinction.
- Deferred and rejected rows are artifact-free: no QASM, provider mapping, or
  finite realization is inferred. Unknown constructs fail closed.
- Verification: the LISS-0479 and neighboring boundary suites passed **19/19**;
  `py_compile` and `git diff --check` passed.
- Process lesson application: the classifier preserves source/reason
  observability and tests unsupported cases for atomic, provider-neutral
  rejection. Compatibility projections remain diagnostic-only and are not
  consulted as semantic authority.

Phase 3 is limited to readability/refactor, review evidence, and ledger
synchronization. It does not broaden family support or authorize provider or
real-QPU work.

## Phase 3 closeout

- Typed approval: user message `承認`, 2026-09-04.
- Refactor: residual row metadata now lives in immutable internal contracts;
  detection and result construction are separate, while family priority and
  all public result fields remain unchanged.
- Verification after refactor: LISS-0479 plus neighboring semantic-boundary
  suites **19/19 passed**; full pytest **1889 passed**; `py_compile` and
  `git diff --check` passed.
- Same-context review: `COMPLETE` / `READY`; no blocking finding. Review
  packet: `docs/collaboration/reviews/2026-09-04-liss-0479-phase3-review.md`.
- Process review: no operating-contract deviation or operational problem found.

The matrix is complete for the bounded residual rows. This does not claim
finite realization support for ideal-limit, observation, or interference, and
does not authorize provider SDK, AWS, deployment, or real-QPU execution.
