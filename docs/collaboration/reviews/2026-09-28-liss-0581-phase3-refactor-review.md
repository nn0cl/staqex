# LISS-0581 Phase 3 Refactor Review

## Review packet

- Scope: `WP-0174 / LISS-0581 Phase 3 Refactor`, explicitly approved
  2026-09-28. Implementation permission was limited to the approved Phase 3
  refactor boundary; no behavior, tests, or assertions were to change.
- Canonical documents: [LISS-0581 specification](../../specs/evaluator-coordinate-liveness.md),
  [ADR 0228](../../architecture/adr/0228-evaluator-coordinate-liveness-boundary.md),
  [Phase 2 verification](2026-09-28-liss-0581-phase2-verification.md),
  [LISS-0581 issue](../../issues/LISS-0581-evaluator-coordinate-liveness-successor.md),
  [WP-0174](../../work-plans/WP-0174-evaluator-residual-responsibility-successors.md).
- Artifacts re-read for review: the canonical documents above, changed
  `compiler/staqex/runtime/evaluation/liveness.py`, the reviewed
  `tests/test_liss_0581_evaluator_coordinate_liveness_red.py`, and actual
  runtime consumers/imports in `evaluator.py`, `evaluation/observation.py`,
  `evaluation/frames.py`, `execution.py`, `pipes.py`, `evolution_ops.py`, and
  `context.py`.
- Changed implementation file: `compiler/staqex/runtime/evaluation/liveness.py`.
  No test assertions or fixtures were changed in Phase 3.
- Current phase: Phase 3 refactor and same-context review passed; the human
  final-review approval is recorded below. Commit and post-commit verification
  remain outstanding.

## Findings and dispositions

1. The 131-line `expr_free_vars` traversal mixed binder semantics, operator
   nodes, and ordinary expression recursion. It is now a compact public
   collector with private binder, operator, and expression traversal helpers.
   **Disposition: applied.** Longest AST function body is 56 lines; the
   `liveness.py` file is 318 lines because named helpers make the one cohesive
   AST analysis explicit.
2. Binder traversal order and shared-set mutation are behavior-sensitive:
   domain/guard/body names are visited in the prior order and each bound name
   is discarded at the same point as before. Operator leaf and child order,
   Evolve seed/body/time/duration/Hamiltonian order, and unknown-node no-op
   behavior are preserved. **Disposition: reviewed against the former
   implementation and accepted.**
3. `expr_free_vars` and `expr_has_inspect` names, compatibility delegates,
   Evaluator state ownership, and direct consumer modules remain unchanged.
   The existing identity and consumer tests pass. **Disposition: preserved.**
4. A same-context review has weaker isolation than a separate-context review.
   The routing config explicitly selects `same_context`; no independent agent
   or model review is claimed. **Disposition: recorded limitation, not
   silently downgraded.**
5. Runtime routing contains no `[source_structure]` budget and no enabled
   `[review.large_change]` override. Qualitative structure assessment applies;
   no numerical budget-compliance claim is made. **Disposition: recorded.**

No blocking findings remain for the Phase 3 refactor. No architecture, test,
semantic, dependency, or consumer boundary changed.

## Verification

- Tested base/HEAD SHA: `83c93a524c7c90710ed965d231ffe85b20dc3163`; worktree was
  dirty and contains the complete uncommitted LISS-0581 branch work. Results
  describe that working tree, not the commit by itself.
- Environment: local macOS 27.0 (build 26A428), Python 3.14.6, `.venv`.
- Focused/consumer/adjacent:
  `.venv/bin/pytest -q tests/test_liss_0581_evaluator_coordinate_liveness_red.py tests/test_trace_out_gc_fn_scope_red.py tests/test_bare_block_trace_out_red.py tests/test_evolve_trace_out_gc_red.py tests/test_interprocedural_trace_out_red.py tests/test_liss_0561_evaluator_observation_dynamic_red.py tests/test_liss_0572_frames_constructors_assignments_red.py tests/test_liss_0573_pipes_successor_red.py`
  — 41 passed, 0 failures/errors (0.33s, after final source formatting).
- All blocking:
  `.venv/bin/pytest tests/ -q` — 2,280 passed, 0 failures/errors
  (313.53s). It ran after the refactor and before a whitespace-only line wrap;
  focused tests, spec verification, compilation, and diff checks were rerun
  after that formatting-only edit.
- Post-commit all-blocking verification:
  `.venv/bin/pytest tests/ -q` on commit
  `7e067d5a136385e85cf497b6bac5d5338c8aff8b` — 2,280 passed, 0
  failures/errors (317.38s); clean worktree at run start, local macOS 27.0
  build 26A428, Python 3.14.6. This verifies the implementation commit. A
  later documentation-only closeout commit will rely on GitHub CI tied to its
  final branch SHA as the delivery gate.
- Specification verification: `python3 tests/spec_verification/run_all.py` —
  161/161 passed (100%), after final source formatting.
- Also passed after the refactor: document lifecycle (1 register), Active Red
  lifecycle (`entries=0`), coverage ledger consistency, Python byte compilation,
  `git diff --check`, and an 88-character source-line check.
- Failure comparison: the Phase 2 all-blocking run on the same host/Python and
  virtual environment passed 2,280 tests with 0 failures. Phase 3 also passed
  2,280 with 0 failures; no failure IDs were introduced or resolved. A clean
  baseline commit run was not performed, so this is a Phase-2-to-Phase-3
  working-tree comparison, not a clean-base comparison.
- Exclusions: none; Active Red exclusions are zero. Out-of-tree/dynamic
  consumers cannot be proven absent by repository search; the discoverable
  private consumer paths and hook identity are covered by inventory and tests.

## Specification and structure disposition

The accepted Phase 2 contract and tests remain authoritative and unchanged.
This is a readability-only Phase 3 change: no acceptance clauses, test
assertions, fixtures, diagnostics, runtime state, traversal inputs, or
Trace-Out semantics were intentionally changed. `evaluator.py` remains at
1,283 lines; this phase reduces the largest AST traversal body from 131 to 56
lines, while the cohesive liveness module grows from 286 to 318 lines to name
the separated responsibilities. That tradeoff is intentional and does not
claim every runtime source file is below a numeric threshold.

## Reviewer empathy summary

The most review-sensitive part is the single shared `names` accumulator:
bound-name removal is intentionally retained at the same traversal point,
rather than replaced with a new scope algorithm. Reviewers should compare the
helper sequence with the existing binder contracts and watch the `OpBinder`,
`SetComprehension`, and `EvolveExpr` child order. The focused tests exercise
actual compatibility hooks and all identified in-repository runtime
consumers; the full suite is green. Same-context review cannot provide
independent-context protection, and a clean-baseline failure comparison is
unavailable.

## Approval and next gate

- Phase 3 Refactor approval: received 2026-09-28.
- Implementation allowed: Phase 3 refactor only; no commit/push/merge approval
  was requested by this phase approval.
- Human final-review decision: approved —
  `WP-0174 / LISS-0581 Phase 3 最終レビュー 承認`, 2026-09-28.
- Implementation commit: `7e067d5a136385e85cf497b6bac5d5338c8aff8b`.
- Process review: no operating-contract deviation or operational problem
  found; recorded in the Issue. The separate status-sync closeout commit must
  pass its final-SHA GitHub CI before merge.
- Next action: push the branch, open the PR in the browser, inspect all checks,
  and merge only after required CI is green.
