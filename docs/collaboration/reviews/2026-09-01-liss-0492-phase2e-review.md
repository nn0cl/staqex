# Review Summary: LISS-0492-C final feature migration

## Review packet

- Scope: migrate the remaining 31 feature/regression `run_unit()` references
  across ports, dynamic/evolve, binders, and the example export test.
- Canonical documents: [LISS-0492](../../issues/LISS-0492-evaluator-run-unit-complete-removal.md),
  consumer-migration Spec, WP-0107, and ADR 0211.
- Changed files: `tests/canonical_execution.py` and 14 feature/regression
  test modules.
- Findings:
  - **F1 — accepted:** all 31 remaining executable test references now use the
    same-compile-result canonical helper.
  - **F2 — accepted:** targeted feature verification passed 65 tests without
    changing scientific assertions.
  - **F3 — accepted as removal gate:** the no-reference scan passes outside
    the LISS-0491/LISS-0492 contract tests; only the public `Evaluator.run_unit`
    attribute remains and its Red assertion fails as expected.
- Dispositions: F1/F2 accepted; F3 is the exact prerequisite for the next
  API-removal batch.
- Verification: **65 passed** for the final feature batch; LISS-0492 guard
  **3 passed, 1 failed** (public API still present); `git diff --check` passed.
- Isolation: `same_context`; weaker than `separate_context`.
- Next approval required: explicit API-removal implementation approval for
  LISS-0492-D. This review does not authorize deleting `run_unit()`.

## Evidence links

- Canonical Register: WP-0107 and LISS-0492.
- Representative Trace: `docs/collaboration/traces/2026-09-01-liss-0492-run-unit-removal-design.md`.
- Detailed Evidence: final feature-batch pytest output and removal-guard output.
