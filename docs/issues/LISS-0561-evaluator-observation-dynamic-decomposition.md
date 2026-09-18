# LISS-0561: Evaluator observation and dynamic-lane decomposition

## Metadata

- Local issue ID: LISS-0561
- Status: done — Phase 3 final review approved 2026-09-18
- Type: Feature Path structural decomposition
- Initial planning size: L
- Current planning size: L
- Parent: WP-0162
- Depends on: LISS-0560
- Blocks: LISS-0565

## Summary

Extract terminal measurement, mixed-state observation, deferred state binding,
dynamic QPU block, wire reset, arm execution, and collapse helpers without
changing terminal `measure` semantics or observation diagnostics.

## Acceptance Notes

- `State<T>` remains uncollapsed until terminal measurement.
- Dynamic provider state is not confused with local observation state.
- Measurement sink/stdout behavior and source spans remain unchanged.
- Fixed-seed marginal and collapse results remain equal.

## Allowed boundary

Candidate internal modules are `runtime/evaluation/observation.py` and
`runtime/evaluation/dynamic_lane.py`, with explicit evaluator context only.
No provider SDK or live dynamic-QPU behavior is added.

## Phase 0 acceptance/profile

LISS-0560 is complete. The current `evaluator.py` is 6,928 lines and the
`Evaluator` class contains 149 methods. The measured first profile is:

| Family | Candidate methods | Measured body lines | Primary state/boundary |
|---|---:|---:|---|
| Observation | 21 | 736 | `Joint`, `MeasureResult`, `MeasureSinkPort`, mixed/POVM maps, RNG and observation flags |
| Dynamic lane | 5 | 175 | `HostInputPort`, `Joint.project_coord`, dynamic outcome confirmation and block-local trace-out |

Observation methods are the deferred State/Measure path, deferred-bind cone
and free-variable eligibility helpers, terminal measurement and sink emission,
POVM/DensityState/Lindblad registration and observation projections. The
dynamic methods are `_run_dynamic_qpu_block`, `_reset_dynamic_wire`,
`_run_dynamic_arm_body`, `_resolve_dynamic_outcome`, and
`_collapse_dynamic_wire`.

### Ownership and dependency decisions

- `Evaluator` remains the only owner of `rng`, `rng_calls`, `measure_sink`,
  `inspect_sink`, `host_input`, `mixed_states`, `ket_labels`, `povms`,
  `execution_lane`, `_dynamic_outcomes_confirmed`, runtime maps, and mutable
  `Joint` execution state.
- `runtime/evaluation/observation.py` receives an explicit context and owns
  only observation execution mechanics: deferred bind orchestration,
  terminal measure, mixed-state/POVM/Lindblad observation, and sink formatting.
- `runtime/evaluation/dynamic_lane.py` receives an explicit context and owns
  only dynamic block recursion, supplied controller outcomes, reset, collapse,
  and block-local disposal. It must not call a provider SDK or sample an
  unapproved live outcome.
- `Evaluator._run_legacy_ast_body` remains the integration owner until the
  extracted callbacks are characterized; it delegates through context rather
  than copying state into either module.
- The public import manifest remains unchanged. New modules are internal;
  no new public semantic authority or provider boundary is introduced.

### Private consumer and characterization profile

The private consumer inventory found `Evaluator._deferred_bind_cone` in
`tests/test_deferred_pushforward_mvp_red.py` and
`Evaluator._main_deferred_eligible` in the existing evaluator path. Phase 1
must preserve these compatibility observations or explicitly record a
replacement test owner before extraction.

The nearest characterization corpus is:

