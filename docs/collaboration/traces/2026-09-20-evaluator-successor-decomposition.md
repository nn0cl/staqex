# LISS-0570 evaluator successor decomposition design trace

## Request

- Date: 2026-09-20
- User request: continue shrinking `evaluator.py`, prefer independent
  cohesive modules over adding unrelated responsibility to dependency files,
  and remove large source files across the project.
- Current phase: Architecture Path Phase 0 design intake.
- Canonical work plan: WP-0167.
- Canonical issue: LISS-0570.

## Context and decisions

- Current evaluator: 3,790 lines / 116 class methods.
- Current largest non-legacy compiler files: `typecheck.py` 4,678 lines and
  `parser.py` 3,679 lines; both are separate compiler phases and do not
  directly reduce evaluator size.
- Preferred direction: new cohesive modules under
  `runtime/evaluation/`, with explicit `EvaluatorContext` callbacks.
- Proposed evaluator units: execution shell; frames/constructors/assignments;
  pipe/polynomial mechanics; state construction/algebra.
- State and DTO ownership remains in `Evaluator`.
- Process lessons applied: evaluator-state-ownership,
  private-consumer-inventory, compatibility-authority-boundary, and
  quantitative-traceability.

## Verification at intake

- Deterministic source/AST inventory completed.
- No production source or tests changed.
- Next approval:
  `WP-0167 / LISS-0570 Architecture Path scope approval`.

## Architecture Path scope acceptance

- Approval: `WP-0167 / LISS-0570 Architecture Path scope approval`
  (2026-09-20).
- Phase 0 inventory completed for evaluator method families, call graph,
  mutable state/DTO writes, private consumers, and candidate module paths.
- Unit A was narrowed to **A1 execution shell**: legacy AST fallback entry,
  run-state initialization, main statement routing, result assembly, and
  compatibility wiring. `_bind`/`_bind_names` are deferred to A2 because
  dynamic-lane, observation, continuous, and direct tests call them.
- Exact A1 paths are evaluator facade, new `evaluation/execution.py`, context,
  compatibility wiring, new Red test, active-Red ledger, and linked records.
- Typechecker/parser decomposition is explicitly separate and will not be
  touched by evaluator work.
- Implementation permission: none.
- Next approval:
  `WP-0167 / LISS-0570 Unit A1 Phase 1 Red 承認`.

## Unit A1 Phase 1 Red execution

- Approval: `WP-0167 / LISS-0570 Unit A1 Phase 1 Red 承認` (2026-09-20).
- Added only the approved Red test and active-Red manifest entry; no
  production execution module was added.
- The suite separates five structural gaps from three runtime
  characterizations covering simple execution, statement routing, and
  fail-closed diagnostics.
- Verification: `PYTHONPATH=. ./.venv/bin/pytest -q
  tests/test_liss_0570_execution_red.py` -> **5 failed, 3 passed**. The five
  failures are the intended successor-file, facade-body, compatibility, and
  context-boundary gaps; all three characterization cases pass.
- `python3 scripts/check-test-lifecycle.py`, document lifecycle, coverage
  consistency, and `git diff --check` passed.
- Next safe action: run the bounded Red suite and request
  `WP-0167 / LISS-0570 Unit A1 Phase 1 Red テストレビュー承認`.

## Unit A1 Phase 1 Red test review

- Approval reviewed: `WP-0167 / LISS-0570 Unit A1 Phase 1 Red テストレビュー承認`
  (2026-09-20).
- Review route: `same_context`, which is weaker than `separate_context`.
- Canonical WP, Issue, Trace, readiness checklist, active-Red manifest, and
  Red suite were re-read from disk.
- Deterministic verification reproduced **5 failed, 3 passed** for the
  bounded suite. Lifecycle, document lifecycle, coverage-ledger consistency,
  and diff checks passed.
- Findings were closed as declared structural gaps, passing runtime
  characterizations, valid active-Red ownership, and preserved A1 boundaries.
  No production implementation was added or authorized.
