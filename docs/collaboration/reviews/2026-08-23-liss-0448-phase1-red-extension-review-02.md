# LISS-0448 Phase 1 Red Extension — Independent Review 02

- Trigger: user-approved Phase 1 Red extension and continuation after the prior NOT READY review.
- Review mode: fresh independent context, read-only; no approval or implementation authority.
- Scope: LISS-0448 canonical Coin/Mix meaning, branch-rule preservation, source provenance, fingerprint sensitivity, and fail-closed legacy QPU projection.
- Branch: `codex/liss-0448-canonical-qasm-coin-mix-projection`.
- Phase: Phase 1 Red extension.
- Allowed mutation scope: tests, fixtures, and review/trace records only; production implementation remains out of scope.

## Inspected artifacts

- `tests/test_liss_0448_coin_mix_semantic_red.py`
- `tests/fixtures/canonical_coin_mix/`
- `compiler/staqex/scientific_semantic_ir.py`
- `compiler/staqex/backend/qasm/lower.py`
- `docs/specs/staqex-canonical-qasm-coin-mix-projection.md`
- `docs/architecture/adr/0213-canonical-mixture-branch-meaning-and-qpu-boundary.md`
- `docs/collaboration/independent-review-perspectives.md`

## Findings

| Priority | Finding | Evidence | Disposition |
| --- | --- | --- | --- |
| P1 | The Red extension was initially not self-contained because the new semantic and Coin-only fixtures were untracked and absent from commit `3d265ea9`. | `git status --short`; `tests/fixtures/canonical_coin_mix/coin_only.sqx`; `tests/fixtures/canonical_coin_mix/mixture_semantics.sqx` | accepted — add both fixtures to the bounded Red commit |
| P1 | The working tree contains earlier Phase 2/3 production and documentation changes, so the Red extension requires an explicit commit boundary and must not be described as an isolated complete diff. | `git status --short`; commits `3d265ea9`, `0fc2be99`, `d7dcd742` | accepted — record the baseline and stage only Red tests/fixtures |
| P1 | Branch-rule assertions derive expected arm identity only from semantic traversal order and do not independently anchor the rules to source order/spans. | `tests/test_liss_0448_coin_mix_semantic_red.py::test_liss_0448_mix_preserves_control_and_branch_rules` | accepted — retain a source-span contract and bind ordered rules to fixture source order |
| P1 | Direct Coin behavior is not isolated when the primary fixture also contains Mix. | `tests/fixtures/canonical_coin_mix/mixture_semantics.sqx`; direct Coin test | accepted — use `coin_only.sqx` |
| P2 | Fingerprint Red coverage currently mutates only one pattern value; control, else-marker, and rule-shape sensitivity are not all independently exercised. | `test_liss_0448_branch_changes_update_semantic_fingerprint` | accepted — add an else/rule mutation assertion within the same bounded test file |

## Correction boundary

Only tests, fixtures, and this review/trace record may be changed in the correction pass. No production implementation, architecture, or phase transition is authorized by this review.

## Readiness verdict

`NOT READY` for Phase 2. The Red contracts are directionally correct but require the accepted in-scope corrections and a fresh independent re-review.

## Reviewer perspectives

- Meaning-preservation / blackboard fidelity.
- Canonical IR authority and source provenance.
- Realization-boundary and fail-closed QPU behavior.
- Test isolation and evidence reproducibility.

## Next review condition

After the Red tests and fixtures are self-contained, source-anchored, and committed as a bounded test-only correction, run a fresh read-only independent review. Phase 2 remains blocked until that review is ready and the user gives separate Phase 2 approval.

## Terminal state

`RE_REVIEW` — not terminal; accepted actionable findings remain.

## Approval status

Phase 1 Red extension is user-approved. Phase 2 Green approval has not been granted.
