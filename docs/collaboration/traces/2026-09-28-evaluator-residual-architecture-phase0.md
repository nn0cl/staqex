# Trace: Evaluator residual responsibility Architecture Path Phase 0

## Request and status

- Date: 2026-09-28
- User request: investigate remaining Evaluator responsibilities under the
  approved Architecture Path Phase 0 scope and prepare an actionable successor
  proposal.
- Current phase: Phase 0 investigation/design only
- Canonical planning: proposed WP-0174 / LISS-0581
- Source inventory SHA: `83c93a524c7c90710ed965d231ffe85b20dc3163`
- Branch: `docs/liss-0581-evaluator-residual-phase0`

## Context ledger

- Included: accepted core decomposition spec; evaluator and evaluation package
  source; runtime routing and collaboration policies; LISS-0561/0572/0573
  consumer contracts; LISS-0580 completed work; current DEC-0005 and recovered
  ADR 0138/0158 text from the recorded archival source commit.
- Omitted: unrelated compiler families, provider/QPU behavior, private user
  data, test execution, and source implementation.
- Assumptions: existing Trace-Out semantics are frozen; static repository
  search identifies discoverable consumers but cannot prove dynamic external
  use.
- Open decisions: Phase 0 acceptance remains pending; the completed static
  test/lifecycle reconciliation and allowed-path matrix are recorded in the
  LISS-0581 specification and Phase 0 acceptance packet.

## Routing and cost/reasoning controls

- Operating path: Architecture Path.
- Route: host reasoning plus deterministic shell/AST/search inventory; live
  routing selects same-context review if/when an agent review packet is
  required. No external model/provider invoked.
- Files read: relevant architecture, collaboration policy, issue/spec/WP,
  evaluator, runtime consumers and direct tests; unrelated compiler areas
  omitted.
- Deterministic checks: `wc -l`, Python AST method count, `rg` consumer search,
  `git show` for recovered accepted ADR text. No tests were run.
- Escalation reason: cross-module responsibility and archived ADR source
  required a boundary proposal.
- Avoided LLM work: deterministic size/callsite evidence gathered locally;
  full unrelated runtime/test context omitted.
- Rework caused by AI output: none identified.
- Model/token usage: host-displayed model and actual token metric unavailable;
  not estimated as actual usage.

## Findings

- `evaluator.py`: 1,307 lines / 75 class methods.
- Strongest cohesive candidate: coordinate liveness/Trace-Out helpers are
  duplicated between Evaluator and frames and serve frames, pipes, evolution,
  execution, and observation.
- Proposed successor: stateless `runtime/evaluation/liveness.py`; proposal
  retains existing facade hook names as thin compatibility delegates and
  requires exact hook/consumer evidence before Phase 1.
- Other candidates remain distinct: runtime-plan eligibility, static
  `forEach`, tensor binding, host coefficient-array resolution, partial-call
  filling, and small classical-state helpers. `_eval_set_comprehension` stays
  with dispatch as required by its accepted specification.
- `docs/collaboration/canonical-document-register.md` is absent. The
  repository's document lifecycle therefore has a navigation gap; this work
  does not infer new canonical authority from historical files.
- Runtime routing has no `[source_structure]` thresholds. No numeric
  structure-budget compliance claim is made.

## Execution record

- One static investigation on main SHA `83c93a52`; no production or test code
  changed. No tests run (not authorized in this Phase 0 scope).
- Artifacts drafted: proposed coordinate-liveness specification, Issue
  LISS-0581, Work Plan WP-0174, Architecture review packet, handoff, and
  factual current metrics in the accepted core decomposition specification.
- Adjudicator approved the boundary and LISS-0581 Phase 0 acceptance on
  2026-09-28; accepted ADR 0228 records the architecture decision. Static
  acceptance mapping found no live `_red.py` lifecycle
  entries; it identified exact evidence for ADR 0138/0142/0153/0158 and gaps
  for eligible post-call live-out retention, Snapshot exclusion, and successor
  ownership/delegate behavior. No test or implementation permission follows.

## Applicable process lessons

- Applied evaluator-state-ownership: successor proposed as stateless.
- Applied private-consumer-inventory and decomposition-callback-boundary:
  callsites, protocol hooks, and source-inspection tests recorded.
- Applied decomposition-source-ownership and decomposition-boundary: avoid
  duplicate bodies and unrelated sibling growth.
- Applied compatibility-hook-identity-contract and compatibility-baseline:
  preserve real hook/export surfaces and require live identity evidence where
  wiring changes.
- Applied acceptance-inventory-reconciliation: Phase 1 clause-to-test mapping
  is explicitly a prerequisite, not claimed complete.
- Applied status-drift: ADR/spec/issue/work plan/review/trace now consistently
  record accepted architecture with Phase 0 acceptance still pending.

## Next safe action

Adjudicator approved the proposed Architecture boundary and LISS-0581 Phase 0
acceptance on 2026-09-28. The Phase 0 acceptance packet records allowed file
sets and clause-to-evidence/gap mapping. Phase 1 Red remains subject to
separate approval; no test or implementation approval is implied.
