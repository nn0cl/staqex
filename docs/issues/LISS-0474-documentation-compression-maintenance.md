# LISS-0474: Documentation compression classifier maintenance

## Metadata

- Local issue ID: LISS-0474
- GitHub issue: none
- Status: done
- Phase: phase-3-review
- Type: documentation/process tooling
- Priority: P2
- Initial planning size: S
- Current planning size: S
- Owner/agent: Adjudicator / documentation maintainer
- Related branch: `docs/wp-0090-reassessment`

## Summary

Complete the bounded maintenance items identified by the LISS-0473 completion
review: remove the unused pre-classifier `historical_candidate` path and make
review-evidence path detection repository-relative rather than dependent on an
absolute host filesystem layout.

This Issue does not change classification policy, add deletion behavior, scan
new document categories, or authorize a compression/deletion batch.

## Acceptance specification

1. `historical_candidate` is removed or otherwise cannot remain a second
   callable classification path; `candidates()` continues to delegate to
   `classify_records`.
2. Review evidence detection uses a repository-relative path predicate and
   behaves identically for the current repository layout.
3. Existing LISS-0473 classifications and candidate output remain unchanged.
4. Tests cover the absence of the legacy path, path-layout-independent review
   evidence detection, and the existing read-only candidate boundary.
5. No file deletion, provider call, network access, or baseline-map rewrite is
   introduced.

## Design intake

- Included: `scripts/documentation_compression.py`, its deterministic tests,
  and this Issue's phase evidence.
- Omitted: document contents, compression-map rows, runtime/compiler code,
  AWS/Rust/provider work, and deletion operations.
- Boundaries: pure classifier remains the policy boundary; filesystem helpers
  remain read-only discovery infrastructure; no new port or dependency is
  needed.
- Ambiguities: none requiring an ADR. The existing relative-path helper and
  `ROOT` are authoritative for repository-local path handling.
- Routing: host-agent implementation with direct Python checks; no external
  provider or network is applicable.

## Dependencies

- Parent: [WP-0090](../work-plans/WP-0090-documentation-canonicalization.md)
- Predecessor: [LISS-0473](LISS-0473-documentation-compression-classifier.md)
- Review evidence: [LISS-0473 completion review](../collaboration/reviews/2026-08-28-liss-0473-completion-phase3-review.md)

## Approval request

Approve **LISS-0474 Phase 1 Red** before adding the deterministic maintenance
tests. Implementation remains unauthorized until the Red tests are reviewed
and Phase 2 Green is separately approved.

## Phase 1 Red artifact

- Added deterministic tests requiring removal of the legacy
  `historical_candidate` definition, repository-relative review evidence
  detection, and continued delegation to the conservative classifier.
- Production code remains unchanged in this phase.
- Phase 2 Green requires separate Adjudicator approval.

## Phase 2 Green artifact

- Removed the unused `historical_candidate` classification path.
- Added repository-relative review path detection that supports both absolute
  paths inside the repository and repository-relative test inputs.
- Existing `classify_records` delegation, classification results, and
  read-only candidate behavior remain unchanged.
- The approved Red tests were not changed.
- LISS-0474 tests, LISS-0473 regression tests, Python syntax compilation, and
  `git diff --check` pass.

## Phase 3 review and completion

- Review packet: [2026-08-29 LISS-0474 completion review](../collaboration/reviews/2026-08-29-liss-0474-completion-phase3-review.md)
- Result: accepted; no blocker found.
- Process review: no operating-contract deviation or operational problem
  found.
- No deletion operation or deletion batch is authorized.
