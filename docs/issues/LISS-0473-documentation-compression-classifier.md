# LISS-0473: Documentation compression classifier safety

## Metadata

- Local issue ID: LISS-0473
- GitHub issue: none
- Status: done
- Phase: phase-3-review
- Type: documentation/process tooling
- Priority: P1
- Initial planning size: M
- Current planning size: M
- Reclassification reason: N/A
- Owner/agent: Adjudicator / documentation maintainer
- Related branch: `docs/wp-0090-reassessment`

## Summary

The current `scripts/documentation_compression.py` classifies 138 records as
historical candidates from status text alone. The result includes
current-generation completed Issues and Work Plans that remain useful as
acceptance or review evidence. Correct the classifier so candidate output is
conservative, explainable, and safe to review before any deletion batch.

This Issue does not delete records, change runtime behavior, or authorize a
new compression batch.

## Acceptance Notes

1. A record referenced by the current open-work register, an active Work Plan,
   an accepted specification/ADR, a review packet, or a current trace is not
   emitted as an unreviewed deletion candidate.
2. Candidate output distinguishes `retain-canonical`, `retain-evidence`,
   `index-pointer`, and `unresolved-review` with a reason and source path.
3. Existing compression-map entries remain stable; no identifier is renumbered
   and no baseline recovery pointer is rewritten.
4. The classifier has deterministic tests covering current-generation completed
   evidence, unresolved records, already-indexed records, and genuinely safe
   historical records.
5. The command produces no deletion side effect unless a separately reviewed
   deletion operation is explicitly invoked; candidate generation is read-only.

## Dependencies

- Parent: [WP-0090](../work-plans/WP-0090-documentation-canonicalization.md)
- Depends on: none
- Blocks: any future WP-0090 deletion/compaction batch
- Related: [WP-0090 reassessment trace](../collaboration/traces/2026-08-28-wp-0090-current-main-reassessment.md)

## Adjudicator Decision Points

- Approve the conservative classification boundary and evidence sources.
- Approve Phase 1 Red tests before changing the classifier.
- Approve any later deletion batch separately after candidate review.

## Context

- Included: `scripts/documentation_compression.py`, compression policy, current
  compression map, open-work register, current Issue/WP/Trace metadata, and
  baseline recovery checks.
- Omitted: compiler/runtime code, AWS, Rust implementation, provider data, and
  deletion of any current document.
- Assumptions: the 2026-08-03 baseline remains the recovery source for records
  already indexed by the map.

## AI Planning Records

### AIP-LISS-0473-001

- Status: proposed
- Created by:
  - Agent/environment: Codex host agent, local repository
  - Model as displayed: N/A
  - Reasoning setting as displayed: N/A
  - N/A reason: runtime does not expose displayed per-task values
- Created at: 2026-08-28
- Planning size: M
- Intended execution route: Feature Path, Phase 1 Red → Phase 2 Green → Phase 3 review
- Intended scope: classifier rules, deterministic tests, and documentation trace only
- Estimated token range: N/A
- Estimated token midpoint: N/A
- Token metric: N/A
- Estimation basis: multiple document categories and deletion-safety boundaries
- Assumptions: current records remain available for evidence classification
- Confidence: medium; exact evidence graph requires Phase 1 inventory
- Revises: none
- Revision reason: N/A
- Superseded by: none

## References

- [Documentation canonicalization policy](../architecture/documentation-canonicalization-policy.md)
- [Documentation compression map](../architecture/documentation-compression-map.md)
- [WP-0090 current-main reassessment](../collaboration/traces/2026-08-28-wp-0090-current-main-reassessment.md)

## Work Notes

- Design intake identified a 138-record false-positive candidate set.
- No records were deleted in the reassessment.

## Phase 1 Red artifact

- Added `tests/test_liss_0473_documentation_compression_classifier_red.py`.
- The tests cover current open-work references, review evidence, unresolved
  records, existing index pointers, and the genuinely safe historical case.
