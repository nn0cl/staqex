# LISS-0567 evaluator classical/frame successor design trace

## Phase 0 design intake

- Date: 2026-09-19
- Scope: continue evaluator decomposition after completed WP-0163.
- Evidence: `evaluator.py` is 4,005 lines with 112 class methods; the largest
  remaining cohesive candidates are method/function frame execution and
  classical value evaluation.
- Proposed boundary: `evaluation/frames.py` for invocation-frame lifetime and
  `evaluation/classical.py` for classical value/constructor policy.
- Retained facade responsibilities: mutable state ownership and the
  cross-family `_run_legacy_ast_body`, `_bind`, and `_bind_names` dispatchers.
- Omitted: parser/typechecker, scientific-family implementation, providers,
  QPU/network work, and public API retirement.
- Decision needed: Architecture Path Phase 0 scope/design approval for
  `LISS-0567 / WP-0164`.
- Next safe action: complete the approved call-graph/state-ownership
  inventory, then propose reviewed Phase 1 Red contracts.

## Phase 0 evidence

- Date: 2026-09-19
- Result: confirmed the frame/value call graph, mutable-state owner, private
  runtime consumers, no-facade dependency direction, and exact Phase 1
  allowed paths.
- Boundary: `frames.py` owns invocation-frame lifetime and receiver cleanup;
  `classical.py` owns classical value/call/constructor policy. The facade
  retains cross-family `_run_legacy_ast_body`, `_bind`, and `_bind_names`.
- Proposed Red: module ownership, context callback completeness, private alias
  preservation, frame restoration, and existing classical characterization.
- Next approval: `WP-0164 / LISS-0567 Architecture Path Phase 0 acceptance 承認`.

## Phase 1 Red

- Date: 2026-09-19
- Approval: `WP-0164 / LISS-0567 Phase 1 Red 承認`
- Result: added eight bounded structural and characterization contracts;
  expected pre-Green result is **5 failed, 3 passed**.
- Scope discipline: only the approved test file, Active-Red lifecycle entry,
  and linked status records changed; no production implementation started.
- Next approval: `WP-0164 / LISS-0567 Phase 1 Red テストレビュー承認`.

## Phase 0 acceptance

- Date: 2026-09-19
- Approval: `WP-0164 / LISS-0567 Architecture Path Phase 0 acceptance 承認`
- Result: accepted the two-module classical/frame boundary, single mutable
  `Evaluator` owner, retained cross-family dispatchers, exact Phase 1 allowed
  paths, and proposed Red contracts.
- Scope: Phase 1 Red test work only; no production extraction or public API
  retirement authorized.
- Next approval: `WP-0164 / LISS-0567 Phase 1 Red 承認`.

## Phase 1 Red test review

- Date: 2026-09-19
- Approval: `WP-0164 / LISS-0567 Phase 1 Red テストレビュー承認`
- Route: `same_context`, weaker than `separate_context`.
- Evidence: focused Red run is **5 failed, 3 passed**. The five failures are
  the expected absent successor modules, callback declarations, and
  compatibility installers. Function-frame, method-receiver, and
  struct-return characterizations pass.
- Checks: test lifecycle, document lifecycle, coverage-ledger consistency,
  and `git diff --check` passed. No production implementation was added.
- Review packet:
  `docs/collaboration/reviews/2026-09-19-liss-0567-phase1-red-review.md`.
- Next approval: `WP-0164 / LISS-0567 Phase 2 Green / Implementation 承認`.

## Phase 2 Green / Implementation

- Date: 2026-09-19
- Approval: `WP-0164 / LISS-0567 Phase 2 Green / Implementation 承認`
- Result: added the explicit frame/classical successor modules and
  compatibility wiring. `Evaluator` remains the sole mutable state owner;
  legacy bodies are retained behind `_legacy_*` callbacks.
- Verification: focused and adjacent evaluator contracts **15 passed**;
  full pytest **2,163 passed**; compileall, lifecycle, document,
  coverage-ledger, and diff checks passed.
- Scope discipline: no parser, Semantic IR, QASM, provider, public API, or
  new language behavior was added. Active-Red ownership was retired after all
  eight LISS-0567 contracts passed.
- Next approval: `WP-0164 / LISS-0567 Phase 3 Refactor 承認`.

## Phase 3 Refactor

- Date: 2026-09-19
- Approval: `WP-0164 / LISS-0567 Phase 3 Refactor 承認`
- Result: clarified callback signatures, context contracts, compatibility
  grouping, and legacy-body responsibilities without changing behavior.
- Verification: focused and adjacent suites **15 passed**; full pytest
  **2,163 passed**; compileall, lifecycle, document, coverage-ledger, and
  diff checks passed.
- Scope discipline: no assertion, fixture, language semantic, provider,
  public API, or mutable-state ownership change.
- Next approval: `WP-0164 / LISS-0567 Phase 3 最終レビュー 承認`.

## Phase 3 final review

- Date: 2026-09-19
- Approval: `WP-0164 / LISS-0567 Phase 3 最終レビュー 承認`
- Result: final review accepted the bounded successor, compatibility wiring,
  state ownership, and structure budget.
- Verification: focused/adjacent **15 passed**, full pytest **2,163 passed**,
  compileall, lifecycle, document, coverage-ledger, and diff checks passed.
- Process review: no operating-contract deviation or operational problem
  found.
- Status: WP-0164 / LISS-0567 complete. Future evaluator body migration and
  private alias retirement require a new approved scope.
