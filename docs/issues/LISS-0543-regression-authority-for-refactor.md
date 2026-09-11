# LISS-0543: Regression authority for structural refactoring

## Metadata

- Local issue ID: LISS-0543
- GitHub issue: none
- Status: proposed
- Phase: phase-0-design
- Type: test infrastructure / process
- Priority: P0
- Initial/current planning size: L / L
- Owner/agent: host implementation; same-context review
- Related branch: `refactor/regression-authority`

## Summary

Replace the global `*_red.py` CI exclusion with explicit issue-linked active-Red
metadata, reconcile the current 19 failures against canonical contracts, and
capture the public-symbol, deterministic-runtime, diagnostic, and QASM
baselines required by later behavior-preserving extraction.

## Acceptance Notes

- A done issue's tests are always blocking.
- An excluded Red test names an open issue, phase, owner, and expiry/review
  condition in machine-readable data.
- CI fails on orphaned, done, unknown, or expired exclusions.
- Current failures are classified individually as regression, superseded test
  with replacement evidence, or active Red. No assertion is weakened silently.
- The final blocking baseline is green before LISS-0544–0550 begin.
- Public import and deterministic representative-output manifests are generated
  by readable repository scripts, not manually maintained snapshots.

## Dependencies

- Parent: WP-0160
- Depends on: none
- Blocks: LISS-0544–0550
- Related: source review finding CR-001 in local commit `a8cc0ac5`

## Adjudicator Decision Points

- Approve explicit active-Red metadata as test lifecycle authority.
- Approve Phase 1 tests for stale/done exclusion rejection.
- Approve each behavior correction separately if reconciliation finds a real
  product defect; such fixes do not enter this process issue silently.

## Context

- Included: CI, all root tests, issue status metadata, public imports, local
  deterministic representative corpus.
- Omitted: production refactoring, provider/live-QPU execution.
- Assumptions: filenames remain descriptive but non-authoritative.

## AI Planning Record — AIP-0543-001

- Status/created: proposed, 2026-09-11
- Agent/environment: Codex host agent; model/reasoning display unavailable
- Planning size/route: L; host implementation and same-context review
- Intended scope: CI lifecycle authority and refactor baseline only
- Estimate: N/A; no compatible repository planning metric
- Basis/assumptions/confidence: 440 excluded files and 19 failures; no product
  behavior changes without separate approval; high confidence
- Revises/Superseded by: none

## Verification

CI selector unit tests, full pytest, Spec Verification 161/161, manifest
determinism, document lifecycle, and diff checks.

## Process Review

- Outcome: not yet
- Lesson written: existing regression-authority lesson will be applied
- Template-feedback path: none
