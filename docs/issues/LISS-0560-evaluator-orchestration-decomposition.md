# LISS-0560: Evaluator orchestration and runtime-plan dispatch

## Metadata

- Local issue ID: LISS-0560
- Status: Phase 1 Red complete — Phase 2 Green pending approval
- Type: Architecture successor / Feature Path decomposition
- Initial planning size: M
- Current planning size: M
- Owner/agent: host implementation, same-context review
- Parent: WP-0162
- Related: WP-0160, ADR 0211, core module decomposition specification

## Summary

Extract runtime-plan dispatch and family selection from `Evaluator` while
keeping mutable runtime state in `Evaluator` and preserving canonical IR
validation, deferred eligibility, and public execution entrypoints.

## Acceptance Notes

- Existing `Evaluator` public construction and `run_canonical_unit` behavior remain.
- Every plan family reaches the same executor and diagnostics.
- No extracted service owns a second runtime map or canonical semantic authority.
- Public symbol and import manifests are unchanged.

## Dependencies

- Depends on: none
- Blocks: LISS-0561, LISS-0562, LISS-0563, LISS-0564

## Allowed design boundary

Candidate files are `runtime/evaluation/orchestration.py`, focused tests, and
the public evaluator facade. Exact paths await Phase 0 dependency mapping.
No language, provider, QASM, or scientific meaning change is allowed.

## Phase 0 acceptance record

Accepted on 2026-09-18. The first extraction boundary is limited to
`Evaluator.run_canonical_unit`, `_execute_unit`, runtime-plan family selection,
and the `_execute_*_plan` dispatch methods. The following mutable state remains
owned by `Evaluator` and must be passed by explicit context or narrow callbacks:

- entropy and deterministic run state: `rng`, `seed`, `rng_calls`, fusion state;
- injected boundaries: `measure_sink`, `inspect_sink`, `host_input`,
  `continuous_field`;
- runtime maps: `operators`, `second_quantized_operators`, `scalars`,
  `scalar_units`, function/class/enum/struct registries, objects;
- quantum/runtime observations: `mixed_states`, `ket_labels`, `povms`,
  `static_register_sizes`, execution lane, and canonical Semantic IR reference.

Phase 1 Red is limited to:

- `tests/test_liss_0560_evaluator_orchestration_red.py`;
- this Issue's Phase 1 evidence and the representative trace;
- no production source edits, no public API edits, and no test exclusion edits.

The Red contract must prove the current dispatch boundary and name the exact
public symbol/import manifest and plan-family characterization cases. Phase 2
may add only the minimum internal orchestration extraction after separate
typed approval.

## Phase 1 Red evidence

Implemented only in `tests/test_liss_0560_evaluator_orchestration_red.py`.
The focused run intentionally reports `3 failed, 1 passed` on the pre-
extraction branch:

- `compiler.staqex.runtime.evaluation.orchestration` does not yet exist;
- all six first-boundary `_execute_*_plan` methods still live on `Evaluator`;
- `Evaluator.run_canonical_unit` still builds and dispatches the runtime plan
  directly instead of delegating through the orchestration boundary;
- the existing family manifest covers `evolution`, `control_mixture`,
  `pure_transformation`, `binder`, `callable`, and `dynamic_lane`.

No production source, public API, or test-exclusion file was changed.

## AI Planning Record

See `AIP-WP-0162-001` in WP-0162. This Issue is a bounded child and does not
authorize implementation until typed Phase 1 approval.

## Verification

Plan-family characterization, public import manifest, import-cycle audit,
Spec Verification, blocking pytest, and `git diff --check`.
