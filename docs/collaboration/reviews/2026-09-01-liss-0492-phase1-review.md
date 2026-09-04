# Review Summary: LISS-0492 Phase 1 Red

## Review packet

- Scope: fixed Red contract for complete evaluator `run_unit()` removal.
- Canonical documents: [LISS-0492](../../issues/LISS-0492-evaluator-run-unit-complete-removal.md),
  consumer-migration Spec, WP-0107, and ADR 0211.
- Changed files: `tests/test_liss_0492_evaluator_run_unit_complete_removal_red.py`,
  Issue/Spec/WP records, and the LISS-0492 trace.
- Findings:
  - **F1 — Phase 2:** public `Evaluator.run_unit` remains present; the Red
    assertion fixes the final API-removal target.
  - **F2 — Phase 2:** 131 executable test/spec-verification references remain;
    caller migration must be split into bounded families.
  - **F3 — accepted:** canonical helper and State/Measure/source authority
    assertions pass without production changes.
- Dispositions: F1/F2 accepted implementation targets; F3 confirmed in scope.
- Remaining blockers: migrate all callers while preserving same-compile-result
  canonical IR provenance; no API removal is permitted before that migration.
- Verification: **2 failed, 2 passed**, no collection errors; `git diff --check`
  passed.
- Isolation: `same_context`; weaker than `separate_context`.
- Next approval required: Phase 2 Green implementation approval. This review
  grants no implementation permission.

## Evidence links

- Canonical Register: WP-0107 and LISS-0492.
- Representative Trace: `docs/collaboration/traces/2026-09-01-liss-0492-run-unit-removal-design.md`.
- Detailed Evidence: Phase 1 Red test file and its 131-reference inventory.
