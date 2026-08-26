# LISS-0437 / ADR 0210 finite Limit policy Red trace

## Approval

- User approved Phase 1 Red on 2026-08-15.
- Scope: acceptance tests for explicit finite `Limit` target policy.
- Not authorized: production implementation, finite Limit execution, QPU
  deployment, S02 numerical migration, or policy inference.

## Acceptance contract under test

- Target profile declares method, order/steps, and error budget explicitly.
- The source and compile provenance retain the written `Limit` transform
  without rewriting it to `exp`; finite target-plan fields are deferred to a
  later implementation phase.
- Missing policy rejects before allocation with no circuit or partial program.

## Test artifact

- `tests/test_liss_0437_limit_policy_red.py`
- Command: `python3 tests/test_liss_0437_limit_policy_red.py`
- Phase 2 Green is now separately approved and implemented; this file remains
  the Phase 1 acceptance history.

## Phase 2 Green result

- `EvolutionTargetProfile` accepts method, order, steps, and error budget.
- Valid policy is retained in target provenance and returns the explicit
  `formal_limit_realization_pending` rejection without allocation.
- Invalid policy remains `EVOLUTION_REALIZATION_REQUIRED`.
- Finite Limit execution and QPU realization remain unimplemented.
- Evidence:
  `tests/test_liss_0437_limit_policy_green.py` → `GREEN: 2/2`.

## Phase 2 Green review

- Review record:
  `docs/collaboration/reviews/2026-08-15-liss-0437-limit-policy-green-review-01.md`
- Verdict: **READY for the approved bounded policy slice**.
- Additional evidence: policy boundary `3/3`; Phase 3 bounded suite `6/6`.
- This review does not approve finite Limit execution or QPU deployment.

## Review gate

- Independent review of the Red acceptance artifacts is required before any
  implementation phase.

## Review result

- Review record:
  `docs/collaboration/reviews/2026-08-15-liss-0437-limit-policy-red-review-01.md`
- Verdict: **READY for Phase 1 Red artifacts**.
- Result: `RED suite: 1/3 failing as expected`.
- Phase 2 Green finite-policy implementation remains separately gated.
