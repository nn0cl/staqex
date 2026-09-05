# LISS-0481: Observation contract

| Field | Value |
|---|---|
| Status | **done — Phase 3 refactor and review complete** |
| Phase | phase-3-refactor-complete |
| Parent | WP-0092 |
| Design authority | [Quantum mental-model follow-up specification](../specs/staqex-v1-quantum-mental-model-follow-up.md#detailed-follow-up-issue-design) |
| Depends on | ADR 0189/0190; existing `DiagnosticView<T>` slice |
| Implementation permission | Granted only for the bounded observation metadata slice |
| Next approval | None for this Issue; public observation execution needs a new Issue/phase approval |

## Scope

Define candidates and boundaries for `Observable<T>`, `Projection<T>`, and
`Observation<T>`, plus `expect`, `project`, `inspect`, `trace_out`, `measure`,
and tomography.

## Acceptance scenarios

- Inspection is non-destructive and does not collapse or allocate a finite plan.
- Terminal `measure` collapses only at the established boundary.
- Dynamic measurement retains its lane identity and provenance.
- Unsupported observation produces no fabricated result.

## Exclusions and stop conditions

No general Hilbert-space storage, POVM/tomography implementation, provider,
or numerical backend choice. Stop for ADR review when any is required.

## Phase 1 candidate files

Observation taxonomy, source fixtures, state/result contract assertions, and
negative Red tests only.

## Phase 1 Red execution record

- Typed approval: user message `承認`, 2026-09-04.
- Added `tests/fixtures/observation_contract/inspect_then_measure.sqx` and
  `tests/test_liss_0481_observation_contract_red.py`.
- The packet fixes the observable operation boundary: `inspect` is a
  non-destructive `DiagnosticView`, `expect`/`project`/`trace_out` do not
  collapse, `tomography` is a Host/protocol observation, and terminal
  `measure` is the only collapsing operation.
- Source identity, operation order, lineage, lane, collapse behavior, and
  fail-closed unsupported observation are covered. No public type or backend
  was added.
- Red verification: **8 failed**, with no collection errors. The failures are
  expected because the Phase 2 provider-neutral observation inspection API is
  not implemented yet.
- `git diff --check` passed.

Phase 2 Green requires a separate approval and remains limited to the reviewed
contract. General POVM/tomography execution, Hilbert-space storage, provider,
and real-QPU work remain excluded.

## Phase 2 Green execution record

- Typed approval: user message `承認`, 2026-09-04.
- Added `compiler/staqex/observation_contract.py`.
- The read-only inspection API exposes immutable operation metadata. Valid
  `Inspect` and terminal `Measure` entries are derived from canonical
  Scientific Semantic IR nodes and preserve source node identity. The
  contract-only operation forms (`expect`, `project`, `trace_out`, and
  `tomography`) expose their non-collapsing or Host/protocol boundary without
  executing them.
- No state sampling, early collapse, finite allocation, provider mapping, or
  general POVM/tomography implementation was added.
- Verification: observation and neighboring semantic-boundary suites
  **25/25 passed**; `py_compile` and `git diff --check` passed.

Phase 3 requires a separate approval and is limited to readability/refactor,
review evidence, and status synchronization.

## Phase 3 closeout

- Typed approval: user message `LISS-0481 Phase 3 承認`, 2026-09-04.
- Refactor: operation metadata construction is centralized by operation kind;
  source-node conversion and contract-only synthetic operation handling share
  one explicit semantic policy. No assertion or boundary behavior changed.
- Verification after refactor: LISS-0481, existing DiagnosticView, and
  neighboring measurement suites **13/13 passed**; `py_compile` and
  `git diff --check` passed.
- Same-context review: `COMPLETE` / `READY`; no blocking finding. Review
  packet: `docs/collaboration/reviews/2026-09-04-liss-0481-phase3-review.md`.
- Process review: no operating-contract deviation or operational problem found.

The bounded observation metadata contract is complete. Public source-level
`Observable<T>`/`Projection<T>`/`Observation<T>` types, general POVM,
tomography execution, and provider/real-QPU work remain separately gated.
