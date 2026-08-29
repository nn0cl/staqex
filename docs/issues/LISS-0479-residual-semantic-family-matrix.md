# LISS-0479: Residual semantic-family coverage matrix

| Field | Value |
|---|---|
| Status | **ready — design complete; Phase 1 Red approval required** |
| Phase | phase-0-design |
| Parent | WP-0120 |
| Design authority | [Real-QPU readiness acceptance](../specs/staqex-real-qpu-readiness-acceptance.md#liss-0479--residual-semantic-family-coverage) |
| Depends on | LISS-0457, LISS-0471, LISS-0472 |
| Implementation permission | None |
| Next approval | Matrix review, then typed Phase 1 Red approval for a selected row |

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
