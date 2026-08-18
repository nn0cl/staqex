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
| LISS-0438 | complete; PR #554; CI run 32114315690 passed | M | M | AIP-0438-001 | LISS-0437 / ADR 0210 | none for bounded slice | `codex/liss-0438-residual-reconciliation` |

## Design Note

- Target behavior: make formal, exact-local, and finite-target evolution lanes
  distinguishable in the S02 representative fixture; retain exact `U_t` for
  local execution and reserve `U_qpu` for finite target-plan evidence.
- Phase executed: Phase 3 refactor/final-review preparation, approved by the
  user on 2026-08-18; bounded slice complete in PR #554.
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
3. Create Red tests only; stop for independent review and implementation
   approval.
4. Implement the minimum approved reconciliation after typed approval.
5. Run fixed-seed and benchmark verification, then independent review.

## Current Next Issue

- Issue: LISS-0438
- Reason it is unblocked: parent finite realization slice is complete and the
  residual boundary is isolated.
- Adjudicator approval needed: none for the bounded slice; seed and metric
  evidence is frozen in the Phase 2 and Phase 3 traces.

### [LISS-0438] Completion

- Status: complete.
- PR: PR #554.
- CI: run 32114315690 passed Repository sanity, Kernel root suites, and Spec
  verification.

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

This WorkPlan records the completed bounded Phase 3 refactor/final-review
packet in PR #554. It does not authorize scope expansion.
