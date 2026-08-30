# LISS-0481: Observation contract

| Field | Value |
|---|---|
| Status | **Phase 1 Red complete; Phase 2 Green approval required** |
| Phase | phase-1-red |
| Parent | WP-0092 |
| Design authority | [Quantum mental-model follow-up specification](../specs/staqex-v1-quantum-mental-model-follow-up.md#detailed-follow-up-issue-design) |
| Depends on | ADR 0189/0190; existing `DiagnosticView<T>` slice |
| Implementation permission | None |
| Next approval | Typed Phase 2 Green approval |

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

## Phase 1 Red result

- Added the LISS-0481 observation contract matrix to the authoritative
  specification, including semantic type, collapse, sampling, lane,
  provenance, and unsupported behavior.
- Added `tests/test_liss_0481_observation_contract_red.py` for the matrix,
  distinct inspect/measure metadata, and Static Kernel tomography rejection.
- No observation runtime, public type annotations, POVM, tomography, provider,
  or QPU implementation was changed.
