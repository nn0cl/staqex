# LISS-0447 Phase 3 Refactor Trace

- Approval: user approved LISS-0447 Phase 3 Refactor.
- Scope: remove obsolete ordinary-QASM AST fallback and unreachable duplicate
  emitter return; migrate the obsolete fallback test to the accepted atomic
  rejection contract.
- Excluded: finite Suzuki/binder compatibility fallback, provider/live QPU,
  S02, solver, syntax, H1, and LISS-0446 public-entry redesign.

## Refactor changes

- Removed `W_QPU_LEGACY_AST_FALLBACK` ordinary-QASM branch from
  `compiler/staqex/backend/qasm/emitter.py`.
- Removed the unreachable duplicate `EmitResult` return.
- Preserved the explicitly scoped finite Suzuki/binder compatibility lowering
  branch.
- Updated the obsolete semantic-core fallback test to assert canonical,
  artifact-free rejection instead.

## Verification

- `.venv/bin/pytest -q tests/test_liss_0447_residual_semantic_consumers_red.py
  tests/test_qasm3_codegen.py tests/test_scientific_semantic_core_red.py
  tests/test_liss_0444_consumer_migration_red.py
  tests/test_liss_0445_consumer_migration_red.py`
  — **69 passed**.
- `git diff --check`: passed.
- No provider/live-QPU, S02, solver, or finite Suzuki compatibility path was
  changed.

## Phase 3 acceptance

- Behavior remains canonical ordinary projection or explicit atomic rejection.
- Separation of concerns is improved: ordinary QASM no longer has a hidden
  AST fallback, while finite compatibility lowering remains visibly bounded.
- Reviewer empathy risk addressed: no dead branch or misleading fallback note
  remains in the ordinary emitter path.

Independent final review returned **READY** with no P0/P1 blocker. It
confirmed removal of the obsolete ordinary AST fallback and duplicate return,
preservation of finite Suzuki/binder compatibility lowering, atomic rejection,
and reproduction of the **69 passed** suite plus `git diff --check`.

The known LISS-0446 Limit expected-code mismatch remains outside this Phase 3
scope. The Phase 3 review loop is `COMPLETE`.

## Completion packet

- Scope: completion of the already-reviewed Phase 3 refactor; no additional
  implementation or architecture decision.
- Applicable review lenses: contract and acceptance completeness; architecture
  and boundary integrity; realization and fail-closed behavior; migration and
  regression safety; phase and approval discipline; evidence and context
  hygiene; canonical authority and implementation reality; projection
  conservation and authority reachability; executable projection integrity.
- Accepted authority: the LISS-0447 Issue, Spec, WP-0110, ADR 0211, and the
  Phase 3 independent review record remain the governing artifacts.
- Deterministic evidence: the focused residual-consumer suite passed 9 tests
  on the current `main`; the recorded Phase 3 suite passed 69 tests and
  `git diff --check` passed.
- PR: **PR #567**
- Completion date: **2026-08-25**
- Final review: **READY / COMPLETE**.
- CI: **3 successful checks**; no merge conflicts.
- Completion status: Issue/WP/trace synchronized as `complete`.
- Follow-up boundary: the known LISS-0446 Limit expected-code mismatch remains
  outside this Issue and requires separate approval.
