# AI Work Trace: Evaluator Unit C pipes and polynomial fusion

## Decision boundary

- Parent: WP-0167 evaluator successor decomposition.
- Proposed issue: LISS-0573.
- Current phase: Architecture Path design intake.
- Requested approval: `WP-0167 / Unit C pipe・block・polynomial Architecture
  Path scope approval`.
- Implementation permission: none.

## Evidence and inventory

- Target: 17 methods in `runtime/evaluator.py`, **302 physical lines**.
- Candidate successor: `runtime/evaluation/pipes.py`, target below 500 lines.
- Families: block binding; fused pipe stage resolution/evaluation; affine and
  polynomial composition; finite coefficient arithmetic; pipe flattening,
  simple-return eligibility, and piped-call hole filling.
- Actual runtime dispatcher consumer: `runtime/evaluation/binding.py`.
- Direct helper consumers: pipeline fusion, polynomial, affine, and bare-block
  Trace-Out tests.
- Result evidence remains Evaluator-owned through `last_algebraic_fusion` and
  `last_poly_fusion`; the successor may only use an explicit setter callback.

## Design decisions proposed

- Keep pipe mechanics and polynomial fusion in one successor because the
  polynomial parser/composer exists solely to decide and execute safe unary
  pipe fusion.
- Keep `typecheck.py` out of scope; runtime extraction must not alter compiler
  pipe typing or syntax.
- Keep all mutable maps, `Joint` mutation, function/object environments,
  trace-out behavior, and result DTO construction on the Evaluator side of the
  context boundary.
- Resolve the exact trace-out callback shape from actual consumers before Red.

## Verification plan

- Red: structural successor/body-retirement/wiring nodes plus positive block,
  unary, affine, polynomial, non-finite, and hole-filling characterizations.
- Green: focused consumer smoke, adjacent regression, and full blocking suite.
- Refactor: duplicate-body absence, successor structure budget, lifecycle,
  coverage-ledger, diff, and same-context review.

## Applicable process lessons

- `decomposition-callback-boundary`: private implicit entrypoints must become
  explicit callbacks before body removal.
- `evaluator-state-ownership`: no copied mutable maps or second runtime state
  owner in `pipes.py`.
- `private-consumer-inventory`: direct helper tests and dynamic compatibility
  wiring must be inventoried before Red.
- `red-contract-scope`: structural failures and positive characterizations are
  reported separately.

## Architecture Path scope approval

- Approval: `WP-0167 / Unit C pipe・block・polynomial Architecture Path scope
  approval` (2026-09-22).
- Scope accepted for design refinement only; implementation and Phase 1 Red
  remain unauthorized.
- Consumer evidence resolved the callback boundary: use explicit context
  declarations for the existing live-coordinate/trace-out behavior and a
  narrow fusion-evidence setter. Evaluator remains the owner of the observable
  fusion fields.
- The next gate is:
  `WP-0167 / LISS-0573 Phase 0 acceptance 承認`.

## Phase 0 acceptance

- Approval: `WP-0167 / LISS-0573 Phase 0 acceptance 承認` (2026-09-22).
- Accepted: runtime-only `pipes.py` successor, explicit context callback
  boundary, Evaluator-owned state/evidence, private-helper compatibility, and
  the below-500-line successor budget.
- Excluded: parser, typecheck, Semantic IR, QASM, providers, QPU, syntax,
  public API retirement, and unrelated state/evolution families.
- No production implementation is authorized. Next gate:
  `WP-0167 / LISS-0573 Phase 1 Red 承認`.

## Phase 1 Red

- Approval: `WP-0167 / LISS-0573 Phase 1 Red 承認` (2026-09-22).
- Added only `tests/test_liss_0573_pipes_successor_red.py` and its active-Red
  ledger entry. No production code changed.
- Contract shape: five structural failures and six passing characterizations
  for block, affine/poly fusion, non-finite handling, pipe holes, and helper
  parsing.
- Exact rerun: **5 failed, 6 passed**. The initial fixture used the wrong
  runtime result API; only the test fixture was corrected before rerunning.
- Next approval:
  `WP-0167 / LISS-0573 Phase 1 Red テストレビュー承認`.

## Phase 1 Red test review

- Approval: `WP-0167 / LISS-0573 Phase 1 Red テストレビュー承認`
  (2026-09-22).
- Same-context rerun: **5 failed, 6 passed**. Structural gaps are intentional;
  positive block/pipe/polynomial/hole characterizations pass.
- The initial fixture API mismatch was corrected only in the test before the
  review rerun. No production implementation was added.
- Review packet:
  `docs/collaboration/reviews/2026-09-22-liss-0573-phase1-red-review.md`.
- Next approval:
  `WP-0167 / LISS-0573 Phase 2 Green / Implementation 承認`.

## Phase 2 Green / Implementation

- Approval: `WP-0167 / LISS-0573 Phase 2 Green / Implementation 承認`
  (2026-09-22).
- Added `evaluation/pipes.py` (**346 lines**) and compatibility wiring. The
  Evaluator remains the sole mutable state/evidence owner; original bodies are
  retained only as explicit Phase 2 `*_body` callbacks.
- Red contract: **11 passed**; focused/adjacent: **71 passed**;
  all-blocking: **2,216 passed in 318.41s**.
- Measurements: Evaluator **2,596** lines; context **244**. The successor is
  below the accepted 500-line target.
- Compile, active-Red, document, coverage-ledger, and diff checks passed.
  Active-Red ownership was retired after Green.
- Tested SHA: `39e995f900574bf63db546a5cee4b89aa872cb39`; dirty worktree,
  macOS, repository virtualenv, Python 3.14; no commit-specific result.
- Next approval: `WP-0167 / LISS-0573 Phase 3 Refactor 承認`.

## Phase 3 Refactor

- Approval: `WP-0167 / LISS-0573 Phase 3 Refactor 承認` (2026-09-22).
- Removed the retained Unit C bodies from Evaluator; `pipes.py` is now the
  sole implementation owner. Context callbacks preserve Evaluator state and
  evidence ownership.
- Focused/adjacent: **71 passed**. All-blocking: **2,216 passed in 315.13s**.
- Measurements: Evaluator **2,246** lines; pipes **346**; context **244**.
  No Unit C `*_body` definitions remain in Evaluator.
- Checks: compile, active-Red lifecycle `entries=0`, document lifecycle,
  coverage-ledger consistency, and `git diff --check` passed.
- Review packet:
  `docs/collaboration/reviews/2026-09-22-liss-0573-phase3-review.md`.
- Next approval: `WP-0167 / LISS-0573 Phase 3 最終レビュー 承認`.

## Phase 3 Final Review

- Approval: `WP-0167 / LISS-0573 Phase 3 最終レビュー 承認` (2026-09-22).
- Re-read design, implementation, private-consumer evidence, and review
  packet. No blocker found.
- Focused/adjacent **71 passed**; all-blocking **2,216 passed in 315.13s**;
  compile, lifecycle, document, coverage-ledger, and diff checks passed.
- Review isolation: `same_context`, weaker than `separate_context`.
- LISS-0573 is complete. No commit, push, or PR was implied by this approval.
- Process review: no operating-contract deviation or operational problem
  found.
