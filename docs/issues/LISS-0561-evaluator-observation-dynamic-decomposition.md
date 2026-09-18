# LISS-0561: Evaluator observation and dynamic-lane decomposition

## Metadata

- Local issue ID: LISS-0561
- Status: proposed — blocked until LISS-0560 completes
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

## AI Planning Record

See `AIP-WP-0162-001` in WP-0162. Phase 1 must enumerate all mutable fields
read or written by the extracted family before implementation.

## Verification

Observation/dynamic characterization corpus, measurement sink tests, fixed-seed
runtime snapshots, import-cycle audit, Spec Verification, and blocking pytest.
