# LISS-0566-B Phase 1 Red Test Review

## Review packet

- Scope: Unit B unitary/gate extraction Red contract.
- Canonical documents:
  - [LISS-0566-B issue](../../issues/LISS-0566-B-unitary-gate-successor.md)
  - [WP-0163](../../work-plans/WP-0163-evaluator-stateful-successor.md)
  - [Core module decomposition](../../specs/staqex-core-module-decomposition.md)
  - [Verification policy](../verification-policy.md)
- Test artifact: `tests/test_liss_0566_unit_b_red.py`
- Lifecycle artifact: `docs/testing/active-red-tests.toml`

## Findings and dispositions

1. The suite covers the approved Unit B ownership boundary: unitary resolver,
   QFT family, `apply`, `capply`, and the coupled polarity parser.
   **Disposition: accepted.**
2. Four structural assertions fail before implementation and three fixed-seed
   QFT/controlled-gate characterizations pass. **Disposition: accepted as the
   intended Red state.**
3. The initial compatibility assertion checked only name presence.
   **Disposition: apply.** It was strengthened to assert exact assignments to
   evaluator private hooks; the Red result remains `4 failed, 3 passed`.
4. The active-Red entry is linked to the non-terminal `LISS-0566-B` issue and
   uses `phase-1-red`. **Disposition: accepted.**

## Blockers

No test-contract blocker. Production implementation is not authorized by this
review; Phase 2 requires separate typed implementation approval.

## Verification

- Focused suite: `4 failed, 3 passed`, no collection errors
- Active-Red lifecycle: passed, one owned entry
- Document lifecycle and coverage-ledger consistency: passed
- `git diff --check`: passed
- No production source, reviewed acceptance, or exclusions were changed

## Review route and next approval

- Isolation: `same_context`; weaker than `separate_context`
- Review approval: `WP-0163 / LISS-0566-B Phase 1 Red テストレビュー承認`
- Next requested approval: `WP-0163 / LISS-0566-B Phase 2 Green / Implementation 承認`
