# LISS-0565: Evaluator facade and structure-budget audit

## Metadata

- Local issue ID: LISS-0565
- Status: historical — superseded by LISS-0566-D
- Type: Feature Path completion and compatibility audit
- Initial planning size: M
- Current planning size: M
- Parent: WP-0162 (historical)
- Depends on: historical WP-0162 graph; successor LISS-0566-D

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

## Historical disposition

Recorded on 2026-09-19 under
`WP-0162/LISS-0562〜0565 整合性整理 承認`.

This planned facade audit was not started as a separate issue. Its accepted
scope was replaced and completed by `WP-0163 / LISS-0566-D`, including the
consumer inventory, compatibility audit, structure review, and final evidence.