- Red is confirmed because the required `classify_records` API does not yet
  exist in `scripts/documentation_compression.py`.
- No production script, deletion operation, or current document was changed by
  the Red phase.

## Phase 2 Green artifact

- Added the pure `ClassificationResult` value and `classify_records` function
  to `scripts/documentation_compression.py`.
- Evidence and unresolved signals are classified conservatively; only an
  unreferenced completed record is a candidate.
- The approved Red test file was not changed.
- The legacy file-scanning candidate command is not yet wired to this API;
  that integration and any deletion decision remain Phase 3 review scope.
- LISS-0473 tests, Python 3.14 syntax compilation, and `git diff --check` pass.

## Phase 3 review

- Same-context review is recorded in
  `docs/collaboration/reviews/2026-08-28-liss-0473-phase3-review.md`.
- Review found a P1 blocker: completion status uses unsafe substring matching
  and can classify `incomplete` as completed.
- Review also found that the new API is not yet connected to the legacy
  filesystem candidate scan.
- Phase 3 is not complete; no deletion batch is authorized.

## P1 correction Phase 1 Red

- Added regression cases proving that `incomplete` and `not complete` cannot
  become deletion candidates.
- The tests intentionally fail against the current substring-based completion
  check; production code remains unchanged in this phase.

## Verification

## P1 correction Phase 2 Green

- Replaced completion substring matching with explicit status recognition.
- `incomplete` and `not complete` now resolve to `unresolved-review` and never
  become candidates.
- The approved Red assertions were preserved; one path assertion was corrected
  to use the existing repository-relative helper because `Candidate.path` is
  an absolute path by contract.
- LISS-0473 tests, Python syntax compilation, and `git diff --check` pass.
- The legacy scan reports 133 candidates instead of 138, but remains a P2
  follow-up until it is wired to the conservative API and reviewed.

## P2 integration Phase 1 Red

- Added filesystem-scan integration assertions to the approved Red test file.
- The decisive test observes that `candidates()` must delegate disposition to
  `classify_records()`; it currently fails because the legacy scan still uses
  `historical_candidate` directly.
- Two protection assertions also pass through existing indirect guards, so
  they are retained as regression coverage but are not treated as proof of
  integration.
- No production code or deletion operation was changed in this phase.

## P2 integration Phase 2 Green

- Connected the filesystem `candidates()` scan to `classify_records()`.
- The scan now collects current-document references, review evidence, and
  existing compression-map pointers before producing candidates.
- The approved Red tests were not changed.
- The integrated scan is read-only and currently produces zero candidates on
  the current tree, which is safe but requires Phase 3 review for possible
  over-retention.
- LISS-0473 tests, Python syntax compilation, and `git diff --check` pass.

## P2 integration Phase 3 review

- Review packet: [2026-08-28 LISS-0473 P2 integration review](../collaboration/reviews/2026-08-28-liss-0473-p2-integration-phase3-review.md)
- Result: not accepted; follow-up implementation is required.
- P1 blocker: `candidates()` discards non-candidate classifications and the
  CLI prints only candidate rows, so the required `retain-canonical`,
  `retain-evidence`, `index-pointer`, and `unresolved-review` dispositions are
  not observable at the command boundary.
- P2 finding: the current-tree integration scan returns zero candidates and
  has no end-to-end fixture proving that a genuinely safe completed historical
  file can flow through the filesystem scan as a candidate. The pure API has
  that case, but the command-level contract remains unproven.
- P2 finding: the retired `historical_candidate` helper remains in the module,
  and review-evidence detection relies on an absolute-path substring. Both
  increase maintenance risk in a deletion-adjacent tool and should be removed
  or made explicit in the next bounded refactor.
- No deletion operation or deletion batch is authorized.

## Follow-up Phase 1 Red

- Added Red tests for an observable classification report containing every
  disposition, source path, and reason.
- Added a deterministic isolated integration fixture proving that a safe
  completed record retains its `index-pointer` classification when it flows
  through `candidates()`.
