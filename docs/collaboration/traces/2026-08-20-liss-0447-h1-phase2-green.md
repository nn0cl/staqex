# LISS-0447 H1 Phase 2 Green Trace

- Approval: user selected and approved `LISS-0447 H1 subcontract Phase 2
  Green`.
- Scope: H1 `compile_source()` early-return authority only.
- Excluded: AlgorithmPlan (complete), ordinary QASM fallback, provider/live
  QPU, S02, solver, syntax, and LISS-0446.

## Implementation

- H1 compilation now builds and returns `ScientificSemanticIR`.
- `execution_authority` is `scientific_semantic_ir`.
- H1-specific `physics_ir` and state-transform data remain authoring/diagnostic
  projections; the old `symbolic_ir` parallel authority is removed.
- H1 semantic inspection/snapshot use the canonical IR.

## Verification

- H1 focused and authoring regression command:
  `.venv/bin/pytest -q tests/test_h1_hamiltonian_authoring_red.py
  tests/test_h1_2_parser_ast_red.py tests/test_liss_0445_consumer_migration_red.py
  -k 'h1'` — **10 passed, 11 deselected**.
- LISS-0447 focused: **7 passed / 2 expected ordinary-QASM failures**.
- `git diff --check`: passed.

Independent H1 Review 01 found three evidence/documentation gaps. They were
accepted as design-preserving corrections: synchronize current evidence,
record the exact rerunnable command/result, and assert canonical node identity
through inspection/snapshot. Fresh Review 02 found **READY** with no remaining
H1 blocker. See
`docs/collaboration/reviews/2026-08-20-liss-0447-h1-phase2-green-review-02.md`.

The H1 review loop terminal state is `COMPLETE`. Ordinary QASM remains
separately unapproved.
