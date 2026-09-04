# Review Summary: LISS-0492-D API removal

## Review packet

- Scope: remove public `Evaluator.run_unit()` and compatibility-only
  deprecation metadata after all executable callers migrated.
- Canonical documents: [LISS-0492](../../issues/LISS-0492-evaluator-run-unit-complete-removal.md),
  consumer-migration Spec, WP-0107, and ADR 0211.
- Findings:
  - **F1 — accepted:** public `Evaluator.run_unit` and
    `execution_deprecation` are removed; canonical execution retains
    `execution_authority` and `source_id`.
  - **F2 — accepted:** no executable `.run_unit()` reference remains outside
    historical removal-contract string assertions.
  - **F3 — accepted:** API-related regressions and Spec Verification pass.
  - **F4 — out of scope:** 10 full-suite failures remain in pre-existing QASM
    and meaning-family Red expectations; they are unrelated to this Issue.
- Dispositions: F1–F3 accepted; F4 remains with its owning issues.
- Verification: API-related **19 passed**; Spec Verification **161/161 passed**;
  full pytest **1823 passed, 10 unrelated failures**; `py_compile` and
  `git diff --check` passed.
- Isolation: `same_context`; weaker than `separate_context`.
- Next approval required: none for LISS-0492; internal AST mechanics remain
  separate future scope.

## Evidence links

- Canonical Register: WP-0107 and LISS-0492.
- Representative Trace: `docs/collaboration/traces/2026-09-01-liss-0492-run-unit-removal-design.md`.
