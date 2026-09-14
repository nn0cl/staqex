# LISS-0559: S02 immutable assay-record regression

## Metadata

- Local issue ID: LISS-0559
- GitHub issue: none
- Status: proposed
- Phase: phase-0-design
- Type: scientific data DTO regression
- Priority: P0
- Initial/current planning size: M / M
- Owner/agent: host implementation; same-context review
- Related branch: `codex/liss-0559-s02-assay-dto`

## Summary

Restore the accepted D01 boundary where a frozen assay snapshot creates an
immutable curated revision whose records expose stable typed identity and
relation fields. The current `__post_init__` is outside the dataclass and
curation returns mapping objects that fail the three accepted field assertions.

## Acceptance Notes

- Introduce or restore one immutable `AssayRecord` DTO with compound, target,
  assay, activity, endpoint, relation, value, unit, replicate, and source IDs.
- `FrozenAssaySnapshot` accepts the approved fixture input shape but owns an
  immutable normalized tuple without mutating the caller's raw dictionaries.
- Accepted and quarantined results retain record field access and censoring.
- Identity collisions preserve both compounds and do not merge records.
- No external download, chemistry normalization, model fit, database, or QPU.

## Dependencies

- Parent: WP-0161
- Depends on: none
- Blocks: none
- Related: LISS-0517, WP-0134, scientific workflow D01

## Adjudicator Decision Points

- Approve the typed DTO compatibility boundary and existing three failing
  nodes as regression authority.

## Verification

Three active nodes, all D01 positive/quarantine cases, immutable raw input,
positive revision validation, and no external resource use.

## AI Planning Record — AIP-0559-001

- Status/date/size: proposed, 2026-09-11, M
- Route/scope: host; S02 assay DTO only
- Estimate: N/A; compatible metric unavailable
- Basis/confidence: accepted WP explicitly requires immutable records and the
  current dataclass hook is not attached; high confidence

## Process Review

- Outcome: not yet
- Lesson written: not yet
- Template-feedback path: none

