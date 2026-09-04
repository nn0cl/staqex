# <LISS-0505: inspect deferred pushforward contract>

## Metadata

- Local issue ID: LISS-0505
- GitHub issue: none
- Status: review
- Phase: phase-3-refactor
- Type: bug
- Priority: P1
- Initial planning size: M
- Current planning size: M
- Reclassification reason: evaluator scheduling and observation semantics intersect
- Owner/agent: host agent
- Related branch: codex/wp-0127-test-failure-recovery

## Summary

Restore the accepted distinction that `Inspect` forces the required eager path while remaining non-collapsing.

## Acceptance Notes

Both deferred-pushforward tests pass and preserve `Inspect` identity/non-collapse semantics.

## Dependencies

- Parent: WP-0127
- Depends on: none
- Blocks: none
- Related: `docs/architecture/physicist-dx-harmony.md`

## Adjudicator Decision Points

- Do not implement observation as terminal measurement or alter `Measure` behavior.

## AI Planning Records

### AIP-0127-0505-001

- Status: accepted
- Created by: host agent; model/reasoning telemetry unavailable
- Created at: 2026-09-04
- Planning size: M
- Intended execution route: Phase 1 → Phase 2 → Phase 3
- Intended scope: deferred evaluator scheduling around `Inspect`
- Estimated token range: N/A
- Token metric: N/A
- Estimation basis: two existing failing tests
- Assumptions: accepted observation contract is authoritative
- Confidence: medium

## References

- `tests/test_deferred_pushforward_mvp_red.py`
- `docs/architecture/physicist-dx-harmony.md`

## Work Notes

- Red reproduced during WP-0127 intake. The canonical `control_mixture`
  dispatcher selected the deferred State/Measure fast path without applying
  the existing `Inspect` eligibility guard.
- Phase 2 fix: `control_mixture` now falls back to the established eager AST
  path whenever the main body is not deferred-eligible; `Inspect` remains
  non-destructive and terminal `Measure` behavior is unchanged.

## Verification

- `./.venv/bin/pytest -q tests/test_deferred_pushforward_mvp_red.py`: 5 passed.

## Process Review

- Outcome: no operating-contract deviation or operational problem found.
- Isolation: same_context; weaker than separate_context.
- Findings: apply none; the fix is limited to the approved evaluator
  scheduling boundary and the targeted deterministic tests pass.
- Next requested approval type: Adjudicator Phase 3 review/acceptance.
