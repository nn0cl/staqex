# LISS-0556: POVM rejection evidence regression

## Metadata

- Local issue ID: LISS-0556
- GitHub issue: none
- Status: proposed
- Phase: phase-0-design
- Type: compiler result regression
- Priority: P0
- Initial/current planning size: M / M
- Owner/agent: host implementation; same-context review
- Related branch: `codex/liss-0556-povm-rejection`

## Summary

Restore the accepted `CompileResult.povm_observation_rejections` evidence
surface for a domain-mismatched POVM request without implementing POVM math.

## Acceptance Notes

- Preserve rejection reason, request/effect identity, source provenance,
  non-repair, and non-fabrication fields.
- A rejection creates no sampled outcome, post-state, finite target, or provider
  artifact.
- Existing computational-basis behavior remains unchanged.

## Dependencies

- Parent: WP-0161
- Depends on: none
- Blocks: none
- Related: LISS-0485, LISS-0084, WP-0092

## Adjudicator Decision Points

- Approve the existing failing node as the regression authority; general POVM
  effect mathematics remains excluded.

## Verification

One active rejection node, the complete LISS-0485 bridge suite, source
provenance, and no fabricated measurement/artifact evidence.

## AI Planning Record — AIP-0556-001

- Status/date/size: proposed, 2026-09-11, M
- Route/scope: host; CompileResult rejection projection only
- Estimate: N/A; compatible metric unavailable
- Basis/confidence: accepted field is absent from current DTO; high confidence

## Process Review

- Outcome: not yet
- Lesson written: not yet
- Template-feedback path: none

