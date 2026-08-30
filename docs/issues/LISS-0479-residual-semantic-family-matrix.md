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

## Phase 2 Green — Product/Tensor row

The Adjudicator approved the Product/Tensor deferred row for Phase 2 Green on
2026-08-31. The existing canonical projection preserves the mathematical
product/state meaning and rejects unsupported finite projection before QASM
artifact creation with `E_QPU_CANONICAL_PROJECTION_UNAVAILABLE`. No
implicit unitary finiteization, provider behavior, or new numerical method was
added, so no production change was required for this row.

Verification: Product/Tensor plus related Coin/Mix and meaning-preservation
tests pass (`16 passed` in the selected run). The matrix-wide Observation row
fixture remains intentionally unresolved under the separate LISS-0481
contract; LISS-0479 overall is not complete.

### Product/Tensor row Phase 3 review

The Adjudicator approved Product/Tensor row Phase 3 review on 2026-08-31.
Same-context review re-read the coverage matrix, Product/Tensor fixture,
canonical semantic projection, QASM rejection boundary, and selected tests.
No blocker was found: mathematical product meaning remains inspectable,
unsupported finite projection is rejected before artifact creation, and this
row does not widen any other family status.

Verification: 16 Product/Tensor-related tests passed, `git diff --check`
passed, and the matrix-wide run's only failure remains the intentionally
deferred Observation fixture. Process review for this row found no
operating-contract deviation or operational problem.
