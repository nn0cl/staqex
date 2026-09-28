# LISS-0581 Phase 1 Red Review Request

## Design Note

- Target behavior or question: lock characterization and extraction contracts
  for the existing coordinate liveness/Trace-Out family without changing
  production behavior.
- Requested phase: Phase 1 Red (test authoring and bounded test execution).
- Proposed next phase: Phase 1 test review; Phase 2 remains separately gated.
- Adjudicator decision needed: authorize only the named Red test file and
  lifecycle registry updates.
- Requested approval type: phase
- Approved scope, if already granted: Architecture boundary in ADR 0228 and
  LISS-0581 Phase 0 acceptance.
- Implementation allowed: no
- Post-review required: yes — review Red failures and coverage before any
  Phase 2 Green/Implementation approval.

## Review Target

- Artifact: [LISS-0581 specification](../../specs/evaluator-coordinate-liveness.md),
  [Issue](../../issues/LISS-0581-evaluator-coordinate-liveness-successor.md),
  and [WP-0174](../../work-plans/WP-0174-evaluator-residual-responsibility-successors.md)
- Current phase: Phase 1 Red approval request
- Requested approval: `WP-0174 / LISS-0581 Phase 1 Red 承認`
- Approval type: phase
- Approved scope: author and run `tests/test_liss_0581_evaluator_coordinate_liveness_red.py`,
  and update `docs/testing/active-red-tests.toml` to register only its active
  Red assertions
- Implementation allowed: no
- Post-review required: yes — separate Phase 1 Red test review; Phase 2 Green
  and implementation require another explicit approval

## Proposed acceptance nodes

1. **Eligible post-call live-out behavior:** compile and run a measure-free
   library-call example whose later call consumes a pre-existing caller
   coordinate and the first call's result, with no `Inspect` or `Snapshot`.
   From the parsed main statements, assert the eligible live-out set includes
   that coordinate and result, then apply caller Trace-Out to a representative
   Joint and assert those names remain while dead caller/callee names disappear.
   Direct intermediate-state source observation is not available without
   introducing an eligibility-disabling observation or violating linear
   consumption, so the policy/helper seam is the observable test boundary.
2. **Inspect exclusion:** parse/compile an `Inspect`-containing main and
   directly assert the ADR 0158 interprocedural eligibility hook rejects its
   statement list. The existing deferred-path test is only adjacent evidence.
3. **Snapshot exclusion:** use established syntax (`Snapshot x to stdout`)
   and assert the same eligibility hook rejects the main statement list.
4. **Successor ownership:** require
   `compiler/staqex/runtime/evaluation/liveness.py` to own the pure coordinate
   enumeration, function/caller Trace-Out, main eligibility/live-var, and AST
   walker functions. Evaluator must not retain their algorithm bodies.
5. **Compatibility and identity:** preserve Evaluator's existing private hook
   names as thin delegates to the corresponding successor functions; verify
   actual runtime hook identity/forwarding rather than source-name presence.
6. **Frame de-duplication:** remove local duplicate coordinate helpers from
   `frames.py` and route frame return paths through the successor.
7. **Read-only/stateless boundary:** successor must not import or instantiate
   Evaluator, own mutable runtime maps, or depend on unrelated observation
   execution services.

Existing evidence for ADR 0138/0142/0153 and dead-caller/result retention is
listed by exact test name in the accepted specification. Those suites remain
adjacent regressions; do not register completed historical tests as active
Red. During Red, report each node's expected/actual result separately and
distinguish structural failures from source fixture failures.

## Context Ledger

- Included: accepted ADR 0228, liveness specification, existing Trace-Out
  tests, relevant LISS-0561/0572/0573 structural contracts, evaluator/context
  hooks, parser's Snapshot syntax, and Active Red lifecycle policy.
- Omitted: other Evaluator successor families, provider/QPU paths, unrelated
  runtime tests, and semantics not named by ADR 0138/0142/0153/0158.
- Assumptions: approved behavior is frozen; the dedicated suite can exercise
  source behavior and AST/runtime hook contracts without production changes.
- Open decisions: none for the proposed node set; implementation details stay
  out of this phase.

## Process lessons applied

- `acceptance-inventory-reconciliation`: each Phase 0 clause maps to existing
  test evidence or one of the explicit new nodes above; unsupported empty or
  correlated-Joint coverage is not claimed.
- `compatibility-hook-identity-contract`: verify actual successor function
  identity/forwarding, not merely imports or attribute strings.
- `private-consumer-inventory` and `decomposition-callback-boundary`: keep
  existing context callbacks and include `frames.py` as a direct consumer.
- `evaluator-state-ownership`: successor stays pure; Evaluator keeps all
  mutable state.
- `status-drift`: Phase 0 approval is synchronized separately; no Phase 1
  tests exist or are registered before this Phase 1 approval.
- Routing: `same_context` review; `host` implementation per live routing.

## Adjudicator Checklist

- [x] The phase is correct.
- [x] The included context is sufficient.
- [x] The omitted context is acceptable.
- [x] Assumptions are visible.
- [x] Open decisions are answered or intentionally deferred.
- [x] The proposed test scope and deterministic verification are adequate.
- [x] Approval type and allowed paths are explicit.
- [x] Implementation permission is explicitly denied.
- [x] Separate test review and later implementation approval are recorded.

## Decision

- [x] Approved
- [ ] Approved with comments
- [ ] Rejected
- [ ] Needs revision

Adjudicator decision on Phase 1 Red: approved —
`WP-0174 / LISS-0581 Phase 1 Red 承認`, 2026-09-28. Test review remains
pending and Phase 2 is not authorized.
