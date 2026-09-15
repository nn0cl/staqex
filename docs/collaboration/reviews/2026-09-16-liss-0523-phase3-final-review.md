# LISS-0523 Phase 3 final review

- Scope: `geosensor-x01-v1` provider-neutral geospatial/sensor metadata profile
- Canonical documents: ADR 0217-A, LISS-0523, WP-0140, X01 acceptance spec,
  Phase 1 Red review
- Isolation: same_context; weaker than separate_context
- Approval received: `LISS-0523 Phase 3 最終レビュー 承認`, 2026-09-16

## Verification

- X01 and existing Metadata Graph regression: **14 passed**.
- Compile, diff, Active-Red, and document lifecycle checks: passed.
- No external dependency, network call, live sensor, or QPU path was used.

## Finding

- Blocker: Phase 0 and X01 require source hash to remain observable as mapping
  evidence, but `GeospatialRecord` and `MappingEvidence` expose only
  `source_id` and profile. The implementation does not preserve or derive a
  record-level source hash, and the positive test does not assert it.
- Disposition: apply. Add the smallest source-hash field/derivation and an
  executable assertion before completion. This requires a bounded Phase 2
  implementation correction and test review; it does not expand the profile.

## Review result

- Final review is **not complete** because the blocker conflicts with the
  accepted Phase 0 profile decision.
- No completion process review or `done` status is recorded.
- Next approval: `LISS-0523 Phase 2 Green / Implementation 再承認` after the
  source-hash correction is designed and approved.
