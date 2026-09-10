# LISS-0533 Phase 3 Final Review

- Date: 2026-09-10 (Asia/Tokyo)
- Approval: `LISS-0533 Phase 3 最終レビュー 承認`
- Scope: R01 discrete graph, interaction law, and explicit Ising projection
- Isolation: `same_context`; this is weaker than `separate_context`.

## Evidence rechecked

- R01 acceptance row in `docs/specs/staqex-scientific-workflow-acceptance.md`
- Phase 0 decisions and Phase 1–3 records in WP-0150/LISS-0533
- `tests/test_liss_0533_discrete_interaction_red.py`
- `compiler/staqex/discrete_interaction_profile.py`
- Phase 0/1/2/3 traces and the Phase 3 commit

## Verification

- Targeted pytest: **5 passed**
- AST parsing: passed
- `git diff --check`: passed
- Document lifecycle check: passed

## Finding

**Blocker — diagnostic contract is not observable.** Phase 0 fixed five
diagnostic codes (`DISCRETE_GRAPH_AS_HAMILTONIAN`,
`DISCRETE_DUPLICATE_EDGE`, `DISCRETE_INDEX_MISMATCH`,
`DISCRETE_SYMMETRY_MISMATCH`, and `DISCRETE_UNSUPPORTED_TARGET`). The current
implementation raises `DiscreteProfileError` with message text only, and the
Red tests match messages rather than asserting those codes. A consumer cannot
reliably distinguish the documented rejection reasons without parsing prose.

Disposition: **apply**. Add a structured code to the rejection error/result,
update the five negative tests to assert exact codes, and keep rejection
atomic. This is a small contract completion, not a reason to broaden R01.

This finding applies the existing acceptance-boundary lesson: every negative
projection assertion must be paired with an exact, scoped rejection contract.

## Status and next step

Keep LISS-0533/WP-0150 at `Phase 3 Refactor complete; final review pending`.
Do not mark the unit done until the diagnostic-code contract is implemented,
tested, and re-reviewed.

No process-review record is added because the issue/work plan is not being
closed.
