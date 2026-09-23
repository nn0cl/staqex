# LISS-0563: Evaluator classical calls and value decomposition

## Metadata

- Local issue ID: LISS-0563
- Status: historical — not started; superseded planning record
- Type: Feature Path structural decomposition
- Initial planning size: L
- Current planning size: L
- Parent: WP-0162 (historical)
- Depends on: LISS-0560
- Blocks: none

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

## Historical disposition

Recorded on 2026-09-19 under
`WP-0162/LISS-0562〜0565 整合性整理 承認`.

No implementation or Phase 1 contract was started under this issue. It is
closed as a stale successor candidate; the call-binding/frame portion was
handled by `WP-0163 / LISS-0566-D`. Any broader classical/value decomposition
must be proposed as a new issue with fresh scope and acceptance evidence.
