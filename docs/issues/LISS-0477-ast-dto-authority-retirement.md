# LISS-0477: AST/DTO semantic-authority retirement

| Field | Value |
|---|---|
| Status | **ready — design complete; Phase 1 Red approval required** |
| Phase | phase-0-design |
| Parent | WP-0107 |
| Design authority | [Scientific Semantic Core](../specs/staqex-scientific-semantic-core.md#consumer-wide-follow-up-design) |
| Depends on | LISS-0476 |
| Implementation permission | None |
| Next approval | Consumer inventory review, then typed Phase 1 Red approval |

## Scope

Inventory remaining evaluator, Equation/Physics DTO, H1, Algorithm Plan, and
QASM helper reads. Classify each as migrate, projection-only, retire, or defer;
assign owner, proof ID, replacement, rollback trigger, and deletion condition.

## Acceptance scenarios

- AST mutation or caller-injected DTO cannot change canonical meaning.
- Missing canonical projection fails closed before consumer artifact creation.
- Every migrated projection retains node identity, role, dimensions, and
  provenance.
- Obsolete helper deletion is blocked until replacement and rollback evidence
  exist.

## Exclusions and stop conditions

No syntax, `Realize`, `State<T>`, terminal `measure`, provider, or deployment
change. Stop if a consumer requires a new semantic authority or changes an
accepted ADR.

## Phase 1 candidate files

Inventory, proof-ID matrix, fixtures, and negative Red tests only.
