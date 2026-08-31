# LISS-0486: Evaluator semantic-authority migration

| Field | Value |
|---|---|
| Status | **done — bounded evaluator semantic-authority slice complete** |
| Phase | phase-3-refactor-complete |
| Parent | WP-0107 |
| Design authority | [Scientific Semantic Consumer Migration](../specs/staqex-scientific-semantic-consumer-migration.md#liss-0486-evaluator-semantic-authority-migration) |
| Related authority | [Scientific Semantic Core](../specs/staqex-scientific-semantic-core.md#consumer-wide-follow-up-design), ADR 0211 |
| Depends on | LISS-0476, LISS-0477, WP-0107 |
| Implementation permission | Phase 3 completed within approved bounded scope |
| Next approval | None for this bounded slice; remaining consumers require separate scope |

## Architecture/spec approval

- The evaluator boundary is accepted as a local downstream consumer of the
  compile-owned Scientific Semantic IR.
- AST traversal remains operational dispatch only; it is not a second semantic
  authority.
- No evaluator semantic redesign, provider/QPU/AWS integration, or Rust work
  is authorized by this approval.

## Phase 1 Red result

- Added `tests/test_liss_0486_evaluator_semantic_authority_red.py`.
- The tests require explicit compile-owned IR propagation, identity retention,
  and rejection of caller-injected semantic projections.
- No evaluator or host implementation was changed.

## Phase 2 Green result

- Evaluator accepts the compile-owned `ScientificSemanticIR` explicitly and
  stores the exact identity for the run.
- Caller-injected or non-canonical semantic projections are rejected.
- Host execution propagates `CompileResult.scientific_semantic_ir` into the
  evaluator without changing evaluator AST dispatch or result envelopes.

## Scope

Define and implement the local runtime boundary where evaluator execution
consumes the compile-owned Scientific Semantic IR. The AST remains the
operational input shape, but it must not independently authorize semantic
meaning, finiteization, collapse, or unsupported fallback behavior.

## Acceptance scenarios

- The evaluator receives the same canonical IR identity produced by compile;
  it does not rebuild or accept a caller-injected replacement.
- AST mutation after compilation cannot change semantic role, dimensions,
  provenance, or realization policy used by the evaluator.
- Intermediate state-preserving operations remain `State<T>` and do not
  collapse early.
- Terminal `Measure` produces the existing measurement envelope and preserves
  source/post-state provenance.
- Unresolved or unsupported semantic meaning returns no fabricated runtime
  result and does not allocate a finite target implicitly.
- Existing local pure/mixed measurement and example behavior remains stable.

## Boundary decisions

- Pass `ScientificSemanticIR` explicitly through the evaluator entry boundary;
  do not use a global cache or reconstruct it from AST.
- Keep AST traversal for operational dispatch only; semantic checks read the
  canonical projection and its evidence fields.
- Preserve existing evaluator value types and measurement envelope APIs in
  the first slice; public API redesign is separate.
- Treat `Realize` as the only finiteization permission and reject unresolved
  canonical meaning before runtime allocation.

## Exclusions and stop conditions

No provider/QPU/AWS, SDK, Rust, solver, automatic integration, Hilbert storage,
new syntax, public result redesign, or broad numerical behavior change.
Stop for a new ADR if evaluator ownership requires changing `State<T>` or the
accepted terminal measurement contract.

## Phase 1 candidate files

Named evaluator boundary tests/fixtures, this Issue/spec/WP status records,
and review record only. Production evaluator changes begin in Phase 2.

## Phase 3 result

- Consolidated typing imports and formatted the canonical IR validation path
  for readability without changing behavior.
- Re-ran the bounded tests and full spec verification suite.
- Review summary: [LISS-0486 Phase 3 review](../collaboration/reviews/2026-08-31-liss-0486-phase3-review.md)
- Process review: no operating-contract deviation or operational problem found.

## Final verification

- LISS-0486 suite: `3 passed` under direct local execution.
- Spec verification: `161/161`, `100.00%`.
- `py_compile` and `git diff --check`: passed.
- Equation/Physics DTO, H1, Algorithm Plan, provider/QPU, AWS, and Rust
  remain outside this bounded slice.
