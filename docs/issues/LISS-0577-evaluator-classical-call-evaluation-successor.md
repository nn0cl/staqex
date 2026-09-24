# LISS-0577: Evaluator classical call evaluation successor

## Metadata

- Local issue ID: LISS-0577
- GitHub issue: none
- Status: in_progress — final review approved; commit and final-SHA verification pending
- Phase: phase-3-refactor
- Type: Architecture Path successor / runtime decomposition
- Priority: normal
- Initial planning size: L
- Current planning size: L
- Owner/agent: Codex host agent
- Related branch: `codex/liss-0577-classical-call-evaluation`
- Parent: WP-0170 / evaluator residual-body successors
- Depends on: WP-0169 / LISS-0576 (done and merged)
- Blocks: none yet

## Summary

Design a bounded, behavior-preserving extraction of the active classical
function/method call evaluation family from `runtime/evaluator.py`. The
approved four-method family occupies 259 lines on the LISS-0576 base and
serves both value evaluation and execution binding. The successor destination,
module-local context boundary, and exact phase paths are accepted in Phase 0.

## Acceptance notes

- Keep `Evaluator` as the only owner of runtime state and DTO identity.
- Preserve callable eligibility, diagnostics, argument precedence, lexical
  shadowing, units, receiver/frame restoration, intermediate assignments,
  struct returns, and current consumer entrypoints.
- Do not absorb classical operator-binder or operator-projection behavior into
  this call-evaluation slice.
- Prefer a focused successor over inflating unrelated modules; justify any
  shared-protocol growth with consumer/callback evidence.
- Record both structural ownership and behavior/consumer compatibility tests.

## Adjudicator decision points

- Scope: the user's “続きをやりたい” in response to the proposed next
  evaluator-residual investigation is treated as permission for investigation
  and design only, not implementation.
- Architecture approval: accept/revise the proposed successor and
  state/callback boundary in `docs/specs/evaluator-classical-call-evaluation.md`.
- Architecture approval recorded: `LISS-0577 Architecture approval 承認`
  (2026-09-24). Accepted the four-method classical-call boundary, one
  Evaluator-owned state/DTO authority, dedicated successor module, and
  compatibility entrypoints; no implementation was authorized.
- Phase 0 acceptance: separately accept the completed consumer inventory,
  behavior matrix, narrow module-local context proposal, and exact allowed
  paths in the specification.
- Phase 0 acceptance recorded: `LISS-0577 Phase 0 acceptance 承認`
  (2026-09-24). The proposed behavior inventory, module-local context
  boundary, and exact allowed paths are accepted. This does not authorize
  Phase 1 tests; those require separate approval.
- Phase 1 Red approval recorded: `Phase 1 Red承認` (2026-09-24). Authorizes
  tests and test-only fixtures in accepted paths only; production
  implementation remains unauthorized.
- Phase 1 Red test set was ready for review with three expected structural
  failures and three passing behavior/state-restoration characterizations.
- Phase 1 Red test approval recorded: `Phase 1 Redテスト承認` (2026-09-24).
  The test contracts are accepted. The focused pytest run with the existing
  project `.venv` produced 3 expected structural failures and 3 passing
  characterizations; no new environment was created. This approval does not
  authorize implementation.
- Phase 2 Green / Implementation approval recorded:
  `LISS-0577 Phase 2 Green / Implementation 承認` (2026-09-24).
- Phase 2 Green acceptance recorded: `Phase 2 Green承認` (2026-09-24).
  Phase 2 is accepted; this does not authorize Phase 3 Refactor.
- Phase 3 Refactor approval recorded: `LISS-0577 Phase 3 Refactor 承認`
  (2026-09-24). Only behavior-preserving refactoring within the accepted
  classical-call family was authorized.
- Phase 2 implementation completed within the approved files. All four
  evaluator bodies moved to `evaluation/classical_calls.py`; the active-Red
  exclusion was removed after the reviewed test suite passed.
