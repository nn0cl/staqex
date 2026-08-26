# LISS-0446 Design and Impact Investigation

- User authorization: investigation only; read-only scope, no implementation.
- Branch: `codex/liss-0438-residual-reconciliation` (non-main).
- Inspected: LISS-0446, ADR 0211, WP-0108, QASM emitter/backend wrappers,
  `codegen_qasm`, CLI, live submit boundary, tests, and spec-verification
  suites.
- Current fact: direct `QASM3Emitter.emit_unit(..., semantic_ir=...)` can
  consume a compile-owned projection. Public convenience APIs still commonly
  accept only `CompilationUnit` and rebuild semantic IR.
- Inventory and proposed ownership design are recorded in the proposed
  Spec/WP-0109.
- Recommended design: propagate the existing `ScientificSemanticIR` through
  source/path/CLI convenience flows; retain optional explicit IR for unit-only
  compatibility; never attach it to AST or cache it globally.
- Impacted local paths: backend QASM wrapper, `codegen.openqasm`,
  `OpenQASM3Generator`, source/path helpers, CLI, and their tests/spec suites.
- Explicitly excluded: `live_submit.py`, provider SDKs, live QPU, S02,
  solver, H1, Algorithm Plan, and unrelated QASM fallback retirement.
- No code or tests were changed during this investigation.
- Next gate: independent review of proposed Spec/WP, then separate Phase 1 Red
  approval. Implementation remains unapproved.
- Initial design review result: **NOT READY**. Accepted corrections are
  recorded in the proposed Spec/WP: explicit dynamic/ch0 exclusions,
  observable call-count/object-identity and artifact-preservation cases,
  fallback-change boundary, and unit-only/mismatched-pair contract.
- Fresh design review result: **READY**. Phase 1 Red may proceed within
  WP-0109; Phase 2 Green and implementation remain separately gated.
- Phase 1 Red result: `.venv/bin/pytest -q
  tests/test_liss_0446_qasm_public_entry_red.py` returned **5 failed, 3
  passed**, with no collection errors. The failures are intentional missing
  public-wrapper IR propagation, source/path forwarding, and mixed-source
  pairing rejection contracts.
- No production implementation or test weakening was performed in Phase 1
  Red. Phase 2 Green requires a separate typed approval.
