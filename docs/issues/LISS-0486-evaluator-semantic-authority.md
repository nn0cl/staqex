# LISS-0486: Evaluator semantic-authority migration

| Field | Value |
|---|---|
| Status | **ready — design complete; Architecture/spec review required** |
| Phase | phase-0-design |
| Parent | WP-0107 |
| Design authority | [Scientific Semantic Consumer Migration](../specs/staqex-scientific-semantic-consumer-migration.md#liss-0486-evaluator-semantic-authority-migration) |
| Related authority | [Scientific Semantic Core](../specs/staqex-scientific-semantic-core.md#consumer-wide-follow-up-design), ADR 0211 |
| Depends on | LISS-0476, LISS-0477, WP-0107 |
| Implementation permission | None |
| Next approval | Architecture/spec review, then typed Phase 1 Red approval |

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
