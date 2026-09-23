# AI Work Trace: Evaluator Unit B frames/constructors/assignments

## Decision boundary

- Parent: WP-0167 evaluator successor decomposition.
- New issue: LISS-0572.
- Scope approval: `WP-0167 / Unit B frames・constructors・assignments Architecture Path scope approval`
  (2026-09-22).
- Current state: Phase 0 design accepted; no Red test or production
  implementation authorized.

## Evidence and inventory

- Target bodies: `_legacy_bind_method` (173 lines),
  `_legacy_bind_user_fun` (145), `_legacy_construct_instance` (59),
  `_run_init` (47), `_legacy_construct_struct` (65), `_exec_assign` (36).
- Proposed owners: existing `evaluation/frames.py`, new
  `evaluation/constructors.py`, and new `evaluation/assignments.py`.
- Actual consumers: `calls.py`, `execution.py`, `classical.py`,
  `evolution.py`, `operators.py`, and direct private/structural tests.
- State boundary: Evaluator owns mutable maps, receiver/frame state, DTOs,
  `Joint`, scalar/unit stores, and ports. Successors receive callbacks only.

## Design decisions

- Keep frame invocation, construction/init, and field assignment as separate
  responsibilities.
- Preserve private aliases, exact diagnostics, mutation order, receiver and
  frame-unit restoration, and local unit propagation.
- Do not touch parser, typechecker, Semantic IR, QASM, providers, network,
  credentials, syntax, Rust, public APIs, or Units C/D.
- Phase 1 Red will define structural failures and positive behavior
  characterizations before any successor implementation.

## Phase 1 Red execution

- Approval: `WP-0167 / LISS-0572 Phase 1 Red 承認` (2026-09-22).
- Added only `tests/test_liss_0572_frames_constructors_assignments_red.py` and
  its issue-owned active-Red entry; no production module or compatibility
  implementation was added.
- Contract: six structural gaps and four passing characterizations covering
  free-function frames, method receivers, class init/assignment, and struct
  construction.
- Next approval:
  `WP-0167 / LISS-0572 Phase 1 Red テストレビュー承認`.

## Phase 1 Red test review

- Approval reviewed: `WP-0167 / LISS-0572 Phase 1 Red テストレビュー承認`
  (2026-09-22).
- Same-context review packet:
  `docs/collaboration/reviews/2026-09-22-liss-0572-phase1-red-review.md`.
- Re-run result: **6 failed, 4 passed** for the bounded Red suite; the
  failures are the declared structural gaps and the passing cases are the
  frame/constructor/assignment characterizations. Active-Red lifecycle,
  document lifecycle, coverage-ledger consistency, and diff checks passed.
- Review found no blocker. No production implementation was authorized. The
  active-Red entry remains owned by LISS-0572 until Green implementation.
- Next approval:
  `WP-0167 / LISS-0572 Phase 2 Green / Implementation 承認`.

## Phase 3 Refactor

- Approval: `WP-0167 / LISS-0572 Phase 3 Refactor 承認` (2026-09-22).
- Completed the bounded body migration into `frames.py`, `constructors.py`,
  and `assignments.py`. Evaluator remains the sole mutable state/DTO owner.
- Added narrow context callbacks for receiver/frame restoration, object
  construction, assignment mutation, unit/scalar stores, and operator
  resolution. No successor imports Evaluator or owns business policy.
- Focused consumer and adjacent regression: **61 passed**.
- All-blocking suite: **2,205 passed in 317.73s**.
- Checks: active-Red lifecycle `entries=0`, document lifecycle passed,
  coverage-ledger consistency passed, and `git diff --check` passed.
- Measurements: Evaluator **2,586** lines; frames **364**;
  constructors **188**; assignments **52**; context **234**.
- Tested SHA: `39e995f900574bf63db546a5cee4b89aa872cb39`; dirty worktree on
  macOS with the repository virtualenv and Python 3.14. No commit-specific
  rerun is claimed because this work is not committed.
- Review packet:
  `docs/collaboration/reviews/2026-09-22-liss-0572-phase3-review.md`.
- Next approval: `WP-0167 / LISS-0572 Phase 3 最終レビュー 承認`.

## Phase 3 Final Review

- Approval: `WP-0167 / LISS-0572 Phase 3 最終レビュー 承認` (2026-09-22).
- Re-read design, implementation, private-consumer evidence, and the review
  packet. No blocker found.
- Focused/adjacent **61 passed**; all-blocking **2,205 passed in 317.73s**;
  lifecycle, document, coverage-ledger, and diff checks passed.
- Review isolation: `same_context`, weaker than `separate_context`.
- LISS-0572 is complete. No commit, push, or PR was implied by this approval.
- Process review: no operating-contract deviation or operational problem
  found.

## Phase 2 Green / Implementation

- Approval: `WP-0167 / LISS-0572 Phase 2 Green / Implementation 承認`
  (2026-09-22).
- Added constructor and assignment successor modules and upgraded frame
  compatibility wiring. Existing evaluator bodies are retained only under
  explicit body-callback names for the reversible Phase 2 boundary; Phase 3
  owns their complete removal.
- Verification: Red contract **10 passed**; focused/consumer/adjacent
  **61 passed**; all-blocking **2,205 passed in 314.28s**; compileall,
  active-Red lifecycle, document lifecycle, coverage-ledger, and diff checks
  passed.
- Measurements: evaluator **3,121 lines**, frames **58**, constructors **24**,
  assignments **16**, context **219**.
- Active-Red ownership was retired after Green. Next approval:
  `WP-0167 / LISS-0572 Phase 3 Refactor 承認`.

## Applicable process lessons

- `decomposition-boundary`: remove legacy bodies rather than treating a facade
  alias as a completed split.
- `private-consumer-inventory`: use actual runtime imports and private-hook
  tests, while recording static-search false positives.
- `evaluator-state-ownership`: keep one Evaluator state owner and DTO identity.
- `compatibility-authority-boundary`: keep aliases thin and directional.
- `quantitative-traceability`: record body, module, and successor measurements.