- deferred State/Measure and `Inspect`/terminal collapse: `test_deferred_pushforward_mvp_red.py`, `test_liss_0481_observation_contract_red.py`, `test_liss0236_kernel_measure_sink_port_red.py`, and `test_povm_measurement_contract_red.py`;
- mixed-state/CPTP/Lindblad: `test_density_cptp_lindblad_runtime_red.py`, `test_density_cptp_lindblad_red.py`, and `test_liss_0485_povm_observation_bridge_red.py`;
- dynamic feed-forward, reset, nested arms, and outcome confirmation: `test_liss_0382_dynamic_mid_circuit_feed_forward_red.py`, `test_liss_0385_dynamic_reuse_reset_demand_red.py`, `test_liss_0387_dynamic_real_mid_circuit_measure_red.py`, `test_liss_0389_dynamic_outcome_confirmation_red.py`, `test_liss_0390_dynamic_reset_keyword_red.py`, and `test_liss_0395_dynamic_arm_body_unification_red.py`;
- canonical execution and Spec Verification: `test_liss_0490_evaluator_canonical_execution_boundary_red.py`, `test_liss_0493_evaluator_runtime_plan_red.py`, and `tests/spec_verification/run_all.py`.

### Phase 1 Red contract and allowed files

Phase 1 Red may add only:

- `tests/test_liss_0561_evaluator_observation_dynamic_red.py`;
- this Issue's Phase 1 evidence and the representative trace;
- no production source, public API, or test-exclusion edits.

The Red contract must assert the two internal module boundaries, enumerate the
observation/dynamic method ownership manifest, verify that extracted modules
do not import the public evaluator facade, and pin the mutable-state owner and
private consumer manifest. Phase 2 may perform only the minimum extraction
after a separate typed implementation approval.

### Phase 0 acceptance decision

Accepted on 2026-09-18:
`Feature Path / Phase 0 acceptance / LISS-0561 evaluator observation and dynamic-lane decomposition 承認`.

This acceptance authorized Phase 1 Red only. It does not authorize production
implementation, Phase 2 Green, provider integration, or live dynamic-QPU
execution.

## Phase 1 Red evidence

Implemented only in `tests/test_liss_0561_evaluator_observation_dynamic_red.py`.
The focused run intentionally reports `3 failed, 2 passed` before extraction:

- `runtime/evaluation/observation.py` and `runtime/evaluation/dynamic_lane.py`
  do not yet exist;
- all 26 profiled observation/dynamic methods remain on `Evaluator`;
- the public evaluator import manifest and private consumer manifest are
captured as passing compatibility characterization contracts. Phase 2
preserves both consumers through explicit compatibility assignments on
`Evaluator`.

No production source, public API, or test-exclusion file was changed.

## Phase 2 Green evidence

Approved on 2026-09-18:
`Feature Path / Phase 2 Green / LISS-0561 evaluator observation and dynamic-lane decomposition 承認`.

Implemented the bounded extraction into two internal modules:

- `compiler/staqex/runtime/evaluation/observation.py` — 21 observation
  functions covering deferred binding, terminal measurement, sink emission,
  POVM/DensityState/Lindblad handling, and marginal calculation.
- `compiler/staqex/runtime/evaluation/dynamic_lane.py` — 5 dynamic-lane
  functions covering block recursion, reset, supplied outcomes, collapse,
  and block-local disposal.
- `compiler/staqex/runtime/evaluator.py` — reduced to 6,065 lines and 123
  class methods; it remains the mutable state owner and exposes compatibility
  aliases for existing private consumers.

The extracted functions receive the existing evaluator instance as an explicit
context. No provider SDK, live QPU behavior, new public API, or semantic policy
was added. The public evaluator import manifest is unchanged.

Verification:

- LISS-0561 focused contracts: `5 passed`.
- Observation/dynamic/orchestration characterization set: `91 passed`.
- Spec Verification: `161/161`, `100.00%`, Gate `PASS`.
- `git diff --check`: passed.

Process review: no operating-contract deviation or operational problem found.

Phase 3 refactoring and final review are complete. The change has not been
pushed or merged.

Review packet: `docs/collaboration/reviews/2026-09-18-liss-0561-phase3-review.md`.

Final review approval: `Feature Path / Phase 3 最終レビュー / LISS-0561
evaluator observation and dynamic-lane decomposition 承認` on 2026-09-18.

## AI Planning Record

See `AIP-WP-0162-001` in WP-0162. Phase 1 must enumerate all mutable fields
read or written by the extracted family before implementation.

## Verification

Observation/dynamic characterization corpus, measurement sink tests, fixed-seed
runtime snapshots, import-cycle audit, Spec Verification, and blocking pytest.
