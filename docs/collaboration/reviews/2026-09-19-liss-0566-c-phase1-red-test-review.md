# LISS-0566-C Phase 1 Red Test Review

## Review packet

- Scope: Unit C operator resolution/lowering extraction Red contract.
- Canonical documents re-read:
  - [LISS-0566-C issue](../../issues/LISS-0566-C-operator-lowering-successor.md)
  - [WP-0163](../../work-plans/WP-0163-evaluator-stateful-successor.md)
  - [Core module decomposition](../../specs/staqex-core-module-decomposition.md)
  - [Verification policy](../verification-policy.md)
  - [Process lessons log](../process-lessons-log.md)
- Test file reviewed: `tests/test_liss_0566_unit_c_red.py`
- Isolation: `same_context`; weaker than `separate_context`.

## Findings and dispositions

1. The structural contract identifies all 11 Unit C implementation bodies,
   successor entrypoints, explicit context callbacks, and exact compatibility
   wiring. **Disposition: already closed with evidence in the intentional Red
   failures.**
2. The no-public-facade and no-second-state-owner assertions are explicit and
   do not rely only on runtime success. **Disposition: already closed with
   evidence; the test passes before extraction.**
3. The characterization set covers nested factory calls, parameterized finite
   binders, receiver method calls, QASM emission, set-projector tree lowering,
   and Jordan-Wigner second-quantized binding. **Disposition: apply**; two
   explicit Unit C nodes were added during review because the initial Red set
   did not name projector-tree and second-quantized coverage directly.
4. The tests preserve existing assertions and do not add a provider, network,
   credential, or Semantic IR authority. **Disposition: already closed with
   evidence.**

## Blockers

No Phase 1 test-review blocker found. The four structural failures are the
expected pre-Green gaps. Phase 2 remains separately gated and requires typed
implementation approval.

## Verification

- Focused command: `./.venv/bin/pytest tests/test_liss_0566_unit_c_red.py -q`
- Result: **4 failed, 7 passed**; exit code 1 is expected for Red.
- Active-Red lifecycle: `ACTIVE_RED_LIFECYCLE_OK entries=1`.
- `git diff --check`: passed.
- Full blocking suite: not run; not required for a test-only Phase 1 review.
- New or unassessed failures: none beyond the four named structural Red
  contracts; no exclusions were added.

## Spec-to-test mapping

The failed structural tests pin ownership, callback, entrypoint, and
compatibility migration. Passing tests pin the existing operator factory,
finite-binder, method receiver, QASM, projector-tree, and second-quantized
behavior. Semantic IR authority, provider boundaries, and live QPU behavior
are explicitly outside this phase.

## Review route and approval

- Reviewer route: `same_context`; weaker than `separate_context`.
- Reviewer recommendation: accept Phase 1 Red test review.
- Adjudicator approval received on 2026-09-19:
  `WP-0163 / LISS-0566-C Phase 1 Red テストレビュー承認`.
- Next approval: `WP-0163 / LISS-0566-C Phase 2 Green / Implementation 承認`.
