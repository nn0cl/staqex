# <LISS-0508: free-function and struct argument binding>

## Metadata

- Local issue ID: LISS-0508
- GitHub issue: none
- Status: done — Phase 3 refactor complete
- Phase: phase-3-refactor-complete
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

- Red reproduced during WP-0127 intake. The callable-plan path routed
  namespace-qualified struct constructors as methods, then attempted to bind
  pure `Float`-returning free functions through Joint coordinates.
- Phase 2 fix: `_bind_call` resolves qualified struct constructors before
  method dispatch, and `_bind_names` sends classical-returning free functions
  through the existing value/frame evaluator. Nested object and field
  projections remain in the callee-local frame.

## Verification

- `PYTHONPATH=. ./.venv/bin/pytest -q tests/test_liss_0290_adr_0180_residuals_red.py tests/test_liss_0292_typefirst_freefn_args_red.py tests/test_liss_0294_nested_freefn_args_red.py`: 11 passed.

## Process Review

- Outcome: no operating-contract deviation or operational problem found.
- Isolation: same_context; weaker than separate_context.
- Findings: apply none; the fix preserves pure value/object boundaries and
  all targeted callable regression cases pass.
