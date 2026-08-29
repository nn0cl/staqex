# LISS-0481: Observation contract

| Field | Value |
|---|---|
| Status | **ready — design complete; specification/Phase 1 approval required** |
| Phase | phase-0-design |
| Parent | WP-0092 |
| Design authority | [Quantum mental-model follow-up specification](../specs/staqex-v1-quantum-mental-model-follow-up.md#detailed-follow-up-issue-design) |
| Depends on | ADR 0189/0190; existing `DiagnosticView<T>` slice |
| Implementation permission | None |
| Next approval | Architecture/spec review, then typed Phase 1 Red approval |

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
