# Work Plan: LISS-0438 explicit evolution residual reconciliation

## Goal

Reconcile the S02 representative source with the accepted explicit evolution
and finite `Realize` boundary while preserving the exact local numerical lane
and keeping target realization visibly separate.

## Scope

- In: design and acceptance specification, S02 source-to-blackboard mapping,
  fixed-seed/benchmark contract, finite realization provenance and rejection
  evidence, bounded corpus inventory.
- Out: implementation until separately approved, S02 numerical retuning,
  live QPU, provider SDK, credentials, network, and broad corpus migration.

## Issue Graph

| Issue | Status | Initial size | Current size | Planning record | Depends on | Blocks | Branch |
| --- | --- | --- | --- | --- | --- | --- | --- |
| LISS-0438 | design and independent review complete; Phase 1 pending | M | M | AIP-0438-001 | LISS-0437 / ADR 0210 | Phase 1 Red | `codex/liss-0438-residual-reconciliation` |

## Design Note

- Target behavior: make formal, exact-local, and finite-target evolution lanes
  distinguishable in the S02 representative fixture; retain exact `U_t` for
  local execution and reserve `U_qpu` for finite target-plan evidence.
- Phase to execute next: Phase 1 Red, pending typed user/Adjudicator approval;
  no AT-TDD phase has been approved.
- Context included: LISS-0438, ADR 0210, accepted explicit evolution Spec,
  `main_selection.sqx`, S02 README, existing S02 regression and benchmark
  tests, independent review perspectives.
- Context omitted: provider SDK details, credentials, live QPU material,
  unrelated examples, and full historical S02 implementation records.
- VO/DTO candidates: `RealizationComparisonRecord`,
  `FixedSeedBaseline`, `RealizationEvidence` (design names only; no code).
- Ports/adapters involved: none in design; later target-plan evidence must
  remain provider-neutral.
- Suggested routing: strong architecture review for boundary decisions;
  deterministic tools for fixed-seed and diff verification after approval.
- Ambiguities: authoritative fixed seed set and benchmark metrics; whether
  future broad corpus inventory deserves a separate Issue.

## Recommended Order

1. Review this WorkPlan and the residual acceptance specification independently.
2. Freeze Phase 1 Red scenarios for source fidelity, baseline stability,
   explicit Realize provenance, and fail-closed target rejection.
3. Obtain explicit Phase 1 approval.
4. Create Red tests only; stop for review and implementation approval.
5. Implement the minimum approved reconciliation.
6. Run fixed-seed and benchmark verification, then independent review.

## Current Next Issue

- Issue: LISS-0438
- Reason it is unblocked: parent finite realization slice is complete and the
  residual boundary is isolated.
- Adjudicator approval needed: typed Phase 1 Red approval and separate
  implementation approval; seed/metric authority must be frozen in Phase 1.

## Risks

- Mixing the exact local lane with finite target realization could silently
  change S02 numerical results.
- A benchmark comparison without frozen Host inputs or seeds would be
  non-reproducible.
- A broad corpus migration could turn a residual reconciliation into an
  unapproved language migration.
- Removing rejection provenance while removing executable allocation would
  violate ADR 0210's evidence contract.

## Verification Plan

- Design: path/link checks and independent review record.
- Later Red: compile/source-shape and provenance assertions only.
- Later Green: fixed-seed exact-lane comparison, target-plan provenance,
  pre-allocation rejection, and full regression.
- Always record exclusions: S02 numerical retuning, live QPU, provider SDK.

## Approval boundary

This WorkPlan authorizes design review only. It does not authorize source,
compiler, test, benchmark, or example changes.
