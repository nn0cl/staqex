# Review Summary: LISS-0492-C operator/expression batch

## Review packet

- Scope: migrate operator-resolution, sigma/pi, projection, binder-adjacent
  arithmetic, and factory coefficient feature tests to canonical execution.
- Canonical documents: [LISS-0492](../../issues/LISS-0492-evaluator-run-unit-complete-removal.md),
  consumer-migration Spec, WP-0107, and ADR 0211.
- Changed files: `tests/canonical_execution.py` and the 12 LISS-0407 through
  LISS-0434 operator/expression test modules.
- Findings:
  - **F1 — accepted:** 42 direct evaluator calls in the selected operator /
    expression family now use the same-compile-result canonical helper.
  - **F2 — accepted:** targeted family verification passed 56 tests without
    changing scientific assertions.
  - **F3 — retained:** 31 direct references remain in port, dynamic, evolve,
    binder, and example tests; final API removal is not ready.
- Dispositions: F1/F2 accepted; F3 remains the next bounded migration scope.
- Verification: **56 passed**; helper compilation and `git diff --check`
  passed.
- Isolation: `same_context`; weaker than `separate_context`.
- Next approval required: continuation approval for the remaining 31-call
  family. This review does not authorize API removal.

## Evidence links

- Canonical Register: WP-0107 and LISS-0492.
- Representative Trace: `docs/collaboration/traces/2026-09-01-liss-0492-run-unit-removal-design.md`.
- Detailed Evidence: targeted pytest output and remaining-reference inventory.
