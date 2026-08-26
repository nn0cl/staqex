# LISS-0448 Phase 1 Red Correction Trace

## Accepted review corrections

- Added a fingerprint-sensitivity Red assertion for branch pattern changes.
- Added direct legacy `Coin` fail-closed coverage.
- Added source-order anchoring for the branch-rule expectation and froze the
  exact `control_source_node_id` / `branch_rules` shape in ADR 0213 and the
  accepted Spec.
- The test/fixture extension is isolated in commit `3d265ea9`:
  `test: extend LISS-0448 branch meaning red contracts`.

## Verification

- Focused command: `.venv/bin/python -m pytest -q
  tests/test_liss_0448_coin_mix_semantic_red.py`.
- Current Red result: **3 failed, 4 passed**.
- Expected failures: missing canonical branch fields, legacy `Mix`→`CX`
  fallback, and unchanged semantic fingerprint after pattern mutation.
- Production implementation remains unmodified by this Phase 1 extension.
- `git diff --check`: passed.

## Next review condition

Fresh independent review of the corrected Red contract is required before
requesting Phase 2 Green approval.
