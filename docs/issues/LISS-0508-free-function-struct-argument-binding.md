# <LISS-0508: free-function and struct argument binding>

## Metadata

- Local issue ID: LISS-0508
- GitHub issue: none
- Status: ready
- Phase: phase-1-red
- Type: bug
- Priority: P1
- Initial planning size: M
- Current planning size: M
- Reclassification reason: shared callable argument/field projection runtime path
- Owner/agent: host agent
- Related branch: codex/wp-0127-test-failure-recovery

## Summary

Restore free-function calls with scalar, struct, nested object, and field-projection arguments.

## Acceptance Notes

All failures in the LISS-0290/LISS-0292/LISS-0294 group pass without changing object-language state semantics.

## Dependencies

- Parent: WP-0127
- Depends on: none
- Blocks: none
- Related: `tests/test_liss_0290_adr_0180_residuals_red.py`, `tests/test_liss_0292_typefirst_freefn_args_red.py`, `tests/test_liss_0294_nested_freefn_args_red.py`

## Adjudicator Decision Points

- Keep DTO/class boundaries and pure free-function semantics unchanged.

## AI Planning Records

### AIP-0127-0508-001

- Status: accepted
- Created by: host agent; model/reasoning telemetry unavailable
- Created at: 2026-09-04
- Planning size: M
- Intended execution route: Phase 1 → Phase 2 → Phase 3
- Intended scope: callable argument binding and field projection
- Estimated token range: N/A
- Token metric: N/A
- Estimation basis: five failures share unsupported method dispatch
- Assumptions: accepted Type-First/free-function contract is authoritative
- Confidence: medium

## References

- `tests/test_liss_0290_adr_0180_residuals_red.py`
- `tests/test_liss_0292_typefirst_freefn_args_red.py`
- `tests/test_liss_0294_nested_freefn_args_red.py`

## Work Notes

- Red reproduced during WP-0127 intake.

## Verification

- Not yet complete.

## Process Review

- Outcome: not yet
- Lesson written: not yet
- Template-feedback path: none
