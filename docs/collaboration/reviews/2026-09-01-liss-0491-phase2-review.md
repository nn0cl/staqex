# Review Summary: LISS-0491 Phase 2 Green

## Review packet

- Scope: minimum implementation for the approved legacy `run_unit()` retirement
  boundary.
- Canonical documents: [LISS-0491](../../issues/LISS-0491-evaluator-legacy-run-unit-retirement.md),
  [consumer migration Spec](../../specs/staqex-scientific-semantic-consumer-migration.md),
  [WP-0107](../../work-plans/WP-0107-scientific-semantic-core.md), and ADR 0211.
- Changed implementation files: `compiler/staqex/runtime/evaluator.py`,
  `compiler/staqex/host.py`, `compiler/staqex/run.py`, `compiler/staqex/cli.py`.
- Findings:
  - **F1 — accepted:** host, run, and inspection delivery paths now call the
    canonical evaluator entry with compile-owned semantic IR.
  - **F2 — accepted:** `EvalResult` exposes `source_id` and a structured
    `LEGACY_RUN_UNIT_DEPRECATED` record; canonical results clear the
    compatibility signal.
  - **F3 — accepted:** the Phase 1 inventory guard now reports no direct
    production `.run_unit()` callers outside `evaluator.py`.
  - **F4 — monitor in Phase 3:** `run_canonical_unit()` still delegates to
    existing evaluator mechanics. This is permitted by the Issue's temporary
    compatibility boundary and is not a Phase 2 defect.
- Dispositions: F1–F3 accepted; F4 retained as the explicit Phase 3 retirement
  candidate, not silently treated as complete.
- Remaining blockers: before Phase 3 removal, define final compatibility
  caller/test policy and prove unchanged-neighbor behavior across the broader
  local suite. No release policy is selected here.
- Verification: LISS-0491, LISS-0490, MeasureSinkPort, SourcePort, and host
  orchestration suites: **27 passed**. `py_compile` and `git diff --check`
  passed.
- Isolation: `same_context`; weaker than `separate_context`.
- Next approval required: Phase 3 refactor/review approval. This packet does
  not authorize removal of `run_unit()`.

## Evidence links

- Canonical Register: WP-0107 and LISS-0491.
- Representative Trace: `docs/collaboration/traces/2026-08-31-liss-0491-run-unit-retirement-design.md`.
- Detailed Evidence: Phase 1 Red test file and 27-test verification output.
