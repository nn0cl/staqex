# AI work trace: LISS-0496 evolution runtime-plan Red

## Request

- Date: 2026-09-01
- User request: continue with the next approved semantic-family task.
- Current phase: Phase 1 Red
- Canonical issue or work plan: LISS-0496 / WP-0107
- AI planning record: design intake in LISS-0496.

## Context Ledger

- Included: LISS-0493–0495, WP-0107, consumer-migration and language Specs,
  Scientific Semantic IR evolution projections, evaluator evolution behavior,
  implementation readiness, and process lessons.
- Omitted: provider/QPU/AWS, Rust, QASM target realization, continuous/open
  systems, solver, and unrelated plan families.
- Assumptions: this slice covers explicit local `Evolve` only; target
  realization remains a separate consumer.
- Open decisions: exact evolution plan payload and executor mechanics remain
  for Phase 2.

## Routing

- Model/assistant/tool: host agent and deterministic pytest/py_compile tools.
- Reason: local Feature Path acceptance contract; no external resource needed.
- Privacy constraints: no secrets, provider data, or network access.

## AI Execution Records

### Attempt 1

- Agent: host agent
- Environment: local qpex workspace
- Model as displayed: N/A
- Reasoning setting as displayed: N/A
- Estimated token range: N/A
- Estimated token midpoint: N/A
- Actual tokens: N/A
- Token metric: N/A
- Token source: N/A
- Token attribution boundary: N/A
- Actual token unavailable reason: host does not expose token telemetry
- Estimate variance: N/A
- Variance reason: N/A
- Scope: design intake, Issue/Spec/WP ledger update, and Phase 1 Red tests
- Result: created the evolution acceptance contract; production code was not
  changed.
- Attempt boundary: completed after correcting the source fixture and rerunning
  deterministic verification.
- Notes: the initial invalid `Evolve()` fixture was corrected before the final
  Red result was recorded.

## Cost / Reasoning Control

- Operating path: Feature Path, Phase 1 Red
- Files read: quickstart, AT-TDD process, implementation readiness, project
  conventions, testing strategy, runtime model, LISS-0495, WP-0107, Spec,
  language specification, process lessons.
- Context intentionally omitted: external providers and unrelated families.
- Deterministic checks used: pytest, py_compile, git diff --check.
- Escalation reason: none.
- Avoided LLM work: no external research or generated implementation.
- Rework caused by AI output: one invalid test fixture was corrected.

## Adjudicator Decisions

- Phase 1 Red approved 2026-09-01.

## Verification

- Commands/checks: `.venv/bin/pytest -q tests/test_liss_0496_evaluator_evolution_plan_red.py`; `py_compile`; `git diff --check`.
- Result: 3 failed, 1 passed, no collection errors; syntax and diff checks
  passed.

## Changed Files

- `docs/issues/LISS-0496-evaluator-evolution-plan.md`
- `docs/specs/staqex-scientific-semantic-consumer-migration.md`
- `docs/work-plans/WP-0107-scientific-semantic-core.md`
- `tests/test_liss_0496_evaluator_evolution_plan_red.py`

## Next Safe Action

Human review of the Red contract. Phase 2 Green requires explicit approval;
do not modify production code before that gate.

## Phase 2 continuation

- Adjudicator decision: Phase 2 Green approved 2026-09-01.
- Result: added canonical evolution projection and a bounded local evolution
  executor. Complex/target-specific forms remain explicit legacy fallback.
- Verification: LISS-0496 4 passed; related evolution/runtime/API regressions
  36 passed; `py_compile` and `git diff --check` passed.
- Next safe action: Phase 3 refactor review.

## Phase 3 continuation

- Adjudicator decision: Phase 3 refactor approved 2026-09-01.
- Result: extracted `_evolution_runtime_unit` to isolate compile-time Operator
  declarations from local runtime bind steps without changing behavior.
- Verification: 40 related tests passed; `py_compile` and `git diff --check`
  passed.
- Review: `docs/collaboration/reviews/2026-09-01-liss-0496-phase3-review.md`.
- Next safe action: Phase 1 Red design for the next semantic family.
