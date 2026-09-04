# Review Summary: LISS-0501 Phase 2 Green

## Review packet

- Scope: remove the direct AST fallback branch from canonical QASM emission.
- Canonical documents re-read: LISS-0501, LISS-0500, LISS-0444, WP-0107, the
  migration Spec, the LISS-0501 trace, and unchanged Red tests.
- Changed file re-read: `compiler/staqex/backend/qasm/emitter.py`.
- Findings:
  - **F1 — accepted:** canonical `emit_unit()` no longer calls the AST lowerer.
  - **F2 — accepted:** the lowerer remains only as an explicit module-level
    compatibility symbol, preserving controlled legacy callers.
  - **F3 — accepted:** canonical Measure and finite Suzuki/binder/ordinary
    projections remain unchanged.
  - **F4 — retained:** explicit compatibility caller retirement and other
    unsupported QASM families require separate contracts.
- Dispositions: F1–F3 accepted; F4 retained as the bounded scope boundary.
- Deterministic verification: LISS-0501 plus finite projection, consumer
  migration, and QASM public-entry tests **36 passed**, `py_compile`, and
  `git diff --check` passed.
- Isolation: `same_context`; weaker than `separate_context`.
- Next requested approval: Phase 3 refactor approval.
