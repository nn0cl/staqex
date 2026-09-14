# LISS-0558: Observation diagnostic-name reconciliation

## Metadata

- Local issue ID: LISS-0558
- GitHub issue: none
- Status: proposed
- Phase: phase-0-design
- Type: diagnostic test synchronization
- Priority: P1
- Initial/current planning size: S / S
- Owner/agent: host implementation; same-context review
- Related branch: `codex/liss-0558-observation-diagnostic`

## Summary

Reconcile the old tomography expectation `OBSERVATION_UNSUPPORTED` with the
current accepted catalog and conformance matrix name
`OBSERVATION_CAPABILITY_UNSUPPORTED`.

## Acceptance Notes

- Preserve explicit Host/kernel boundary rejection and absence of
  `LINEAR_DUPLICATE_USE` masking.
- Update only the stale expected code if the current spec and conformance matrix
  agree; otherwise stop for an architecture decision.
- No tomography implementation or diagnostic alias is added merely for an old
  test spelling.

## Dependencies

- Parent: WP-0161
- Depends on: none
- Blocks: none
- Related: LISS-0483, ADR 0189, WP-0092

## Verification

One active node plus the LISS-0483 observation conformance and source-evidence
suites.

## Process Review

- Outcome: not yet
- Lesson written: not yet
- Template-feedback path: none

