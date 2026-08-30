# LISS-0479: Residual semantic-family coverage matrix

| Field | Value |
|---|---|
| Status | **Phase 1 Red complete; Phase 2 Green approval required** |
| Phase | phase-1-red |
| Parent | WP-0120 |
| Design authority | [Real-QPU readiness acceptance](../specs/staqex-real-qpu-readiness-acceptance.md#liss-0479--residual-semantic-family-coverage) |
| Depends on | LISS-0457, LISS-0471, LISS-0472 |
| Implementation permission | None |
| Next approval | Typed Phase 2 Green approval for a selected row |

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

## Phase 1 Red result

The Adjudicator approved `LISS-0479 Phase 1 Red` on 2026-08-31. Added the
coverage matrix baseline to the Real-QPU readiness acceptance Spec and added
`tests/test_liss_0479_residual_semantic_family_matrix_red.py`.

The packet covers required matrix fields, deferred Product/Tensor no-artifact
behavior, Interfer/phase/branch inspectability, and terminal-versus-dynamic
measurement rows. Four tests pass. The observation row reachability test is
intentionally Red because its fixture is reserved for the separately designed
LISS-0481 observation contract and does not yet exist. No production code or
provider behavior was changed.

Verification: `./.venv/bin/pytest -q
tests/test_liss_0479_residual_semantic_family_matrix_red.py` reports `1 failed,
4 passed`, and `git diff --check` passes. Phase 2 Green requires a separate
approval for a selected row.
