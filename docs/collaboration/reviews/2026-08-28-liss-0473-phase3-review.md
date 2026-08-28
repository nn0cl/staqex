# LISS-0473 Phase 3 same-context review

| Field | Value |
|---|---|
| Issue | [LISS-0473](../../issues/LISS-0473-documentation-compression-classifier.md) |
| Work plan | [WP-0090](../../work-plans/WP-0090-documentation-canonicalization.md) |
| Phase | Phase 3 refactor/review |
| Isolation | same_context (runtime routing file absent; weaker than separate-context) |
| Reviewer | Codex host agent, reviewer role |
| Date | 2026-08-28 |

## Review scope

Re-read the Issue, acceptance notes, Red tests, Green implementation, current
compression policy, and changed files. No prior author reasoning was treated
as review evidence. No provider, network, or deletion operation was used.

## Findings

### P1 — completion classification uses unsafe substring matching

`classify_records` checks `any(word in status for word in COMPLETED_WORDS)`.
This classifies statuses such as `incomplete` or `not complete` as completed
because `complete` is a substring. In a document-deletion tool, that can turn
an unresolved or explicitly negative status into a deletion candidate.

Disposition: blocker. Replace substring matching with an exact/structured
status interpretation and add Red coverage before claiming Phase 3 complete.

### P2 — new pure API is not connected to the legacy filesystem scan

The existing command still uses `historical_candidate` directly, so the
current CLI candidate output can still report the 138-record false-positive
set. The pure API is useful and tested, but it does not yet enforce the safety
contract at the command boundary.

Disposition: follow-up implementation slice. Do not run `--delete-indexed` or
any deletion batch until the command path uses the conservative classifier and
its output is reviewed.

## Positive observations

- The Phase 2 implementation is small, readable, and has no provider or runtime
  dependency.
- The approved Red test file was not modified.
- Existing compression-map recovery rows remain untouched.
- Candidate generation itself remains read-only in this slice.

## Verification

- LISS-0473 Red contract: passed after Green implementation.
- Python syntax compilation: passed.
- `git diff --check`: passed.
- Full Phase 3 acceptance: blocked by P1 and P2 above.

## Reviewer empathy summary

The API boundary is easy to understand, but a maintainer could reasonably
assume that the command is already protected because the new classifier is
near the legacy candidate logic. The exact status semantics and the command
integration boundary must be explicit before a deletion operation is trusted.
