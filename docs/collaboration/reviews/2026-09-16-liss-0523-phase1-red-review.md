# LISS-0523 Phase 1 Red test review

- Issue/WP: LISS-0523 / WP-0140
- Scope: `geosensor-x01-v1` fixed in-memory geospatial/sensor profile
- Path/phase: Feature Path / Phase 1 Red
- Isolation: same_context, weaker than separate_context
- Approval received: `LISS-0523 Phase 1 Red テストレビュー承認`, 2026-09-16
- Implementation permission: not granted by this review

## Reviewed contract

The six Red nodes cover the accepted X01 envelope: preservation of city and
sensor observation meaning, unknown CRS and uninterpreted extension evidence,
malformed/dangling input rejection, non-inference of routing/tasking, and the
Metadata Graph's lack of execution authority.

## Evidence

- The exact pytest suite was rerun unchanged: **6 failed**.
- All failures are caused by the intentionally absent
  `compiler.staqex.geospatial_metadata` implementation module.
- The direct runner collected and reported all six failures.
- No production adapter, external dependency, network call, or existing test
  assertion was changed.

## Findings and dispositions

- Fixed fixture and fake-port boundary: accepted and applied.
- Direction and parallel-edge preservation: accepted and covered by the
  positive node.
- Unknown/malformed CRS handling: accepted and covered by the evidence and
  rejection nodes.
- Routing/tasking inference and direct execution authority: accepted as
  negative boundaries; out of scope for the profile implementation.
- Technology selection and live integration: out of scope; requires a
  separate decision.

## Next gate

Request `LISS-0523 Phase 2 Green / Implementation 承認`.