- Applied process lessons: red-contract-scope, private-consumer-inventory,
  evaluator-state-ownership, compatibility-authority-boundary, and
  quantitative-traceability.
- Next approval:
  `WP-0167 / LISS-0570 Unit A1 Phase 2 Green / Implementation 承認`.

## Unit A1 Phase 2 Green / Implementation

- Approval: `WP-0167 / LISS-0570 Unit A1 Phase 2 Green / Implementation 承認`
  (2026-09-21).
- Implementation route: host agent, as required by
  `runtime-routing.toml` (`implementation.isolation = "host"`).
- Extracted the approved execution shell to
  `runtime/evaluation/execution.py` and installed `_run_legacy_ast_body` /
  `_run_unit_body` as compatibility aliases. No `runtime.evaluator` import,
  second mutable state store, or DTO redefinition was introduced.
- Measurements: `evaluator.py` **3,371 lines**; `execution.py` **442 lines**.
- Verification: Phase 1 Red contract **8 passed**; focused/adjacent **40
  passed**; all-blocking **2,187 passed in 310.23s**; compileall, lifecycle,
  document, coverage-ledger, and diff checks passed.
- First all-blocking run exposed 15 identical `evaluate_value` import failures;
  the missing successor import was added within the allowed execution module,
  the affected 40-test set passed, and the complete suite was rerun green.
- Active-Red entry retired. Phase 3 refactor and same-context review remain.
- Next approval:
  `WP-0167 / LISS-0570 Unit A1 Phase 3 Refactor 承認`.

## Unit A1 Phase 3 Refactor

- Approval: `WP-0167 / LISS-0570 Unit A1 Phase 3 Refactor 承認`
  (2026-09-21).
- Refactored the successor into named helpers for execution-context setup and
  terminal result assembly. Behavior, diagnostics, ordering, DTO identity,
  private aliases, and state ownership were preserved.
- Same-context review packet:
  `docs/collaboration/reviews/2026-09-21-liss-0570-a1-phase3-review.md`.
- Verification: focused/adjacent **23 passed**; all-blocking **2,187 passed in
  318.00s**; compileall, lifecycle, document, coverage-ledger, and diff checks
  passed.
- `review-change.py` could not quantify the dirty working-tree diff; this is
  recorded as an unknown evidence field, not as zero change.
- No blocker found. Next approval:
  `WP-0167 / LISS-0570 Unit A1 Phase 3 最終レビュー 承認`.

## Unit A1 Phase 3 final review

- Approval: `WP-0167 / LISS-0570 Unit A1 Phase 3 最終レビュー 承認`
  (2026-09-21).
- Final review packet:
  `docs/collaboration/reviews/2026-09-21-liss-0570-a1-final-review.md`.
- Result: accepted. Focused/adjacent **23 passed**; latest all-blocking run on
  the unchanged implementation tree **2,187 passed**; compileall, lifecycle,
  document, coverage-ledger, and diff checks passed.
- Process review: no operating-contract deviation or operational problem
  found.
- LISS-0570 is complete. WP-0167 remains open for independently approved A2
  and Units B–D.

## Unit A2 binder dispatch design intake

- Approval: `WP-0167 / Unit A2 binder dispatch Architecture Path scope approval`
  (2026-09-21).
- New design issue: LISS-0571.
- Inventory: `_bind_names` **111 lines**, `_bind` **143 lines**; actual runtime
  consumers are execution, observation, dynamic-lane, and evolution, with
  direct private-hook characterization tests.
- Proposed successor: `runtime/evaluation/binding.py`, dispatcher control flow
  only. Tensor, ket, block, when, state-scaling, pipe, evolution, and
  continuous family bodies remain outside A2 unless separately approved.
- State ownership, DTO identity, `Joint` lifecycle, diagnostics, ordering,
  logs, inspection sinks, and private aliases remain under the accepted
  Evaluator boundary.
