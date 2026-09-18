# AI Work Trace: QASM CI canonical-consumer migration

## Request

- Date: 2026-09-18
- User request: `エラーは修正が必要。`
- Current phase: CI regression remediation / implementation and verification
- Canonical references: ADR 0222, LISS-0554, LISS-0393, LISS-0396, and the
  existing QASM consumer contracts

## Context Ledger

- Included: root-suite failures introduced/exposed by the strict canonical
  QASM emitter boundary, static live-QPU submission, and direct emitter tests.
- Omitted: provider credentials, live QPU execution, AWS network calls, Rust,
  dynamic-QPU emission design, and unrelated application behavior.
- Decision: preserve the accepted rule that `QASM3Emitter.emit_unit()` rejects
  a missing compile-owned semantic projection; migrate callers to pass the
  projection explicitly.

## Execution Records

### Attempt 1

- Scope: PR CI diagnosis and evaluator compatibility repair.
- Result: fixed the extracted observation lane's operator callback and pushed
  the PR-specific correction. Root suite still reported stale direct-emitter
  consumers and a static live-submit path without canonical provenance.

### Attempt 2

- Scope: canonical consumer migration and static live-submit repair.
- Result: updated direct-emitter tests to pass
  `compiled.scientific_semantic_ir`, corrected the stale `EmitResult` notes
  assertion, and updated `submit_live_qpu()` to pass the compile-owned
  projection on its static path. Dynamic QPU emission remains separate.
- Verification: focused consumer/live-submit tests **150 passed** across the
  migrated groups; full root suite **2117 passed**.

## Constraints and Review Notes

- No AST fallback or synthetic semantic IR was added.
- No provider SDK or live submission was executed.
- Test assertions and accepted behavior were preserved; only caller
  provenance and the stale diagnostic attribute were corrected.

## Changed Files

- `compiler/staqex/live_submit.py`
- direct QASM consumer tests under `tests/`

## Next Safe Action

Push the remediation commit to the existing PR and wait for repository CI.
