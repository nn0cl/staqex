# LISS-0478: Interfer/phase/branch meaning preservation

| Field | Value |
|---|---|
| Status | **ready — design complete; Phase 1 Red approval required** |
| Phase | phase-0-design |
| Parent | WP-0113 |
| Design authority | [Meaning Preservation Specification](../specs/staqex-semantic-ir-meaning-preservation.md#residual-follow-up-design-liss-0478) |
| Depends on | LISS-0450 bounded Coin/when slice |
| Implementation permission | None |
| Next approval | Family contract review, then typed Phase 1 Red approval |

## Scope

Define canonical semantic roles for interference, phase, branch/control
relationships, operand identity, exactness, and provenance. Define explicit
unsupported finite projection behavior.

## Acceptance scenarios

- Branch/control identity survives semantic projection.
- Phase is not discarded or reinterpreted as classical probability.
- Unsupported finite projection retains source meaning and emits no artifact.
- Source-derived nodes remain inspectable without QPU support.

## Exclusions and stop conditions

No gate synthesis, numerical approximation, provider, QPU, or Hilbert-space
storage choice. Stop for ADR review if approximation or new representation is
required.

## Phase 1 candidate files

Representative `.sqx` fixtures, meaning-role assertions, negative projection
tests, and this Issue/spec/review record only.
