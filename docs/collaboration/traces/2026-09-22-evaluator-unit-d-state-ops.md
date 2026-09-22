# AI Work Trace: Evaluator Unit D state construction and algebra

## Decision boundary

- Parent: WP-0167 evaluator successor decomposition.
- Proposed issue: LISS-0574.
- Current phase: Architecture Path design intake.
- Requested approval: `WP-0167 / Unit D state construction・algebra
  Architecture Path scope approval`.
- Implementation permission: none.

## Evidence and inventory

- Target: 9 methods in `runtime/evaluator.py`, **192 physical lines**.
- Candidate successor: `runtime/evaluation/state_ops.py`, target below 400
  lines and below the repository 1,200-line guardrail.
- Families: ket literal, unnormalized ket-sum, State-producing classifier,
  scalar scaling, explicit norm division, norm, selection preparation, inner,
  and outer materialization.
- Consumers: binding, calls, execution, observation, and direct LISS-0229,
  LISS-0324, LISS-0420/0422, and LISS-0426 tests.
- State boundary: Evaluator owns mutable maps, `Joint` lifecycle, DTO identity,
  and object/scalar stores; the successor receives explicit callbacks.

## Design decisions proposed

- Keep state construction and State/Operator algebra in one successor because
  the shared boundary is Joint-based state meaning, not generic matrix math.
- Preserve unnormalized Sigma semantics and explicit `/ ||state||` behavior.
- Preserve `inner` as classical overlap and `outer` as Operator-only
  materialization.
- Resolve scientific binding and DenseMatrixOp callback/direct-dependency
  shape from actual consumers before Red.

## Verification plan

- Red: structural successor/body-retirement/wiring nodes plus positive and
  negative State/Operator boundary characterizations.
- Green: focused consumers, adjacent state/operator regressions, and full
  blocking suite.
- Refactor: duplicate-body absence, successor structure budget, lifecycle,
  coverage-ledger, diff, and same-context review.

## Applicable process lessons

- `evaluator-state-ownership`: no copied mutable state or second Joint owner.
- `private-consumer-inventory`: binding/call/execution/observation and direct
  private tests must be inventoried before Red.
- `boundary-completeness`: preserve explicit State/Operator and normalization
  boundaries rather than hiding policy in an adapter.
- `decomposition-callback-boundary`: promote implicit runtime entrypoints to
  explicit context callbacks before body removal.

## Architecture Path scope approval

- Approval: `WP-0167 / Unit D state construction・algebra Architecture Path
  scope approval` (2026-09-22).
- Scope accepted for design refinement only; Phase 1 Red and implementation
  remain unauthorized.
- Consumer inspection resolved that the successor may directly use the pure
  `resolve_scientific_binding` helper and pure `DenseMatrixOp` DTO definition.
  It must not import Evaluator; nested binding and Joint mutation remain
  explicit context operations.
- Next approval: `WP-0167 / LISS-0574 Phase 0 acceptance 承認`.

## Phase 0 acceptance

- Approval: `WP-0167 / LISS-0574 Phase 0 acceptance 承認` (2026-09-22).
- The nine-method state construction/algebra boundary and the
  `state_ops.py` successor were accepted for Red preparation.
- Pure scientific-binding and `DenseMatrixOp` dependencies are permitted;
  Evaluator import, Joint ownership, nested binding, and mutable state remain
  context-owned boundaries.
- Consumer/import inventory and callback ambiguity resolution are complete.
  No production implementation or test rewrite was performed.
- Next approval: `WP-0167 / LISS-0574 Phase 1 Red 承認`.

## Phase 1 Red

- Approval: `WP-0167 / LISS-0574 Phase 1 Red 承認` (2026-09-22).
- Added the bounded structural/characterization Red suite and active-Red
  ledger entry only; no production implementation was made.
- The suite declares five structural gaps and six passing state-construction/
  algebra characterizations.
- Exact bounded run: **5 failed, 6 passed** in 0.17s with the repository
  Python 3.14 virtual environment. The failures match the declared missing
  successor/wiring contracts; lifecycle, coverage-ledger, and diff checks
  passed.
- Next approval: `WP-0167 / LISS-0574 Phase 1 Red テストレビュー承認`.

## Phase 1 Red test review

- Approval: `WP-0167 / LISS-0574 Phase 1 Red テストレビュー承認`
  (2026-09-22).
- Review packet:
  `docs/collaboration/reviews/2026-09-22-liss-0574-phase1-red-review.md`.
- Same-context review reproduced the declared **5 failed, 6 passed**
  result; the omitted-extension command was corrected before disposition.
- No production implementation was added. Next approval:
  `WP-0167 / LISS-0574 Phase 2 Green / Implementation 承認`.

## Phase 2 Green / Implementation

- Approval: `WP-0167 / LISS-0574 Phase 2 Green / Implementation 承認`
  (2026-09-22).
- Added the 168-line `state_ops.py` successor and compatibility wiring;
  removed all nine Unit D bodies from the Evaluator facade.
- Red suite: **11 passed**. Focused/adjacent state/operator regression:
  **25 passed**. All-blocking: **2,227 passed in 315.50s** on dirty SHA
  `39e995f900574bf63db546a5cee4b89aa872cb39`.
- Compileall, lifecycle, coverage-ledger, and diff checks passed. The final
  post-commit blocking rerun remains pending by policy.
- Next approval: `WP-0167 / LISS-0574 Phase 3 Refactor 承認`.

## Phase 3 Refactor

- Approval: `WP-0167 / LISS-0574 Phase 3 Refactor 承認` (2026-09-22).
- Final successor measurement: `state_ops.py` 167 lines / 9 functions;
  `evaluator.py` 2,048 lines with no Unit D method bodies.
- Focused/adjacent: **36 passed**; all-blocking: **2,227 passed in 313.88s**.
- Review packet:
  `docs/collaboration/reviews/2026-09-22-liss-0574-phase3-review.md`.
- Next approval: `WP-0167 / LISS-0574 Phase 3 最終レビュー 承認`.

## Phase 3 Final Review

- Approval: `WP-0167 / LISS-0574 Phase 3 最終レビュー 承認` (2026-09-22).
- No blocking issue found. LISS-0574 state construction/algebra extraction
  is complete and the parent WP remains open only for consolidation.
- Process review: no operating-contract deviation or operational problem
  found.
