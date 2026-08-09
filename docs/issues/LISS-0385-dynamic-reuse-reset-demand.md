# LISS-0385: Dynamic reuse/reset capability demand inference (ADR 0199)

## Metadata

- Local issue ID: LISS-0385
- Status/phase: **complete** (2026-08-09) — Adjudicator Continuation /
  Completion; PR pending on branch
  `feature/liss-0383-0385-fake-demand-green`
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
- Related: [LISS-0383](LISS-0383-dynamic-fake-executor-wire.md); [LISS-0028](LISS-0028-dynamic-qpu-lane.md)
- Blocks: none (profile-enable Issue is separate)
- Branch: `feature/liss-0383-0385-fake-demand-green`
- GitHub Issue / PR: (fill after `gh pr create`)

## Intent

Implement ADR 0199 Decisions 1–5 boundary: infer `needs_reuse` /
`needs_reset` honestly without a `reset` keyword, and fail closed on P0
profiles.

## Explicitly out of scope

- Lane-local `reset q` surface (future Architecture Accept).
- Enabling Fake profiles that actually perform reset/reuse.
- Fake-exec AST wire beyond coordination (LISS-0383).
- JobResult `dynamic_trace` (LISS-0384 complete).
- OpenQASM `reset` emission; live provider.

## Plan-locked decisions (Adjudicator 2026-08-09)

1. **`needs_reset`:** never auto-inferred from source in this Issue.
2. **`needs_reuse`:** inferred when a mid-circuit-measured wire is later
   used as a quantum target in the same `dynamic qpu` block (including
   inside `match` arms). Measure alone / match without further ops on that
   wire → `needs_reuse=false`.
3. **`within`:** does not set reuse/reset demands.
4. **Diagnostics:** both compile-time (when inferred demand meets
   unsupported profile / P0 path) and Fake-verify (`DYN_CAPABILITY_*`).

## Acceptance reference

[`staqex-dynamic-qpu-lane.md`](../specs/staqex-dynamic-qpu-lane.md)
§ "Acceptance scenarios — reuse/reset demand inference (… LISS-0385)".

## AI planning record (size M)

- Status: Plan approved; awaiting Phase 1 Red
- Authoring environment: Cursor (Grok 4.5), 2026-08-09
- Size: `M` — demand inference + diagnostics; no new keyword.
- Route: AT-TDD after Phase 1 Red approval.
- Confidence: high after Plan lock.
- Revision links: none yet.

## Exit criteria

- [x] Plan approval + Gherkin locked.
- [x] Phase 1 Red: `tests/test_liss_0385_dynamic_reuse_reset_demand_red.py`
      (**collection ImportError**, 2026-08-09): missing
      `compiler.staqex.dynamic_capability.infer_dynamic_capability_demand`.
- [x] Phase 2 Green / Phase 3 light Refactor (2026-08-09):
      `dynamic_capability.infer_dynamic_capability_demand` + soft compile
      `DYN_CAPABILITY_REUSE` via `reuse_demand_diagnostics`.
- [x] Completion approval (2026-08-09 Continuation); regression 1372 passed.
