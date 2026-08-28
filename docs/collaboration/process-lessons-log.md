# Process Lessons Log

Target-owned. Created from `docs/templates/process-lesson.md`. Do not store
secrets. Policy: `docs/collaboration/process-lessons.md`.

Record meta-level patterns only. No session transcripts.

## Lesson

- Date: 2026-08-26
- Class: status-drift
- Pattern: ISSUE and work-plan status stayed `review` or `in_progress` after
  the work had already merged to `main`. Later agents treating the ledger as
  current work would resume closed process changes.
- What later design or implementation must do: when a process PR merges,
  update the issue and work-plan status in the same context or immediately
  after. Leftover `review` / `in_progress` after merge is ledger drift, not
  open work.
- Source issue or work plan (adopter's own ID, if any): LISS-0024
- Status: applied

## Lesson

- Date: 2026-08-28
- Class: review-boundary-observability
- Pattern: a safe internal classification API was integrated into a command,
  but the command discarded the disposition metadata needed for human review.
  Unit tests therefore passed while the operational review boundary remained
  opaque.
- What later design or implementation must do: define and test the observable
  command/report contract separately from the pure classifier, preserving
  classification, reason, and source path for every reviewed record.
- Source issue or work plan (adopter's own ID, if any): LISS-0473 / WP-0090
- Status: applied

## Lesson

- Date: 2026-08-26
- Class: other
- Pattern: two local issues shared one LISS ID. Filename uniqueness is not
  the same as ID uniqueness; skipped numbers must stay unused.
- What later design or implementation must do: assign the next free ID only
  after listing existing `docs/issues/LISS-*` files and their metadata IDs.
  Do not reuse a skipped or colliding number. If a collision is found, keep
  the earlier claim on the ID and renumber the later file.
- Source issue or work plan (adopter's own ID, if any): LISS-0024
- Status: applied
