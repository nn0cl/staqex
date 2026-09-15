# LISS-0558: Observation diagnostic-name reconciliation

## Metadata

- Local issue ID: LISS-0558
- GitHub issue: none
- Status: done
- Phase: done
- Type: diagnostic test synchronization
- Priority: P1
- Initial/current planning size: S / S
- Owner/agent: host implementation; same-context review
- Related branch: `codex/liss-0558-observation-diagnostic`

## Summary

Reconcile the old tomography expectation `OBSERVATION_UNSUPPORTED` with the
current accepted catalog and conformance matrix name
`OBSERVATION_CAPABILITY_UNSUPPORTED`.

## Acceptance Notes

- Preserve explicit Host/kernel boundary rejection and absence of
  `LINEAR_DUPLICATE_USE` masking.
- Update only the stale expected code if the current spec and conformance matrix
  agree; otherwise stop for an architecture decision.
- No tomography implementation or diagnostic alias is added merely for an old
  test spelling.

## Phase 0 design intake

### [DESIGN CHECK]

- Scope and expected behavior: reconcile the Static Kernel rejection
  diagnostic for a `tomography` request without implementing tomography,
  POVM execution, or a provider adapter.
- Specifications and evidence inspected: the accepted observation follow-up
  specification, the v1 diagnostic catalog, LISS-0481, LISS-0483, and
  `tests/test_quantum_observation_contract_red.py`.
- Boundary: tomography remains a Host/protocol observation request; the Static
  Kernel must reject it without implicit measurement, classical approximation,
  or `LINEAR_DUPLICATE_USE` masking.
- Process lessons applied: retain the existing Red node as the acceptance
  contract; do not alter an assertion until the canonical diagnostic owner is
  established.
- Omitted context: tomography/POVM implementation, QPU/provider integration,
  and unrelated observation-family design.

### Phase 0 evidence and decision boundary

The inspected accepted follow-up specification explicitly requires
`OBSERVATION_UNSUPPORTED` for Static Kernel tomography rejection. The current
Red test asserts the same code. A repository-wide search did not find
`OBSERVATION_CAPABILITY_UNSUPPORTED` in the current diagnostic catalog or
conformance evidence. Therefore the catalog/spec/test set does not currently
agree with the proposed rename.

Phase 0 acceptance is recorded as **blocked at the naming decision boundary**:
no test fixture, implementation, or diagnostic alias may be changed until an
Architecture decision establishes whether the canonical code remains
`OBSERVATION_UNSUPPORTED` or the specification/catalog are amended to adopt
`OBSERVATION_CAPABILITY_UNSUPPORTED`.

ADR 0226 was accepted with `ADR 0226 Architecture 承認` on 2026-09-16.
It retains `OBSERVATION_UNSUPPORTED` as the canonical code and authorizes the
bounded Phase 1 catalog/conformance reconciliation only.

### Next gate

Request `LISS-0558 Phase 1 Red 承認`.

## Phase 1 Red result

- Adjudicator approval: `LISS-0558 Phase 1 Red 承認`, received 2026-09-16.
- The existing Active-Red node was executed without changing the test or
  production code.
- Result: **1 failed**. The compiler returned
  `OBSERVATION_CAPABILITY_UNSUPPORTED` together with
  `HOST_TYPE_IN_KERNEL_ERROR`, `QSEM_APPROXIMATION_OBLIGATION_MISSING`, and
  `QSEM_FINITE_EVIDENCE_MISSING`; the reviewed assertion requires
  `OBSERVATION_UNSUPPORTED` and forbids `LINEAR_DUPLICATE_USE` masking.
- This is the exact bounded naming mismatch identified in Phase 0. No
  implementation or assertion change is authorized in this phase.

## Phase 1 Red review result

- Adjudicator approval: `LISS-0558 Phase 1 Red テストレビュー承認`, received
  2026-09-16.
- The existing Red node is accepted unchanged as the bounded contract. Its
  failure is a diagnostic-name mismatch, not a request for tomography or
  provider implementation.
- Review evidence is recorded in
  `docs/collaboration/reviews/2026-09-16-liss-0558-phase1-red-review.md`.
- No implementation permission is inferred from this review.

### Next gate

Request `LISS-0558 Phase 2 Green / Implementation 承認`.

## Phase 2 Green / Implementation result

- Adjudicator approval: `LISS-0558 Phase 2 Green / Implementation 承認`,
  received 2026-09-16.
- Updated the single Static Kernel tomography rejection producer and its hard
  diagnostic set from `OBSERVATION_CAPABILITY_UNSUPPORTED` to the ADR 0226
  canonical `OBSERVATION_UNSUPPORTED`.
- Registered the canonical code in the v1 diagnostic catalog and synchronized
  the LISS-0483 conformance matrix.
- No diagnostic alias, tomography implementation, provider adapter, or QPU
  behavior was added. The reviewed Red test was unchanged.
- Next gate: `LISS-0558 Phase 3 Refactor 承認`.

## Phase 3 Refactor result

- Adjudicator approval: `LISS-0558 Phase 3 Refactor 承認`, received 2026-09-16.
- No production refactor was necessary: the implementation is already the
  smallest readable two-site diagnostic-name synchronization. The catalog,
  conformance matrix, and hard-diagnostic set remain aligned with the single
  type-check producer.
- Boundary review confirms no alias, second diagnostic path, tomography
  implementation, provider adapter, or QPU behavior was added.
- Review record:
  `docs/collaboration/reviews/2026-09-16-liss-0558-phase3-refactor-review.md`.
- Verification: 16 related tests passed; compilation, diff, lifecycle,
  document, and coverage checks passed.
- Next gate: `LISS-0558 Phase 3 最終レビュー 承認`.

## Completion

- Final review approval: `LISS-0558 Phase 3 最終レビュー 承認`, received
  2026-09-16.
- LISS-0558 is closed. The Active-Red exclusion was removed after the
  canonical diagnostic producer, hard-code set, catalog, and conformance
  matrix were synchronized.

## Process Review

- Outcome: no operating-contract deviation or operational problem found.
- Lesson written: existing red-contract-reuse, diagnostic-scope, and
  compatibility-baseline lessons were applied.
- Template-feedback path: none.

## Dependencies

- Parent: WP-0161
- Depends on: none
- Blocks: none
- Related: LISS-0483, ADR 0189, WP-0092

## Verification

One active node plus the LISS-0483 observation conformance and source-evidence
suites.

## Process Review

- Outcome: not yet
- Lesson written: not yet
- Template-feedback path: none
