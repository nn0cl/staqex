# LISS-0557 Phase 1 Red Test Review

## Scope

- Reviewed the two existing LISS-0486 active nodes assigned to LISS-0557.
- Review isolation: `same_context`, weaker than `separate_context`.
- Implementation permission: not granted by this review.

## Artifacts re-read

- `docs/issues/LISS-0557-evaluator-authority-evidence-contract.md`
- `docs/architecture/adr/0225-evaluator-authority-observable-boundary.md`
- `docs/specs/staqex-scientific-semantic-consumer-migration.md`
- `tests/test_liss_0486_evaluator_semantic_authority_red.py`
- `compiler/staqex/runtime/evaluator.py`
- `compiler/staqex/pipeline.py`
- `docs/testing/active-red-tests.toml`

## Findings and dispositions

1. The compile-owned IR identity observation node fails because
   `Evaluator.semantic_ir` is absent. **Accepted:** this exposes the approved
   migration from mutable-authority wording to an explicit compatibility
   observation/result-evidence contract.
2. The caller-injection node fails with `KernelDiagnosticError` while the
   historical assertion catches `ValueError`. **Accepted:** this is the exact
   ADR 0225 exception-hierarchy decision surface; Green must preserve the
   stable diagnostic code without creating a second rejection path.
3. The existing specification-contract node passes. **Closed with evidence:**
   the test file has no collection error and the accepted authority terms are
   present.

## Red evidence

- Direct suite: **2 failed, 1 passed**, with no collection errors.
- No production code or reviewed test assertion was changed.
- The two Active-Red entries now carry `phase-1-red` for LISS-0557.

## Blockers

- No Red test-contract blocker.
- Phase 2 requires explicit implementation approval after this test review.

## Next requested approval

`LISS-0557 Phase 1 Red テストレビュー承認`
