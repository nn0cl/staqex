# LISS-0523 / WP-0140 design trace

- Date: 2026-09-16
- Path: Feature Path / Phase 0 acceptance/profile review
- Scope: one offline `geosensor-x01-v1` mapping profile
- Authority: ADR 0217-A, X01 acceptance specification, WP-0140
- Implementation permission: none

## Phase 0 acceptance result

- CityGML object/geometry/LoD, graph direction/multiplicity, and
  SOSA/SensorThings observation roles are mapped to the Metadata Graph while
  preserving external identity, source, time, and CRS/frame evidence.
- Missing CRS remains `unknown`; malformed CRS is quarantined; geometry does
  not imply passability or routing.
- Uninterpreted extensions remain hash-addressed raw evidence and cannot become
  execution authority.
- No GIS reader, graph database, ontology engine, sensor client, network, or
  live device is selected or used.
- Phase 1 Red is limited to fixed in-memory fixtures and five positive/negative
  acceptance groups.

## Review

- Phase 0 acceptance/profile review: profile ready; Adjudicator acceptance was
  received and Phase 1 Red remains separately gated.
- Review packet: `docs/collaboration/reviews/2026-09-16-liss-0523-phase0-acceptance-review.md`
- Adjudicator acceptance: `LISS-0523 Phase 0 acceptance 承認`, received
  2026-09-16.

## Next safe action

Request `LISS-0523 Phase 1 Red 承認`.

## Phase 1 Red — 2026-09-16

- Phase 1 approval was received and six focused X01 tests were added only.
- Pytest reports **6 failed** because the planned
  `compiler.staqex.geospatial_metadata` contract is not implemented.
- The direct runner collects all six failures; no production or existing test
  assertion changed.
- Active-Red entries are recorded for all six nodes.

## Next safe action

Request `LISS-0523 Phase 1 Red テストレビュー承認`.

## Phase 1 Red test review — 2026-09-16

- The six X01 Red nodes were accepted unchanged after rerunning the exact
  suite (**6 failed**) and the direct runner (all six collected).
- Review evidence: `docs/collaboration/reviews/2026-09-16-liss-0523-phase1-red-review.md`.
- No implementation permission was inferred.

## Next safe action

Request `LISS-0523 Phase 2 Green / Implementation 承認`.

## Phase 2 Green / Implementation — 2026-09-16

- Phase 2 approval was received. The new provider-neutral
  `geospatial_metadata` profile validates and stores the accepted X01 record
  and relation contract without adding external dependencies.
- X01 and existing Metadata Graph tests passed: **14 passed**.
- All six Active-Red nodes passed and were removed from the manifest.
- Execution, routing, tasking, Semantic IR, QPU, and live sensor boundaries
  remain excluded.

## Next safe action

Request `LISS-0523 Phase 3 Refactor 承認`.

## Phase 3 Refactor — 2026-09-16

- Phase 3 approval was received. CRS validation and raw-extension evidence
  generation were extracted into focused helpers; assertions and behavior were
  preserved.
- X01 and Metadata Graph tests passed: **14 passed**. Compile, diff, and
  lifecycle/document checks passed.

## Next safe action

Request `LISS-0523 Phase 3 最終レビュー 承認`.

## Phase 3 final review — 2026-09-16

- Verification passed (**14 passed** plus compile/diff/lifecycle checks).
- Review blocker: accepted source-hash evidence is not exposed by the
  implementation or asserted by the positive test.
- Review packet: `docs/collaboration/reviews/2026-09-16-liss-0523-phase3-final-review.md`.

## Next safe action

Request `LISS-0523 Phase 2 Green / Implementation 再承認` after the bounded
source-hash correction is prepared.

## Phase 2 Green correction — 2026-09-16

- The requested reapproval was received for the bounded source-hash
  observability correction.
- Fixed fixtures carry deterministic offline SHA-256 values. Mapping now
  validates and preserves each value on the record and mapping-evidence
  surfaces; the positive test checks both surfaces.
- Verification: **14 passed**, compile succeeded, and `git diff --check`
  succeeded.
- No authority or integration boundary changed. The prior final-review packet
  remains historical evidence of the blocker that triggered this correction.
- Correction evidence:
  `docs/collaboration/reviews/2026-09-16-liss-0523-phase2-source-hash-correction.md`.

## Next safe action

Request `LISS-0523 Phase 3 最終レビュー 再承認`.

## Phase 3 final review re-review — 2026-09-16

- Approval received: `LISS-0523 Phase 3 最終レビュー 再承認`.
- The source-hash blocker is closed with record/evidence exposure and
  assertions. Verification remained **14 passed**, with compile, lifecycle,
  and diff checks passing.
- Review packet:
  `docs/collaboration/reviews/2026-09-16-liss-0523-phase3-final-review-rerun.md`.
- Process review found no operating-contract deviation or operational problem.
- LISS-0523/WP-0140 are complete for the bounded offline X01 profile. External
  GIS/SOSA readers, live sensors, AWS, QPU, and scientific execution remain
  separate scope.