- The tests intentionally require `render_classification_report` and a
  classification field on integrated candidates; production code remains
  unchanged in this phase.
- Phase 2 Green is not started; it requires separate Adjudicator approval.

## Follow-up Phase 2 Green

- Added `render_classification_report`, which preserves the classification,
  source path, and reason for every scanned record in read-only output.
- Extended integrated `Candidate` values with their classification while
  preserving the existing constructor compatibility for historical callers.
- Wired the normal candidate command to print the complete classification
  report before its candidate count; no deletion behavior was added.
- The approved Red tests were not changed.
- Python syntax compilation, the LISS-0473 contract script, and
  `git diff --check` are required before Phase 3 review.

## Follow-up Phase 3 review

- Review packet: [2026-08-28 LISS-0473 follow-up Phase 3 review](../collaboration/reviews/2026-08-28-liss-0473-follow-up-phase3-review.md)
- Result: blocked; the report boundary is present, but the required
  `retain-canonical` disposition is not produced by the classifier.
- The legacy `historical_candidate` helper and absolute-path review check
  remain as bounded cleanup findings.
- No deletion operation or deletion batch is authorized.

## Canonical disposition slice Phase 1 Red

- Added a failing test requiring an explicit `canonical` input signal to
  produce the `retain-canonical` disposition with a deterministic reason.
- Production code remains unchanged in this phase.
- Phase 2 Green requires separate Adjudicator approval.

## Canonical disposition slice Phase 2 Green

- Added an explicit `canonical` record signal and `retain-canonical`
  classification with a deterministic retention reason.
- Marked the current README, decision register, canonicalization policy, and
  open-work register as canonical inputs to the filesystem scan.
- Canonical records are protected before index/reference checks and are never
  candidates.
- The approved Red tests were not changed.
- LISS-0473 tests, Python syntax compilation, and `git diff --check` pass.

## Canonical disposition slice Phase 3 review

- Review packet: [2026-08-28 LISS-0473 canonical disposition review](../collaboration/reviews/2026-08-28-liss-0473-canonical-disposition-phase3-review.md)
- Result: blocked; the explicit Canonical path set is not included in the
  filesystem source roots, so the normal CLI cannot emit `retain-canonical`
  for those pages.
- No deletion operation or deletion batch is authorized.

## Canonical disposition follow-up Phase 1 Red

- Added a failing filesystem-record test requiring current Canonical pages to
  enter the normal source scan with an explicit `canonical` signal.
- Added report-boundary coverage requiring all four policy dispositions to be
  renderable together.
- Production code remains unchanged in this phase.
- Phase 2 Green requires separate Adjudicator approval.

## Canonical disposition follow-up Phase 2 Green

- Added the explicit Canonical paths to filesystem record construction while
  preserving the existing Issue, Work Plan, and Trace scans.
- Canonical records now flow through the same report boundary and emit
  `retain-canonical` with no candidate flag.
- Duplicate paths are avoided and missing configured paths are skipped
  deterministically.
- The approved Red tests were not changed.
- LISS-0473 tests, Python syntax compilation, CLI execution, and
  `git diff --check` pass.

## Completion Phase 3 review

- Review packet: [2026-08-28 LISS-0473 completion review](../collaboration/reviews/2026-08-28-liss-0473-completion-phase3-review.md)
- Result: accepted for the classifier safety scope.
- Non-blocking follow-ups: remove the unused `historical_candidate` helper and
  replace absolute-path review detection with repository-relative detection in
  a later maintenance slice.
- No deletion operation or deletion batch is authorized.

- Phase 0: candidate inventory and source classification review.
- Phase 1: failing tests only for conservative classification and read-only behavior.
- Phase 2: minimum classifier implementation after test review.
- Phase 3: same-context or separate-context review, recovery check, and link scan.

## Process Review

- Outcome: no operating-contract deviation or operational problem found.
- Lesson written: not applicable
- Template-feedback path: none
