# LISS-0543: Regression authority for structural refactoring

## Metadata

- Local issue ID: LISS-0543
- GitHub issue: none
- Status: phase-3-final-review-approved-active-red-reconciliation-required
- Phase: phase-3-refactor
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

## Phase 1 Red record

- Approval: `LISS-0543 Phase 1 Red 承認`, received 2026-09-11.
- Added `tests/test_liss_0543_test_lifecycle_red.py` with eight contracts for a
  valid open Phase 1 entry, done/unknown issue rejection, missing test,
  duplicate registration, deterministic review expiry, global glob rejection,
  and validated per-file pytest arguments.
- Added `tests/test_liss_0543_refactor_baseline_red.py` with four contracts for
  deterministic baseline bytes, required public/behavior evidence, absence of
  machine-specific paths/timestamps, and atomic missing-input rejection.
- Added only test fixtures under `tests/fixtures/liss_0543/`. No checker,
  baseline generator, CI change, active-Red production manifest, or compiler
  implementation was added.
- Focused pytest collected and failed all 12 tests because
  `scripts/check-test-lifecycle.py` and
  `scripts/capture-refactor-baseline.py` do not exist. Both test files pass
  `py_compile`; `git diff --check` passes.
- Review packet:
  [2026-09-11 LISS-0543 Phase 1 Red](../collaboration/reviews/2026-09-11-liss-0543-phase1-red-review.md).
- Next approval after review: `LISS-0543 Phase 2 Green / Implementation 承認`.

## Phase 2 Green record

- Approval: `LISS-0543 Phase 2 Green / Implementation 承認`, received
  2026-09-11.
- Added a standard-library lifecycle checker and an issue-linked TOML manifest
  for the 19 currently active Red nodes. CI now deselects only those exact
  nodes and rejects global `*_red.py` exclusions, stale issues, missing tests,
  duplicate entries, phase drift, and expired review dates.
- Added an atomic deterministic baseline generator and committed evidence for
  six public modules plus representative fixed-seed runtime, QASM, and
  diagnostic cases.
- CI regenerates and byte-compares the baseline, and pins Python 3.12 for the
  repository-sanity scripts that use `tomllib`.
- No compiler, runtime, language semantics, diagnostic, QASM, or provider
  implementation changed.
- Acceptance review packet:
  [2026-09-11 LISS-0543 Phase 2 Green](../collaboration/reviews/2026-09-11-liss-0543-phase2-green-review.md).
- Next approval after Green review: `LISS-0543 Phase 3 Refactor 承認`.

## Phase 3 Refactor record

- Approval: `LISS-0543 Phase 3 Refactor 承認`, received 2026-09-11.
- Split lifecycle validation into test-reference, review-deadline, and
  issue-reference responsibilities.
- Split baseline orchestration into case collection and evidence capture.
- Preserved CLI output, diagnostic codes, exact pytest selection, baseline
  bytes, tests, and assertions.
- Final review packet:
  [2026-09-11 LISS-0543 Phase 3 Refactor](../collaboration/reviews/2026-09-11-liss-0543-phase3-refactor-review.md).
- Final review approval: `LISS-0543 Phase 3 最終レビュー 承認`, received
  2026-09-11.
- Completion blocker: all 19 active-Red entries currently name LISS-0543 as
  their open owner. Marking this issue done would correctly fail lifecycle
  validation. They require accepted successor issue ownership before this
  issue can close.

## Process Review

- Outcome: operational problem found — final approval cannot be converted to
  `done` while LISS-0543 remains the owner of 19 active-Red exclusions.
- Lesson written: existing regression-authority lesson will be applied
- Template-feedback path: none
