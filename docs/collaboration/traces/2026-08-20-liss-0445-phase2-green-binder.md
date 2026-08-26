# LISS-0445 Phase 2 Green — Binder Canonical Projection Trace

- Approval: user approved Phase 2 Green and implementation for this bounded
  binder slice.
- Scope: one compile-owned `ScientificSemanticIR` binder projection reused by
  projection diagnostics, QPU diagnostics, pipeline, and QASM diagnostics.
- Excluded: Algorithm Plan integration, H1 early-return, ordinary QASM AST
  fallback removal, provider SDK, live QPU, S02, solver, and ADR changes.
- Implementation files:
  `compiler/staqex/scientific_semantic_ir.py`,
  `compiler/staqex/qpu_ir.py`, `compiler/staqex/pipeline.py`,
  `compiler/staqex/backend/qasm/emitter.py`, and the focused LISS-0445 test
  call-site.
- Verification before QASM-entry correction:
  - focused LISS-0445 suite: **9 passed, 3 failed**;
  - related regression: **27 passed**;
  - full regression: **1659 passed, 3 failed**.
- Verification after QASM-entry correction:
  - combined focused and related suite: **33 passed, 3 failed**;
  - the three failures are intentional Algorithm Plan, H1, and ordinary
    QASM fallback Red contracts;
  - `git diff --check`: pass.
- The three failures are intentional Red contracts for the excluded slices.
- Historical condition before the final review: independent context review was
  required before Phase 2 closeout.
- Review 01 found and accepted one in-scope gap: the QASM入口 still rebuilt
  semantic IR internally. The correction adds an explicit `semantic_ir`
  parameter and shares one QPU program through the QASM path. A fresh review
  is required.
- Review 02 found no code blocker but identified this trace and the review
  record as stale; that documentation correction is recorded before the next
  independent review.
- Review 03 identified the public QASM convenience facades as a separate
  boundary. Disposition: deferred, because they compile from `CompilationUnit`
  without retaining `CompileResult.scientific_semantic_ir`; a follow-up QASM
  entry migration Issue is required. The direct `emit_unit` canonical-sharing
  contract remains within this approved slice.
- Follow-up issue created for the deferred boundary:
  [LISS-0446](../issues/LISS-0446-qasm-public-entry-canonical-sharing.md).
  It is parked with no implementation approval. The LISS-0445 binder slice is
  otherwise ready for final independent closeout review.
- Final independent review: **READY / COMPLETE**. The implementation slice is
  complete, LISS-0446 is explicitly parked, and no in-scope review blocker
  remains. This trace is the Phase 2 Green closeout record.
- Latest related verification recorded during final review: **55 passed, 3
  failed**, with the same three explicitly excluded Red contracts.
