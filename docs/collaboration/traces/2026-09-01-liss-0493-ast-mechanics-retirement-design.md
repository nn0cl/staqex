# AI work trace: LISS-0493 evaluator AST mechanics retirement design

- Date: 2026-09-01
- User target: continue with the separate evaluator internal AST mechanics
  retirement task after LISS-0492 completed public API removal.
- Current phase: architecture design; implementation permission not granted.
- Canonical issue: `docs/issues/LISS-0493-evaluator-ast-mechanics-retirement.md`.
- Included context: evaluator dispatch and helper inventory, Scientific
  Semantic IR, runtime execution model, backend boundaries, WP-0107, and the
  consumer-migration Spec.
- Omitted: provider/QPU/AWS, Rust, solver, serialization, and release policy.
- Design decision: introduce a non-public runtime execution plan lowered from
  canonical semantic IR and migrate semantic families incrementally; retain
  AST only as temporary mechanics/source metadata.
- Applicable lessons: canonical authority must remain observable; compatibility
  and derived views cannot become execution authority; stop on boundary drift.
- Next gate: Architecture approval, then separately approved Phase 1 Red plan
  contract tests.
- Phase 1 result: added the fixed runtime-plan contract tests; verification
  produced 4 failures and no collection errors. Missing builder, provenance,
  unresolved fail-closed behavior, and AST-dispatch bypass are exposed.
- Phase 1 review: same-context review accepted the Red contract; see
  `docs/collaboration/reviews/2026-09-01-liss-0493-phase1-review.md`.
- Next gate: separately approved Phase 2 Green implementation.
- Phase 2 result: added canonical `RuntimeExecutionPlan`/`RuntimePlanNode`,
  fail-closed authority validation, and canonical execution plan wiring; 35
  related tests passed. `_run_legacy_ast_body` remains an explicit fallback.
- Phase 2 review: same-context review accepted the bounded implementation;
  see `docs/collaboration/reviews/2026-09-01-liss-0493-phase2-review.md`.
- Next gate: separately approved Phase 3 first-family fallback retirement.
- Phase 3 result: added the dedicated State/Measure runtime-plan executor;
  canonical execution no longer reaches `_run_legacy_ast_body` for the first
  family. The legacy path remains explicit for unsupported families.
- Phase 3 verification: 47 related regression tests passed; `py_compile` and
  `git diff --check` passed.
- Next gate: Phase 1 Red approval for the pure-transformation family.