- Verification (working tree dirty; HEAD/base SHA
  `9b2e2e0f8e56399ba8cbd662bbc3bf6d569cb7b7`; no comparable baseline run): on
  macOS 27.0 / Darwin 27.0, Python 3.14.6 and pytest 9.1.1, focused
  `tests/test_liss_0577_classical_calls_red.py` **6 passed**; consumer tests
  listed in the spec table **32 passed**; adjacent
  `test_liss_0566_unit_d_red.py` + `test_liss_0567_classical_frame_red.py`
  **16 passed**. All-blocking command from
  `/Users/nn0cl/.codex/worktrees/liss-0577-classical-call-evaluation/qpex`:
  `/Users/nn0cl/Documents/git/qpex/.venv/bin/python -m pytest
  -p no:cacheprovider tests/ -q` → **2,255 passed,
  0 failed** in 331.53s. Run window approximately 2026-09-24 10:54–11:00 JST.
  CI/final-commit rerun remains required.
  Lifecycle, document lifecycle, coverage-ledger, in-memory syntax, and diff
  checks passed. After-commit blocking rerun remains required.
- Phase 3 refactor and [review summary](../collaboration/reviews/2026-09-24-liss-0577-phase3-refactor-review.md): repeated class-method lookup and return-expression
  selection were consolidated into local helpers. The Phase 1 assertions and
  accepted module ownership contract were not changed. Focused, consumer,
  adjacent, and all-blocking verification passed; see the Phase 3 Review
  Summary for SHA/environment and failure comparison.
- Structure budget disposition: `classical_calls.py` is now 324 lines, above
  the advisory 300-line default. It remains a single accepted cohesive
  call-evaluation family; splitting it would conflict with the reviewed
  structural ownership contract and add an extra module boundary. Owner:
  Codex host agent; deadline: before LISS-0577 is marked done, decide at final
  review whether to accept the bounded exception or authorize further split.
- Phase 3 is complete and final Adjudicator review is approved. No commit has
  been made; blocking suites must be rerun after the final commit.
- Final review approved: `別ゲートの最終レビュー承認` (2026-09-24). The
  Phase 3 refactor and bounded 324-line structure disposition are accepted;
  no additional module split was requested. The Issue remains open until the
  approved changes are committed and all blocking suites pass on the final
  commit SHA.

## Context

- Included: current main Evaluator, `evaluation/classical.py`,
  `evaluation/execution.py`, `evaluation/context.py`, compatibility wiring,
  relevant direct consumer search, process lessons, source-quality and
  verification policies.
- Omitted: operator expression evaluation, unrelated residual evaluator
  families, parser/typechecker, provider/QPU code, and private external data.
- Phase 0 acceptance closed: the module-local context and failure-restoration
  characterization are accepted; no shared `EvaluatorContext` expansion is
  proposed.

## AI Planning Record

### AIP-0577-001

- Status: proposed
- Created by: Codex host agent, local isolated worktree
- Model / reasoning: not exposed by host UI
- Created at: 2026-09-24
- Planning size: L
- Intended route: host agent with AST/search/import tools; same-context review
  if a review packet is required by the effective routing
- Intended scope: Phase 0 call-family consumer/state inventory and accepted
  successor boundary only; no tests or implementation
- Estimated token range: 10,000–18,000 input+output tokens
- Estimated midpoint: 14,000 tokens
- Token metric: estimated model input+output tokens
- Basis: multiple runtime consumers, stateful frame/receiver contracts,
  characterization matrix, and full blocking verification planning
- Assumptions: no new language behavior or provider boundary is needed
- Confidence: medium
- Revises: none
- Superseded by: none

## References

- [Proposed acceptance design](../specs/evaluator-classical-call-evaluation.md)
- [Core module decomposition](../specs/staqex-core-module-decomposition.md)
- [Evaluator residual cleanup predecessor](../work-plans/WP-0169-evaluator-residual-body-cleanup.md)
- [AI work trace](../collaboration/traces/2026-09-24-liss-0577-phase0.md)
