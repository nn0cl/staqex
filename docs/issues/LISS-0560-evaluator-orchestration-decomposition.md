# LISS-0560: Evaluator orchestration and runtime-plan dispatch

## Metadata

- Local issue ID: LISS-0560
- Status: proposed — Phase 0 acceptance pending
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

## AI Planning Record

See `AIP-WP-0162-001` in WP-0162. This Issue is a bounded child and does not
authorize implementation until typed Phase 1 approval.

## Verification

Plan-family characterization, public import manifest, import-cycle audit,
Spec Verification, blocking pytest, and `git diff --check`.
