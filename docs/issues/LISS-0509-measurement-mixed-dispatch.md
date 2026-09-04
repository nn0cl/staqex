# <LISS-0509: measurement mixed dispatch>

## Metadata

- Local issue ID: LISS-0509
- GitHub issue: none
- Status: review
- Phase: phase-3-refactor
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

- Red reproduced during WP-0127 intake. The deferred callable path did not
  register a terminal POVM declaration before resolving the measurement
  effect, so a call-form `DensityState` measurement raised
  `INVALID_POVM_EFFECT` even though the named form passed.
- Phase 2 fix: deferred bind processing registers `POVM` and `DensityState`
  metadata through their existing dedicated handlers before terminal
  measurement. The call-form density resolver and terminal collapse boundary
  remain unchanged.

## Verification

- `PYTHONPATH=. ./.venv/bin/pytest -q tests/test_liss_0377_measure_call_mixed_dispatch_red.py`: 4 passed.

## Process Review

- Outcome: no operating-contract deviation or operational problem found.
- Isolation: same_context; weaker than separate_context.
- Findings: apply none; named and call-form measurement paths now share the
  existing POVM/mixed-state handlers and the targeted contract tests pass.
- Next requested approval type: Adjudicator Phase 3 review/acceptance.

## Process Review

- Outcome: not yet
- Lesson written: not yet
- Template-feedback path: none
