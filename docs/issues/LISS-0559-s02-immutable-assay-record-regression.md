# LISS-0559: S02 immutable assay-record regression

## Metadata

- Local issue ID: LISS-0559
- GitHub issue: none
- Status: done
- Phase: done
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

## Phase 0 design intake

### [DESIGN CHECK]

- Scope: create an immutable typed `AssayRecord` surface for one bounded
  biochemical-inhibition/IC50 profile, preserve the raw snapshot, and return a
  new curated revision or an explicit quarantine result.
- Authoritative context: the accepted D01 section of
  `docs/specs/staqex-scientific-workflow-acceptance.md`, the S02 benchmark
  specification, the three existing D01 Red nodes, and the current
  `s02_assay_profile.py` module.
- DTO boundary: `AssayRecord`, `FrozenAssaySnapshot`,
  `AssayCurationResult`, and `AssayDiagnostic` are Host-side scientific data
  records. No database, external data port, chemistry normalizer, model, QPU,
  or deployment adapter is included.
- Invariants: raw mappings are copied into immutable records; endpoint/unit,
  target and assay-family compatibility are checked; `=`, `<`, and `>` are
  preserved; identity and replicate collisions quarantine without merging;
  checksum/license provenance is required.
- Applied lessons: keep source and curated revisions distinct, preserve
  scientific meaning instead of normalizing away censoring, and use the
  existing Red nodes as the acceptance authority.
- Omitted context: quantum encoding/projection, fitting, candidate selection,
  live assay acquisition, provider integration, and Rust migration.
- Routing: host implementation with deterministic pytest, compilation, and
  lifecycle checks; same-context review.
- AI output contract: not applicable; no AI/model output is used.
- Open decisions: none for this bounded D01 profile. Broader endpoints,
  unit conversion, model fitting, and prospective assay integration remain
  separate scopes.

## Phase 0 acceptance result

- Adjudicator approval: `LISS-0559 Phase 0 acceptance 承認`, received
  2026-09-16.
- The typed DTO compatibility boundary and the three existing D01 Red nodes
  are accepted as the implementation contract.
- Phase 1 is limited to running/reviewing those nodes; no test assertion may
  be weakened or replaced.

### Next gate

Request `LISS-0559 Phase 1 Red 承認`.

## Phase 1 Red result

- Adjudicator approval: `LISS-0559 Phase 1 Red 承認`, received 2026-09-16.
- The three existing D01 Active-Red nodes were executed unchanged.
- Result: **3 failed**. Accepted curation currently returns dictionary records,
  so the required typed fields `activity_id`, `relation`, and `compound_id`
  are not attribute-accessible. The identity-collision case does return
  `ASSAY_IDENTITY_COLLISION` and preserves two raw records, but still fails the
  typed record surface assertion.
- No production code or test assertion was changed.

## Phase 1 Red review result

- Adjudicator approval: `LISS-0559 Phase 1 Red テストレビュー承認`, received
  2026-09-16.
- The three existing D01 nodes are accepted unchanged. Their common gap is the
  missing typed record surface; the collision diagnostic and raw-record
  preservation remain required behavior.
- Review evidence is recorded in
  `docs/collaboration/reviews/2026-09-16-liss-0559-phase1-red-review.md`.
- No implementation permission is inferred from this review.

### Next gate

Request `LISS-0559 Phase 2 Green / Implementation 承認`.

## Phase 2 Green / Implementation result

- Adjudicator approval: `LISS-0559 Phase 2 Green / Implementation 承認`,
  received 2026-09-16.
- Added the immutable, slotted `AssayRecord` DTO and normalized approved
  mapping-shaped fixture records into it at `FrozenAssaySnapshot` creation.
- Corrected the misplaced snapshot `__post_init__` hook so metadata and records
  are copied into immutable snapshot-owned values.
- Updated curation and collision checks to use typed fields without changing
  quarantine diagnostics, censored relations, or raw-record retention.
- D01 suite: **7 passed**; compilation and diff checks passed. Reviewed tests
  were unchanged.
- Next gate: `LISS-0559 Phase 3 Refactor 承認`.

## Phase 3 Refactor result

- Adjudicator approval: `LISS-0559 Phase 3 Refactor 承認`, received 2026-09-16.
- No additional production refactor was necessary. `AssayRecord`,
  `FrozenAssaySnapshot`, and curation each retain a clear single
  responsibility and the implementation remains within the Host-side D01
  boundary.
- Review confirms censoring, raw-input immutability, collision quarantine, and
  record retention are unchanged. No external integration was added.
- Review record:
  `docs/collaboration/reviews/2026-09-16-liss-0559-phase3-refactor-review.md`.
- Verification: D01 suite 7 passed; compilation, diff, lifecycle, document,
  and coverage checks passed.
- Next gate: `LISS-0559 Phase 3 最終レビュー 承認`.

## Completion

- Final review approval: `LISS-0559 Phase 3 最終レビュー 承認`, received
  2026-09-16.
- LISS-0559 is closed. All three D01 Active-Red exclusions were removed after
  the immutable typed record, raw snapshot, and quarantine contracts passed.

## Process Review

- Outcome: no operating-contract deviation or operational problem found.
- Lesson written: existing scientific-meaning-preservation,
  red-contract-reuse, and boundary-completeness lessons were applied.
- Template-feedback path: none.

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
