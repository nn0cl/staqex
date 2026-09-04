# <LISS-0506: Jordan-Wigner mapping provenance>

## Metadata

- Local issue ID: LISS-0506
- GitHub issue: none
- Status: review
- Phase: phase-3-refactor
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

- Red reproduced during WP-0127 intake. The numerical Jordan–Wigner and QASM
  paths were already green; the failing assertions treated the canonical
  `compile_source().symbolic_ir` view as if it still owned legacy mapping and
  second-quantized metadata.
- Phase 2 fix: migrated these assertions to the explicit
  `build_symbolic_ir(compiled.unit)` compatibility API. This preserves the
  accepted metadata contract without restoring an AST-derived parallel
  authority to the canonical compile result.

## Verification

- `./.venv/bin/pytest -q tests/test_jordan_wigner_mapping_red.py tests/test_second_quantized_operators_red.py`: 18 passed.

## Process Review

- Outcome: no operating-contract deviation or operational problem found.
- Isolation: same_context; weaker than separate_context.
- Findings: apply none; the change is a compatibility-test migration and the
  targeted numerical, QASM, and provenance tests pass.
- Next requested approval type: Adjudicator Phase 3 review/acceptance.

## Process Review

- Outcome: not yet
- Lesson written: not yet
- Template-feedback path: none
