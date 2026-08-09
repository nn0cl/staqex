# LISS-0385: Dynamic reuse/reset capability demand inference (ADR 0199)

## Metadata

- Local issue ID: LISS-0385
- Status/phase: **proposed** / `phase-0-design` — awaiting Plan approval
  (Architecture Accept of ADR 0199 done 2026-08-09; Option B declined;
  no Red until Plan)
- Type: Feature Path (Kernel/Fake — demand inference + fail-closed
  diagnostics; no new `reset` keyword)
- Priority: P1
- Initial planning size: `M`
- Current planning size: `M`
- Owner / agent: Cursor (Grok)
- Program: [ADR 0199](../architecture/adr/0199-dynamic-qubit-reuse-reset.md)
  Follow-up item 1
- Parent: [ADR 0199](../architecture/adr/0199-dynamic-qubit-reuse-reset.md)
  (**Accepted** 2026-08-09; Option B declined)
- Depends on: ADR 0199 (Accepted); LISS-0077 Fake demand flags; LISS-0382
  mid-circuit witnesses (complete)
- Related: [LISS-0383](LISS-0383-dynamic-fake-executor-wire.md) (must keep
  P0 reject-on-demand); [LISS-0028](LISS-0028-dynamic-qpu-lane.md)
- Blocks: none (profile-enable Issue is separate)
- Branch: TBD at Plan approval
- GitHub Issue / PR: none yet

## Intent

Implement ADR 0199 Decisions 1–5 boundary in Kernel/Fake diagnostics:

1. Reset/reuse demands are Dynamic-lane only.
2. Unsupported profile demands fail closed (no Host silent emulate).
3. No new `reset` keyword (Option B declined).
4. `within` timing does not imply reuse.
5. Mid-circuit `measure` / `match` do not by themselves set reuse as
   satisfied preparation.

Default Plan: infer or record `needs_reset` / `needs_reuse` where source
or lowering would demand them, emit stable diagnostics on P0
feedback-only profiles, and leave profiles unchanged (still reject).

## Explicitly out of scope

- Lane-local `reset q` surface (needs future Architecture Accept).
- Enabling Fake profiles that actually perform reset/reuse.
- Fake-exec AST wire (LISS-0383) beyond coordination.
- JobResult `dynamic_trace` (LISS-0384).
- OpenQASM `reset` emission; live provider.

## Acceptance reference

[ADR 0199](../architecture/adr/0199-dynamic-qubit-reuse-reset.md)
Decisions 1–5; Gherkin to be locked under Plan approval.

## AI planning record (size M)

- Status: proposed, pre-Plan-approval
- Authoring environment: Cursor (Grok 4.5), 2026-08-09
- Size: `M` — demand inference rules + diagnostics; bounded by Accepted
  ADR; no new keyword.
- Route: AT-TDD after Plan + Phase approvals.
- Assumptions: first slice needs no new QSem Region type.
- Confidence: medium-high — inference triggers from source forms need Plan
  lock (what counts as a reuse demand without `reset` syntax).
- Revision links: none yet.

## Exit criteria

- [ ] Plan approval + Gherkin locked (especially: what source shapes set
      `needs_reuse` / `needs_reset` without Option B).
- [ ] Phase 1 Red / Phase 2 Green / Phase 3 Refactor.
- [ ] Completion approval before merge.

## Adjudicator decision points (Plan)

1. Which source/IR patterns set `needs_reuse` vs `needs_reset` in the
   absence of a `reset` keyword (conservative: only explicit future
   annotations vs heuristic from post-measure apply).
2. Whether diagnostics are compile-time only, Fake-verify only, or both.
