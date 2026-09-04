# Review Summary: LISS-0491 Phase 3

## Review packet

- Scope: refactor canonical evaluator execution away from the public legacy
  `run_unit()` compatibility entry.
- Canonical documents: [LISS-0491](../../issues/LISS-0491-evaluator-legacy-run-unit-retirement.md),
  [consumer migration Spec](../../specs/staqex-scientific-semantic-consumer-migration.md),
  [WP-0107](../../work-plans/WP-0107-scientific-semantic-core.md), and ADR 0211.
- Changed implementation file: `compiler/staqex/runtime/evaluator.py`.
- Findings:
  - **F1 — accepted:** canonical execution now calls `_execute_unit()`
    directly, so the compatibility authority/deprecation decoration in
    `run_unit()` cannot be selected accidentally.
  - **F2 — accepted:** `run_unit()` remains available and retains its explicit
    legacy authority and deprecation metadata for the compatibility window.
  - **F3 — accepted:** no direct production callers remain outside
    `evaluator.py`; the inventory guard and existing delivery tests cover this.
  - **F4 — retained for future work:** `_execute_unit()` still contains the
    evaluator's AST mechanics. This Issue does not authorize rewriting or
    deleting those mechanics.
- Dispositions: F1–F3 accepted; F4 explicitly retained as a future migration
  candidate, not hidden as completed retirement.
- Remaining blockers: complete removal of `run_unit()` requires a separate
  compatibility-window decision and broader local regression evidence.
- Verification: LISS-0491, LISS-0490, MeasureSinkPort, SourcePort, and host
  orchestration suites **27 passed**; `py_compile` and `git diff --check`
  passed.
- Isolation: `same_context`; weaker than `separate_context`.
- Next approval required: none for this bounded Issue; future API removal is
  separate scope.

## Evidence links

- Canonical Register: WP-0107 and LISS-0491.
- Representative Trace: `docs/collaboration/traces/2026-08-31-liss-0491-run-unit-retirement-design.md`.
- Detailed Evidence: evaluator refactor and 27-test verification output.
