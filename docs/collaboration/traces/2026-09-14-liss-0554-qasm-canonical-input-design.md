# AI Work Trace: LISS-0554 QASM canonical input design

## Request

- Date: 2026-09-14
- User request: `LISS-0554 Phase 0 acceptance / Architecture review`
- Current phase: Architecture Path / Phase 0
- Canonical issue or work plan: LISS-0554 / WP-0161
- AI planning record: AIP-0554-001

## Context Ledger

- Included: QASM public-entry and consumer-migration specifications, ADR 0211,
  ADR 0220, emitter/lowerer entry points, LISS-0477, LISS-0446, LISS-0501,
  and active-Red ownership.
- Omitted: Phase 1–3 implementation, provider/live-QPU/AWS, dynamic QASM,
  CH0, Rust, S02, and lowerer retirement.
- Assumptions: QASM consumes canonical QPU projection; accepted canonical
  public facades remain behaviorally stable.
- Open decisions: Adjudicator approval of ADR 0222 and Phase 1 contract.

## Routing

- Model/assistant/tool: Codex host agent; deterministic repository tools
- Reason: same-context review is configured
- Privacy constraints: no secrets or provider data included

## Execution Record

- Scope: Phase 0 architecture design and review packet only
- Result: proposed ADR, Issue refinement, review summary, and trace created;
  no source/test implementation changed
- Exact verification: LISS-0477 missing-projection node failed because raw
  input emitted QASM (`ok=True`).
- Isolation: `same_context`, weaker than `separate_context`.

Architecture approval: `ADR 0222 Architecture / LISS-0554 Phase 0 acceptance
承認`, received 2026-09-14.

## Next Safe Action

Next safe action: request `LISS-0554 Phase 1 Red 承認` before changing tests.

### Phase 1 Red

- Adjudicator approval: `LISS-0554 Phase 1 Red 承認`, 2026-09-14.
- Scope: reuse the missing-projection test and add a no-rebuild assertion.
- Result: **2 failed, 3 passed**, no collection errors; no production source
  changed.
- Next approval: `LISS-0554 Phase 1 Red テストレビュー承認`.

Phase 1 Red review approval received: `LISS-0554 Phase 1 Red テストレビュー
承認`, 2026-09-14. Next approval is `LISS-0554 Phase 2 Green / Implementation
承認`.

### Phase 2 conflict

- Phase 2 implementation approval was received, but the early missing-IR
  guard breaks the accepted LISS-0446 unit-only compatibility test.
- The guard was removed and implementation is paused pending an architecture
  decision on whether ADR 0222 supersedes that compatibility allowance.

### Phase 2 resolved implementation

- Layered resolution approved: strict direct emitter plus one-shot unit-only
  facade compatibility build.
- Implemented the emitter guard and facade-owned build; updated the build-count
  observation point.
- Verification: **25 passed**, `py_compile` passed; no live-QPU test.

### Phase 3 Refactor

- Adjudicator approval: `LISS-0554 Phase 3 Refactor 承認`, 2026-09-14.
- Extracted missing-IR rejection into a private helper and simplified the
  identity guard with unchanged behavior.
- Verification: **25 passed** plus static/lifecycle checks.

Final review approval: `LISS-0554 Phase 3 最終レビュー 承認`, 2026-09-14.
LISS-0554 is complete and its active-Red entry was removed. Next safe action:
`LISS-0555 Phase 0 acceptance / Architecture review`.
