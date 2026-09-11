# Review Summary: LISS-0515 Phase 1 Red

## Review packet

- Scope: WP-0132 / LISS-0515 M0 G01/G02/G03 Phase 1 Red tests only.
- Canonical documents:
  - `docs/specs/staqex-scientific-workflow-acceptance.md` (M0, G01–G03)
  - `docs/work-plans/WP-0132-scientific-metadata-graph.md`
  - `docs/issues/LISS-0515-scientific-metadata-graph.md`
  - ADR 0217-A accepted boundary
- Changed files: `tests/test_scientific_metadata_graph_red.py` and this review record.
- Isolation: `same_context`; a separate review task was attempted but returned no
  review body. This packet is therefore weaker than a separate-context review.
- Findings: none after review correction.
- Dispositions: the query-order assumption was corrected to set comparison;
  G03 now includes both original and corrected revisions. No implementation
  or unrelated scope was added.
- Remaining blockers: local pytest execution is unavailable because pytest is
  not installed. CI execution is required to record the expected Red result.
- Verification result: Python `compile()` and `git diff --check` pass. The test
  module is intentionally absent, so the tests are expected to fail in CI until
  Phase 2 implements the approved contract.
- Next approval required: after CI records the Red result and the Adjudicator
  accepts this test review, request separate `WP-0132 / LISS-0515 Phase 2
  Green / Implementation approval`. No implementation is authorized by this
  review.

## Findings by scenario

- G01: covers six-profile registration, order-independent identity, immutable
  snapshot, duplicate identity, dangling relation, and dimension conflict.
- G02: covers observed zero, not-measured, below-detection, model estimate, and
  language candidate without promoting candidate or converting missing to zero.
- G03: covers supporting/refuting evidence, generated activity, correction
  lineage, raw revision preservation, and provenance cycle rejection.
- Boundary: tests assert that the graph is descriptive and has no execute,
  QPU projection, or direct Semantic IR authority.

## Evidence links

- Canonical acceptance: `docs/specs/staqex-scientific-workflow-acceptance.md`
- Work plan: `docs/work-plans/WP-0132-scientific-metadata-graph.md`
- Issue: `docs/issues/LISS-0515-scientific-metadata-graph.md`
- Test: `tests/test_scientific_metadata_graph_red.py`
- Representative trace: `docs/collaboration/traces/2026-09-08-scientific-workflow-design.md`
