# LISS-0565: Evaluator facade and structure-budget audit

## Metadata

- Local issue ID: LISS-0565
- Status: proposed — blocked until LISS-0561–0564 complete
- Type: Feature Path completion and compatibility audit
- Initial planning size: M
- Current planning size: M
- Parent: WP-0162
- Depends on: LISS-0561, LISS-0562, LISS-0563, LISS-0564

## Summary

Complete the evaluator decomposition by auditing the public facade, symbol
manifest, imports, cycles, mutable-state ownership, source-size budget, and
full regression evidence.

## Acceptance Notes

- `compiler.staqex.runtime.evaluator` remains import-compatible.
- The facade contains no duplicated business logic.
- New internal modules have clear ownership and no vague utility bucket.
- All approved behavior and diagnostics remain unchanged.
- Current evaluator size and successor disposition are recorded in WP-0162.

## Allowed boundary

Public facade, internal package `runtime/evaluation/`, manifests, focused tests,
and canonical documentation only. No new feature or public API removal.

## AI Planning Record

See `AIP-WP-0162-001` in WP-0162. Completion requires a same-context review,
process review, and explicit final approval.

## Verification

Public symbol/import manifest, import-cycle audit, structure metrics, fixed-seed
snapshots, QASM goldens, complete blocking pytest, Spec Verification,
document lifecycle, and `git diff --check`.
