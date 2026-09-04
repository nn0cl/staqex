# <LISS-0507: linked operator factory runtime>

## Metadata

- Local issue ID: LISS-0507
- GitHub issue: none
- Status: ready
- Phase: phase-1-red
- Type: bug
- Priority: P1
- Initial planning size: M
- Current planning size: M
- Reclassification reason: linked module/operator factory execution crosses compiler and runtime
- Owner/agent: host agent
- Related branch: codex/wp-0127-test-failure-recovery

## Summary

Restore runtime resolution of operator values returned by imported operator factories.

## Acceptance Notes

The linked operator factory tests execute successfully without bypassing the canonical semantic authority.

## Dependencies

- Parent: WP-0127
- Depends on: none
- Blocks: none
- Related: `tests/test_liss0051_operator_factory_runtime_red.py`, `tests/test_liss0107_examples_linker_runtime_red.py`

## Adjudicator Decision Points

- Keep module linking and runtime operator resolution provider-neutral.

## AI Planning Records

### AIP-0127-0507-001

- Status: accepted
- Created by: host agent; model/reasoning telemetry unavailable
- Created at: 2026-09-04
- Planning size: M
- Intended execution route: Phase 1 → Phase 2 → Phase 3
- Intended scope: linked operator factory bind/evaluation path
- Estimated token range: N/A
- Token metric: N/A
- Estimation basis: two tests fail at `OpVar` bind
- Assumptions: canonical runtime remains the execution authority
- Confidence: medium

## References

- `tests/test_liss0051_operator_factory_runtime_red.py`
- `tests/test_liss0107_examples_linker_runtime_red.py`

## Work Notes

- Red reproduced during WP-0127 intake.

## Verification

- Not yet complete.

## Process Review

- Outcome: not yet
- Lesson written: not yet
- Template-feedback path: none
