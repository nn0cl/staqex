# LISS-0581 Phase 1 Red Test Review

## Review Target

- Artifact: [approved test design](2026-09-28-liss-0581-phase1-red-review.md),
  [new Red suite](../../../tests/test_liss_0581_evaluator_coordinate_liveness_red.py),
  [Active Red registry](../../testing/active-red-tests.toml), and
  [LISS-0581 specification](../../specs/evaluator-coordinate-liveness.md)
- Current phase: Phase 1 Red test review
- Requested approval: `WP-0174 / LISS-0581 Phase 1 Red テストレビュー承認`
- Approval type: phase review
- Approved scope: the Phase 1 tests and the two registered structural Red
  nodes; no production implementation
- Implementation allowed: no
- Post-review required: yes — separate Phase 2 Green and implementation
  approval

## Evidence

- Tested baseline HEAD: `83c93a524c7c90710ed965d231ffe85b20dc3163`
- Worktree: dirty; branch `feature/liss-0581-red`
- Environment: Python 3.14.6, local macOS host
- Focused command: `pytest -q tests/test_liss_0581_evaluator_coordinate_liveness_red.py`
- Focused result: 3 passed, 2 failed as expected (structural Red)
- Active-Red characterization only: 3 passed, 2 deselected
- Adjacent command covered Trace-Out function, block, evolve, interprocedural,
  LISS-0561 observation/dynamic, LISS-0572 frames, and LISS-0573 pipes suites
- Adjacent result: 36 passed
- Lifecycle: `ACTIVE_RED_LIFECYCLE_OK entries=2`
- `git diff --check`: passed
- Full blocking suite: not run in Phase 1; no implementation or final Green is
  claimed.

## Acceptance Reconciliation

| Acceptance node | Result | Disposition |
|---|---|---|
| Eligible post-call live-out names feed Trace-Out retention without Inspect/Snapshot | Passed | Parsed StateBind live-out set and representative Joint transformation retain `keep` and result `r`, while dropping dead `x`/`y`; source program compiles/runs with expected terminal value |
| Inspect excludes interprocedural liveness | Passed | Direct eligibility assertion on parsed main statements |
| Snapshot excludes interprocedural liveness | Passed | Existing Snapshot syntax parsed; direct eligibility assertion |
| Successor owns algorithms and Evaluator AST walker hooks retain successor identity | Expected Red | Successor module does not yet exist |
| Frames no longer duplicate coordinate helpers | Expected Red | `frames.py` still owns both local helper bodies |

An initial run exposed test setup issues (repository import path and a linear
state fixture); both were corrected. They are not counted as product failures.
No test or source change weakened an existing assertion. Existing adjacent
tests all passed in the final run.

## Decision

- [x] Accepted
- [ ] Needs correction
- [ ] Rejected

Adjudicator decision: accepted — `WP-0174 / LISS-0581 Phase 1 Red テストレビュー承認`,
2026-09-28. Phase 2 is not authorized by this test review.
