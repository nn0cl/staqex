# LISS-0560 Phase 3 Refactor review packet

## Review Target

- Artifact: evaluator orchestration decomposition
- Current phase: Feature Path Phase 3 Refactor
- Requested approval: Phase 3 final review
- Approval type: phase/final review
- Approved scope: runtime-plan orchestration and six plan-family dispatch
  callbacks; preserve Evaluator state ownership and public compatibility
- Implementation allowed: no further implementation until final review
- Post-review required: status synchronization and process review after human
  final approval

## Canonical Documents and Files Re-read

- [LISS-0560 Issue](../../issues/LISS-0560-evaluator-orchestration-decomposition.md)
- [WP-0162](../../work-plans/WP-0162-evaluator-body-decomposition.md)
- [Core module decomposition specification](../../specs/staqex-core-module-decomposition.md)
- [Definition of Done](../definition-of-done.md)
- [Verification policy](../verification-policy.md)
- `compiler/staqex/runtime/evaluator.py`
- `compiler/staqex/runtime/evaluation/orchestration.py`
- `compiler/staqex/runtime/evaluation/plans.py`
- `compiler/staqex/runtime/evaluation/context.py`
- `tests/test_liss_0560_evaluator_orchestration_red.py`
- related plan-family characterization tests

## Findings and Dispositions

- Already closed with evidence: canonical runtime-plan construction and family
  selection are owned by `evaluation.orchestration`.
- Already closed with evidence: `Evaluator` remains the single mutable runtime
  state owner; no extracted service constructs or caches a second evaluator.
- Already closed with evidence: `evaluation.plans.dispatch_runtime_plan`
  remains an import-compatible facade and resolves to the same dispatcher.
- Already closed with evidence: all six plan families plus fallback remain
  characterized, and private compatibility attributes preserve existing
  consumer tests without owning dispatch.
- Apply: retain the explicit context contract and direct context validation
  calls introduced by the Phase 3 readability refactor.
- Out of scope: observation/dynamic, evolution/operator, classical/value, and
  scientific-family extraction, which belong to LISS-0561–0564.

## Blockers

No LISS-0560-specific blocker was found. Repository-wide full Green is not
established: the blocking pytest run reproduced the known QASM
`E_QPU_CANONICAL_PROVENANCE` failures and was interrupted by the existing
long-running sparse-pauli case.

## Deterministic Verification

- Tested SHA: `a86658c0`; tree clean at test start; local macOS workspace,
  Python 3.14.6, project `.venv` dependencies.
- Focused and adjacent orchestration/plan suites: **36 passed**.
- Canonical Spec Verification: **161/161**, 100%.
- Consumer import smoke: passed, including compatibility identity between
  `evaluation.plans` and `evaluation.orchestration` dispatch.
- Document lifecycle: passed.
- Execution-batch review validation: passed for 20 records.
- `git diff --check`: passed.
- Full repository pytest: **837 passed, 26 failed before interruption**;
  failures were the known canonical-provenance/QASM baseline family and the
  run did not complete; the interrupt occurred in the existing
  `sparse_pauli.py` long-running case.

## Isolation and Review Limits

Review isolation is `same_context`, which is weaker than `separate_context`.
The host reviewed the committed artifacts from disk as a reviewer, but this
packet is not independent human approval. The structure tool reported
ambiguous module ownership for the runtime modules; this is a review gap to
carry into WP-0162's later facade/budget audit, not a reason to expand
LISS-0560.

## Reviewer Empathy Summary

The public evaluator entrypoint remains easy to find, while plan selection is
now in one small internal module. A reviewer can follow the state boundary by
reading `EvaluatorContext`; the compatibility `plans` import avoids forcing
existing consumers to move in this Issue. The next extraction should reuse
this context boundary rather than widen orchestration into a second evaluator.

## Next Approval Required

`Feature Path / Phase 3 最終レビュー / LISS-0560 evaluator orchestration
decomposition 承認`
