# LISS-0564: Evaluator scientific and continuous-family decomposition

## Metadata

- Local issue ID: LISS-0564
- Status: proposed — blocked until LISS-0560 completes
- Type: Feature Path structural decomposition
- Initial planning size: L
- Current planning size: L
- Parent: WP-0162
- Depends on: LISS-0560
- Blocks: LISS-0565

## Summary

Extract selection preparation, finiteization, continuous field composition,
host-field binding, projection, and scientific set-comprehension mechanics
without broadening supported physical families.

## Acceptance Notes

- Scientific Semantic IR remains the source-derived authority.
- `Realize` and finite realization boundaries remain explicit.
- Continuous/open-system unsupported cases retain their current diagnostics.
- Host input remains a port boundary; no provider or datastore dependency enters.

## Allowed boundary

Candidate module is `runtime/evaluation/scientific.py`, subject to Phase 0
dependency evidence. No solver, automatic integration, or new scientific
syntax is included.

## AI Planning Record

See `AIP-WP-0162-001` in WP-0162. Phase 1 must map every scientific helper to
its canonical IR input and output evidence.

## Verification

S02 and scientific-family characterization, provenance and realization checks,
host-port tests, Spec Verification, and blocking pytest.
