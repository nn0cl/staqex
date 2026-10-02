# LISS-0582 Phase 1 Red test review

## Review Target

- Issue: [LISS-0582](../../issues/LISS-0582-evaluator-runtime-plan-eligibility.md)
- Specification: [Evaluator runtime-plan eligibility and projection successor](../../specs/evaluator-runtime-plan-eligibility.md)
- Work Plan: [WP-0174](../../work-plans/WP-0174-evaluator-residual-responsibility-successors.md)
- Current phase: Phase 1 Red
- Requested approval: Phase 1 Red test review
- Approval type: phase
- Implementation allowed: no
- Post-review required: separate Phase 2 Green / implementation approval

## Approved test boundary

The test-only change is limited to:

- `tests/test_liss_0582_runtime_plan_eligibility_red.py`
- the LISS-0582 entry in `docs/testing/active-red-tests.toml`

The contract covers successor ownership, facade body removal, absence of
copied mutable state, orchestration wiring, and compatibility callable identity.
Existing LISS-0493–0498 runtime-plan behavior suites remain the behavioral
authority and are not duplicated.

## Red verification

- Tested SHA: `d074bbf59d4d519c81ad51950c40dec6c3f9b20a`
- Tree state: dirty with the Phase 1 Red test/docs changes; production source
  unchanged
- Environment: local macOS worktree, Python 3.14.6, `.venv`
- Command: `.venv/bin/pytest -q tests/test_liss_0582_runtime_plan_eligibility_red.py`
- Result: **5 failed**, 0 passed, 0 collection errors after repairing the
  test-only import-path setup
- Failure classification: missing successor module; seven candidate bodies
  still on `Evaluator`; orchestration does not yet call successor policy; and
  compatibility identity is not yet installed. These are the intended Green
  gaps, not behavior fixture failures.
- Lifecycle: `python3 scripts/check-test-lifecycle.py --root .` —
  `ACTIVE_RED_LIFECYCLE_OK entries=1`
- Formatting: `git diff --check` — passed

## Review notes

- The initial run had one test collection error because the new test did not
  initialize the repository import path. The setup was corrected to match the
  nearest authoritative Red suites, then the exact bounded suite was rerun.
- The first orchestration assertion checked only source substrings. During
  review it was strengthened to inspect imports and actual AST call nodes, so
  a dead compatibility string cannot satisfy the contract.
- No production code, public API, semantic-plan builder, or unrelated test was
  changed.
- The test asserts the accepted candidate module name
  `runtime/evaluation/plan_eligibility.py`; changing that boundary requires a
  renewed design decision before Phase 2.

## Decision

- [x] Phase 1 Red accepted
- [ ] Phase 1 Red rejected
- [ ] Needs correction

Review disposition: the initial stale Issue wording and weak substring
assertion were corrected. No blocking test-design finding remains. Human
Adjudicator acceptance was received in the thread on 2026-09-29:
`Phase 1 Red acceptance承認`. Phase 2 Green / implementation is not authorized
by this packet.

## Same-context reviewer disposition

- **Isolation:** `same_context`, as selected by
  `docs/collaboration/runtime-routing.toml`; this is weaker than an independent
  `separate_context` review.
- **Acceptance inventory:** all five Phase 1 Red tests map to the accepted
  structural boundary; existing LISS-0493–0498 suites remain the named
  behavior evidence rather than being duplicated.
- **Private consumers:** the review re-read the actual orchestration,
  evaluator, observation, context, execution, compatibility, and test import
  paths. The test contract requires successor callable identity, not merely
  matching names.
- **Findings:** initial test setup import error and source-substring assertion
  were corrected; the stale Issue wording was synchronized. No blocking
  finding remains.
- **Next requested approval:** human **Phase 2 Green / implementation
  approval**. Implementation remains explicitly unauthorized until that
  approval.