- Phase 0 design is complete. No Red test or production implementation was
  authorized. Next approval:
  `WP-0167 / LISS-0571 Phase 1 Red 承認`.

## Unit A2 Phase 1 Red execution

- Approval: `WP-0167 / LISS-0571 Phase 1 Red 承認` (2026-09-21).
- Added only `tests/test_liss_0571_binder_dispatch_red.py` and its
  issue-owned active-Red entry; no `binding.py` or production compatibility
  implementation was added.
- Contract: five structural gaps and three passing binder characterizations.
- Next approval:
  `WP-0167 / LISS-0571 Phase 1 Red テストレビュー承認`.

## Unit A2 Phase 1 Red test review

- Approval reviewed: `WP-0167 / LISS-0571 Phase 1 Red テストレビュー承認`
  (2026-09-21).
- Same-context review packet:
  `docs/collaboration/reviews/2026-09-21-liss-0571-phase1-red-review.md`.
- Re-run result: **5 failed, 3 passed** for the bounded Red suite; the
  failures are the declared structural gaps and the passing cases are binder
  characterizations. Active-Red lifecycle, document lifecycle,
  coverage-ledger consistency, and diff checks passed.
- Review found no blocker. No production implementation was authorized.
  The active-Red entry remains owned by LISS-0571 until Green implementation.
- Next approval:
  `WP-0167 / LISS-0571 Phase 2 Green / Implementation 承認`.

## Unit A2 Phase 2 Green / Implementation

- Approval: `WP-0167 / LISS-0571 Phase 2 Green / Implementation 承認`
  (2026-09-22).
- Added the binder dispatcher successor at
  `compiler/staqex/runtime/evaluation/binding.py` and installed its two
  entrypoints through compatibility wiring. The successor does not import or
  instantiate `runtime.evaluator`; Evaluator remains the single state owner.
- Extended `EvaluatorContext` with explicit binder and family callbacks. The
  approved A2 boundary did not absorb tensor, ket, state-scaling, block, when,
  pipe, or other family bodies.
- Verification: Red contract **8 passed**; focused/adjacent **41 passed**;
  all-blocking **2,195 passed in 318.31s**; compileall, lifecycle,
  coverage-ledger, and diff checks passed.
- Active-Red ownership was retired after Green. Phase 3 readability and
  successor/facade structure review remain required.
- Next approval:
  `WP-0167 / LISS-0571 Phase 3 Refactor 承認`.

## Unit A2 Phase 3 Refactor

- Approval: `WP-0167 / LISS-0571 Phase 3 Refactor 承認` (2026-09-22).
- Same-context review packet:
  `docs/collaboration/reviews/2026-09-22-liss-0571-phase3-review.md`.
- Removed the duplicate legacy binder dispatcher bodies from `Evaluator`.
  `binding.py` is the sole dispatcher owner; existing family bodies remain
  callback-owned and the single Evaluator state owner is unchanged.
- Verification: compileall passed; focused/consumer/adjacent **49 passed**;
  all-blocking **2,195 passed in 314.09s**; active-Red lifecycle,
  document lifecycle, coverage-ledger, and diff checks passed.
- Result: Phase 3 Refactor accepted. Next approval:
  `WP-0167 / LISS-0571 Phase 3 最終レビュー 承認`.

## Unit A2 Phase 3 final review

- Approval: `WP-0167 / LISS-0571 Phase 3 最終レビュー 承認` (2026-09-22).
- Final review packet:
  `docs/collaboration/reviews/2026-09-22-liss-0571-final-review.md`.
- Result: accepted. Binder ownership, single Evaluator state ownership,
  private consumer compatibility, excluded scope, and verification evidence
  are consistent with the accepted design.
- Final evidence: focused/consumer/adjacent **49 passed**; all-blocking
  **2,195 passed in 314.09s**; compileall and lifecycle checks passed.
- Process review: no operating-contract deviation or operational problem
  found. LISS-0571 is complete; WP-0167 remains open for Units B–D.
