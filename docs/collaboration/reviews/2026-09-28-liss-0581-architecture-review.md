# LISS-0581 Architecture Review Request

## Review Target

- Artifact: [proposed specification](../../specs/evaluator-coordinate-liveness.md),
  [Issue](../../issues/LISS-0581-evaluator-coordinate-liveness-successor.md),
  and [Work Plan](../../work-plans/WP-0174-evaluator-residual-responsibility-successors.md)
- Current phase: Architecture Path Phase 0 investigation/design complete
- Requested approval: accept or revise the proposed liveness successor
  architecture boundary
- Approval type: architecture
- Approved scope: investigate remaining Evaluator responsibilities and prepare
  a behavior-preserving successor design; this request is limited to the
  proposed coordinate-liveness/Trace-Out boundary
- Implementation allowed: no
- Post-review required: yes — if accepted, record the decision in an ADR, then
  obtain separate LISS-0581 Phase 0 acceptance before any Phase 1 Red work

## What Changed

- Proposed `runtime/evaluation/liveness.py` as the owner of pure AST
  liveness/inspection and coordinate Trace-Out algorithms.
- Documented actual consumers in frames, pipes, evolution, execution, and
  observation; identified duplicate frame helpers and existing private-hook
  tests.
- Reconciled the behavior boundary to accepted ADR 0138/0142/0153/0158 text.
- Refreshed the accepted core decomposition document's factual current
  measurements and merged/completed status.
- No tests, source implementation, ADR acceptance, or language behavior
  changes were made.

## Why It Matters

This is a cohesive cross-module family with direct implementation duplication,
but `_expr_free_vars` and `_expr_has_inspect` also support existing observation
analysis and tests. Their relocation and facade compatibility must be explicit
to avoid an accidental LISS-0561 scope change. The successor is proposed as
stateless; Evaluator remains the sole mutable runtime-state owner.

## Adjudicator Checklist

- [ ] The phase is correct.
- [ ] The included context is sufficient.
- [ ] The omitted context is acceptable.
- [ ] Assumptions are visible.
- [ ] Open decisions are answered or intentionally deferred.
- [ ] Static verification is adequate for Architecture Path Phase 0.
- [ ] Approval type and scope are explicit.
- [ ] Implementation permission is explicitly denied.
- [ ] Post-review ADR and separate Phase 0 acceptance are recorded as required.

## Decision

- [x] Approved
- [ ] Approved with comments
- [ ] Rejected
- [ ] Needs ADR

Adjudicator decision: approved — `WP-0174 / LISS-0581 Architecture boundary 承認`, 2026-09-28. Recorded in ADR 0228. Implementation remains unauthorized.
