# LISS-0477: AST/DTO semantic-authority retirement

| Field | Value |
|---|---|
| Status | **Phase 2 Green complete; Phase 3 review required** |
| Phase | phase-2-green |
| Parent | WP-0107 |
| Design authority | [Scientific Semantic Core](../specs/staqex-scientific-semantic-core.md#consumer-wide-follow-up-design) |
| Depends on | LISS-0476 |
| Implementation permission | None |
| Next approval | Typed Phase 3 refactor/review approval |

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

## Phase 1 Red result

The Adjudicator approved `LISS-0477 Phase 1 Red` on 2026-08-30. Added only
`tests/test_liss_0477_ast_dto_authority_retirement_red.py`.

The packet covers the consumer/proof inventory, caller-created canonical
projection rejection, identity/role/dimensions/provenance retention, and the
missing-canonical-projection QASM boundary. Three tests pass against the
current implementation. The missing-canonical-projection test fails because
the QASM helper still rebuilds from the AST and emits an artifact without an
explicit canonical projection. No production code was changed.

Verification: `./.venv/bin/pytest -q
tests/test_liss_0477_ast_dto_authority_retirement_red.py` reports `1 failed,
3 passed`, and `git diff --check` passes. Phase 2 Green requires separate
Adjudicator approval.

## Phase 2 Green result

The Adjudicator approved `LISS-0477 Phase 2 Green` on 2026-08-30. QASM
consumers now use the compile-owned canonical Scientific Semantic IR attached
to a compiled unit; a raw unit without that projection rejects with
`E_QPU_CANONICAL_PROVENANCE` before artifact creation. AST fallback is not
used for the missing-projection case.

Changed production files: `compiler/staqex/pipeline.py` and
`compiler/staqex/backend/qasm/emitter.py`. The Phase 1 acceptance assertions
were preserved; only the missing-projection setup was corrected to use a raw
parser unit so it represents an actually absent canonical projection.

Verification: LISS-0477 tests pass (`4 passed`), Python compilation passes,
and `git diff --check` passes. Three historical QASM expectations remain
outside this bounded slice because they assert separate legacy fallback
behavior. Phase 3 review/refactor requires separate approval.
