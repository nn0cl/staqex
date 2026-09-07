# Process Lessons Log

Target-owned. Created from `docs/templates/process-lesson.md`. Do not store
secrets. Policy: `docs/collaboration/process-lessons.md`.

Record meta-level patterns only. No session transcripts.

## Lesson

- Date: 2026-08-31
- Class: authority-boundary
- Pattern: a compatibility projection can retain legacy DTO nodes while still
  making the canonical semantic authority explicit and machine-checkable.
- What later design or implementation must do: preserve compatibility only
  with an explicit diagnostic-only role and negative authorization metadata;
  never let retained DTOs silently become execution or finiteization authority.
- Source issue or work plan (adopter's own ID, if any): LISS-0487 / WP-0107
- Status: applied

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

- Date: 2026-09-07
- Class: acceptance-boundary
- Pattern: a fail-closed semantic-family check can overmatch a valid neighboring
  representation, such as treating Hamiltonian coefficient terms as a direct
  non-unitary transform.
- What later design or implementation must do: pair every negative projection
  assertion with positive neighboring forms and scope rejection to the exact
  source ownership/context that is unsupported.
- Source issue or work plan (adopter's own ID, if any): LISS-0511 / WP-0128
- Status: applied

## Lesson

- Date: 2026-09-03
- Class: phase-acceptance-boundary
- Pattern: a canonical consumer migration can appear successful for supported
  projections while an unsupported semantic family still produces a partial
  artifact through a compatibility path.
- What later design or implementation must do: include an explicit unsupported
  acceptance scenario for each consumer migration and verify atomic,
  provider-neutral rejection before declaring the boundary complete.
- Source issue or work plan (adopter's own ID, if any): LISS-0503 / WP-0107
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
