# LISS-0563: Evaluator classical calls and value decomposition

## Metadata

- Local issue ID: LISS-0563
- Status: proposed — blocked until LISS-0560 completes
- Type: Feature Path structural decomposition
- Initial planning size: L
- Current planning size: L
- Parent: WP-0162
- Depends on: LISS-0560
- Blocks: LISS-0565

## Summary

Extract classical user-function calls, methods, struct/class construction,
attribute access, unit conversion, literals, and value evaluation while
preserving interprocedural tracing and ownership of local bindings.

## Acceptance Notes

- Classical values remain distinct from quantum `State<T>` values.
- Struct/class fields, units, partial values, and callable binding retain the
  same diagnostics and exactness policy.
- No extracted evaluator stores a copied local environment beyond one call.

## Allowed boundary

Candidate modules are `runtime/evaluation/classical.py` and
`runtime/evaluation/values.py`. DTO ownership remains in the existing modules
unless a separate accepted decision is recorded.

## AI Planning Record

See `AIP-WP-0162-001` in WP-0162. Phase 1 must inventory all environment,
receiver, and local-binding mutation paths.

## Verification

Class/method/function fixtures, unit conversion tests, partial-value tests,
public import manifest, Spec Verification, and blocking pytest.
