# <LISS-0509: measurement mixed dispatch>

## Metadata

- Local issue ID: LISS-0509
- GitHub issue: none
- Status: ready
- Phase: phase-1-red
- Type: bug
- Priority: P1
- Initial planning size: M
- Current planning size: M
- Reclassification reason: named-path and call-form measurement dispatch share effect validation
- Owner/agent: host agent
- Related branch: codex/wp-0127-test-failure-recovery

## Summary

Restore equivalent behavior between named and call-form density measurement dispatch.

## Acceptance Notes

`test_call_density_measure_matches_named_path` passes while preserving measurement as the terminal collapse boundary.

## Dependencies

- Parent: WP-0127
- Depends on: none
- Blocks: none
- Related: `tests/test_liss_0377_measure_call_mixed_dispatch_red.py`

## Adjudicator Decision Points

- No early collapse and no provider-specific behavior in the Kernel.

## AI Planning Records

### AIP-0127-0509-001

- Status: accepted
- Created by: host agent; model/reasoning telemetry unavailable
- Created at: 2026-09-04
- Planning size: M
- Intended execution route: Phase 1 → Phase 2 → Phase 3
- Intended scope: density measurement dispatch and effect validation
- Estimated token range: N/A
- Token metric: N/A
- Estimation basis: one focused failing test with a terminal measurement error
- Assumptions: named and call forms are required to be semantically equivalent
- Confidence: medium

## References

- `tests/test_liss_0377_measure_call_mixed_dispatch_red.py`
- `docs/specs/staqex-language-specification.md` §5.7

## Work Notes

- Red reproduced during WP-0127 intake.

## Verification

- Not yet complete.

## Process Review

- Outcome: not yet
- Lesson written: not yet
- Template-feedback path: none
