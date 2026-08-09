# LISS-0383: Wire Dynamic lane AST/QSem to FakeDynamicExecutor (supplied outcomes)

## Metadata

- Local issue ID: LISS-0383
- Status/phase: **complete** (2026-08-09) — Adjudicator Continuation /
  Completion; PR [#483](https://github.com/nn0cl/staqex/pull/483)
- Type: Feature Path (Kernel — Fake-exec wire under supplied outcomes;
  `physical_execution_claimed=False`)
- Priority: P1
- Initial planning size: `L`
- Current planning size: `L`
- Owner / agent: Cursor (Grok)
- Program: [ADR 0197](../architecture/adr/0197-dynamic-mid-circuit-feed-forward.md)
  Follow-up #4 / Decision 7 Option B lineage
- Parent: ADR 0197 (Accepted); Fake vocabulary [LISS-0077](../architecture/documentation-compression-map.md)
  (complete)
- Depends on: ADR 0197 / LISS-0382 (**complete**); LISS-0077 Fake module
  (shipped); [ADR 0198](../architecture/adr/0198-dynamic-jobresult-composition.md)
  / [LISS-0384](LISS-0384-dynamic-jobresult-trace.md) (**complete**) for
  `dynamic_trace` projection. Soft-depends on
  [ADR 0199](../architecture/adr/0199-dynamic-qubit-reuse-reset.md) /
  [LISS-0385](LISS-0385-dynamic-reuse-reset-demand.md) — retain P0
  reject-on-demand when Fake request carries demand; Host Fake AST builder
  does not yet auto-attach inferred reuse (0385 compile/infer separate).
- Related: LISS-0028; ADR 0071; `compiler/staqex/dynamic_qpu.py`;
  `compiler/staqex/dynamic_fake_wire.py`
- Blocks: live provider feed-forward; OpenQASM dynamic emission (still
  separate)
- Branch: `feature/liss-0383-0385-fake-demand-green`
- GitHub Issue / PR: [#483](https://github.com/nn0cl/staqex/pull/483)

## Intent

Connect **source-derived** dynamic mid-circuit / match programs (LISS-0382)
to `FakeDynamicExecutor` under **supplied outcomes**, project into
`JobResult.dynamic_trace`, without claiming physical execution.

## Explicitly out of scope

- Live QPU provider submit / credentials / network.
- OpenQASM dynamic emission.
- Enabling reset/reuse on Fake profiles (LISS-0385 + future profile Issue).
- Weakening Static NLTS; reviving `observe` / classical `branch`.

## Plan-locked decisions (Adjudicator 2026-08-09)

1. **Fake gate:** Host `settings["dynamic_fake_profile"]` ∈
   `{SIM0_EXACT, CH1_DIGITAL_RESEARCH}`. Absent/unknown → fail closed;
   compile/submit without gate keeps today's
   `DYNAMIC_CAPABILITY_REQUIRED_ERROR` /
   `DYNAMIC_UNSUPPORTED_FEATURE_ERROR`.
2. **Supplied outcomes:** `settings["dynamic_supplied_outcomes"]` map.
3. **JobResult:** same Issue projects accepted Fake results into
   `dynamic_trace` via `project_dynamic_trace` (LISS-0384).
4. **`DYNAMIC_*`:** retained when Fake gate absent; Fake success path does
   not claim physical execution and must not silent-emulate reset/reuse.

## Acceptance reference

[`staqex-dynamic-qpu-lane.md`](../specs/staqex-dynamic-qpu-lane.md)
§ "Acceptance scenarios — Fake-exec wire (… LISS-0383)".

## AI planning record (size L)

- Status: Plan approved; awaiting Phase 1 Red
- Authoring environment: Cursor (Grok 4.5), 2026-08-09
- Size: `L` — Host settings gate, AST/QSem → Fake request build, Fake exec,
  `dynamic_trace` projection, tests.
- Route: AT-TDD after Phase 1 Red approval.
- Confidence: high after Plan lock.
- Revision links: none yet.

## Exit criteria

- [x] Plan approval + Spec Gherkin locked.
- [x] Phase 1 Red: `tests/test_liss_0383_dynamic_fake_executor_wire_red.py`
      (**1 failed / 2 passed**, 2026-08-09): Fake-gated Host path fails;
      gate-absent reject and Fake `DYN_CAPABILITY_REUSE` already pass.
- [x] Phase 2 Green / Phase 3 light Refactor (2026-08-09): Host Fake gate +
      `dynamic_fake_wire` → `FakeDynamicExecutor` → `project_dynamic_trace`;
      evaluator skips `DynamicQpuStmt`.
- [x] Completion approval (2026-08-09 Continuation); regression 1372 passed.
