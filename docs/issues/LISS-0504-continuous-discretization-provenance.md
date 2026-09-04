# <LISS-0504: continuous discretization provenance>

## Metadata

- Local issue ID: LISS-0504
- GitHub issue: none
- Status: review
- Phase: phase-3-refactor
- Type: bug
- Priority: P1
- Initial planning size: M
- Current planning size: M
- Reclassification reason: multiple IR/provenance layers are involved
- Owner/agent: host agent
- Related branch: codex/wp-0127-test-failure-recovery

## Summary

Restore the accepted continuous discretization bridge contract so resolved theory/discretization provenance is retained in the canonical projection.

## Acceptance Notes

`tests/test_continuous_discretization_red.py::test_discretization_bridge_preserves_theory_and_contract_provenance` passes without weakening provenance assertions.

## Dependencies

- Parent: WP-0127
- Depends on: none
- Blocks: none
- Related: `docs/specs/staqex-continuous-discretization.md`

## Adjudicator Decision Points

- Preserve current accepted DTO/provenance fields; do not invent a new discretization model.

## AI Planning Records

### AIP-0127-0504-001

- Status: accepted
- Created by: host agent; model/reasoning telemetry unavailable
- Created at: 2026-09-04
- Planning size: M
- Intended execution route: Phase 1 → Phase 2 → Phase 3
- Intended scope: bridge resolution and its regression tests
- Estimated token range: N/A
- Token metric: N/A
- Estimation basis: existing failing test and related spec
- Assumptions: accepted test expectation remains current
- Confidence: medium

## References

- `docs/specs/staqex-continuous-discretization.md`
- `tests/test_continuous_discretization_red.py`

## Work Notes

- Red reproduced during WP-0127 intake. The failing assertion depended on
  the retired AST-derived `symbolic_ir` authority; the accepted contract is
  already represented by `compiled.discretization_bridges`.

## Verification

- Targeted test passes after removing the stale parallel-authority assertion.

## Process Review

- Outcome: not yet
- Lesson written: not yet
- Template-feedback path: none
