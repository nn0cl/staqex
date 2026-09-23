# Work Plan: Evaluator residual body cleanup

## Goal

Continue reducing the evaluator facade without moving behavior into unrelated
modules or changing runtime meaning. Begin with the narrowly accepted cleanup
of method bodies that are shadowed by compatibility wiring.

## Scope

- In: LISS-0576, removal of five source definitions in `runtime/evaluator.py`
  after Phase 1 contract review and separate Phase 2 implementation approval.
- Out: extracting active classical, operator, dynamic, or execution-plan
  responsibilities; modifying successor implementations; changing runtime
  semantics, APIs, diagnostics, QASM, or provider behavior.

## Issue Graph

| Issue | Status | Initial size | Current size | Planning record | Depends on | Blocks | Branch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| LISS-0576 | ready — Phase 0 accepted | M | M | AIP-0576-001 | - | - | docs/liss-0576-phase0-design |

## Recommended Order

1. LISS-0576 Phase 1 Red: add structural absence and runtime hook-identity
   assertions, plus focused existing behavior characterizations; obtain test
   review before implementation.
2. LISS-0576 Phase 2 Green: remove only the five accepted definitions; run
   consumer smoke, focused/adjacent regressions, and all declared blocking
   suites against the final commit SHA.
3. Phase 3/final review and process review; synchronize the Issue, this plan,
   and evidence before marking work done.

## Current Next Issue

- Issue: LISS-0576
- Reason it is unblocked: Phase 0 acceptance was granted 2026-09-24; no
  dependency remains open.
- Adjudicator approval needed: `LISS-0576 Phase 1 Red 承認`.
- Implementation allowed: no.

## Risks

- Compatibility assignments are dynamic. Static method-name searches alone do
  not prove the installed callable identity; tests must exercise the imported
  Evaluator class and verify hook identities.
- Future reordering/removal of an installer could make a currently shadowed
  body active. Scope excludes installer changes and preserves its current
  identity contract.
- Dynamic/reflection-based third-party consumers are not exhaustively
  enumerable; only repository consumers are in scope.

## Verification Plan

- Phase 0: AST definition/reassignment inventory, private-consumer search,
  responsibility overlap review, and boundary acceptance.
- Phase 1: focused structural Red plus positive compatibility/hook
  characterizations; no production source edits.
- Phase 2/3: consumer import/hook smoke, affected continuous/assignment tests,
  adjacent evaluator suite, complete blocking pytest, compile/import checks,
  active-Red lifecycle, document lifecycle, coverage ledger, and diff checks.
- Report focused and all-blocking results separately with exact SHA,
  environment, baseline comparison, and run evidence.

## Process Review

- Outcome: not yet
- Lesson written: not applicable
- Template-feedback path: none
