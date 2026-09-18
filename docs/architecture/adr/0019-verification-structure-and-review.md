# ADR 0019: Verification evidence, structure budgets and conditional review

## Status

Accepted for implementation with the integrated plan on 2026-09-17.
Final implementation review remains required; automated checks are not approval.

## Decision

1. `docs/collaboration/verification-policy.md` is Canonical for focused versus
   all-blocking verification, tested SHA and consumer compatibility evidence.
   Project suite commands and layout live in target-owned project conventions.
2. Add optional `[source_structure]` and `[review.large_change]` to the existing
   target-owned runtime-routing TOML. Old files remain valid. Missing settings
   retain old routing. Form defaults suggest 300/500/5 without enabling review
   escalation automatically. Conditions use strict greater-than and OR.
3. A local Python standard-library tool measures a Git base/head diff and emits
   JSON evidence and selected routing. It never launches a model or claims to
   prove semantic responsibility separation. Python 3.11+ supplies tomllib.
4. Conditional isolation applies to reviews already required by the process,
   preserving ADR 0015's gate scope. Human approval remains independent.
   Unknown evidence requests adjudication; insufficient budget or unavailable
   separate context must not silently reduce isolation.
5. Copy/update reject dirty distributed source rather than recording an
   inaccurate SHA. Copy preserves an existing marker; first copy records the
   source baseline, with skipped files remaining local divergence.
6. Update checks branch availability before applying files and creates the
   review branch before mutation. Number collisions block automated delivery.
   An interrupted application may leave a partial diff on that review branch;
   it must be inspected, not treated as a successful sync.
7. Active batch expiry and batch-path validation are separate from historical
   record validation. Completed status never bypasses path limits on the active
   batch branch. Actual reviewer identity remains a human/hosting responsibility.

## Consequences

Evidence attached to a tested commit avoids self-referential evidence commits.
Any later commit needs new blocking evidence. Structure warnings prompt a
documented disposition rather than mechanically forcing fragmentation.
The additional regression suite tests normal and rejected paths. Adopter
facts are no longer edits to template-owned layout/testing documents.

## References

- `docs/specs/quality-and-review.md`
- `docs/issues/LISS-0027-integrated-quality-review.md`
- `docs/collaboration/reviews/2026-09-17-project-wide-quality-review.md`
