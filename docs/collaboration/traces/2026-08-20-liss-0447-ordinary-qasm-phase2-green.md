# LISS-0447 Ordinary QASM Phase 2 Green Trace

- Approval: user approved the ordinary-QASM Phase 2 Green subcontract after
  H1 completion.
- Scope: canonical ordinary-gate fixture and the shared static ordinary-gate
  projection path.
- Excluded: finite Suzuki compatibility lowering, provider/live QPU, S02,
  solver, syntax, H1, and LISS-0446 public-entry redesign.

## [DESIGN CHECK]

- **Scope and expected behavior:** source-derived canonical projection emits
  ordinary preparation, `apply`, `cnot`, `capply`, and terminal measurement;
  unsupported inputs reject without QASM, gates, allocation, or partial
  program.
- **Specifications and files inspected:** LISS-0447 Issue/Spec/WP, ADR 0211,
  `scientific_semantic_ir.py`, `qpu_ir.py`, QASM emitter, and fixed Red tests.
- **Component boundaries:** Scientific Semantic IR owns source-derived
  operation intent; QPU IR is its executable projection; QASM only renders
  the validated QPU projection. AST lowering remains only in the explicitly
  retained finite Suzuki compatibility path.
- **Applicable constraints:** no implicit finiteization, no provider SDK/live
  submit, no S02 or solver work, and no H1 changes.
- **Independent review lenses:** canonical authority, projection
  conservation, fallback retirement, fail-closed atomic rejection, and
  regression safety.
- **Verification plan:** fixed LISS-0447 tests, QASM regression tests,
  LISS-0445/0446 related tests, `git diff --check`, then fresh independent
  review.

## Implementation

- Added canonical ordinary operations for ket preparation, direct `apply`,
  `cnot`, `capply`, and terminal measurement with source node identity.
- Added S/T/CZ operation vocabulary and preserved rotation scalar handling.
- Removed the ordinary no-projection AST fallback; unsupported ordinary
  inputs return `E_QPU_CANONICAL_PROVENANCE` atomically.
- Preserved the finite Suzuki/binder compatibility fallback as out of scope.

## Verification

- `.venv/bin/pytest -q tests/test_liss_0447_residual_semantic_consumers_red.py
  tests/test_qasm3_codegen.py tests/test_liss_0445_consumer_migration_red.py
  tests/test_liss_0446_qasm_public_entry_red.py`
  — **42 passed, 1 pre-existing failure**.
- The pre-existing failure is the LISS-0446 Limit rejection assertion whose
  expected code predates the AlgorithmPlan canonical-provenance correction;
  it is outside this subcontract.
- Ordinary-QASM and LISS-0447 focused assertions pass, including no AST
  fallback and atomic unsupported rejection.
- `git diff --check`: passed.

Independent Review 01 returned **READY** with no P0/P1 blocker. It confirmed
canonical operation coverage, instruction-level source provenance, no AST
fallback for the ordinary path, atomic unsupported rejection, and preservation
of the finite Suzuki compatibility boundary. The reviewer recorded two P2
observations: dirty-worktree attribution limits and optional expansion of
direct per-operation provenance assertions. Neither changes the accepted
contract or blocks completion.

The ordinary-QASM review loop terminal state is `COMPLETE`. Phase 3 Refactor
is not approved by this record.
