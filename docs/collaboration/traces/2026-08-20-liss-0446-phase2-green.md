# LISS-0446 Phase 2 Green Trace

- Trigger: user typed approval `承認` for `LISS-0446 Phase 2 Green`.
- Scope: WP-0109 Phase 2 Green only; local static QASM public facades.
- Excluded: live submission, provider SDK, dynamic QPU QASM, CH0 subset, S02,
  solver, Algorithm Plan, H1, and QASM fallback retirement.
- Branch: `codex/liss-0438-residual-reconciliation`.
- Implementation files: `compiler/staqex/scientific_semantic_ir.py`,
  `compiler/staqex/backend/qasm/emitter.py`,
  `compiler/staqex/codegen/openqasm.py`,
  `compiler/staqex/codegen_qasm.py`, and `compiler/staqex/cli.py`.
- Test files: `tests/test_liss_0446_qasm_public_entry_red.py`.

## Changes

- Propagated the compile-owned `ScientificSemanticIR` through backend,
  codegen, source/path, and CLI static QASM entry points.
- Added a source-unit identity pairing contract; mismatched unit/IR inputs are
  rejected before QPU projection and leave no QASM or partial circuit artifact.
- Preserved unit-only compatibility as one invocation-local build without an
  AST or process cache.

## Verification

- Focused LISS-0446: initially 8 passed; after review evidence corrections,
  **12 passed**.
- The final focused set covers CLI source and path compile-once for both
  `cmd_run` and `cmd_emit_qasm`.
- Spec verification: **161/161 passed**.
- Full pytest: **1667 passed / 3 known pre-existing LISS-0445 Red failures**.
- Known failures are Algorithm Plan projection, H1 early-return authority, and
  ordinary QASM AST-fallback retirement; they remain outside this Issue.
- `git diff --check`: passed before the evidence-correction pass.

## Independent review status

- Phase 2 Green review 01: `NOT READY`; accepted evidence corrections were
  applied and re-reviewed.
- Final independent review: `READY`; review loop terminal state `COMPLETE`.
- Accepted design-preserving findings: record this approval/trace, add direct
  public-entry identity coverage, assert atomic rejection artifacts, and add a
  direct Limit rejection boundary test.
- No architecture, technology, provider, or scope change was accepted.
- No review blocker remains. No subsequent phase or scope is approved by this
  record.
