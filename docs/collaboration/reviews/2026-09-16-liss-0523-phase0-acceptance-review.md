# WP-0140 / LISS-0523 Phase 0 acceptance/profile review

- Scope: `geosensor-x01-v1` offline CityGML・graph・SOSA/SensorThings mapping
- Canonical documents: ADR 0217-A, LISS-0523, WP-0140, X01 acceptance spec,
  Scientific Workflow complete design
- Isolation: same_context; this is weaker than separate_context
- Review result: profile ready for Adjudicator Phase 0 acceptance; no implementation permission
- Review date: 2026-09-16

- Adjudicator acceptance: `LISS-0523 Phase 0 acceptance 承認`, received
  2026-09-16

## Decisions

- CityGML objects map to Entity/FeatureOfInterest and geometry/LoD to Space;
  no passability or routing meaning is inferred.
- Node/edge data remains typed Relation with direction, multiplicity, weight,
  validity, and endpoint identity.
- SOSA/SensorThings roles map to observation metadata roles without introducing
  quantum Observation syntax or execution authority.
- Phenomenon/result/ingest time, source identity, CRS/frame, and unknown state
  are preserved independently.
- Missing CRS is stored as `unknown`; spatial computation requires
  reject/review-required. Malformed CRS is quarantined.
- Uninterpreted extensions remain hash-addressed evidence and cannot authorize
  execution.
- No external dependency or technology is selected in this profile.

## Findings and dispositions

- Metadata Graph versus Semantic IR authority: already closed by ADR 0217-A.
- Positive/negative X01 envelope: applied in the five Phase 1 Red groups.
- Fixture and source/API boundary: applied with fixed in-memory records and a
  fake port boundary.
- Technology/version choice: out of scope; requires a separate decision.
- Live sensor, GIS tasking, routing, QPU, and source syntax: out of scope.

## Required evidence for Phase 1

The Red suite must demonstrate field preservation, unknown/missing handling,
malformed-input rejection, non-inference of passability/routing, and rejection
of direct Graph/DTO execution injection. It must not add a production adapter.

## Next approval

Request `LISS-0523 Phase 1 Red 承認`.
