# <LISS-0506: Jordan-Wigner mapping provenance>

## Metadata

- Local issue ID: LISS-0506
- GitHub issue: none
- Status: ready
- Phase: phase-1-red
- Type: bug
- Priority: P1
- Initial planning size: M
- Current planning size: M
- Reclassification reason: mapping metadata crosses physics/consumer projections
- Owner/agent: host agent
- Related branch: codex/wp-0127-test-failure-recovery

## Summary

Restore name and qubit-count provenance for Jordan-Wigner mappings.

## Acceptance Notes

The one-body and two-body mapping provenance tests pass with stable mapping records.

## Dependencies

- Parent: WP-0127
- Depends on: none
- Blocks: none
- Related: `tests/test_jordan_wigner_mapping_red.py`

## Adjudicator Decision Points

- Preserve source and qubit-count provenance; do not silently infer a different mapping.

## AI Planning Records

### AIP-0127-0506-001

- Status: accepted
- Created by: host agent; model/reasoning telemetry unavailable
- Created at: 2026-09-04
- Planning size: M
- Intended execution route: Phase 1 → Phase 2 → Phase 3
- Intended scope: Jordan-Wigner mapping metadata production and consumers
- Estimated token range: N/A
- Token metric: N/A
- Estimation basis: two failing provenance assertions
- Assumptions: current mapping contract is authoritative
- Confidence: medium

## References

- `tests/test_jordan_wigner_mapping_red.py`
- `docs/specs/staqex-v1-physics-ir-golden-catalog.md`

## Work Notes

- Red reproduced during WP-0127 intake.

## Verification

- Not yet complete.

## Process Review

- Outcome: not yet
- Lesson written: not yet
- Template-feedback path: none
