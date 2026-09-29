# LISS-0582 Phase 0 acceptance

## Review Target

- Artifact: [LISS-0582 design specification](../../specs/evaluator-runtime-plan-eligibility.md)
- Current phase: Phase 0 design
- Requested approval: Phase 0 acceptance
- Approval type: phase
- Approved scope: consumer/authority inventory and the proposed stateless
  runtime-plan eligibility/projection boundary for LISS-0582
- Implementation allowed: no
- Post-review required: yes — Phase 1 Red test review before any implementation

## What Changed

- The Phase 0 design identifies callable eligibility, Operator-attribute
  walking, minimal-evolution and first-family checks, and runtime-unit shaping
  as the candidate family.
- The boundary preserves compile-owned Scientific Semantic IR authority,
  Evaluator's single mutable-state ownership, private compatibility hooks, and
  canonical/legacy fallback behavior.
- The semantic runtime-plan builder remains an explicit ambiguity boundary;
  it is not merged into the evaluator policy successor without a later
  authority decision.

## Why It Matters

This is the next bounded successor in WP-0174's evaluator decomposition. The
acceptance prevents a line-count-driven split from conflating semantic
projection, runtime eligibility, deferred observation, and legacy fallback.

## Adjudicator Checklist

- [x] The phase is correct.
- [x] The included context is sufficient.
- [x] The omitted context is acceptable.
- [x] Assumptions are visible.
- [x] Open decisions are intentionally deferred.
- [x] Deterministic static inspection is adequate for this design step.
- [x] The approval type and scope are explicit.
- [x] Implementation permission is explicitly denied.
- [x] The Phase 1 Red review requirement is recorded.

## Decision

- [x] Approved
- [ ] Approved with comments
- [ ] Rejected
- [ ] Needs ADR

Approval received from the human Adjudicator in the thread on 2026-09-29:
`Phase 0 acceptance`.

## Next Gate

Prepare the Phase 1 Red test-only contract and request separate Phase 1 Red
approval. Do not edit production source or broaden the accepted boundary.
