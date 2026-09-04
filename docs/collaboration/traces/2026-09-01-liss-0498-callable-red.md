# AI Work Trace

## Request

- Date: 2026-09-01
- User request: Continue the approved local semantic-family migration.
- Current phase: Phase 1 Red
- Canonical issue or work plan: LISS-0498 / WP-0107
- AI planning record: selected callable/object mechanics as the next family
  after binders, following the migration Spec sequence.

## Context Ledger

- Included: canonical function/class/call/receiver nodes, evaluator callable
  mechanics, runtime-plan boundary, and local AT-TDD rules.
- Omitted: provider/QPU/AWS, Rust, QASM, recursive/cross-module dispatch,
  dynamic lanes, and target realization.
- Assumptions: LISS-0493 remains the runtime-plan architecture authority.
- Open decisions: exact callable payload shape and bounded executor mechanics
  are Phase 2 decisions.

## Routing

- Model/assistant/tool: Codex host agent with same-context review routing.
- Reason: local repository work under sequential phase gates.
- Privacy constraints: repository-local context only.

## Adjudicator Decisions

- User approved continuation on 2026-09-01.

## Verification

- Commands/checks: `.venv/bin/pytest -q
  tests/test_liss_0498_evaluator_callable_plan_red.py`, `py_compile`, and
  `git diff --check`.
- Result: 3 failed, 1 passed, no collection errors; `py_compile` and
  `git diff --check` passed.

## Phase 2 Green continuation

- Scope: implement the reviewed minimum callable projection and bounded local
  callable/object executor.
- Result: LISS-0498 **4 passed**; related runtime-plan tests **21 passed**;
  manual canonical execution returned a measured value with canonical
  authority; `py_compile` and `git diff --check` passed.
- Changed production files: `compiler/staqex/scientific_semantic_ir.py` and
  `compiler/staqex/runtime/evaluator.py`.
- Boundary preserved: no target realization, dynamic lane, cross-module
  dispatch, QASM, or provider execution.

## Phase 3 continuation

- Refactored callable projection into a dedicated helper.
- Added and documented an explicit class-constructor compatibility boundary
  after regression testing exposed that the deferred State/Measure path does
  not own constructor mechanics yet.
- Same-context review: no blocking finding.
- Verification: LISS-0498 plus related runtime-plan and namespace/class tests
  **23 passed**; `py_compile` and `git diff --check` passed.

## Changed Files

- `tests/test_liss_0498_evaluator_callable_plan_red.py`
- `docs/issues/LISS-0498-evaluator-callable-plan.md`
- `docs/specs/staqex-scientific-semantic-consumer-migration.md`
- `docs/work-plans/WP-0107-scientific-semantic-core.md`

## Next Safe Action

Issue complete. The next safe action is a new semantic-family Phase 1 Red
contract.
