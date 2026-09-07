# AI Work Trace: Basic migration of the current S02 sample

- User request: organize the current S02 under Basics before redesigning S02 as a realistic quantum-drug-discovery program.
- Current phase: Feature Path / Phase 2 Green.
- Canonical issue/work plan: LISS-0513 / WP-0130.
- Operating path: Feature Path.
- Included context: current S02 example tree, current S02 acceptance boundary, Basic example naming, current tests and references.
- Omitted context: new realistic S02 chemistry design, datasets, providers, credentials, live QPU, Rust.
- Routing: deterministic repository inspection and tests; no model-generated scientific data.
- Adjudicator decision: `Feature Path / Phase 1 Red / 現行S02のBasic移管 承認`, 2026-09-07.
- Assumption: `B19_constrained_selection` is the next available Basic example slot.
- Open decision: Phase 3 review is required before final closeout.

## Attempt 1

- Scope: add only migration acceptance tests and planning evidence.
- Result: **3 failed, 0 passed**, with no collection errors; expected Red state.
- Verification: `PYTHONPATH=. .venv/bin/pytest -q tests/test_liss_0513_basic_s02_example_migration_red.py`; `git diff --check` passed.
- Changed files: LISS-0513, WP-0130, this trace, and the Phase 1 test.
- Next safe action: review the Green result and request Phase 3 approval.

## Phase 2 Green

- Adjudicator decision: `Feature Path / Phase 2 Green / 現行S02のBasic移管 実装承認`, 2026-09-07.
- Scope: move and simplify the current boundary sample; update current
  references and preserve historical evidence.
- Result: Basic migration and boundary suites **42 passed**; S02 execution and
  baseline suites **14 passed**.
- Verification: `PYTHONPATH=. .venv/bin/pytest -q` on the focused migration,
  boundary, execution, and baseline suites; `git diff --check` passed.
- Changed files: Basic example tree, current tests/catalog/WP references,
  baseline identity, and this issue/WP/trace.
- Next safe action: review the Green result and request Phase 3 approval.
