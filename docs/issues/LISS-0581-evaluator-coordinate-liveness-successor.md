# LISS-0581: Evaluator coordinate liveness successor

## Metadata

- Local issue ID: LISS-0581
- GitHub issue: none
- Status: active — Phase 3 final review approved; commit and post-commit verification pending
- Phase: phase-3-final-review-approved
- Type: behavior-preserving evaluator decomposition
- Priority: normal
- Initial planning size: M
- Current planning size: M
- Owner/agent: Codex host agent
- Related branch: `feature/liss-0581-red`
- Parent: WP-0174
- Depends on: none; architecture boundary accepted by ADR 0228

## Summary

Extract existing coordinate liveness and Trace-Out helper bodies from the
Evaluator and duplicated frame helpers into a cohesive stateless successor.
Preserve ADR 0138/0142/0153/0158 behavior and all current consumer entrypoints;
Phase 3 and final completion remain separately gated.

## Design Check

- Scope: static Phase 0 design for current coordinate-liveness and Trace-Out
  responsibilities only.
- Specifications inspected: accepted core module decomposition; LISS-0561,
  LISS-0572, LISS-0573 contracts; runtime DEC-0005 and recovered ADR 0138 / 0158.
- Proposed component boundary: pure AST/liveness and `Joint` coordinate
  transforms in `runtime/evaluation/liveness.py`; Evaluator retains state and
  compatibility hooks. No ports/adapters or new DTOs.
- Implementation permission at intake: no. Phase 2 and Phase 3 were later
  explicitly approved on 2026-09-28; no commit/push/merge authorization follows.
- Requested approval type after this design: separate Phase 0 acceptance.
  Phase 0 and Phase 1 Red/test review are accepted.
- Post-review: same-context review required if a review packet is later
  required; human Adjudicator architecture decision remains mandatory.

## Scope and evidence

See the [specification](../specs/evaluator-coordinate-liveness.md). The
Architecture boundary was accepted as [ADR 0228](../architecture/adr/0228-evaluator-coordinate-liveness-boundary.md)
on 2026-09-28; the [review packet](../collaboration/reviews/2026-09-28-liss-0581-architecture-review.md)
records that typed approval.
Phase 0 measured the current facade at 1,307 physical lines / 75 methods on
`83c93a52` and statically found duplicate frame helpers plus consumers in
execution, observation, pipes, and evolution.

Phase 1 Red added the dedicated characterization/ownership suite and active
Red registry entries. At that phase, three behavior tests passed and two
structural assertions failed as expected. Phase 2 later resolved those
structural assertions; no Active Red entries remain.

## Applicable Process Lessons

Applied in the proposed spec: evaluator state ownership; private consumer
inventory and explicit callback boundaries; successor source ownership;
compatibility hook identity and export baseline; acceptance-to-test mapping;
and status synchronization. Detailed dispositions are in the spec.

## Open decisions

- Commit authorization/action and post-commit all-blocking verification remain
  outstanding; this approval did not request a commit.

## Next safe action

Phase 2 implementation and verification are recorded in the
[Phase 2 verification record](../collaboration/reviews/2026-09-28-liss-0581-phase2-verification.md).
Phase 3 changes and the same-context review are recorded in the
[Phase 3 review packet](../collaboration/reviews/2026-09-28-liss-0581-phase3-refactor-review.md).
Human Phase 3 final-review approval is recorded in the
[Phase 3 review packet](../collaboration/reviews/2026-09-28-liss-0581-phase3-refactor-review.md).
The working tree remains uncommitted; after an authorized commit, rerun all
blocking suites against its exact SHA before considering issue closure.
