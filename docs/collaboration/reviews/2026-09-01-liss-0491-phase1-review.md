# Review Summary: LISS-0491 Phase 1 Red

## Review packet

- Scope: Phase 1 Red acceptance tests for staged retirement of evaluator
  `run_unit()`.
- Canonical documents: [LISS-0491](../../issues/LISS-0491-evaluator-legacy-run-unit-retirement.md),
  [consumer migration Spec](../../specs/staqex-scientific-semantic-consumer-migration.md),
  [WP-0107](../../work-plans/WP-0107-scientific-semantic-core.md), and ADR 0211.
- Changed files: `tests/test_liss_0491_evaluator_legacy_run_unit_retirement_red.py`,
  LISS-0491 Issue/Spec/WP records, and the representative trace.
- Findings:
  - **F1 — apply in Phase 2:** host and `run.py` still bypass the canonical
    entry; the tests identify the exact delivery migration seam.
  - **F2 — apply in Phase 2:** `EvalResult` lacks an observable deprecation
    record and source provenance required by the compatibility contract.
  - **F3 — apply in Phase 2:** four direct production callers remain in
    `host.py`, `run.py`, and `cli.py`; the inventory guard makes new bypasses
    visible.
  - **F4 — already closed with evidence:** no production implementation,
    provider integration, API removal, or fixture expansion was performed in
    Red.
- Dispositions: F1–F3 are accepted implementation targets; F4 is confirmed
  within the approved Phase 1 scope.
- Remaining blockers: Phase 2 must choose and document the concrete
  deprecation metadata shape without introducing a release policy or new
  provider boundary. Delivery migration must preserve State/Measure and port
  behavior.
- Verification result: `./.venv/bin/pytest -q
  tests/test_liss_0491_evaluator_legacy_run_unit_retirement_red.py` returned
  **5 failed, 0 collection errors**, as required for Red. `git diff --check`
  passed.
- Isolation: `same_context`; weaker than `separate_context`.
- Next approval required: Phase 2 Green implementation approval. This review
  does not grant implementation permission.

## Evidence links

- Canonical Register: WP-0107 and LISS-0491.
- Representative Trace: `docs/collaboration/traces/2026-08-31-liss-0491-run-unit-retirement-design.md`.
- Detailed Evidence: the Phase 1 Red test file and its recorded five failures.
