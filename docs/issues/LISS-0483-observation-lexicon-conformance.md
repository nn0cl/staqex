# LISS-0483: Observation and lexicon conformance closure

| Field | Value |
|---|---|
| Status | **ready — design complete; Phase 1 Red approval required** |
| Phase | phase-0-design |
| Parent | WP-0092 |
| Design authority | [Quantum mental-model follow-up specification](../specs/staqex-v1-quantum-mental-model-follow-up.md#detailed-follow-up-issue-design) |
| Depends on | LISS-0480, LISS-0481, LISS-0482 |
| Implementation permission | None |
| Next approval | Conformance review, then typed Phase 1 Red approval |

## Scope

Build the cross-feature conformance matrix for aliases, `mix`, `superpose`,
`controlled`, `when` retirement, inspection, projection, and terminal measure.
Map each proof to a deterministic test and preserve shipped behavior.

## Acceptance scenarios

- Every accepted spelling and observation operation has one observable path.
- Deferred forms reject explicitly with stable diagnostics.
- Source meaning and review-boundary metadata remain observable.
- Conformance does not imply provider or hardware support.

## Exclusions and stop conditions

No normative grammar change, provider, QPU, Rust, or broad example rewrite.
Stop when a test exposes an ADR/spec conflict; resolve it before Phase 1.

## Phase 1 candidate files

Cross-feature fixtures, proof matrix, conformance Red tests, and documentation
links only.
