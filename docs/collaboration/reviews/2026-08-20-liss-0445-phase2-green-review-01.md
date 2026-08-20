# LISS-0445 Phase 2 Green Independent Review 01

| Field | Value |
|---|---|
| Trigger | User-approved Phase 2 Green implementation and post-Green review |
| Context boundary | Fresh read-only reviewer; no edits, approval, or implementation |
| Result | **NOT READY**; one in-scope correction required |
| Scope | Binder canonical projection and its QPU/QASM diagnostic consumers only |

## Verification before correction

- Focused LISS-0445 suite: **9 passed, 3 failed**.
- Related regression: **27 passed**.
- Full regression: **1659 passed, 3 failed**.
- `git diff --check`: pass.
- Binder lowering was reduced to one compile-time build and pipeline/QPU
  diagnostics reused the compile-owned IR.

## Finding and disposition

| Priority | Finding | Disposition | Correction |
|---|---|---|---|
| P1 | `QASM3Emitter.emit_unit()` and its private QPU entry rebuilt `ScientificSemanticIR` from `CompilationUnit`, so the QASM入口 did not necessarily consume the compile-owned projection. | accepted | Added an optional `semantic_ir` input, build the QPU program once from that projection, pass the resulting program through the private QASM path, and updated the focused test to reject hidden semantic-IR rebuilding. |

## Non-blocking boundaries

The remaining Red failures are the explicitly excluded Algorithm Plan, H1
early-return, and ordinary QASM AST-fallback migrations. They remain separate
Green slices and were not changed by this correction.

## Reusable perspectives

- A consumer's internal helper may still bypass canonical authority even when
  its diagnostic function accepts a canonical projection; inspect the public
  entry and all private construction paths.
- When passing canonical IR explicitly, test that reconstruction is forbidden
  at the entry point, not only that downstream metadata matches.
- Keep excluded consumer migrations as explicit failures rather than broadening
  a bounded Green slice.

## Next review condition

Run a fresh independent review after the QASM入口 correction. Close Phase 2
Green only if the new review is READY/COMPLETE and the scoped regression
remains green apart from the three explicitly excluded Red contracts.
