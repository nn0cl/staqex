# LISS-0384: Additive `JobResult.dynamic_trace` for Dynamic QPU runs (ADR 0198)

## Metadata

- Local issue ID: LISS-0384
- Status/phase: **complete** (2026-08-09) — Adjudicator Completion
  approved; PR pending
- Type: Feature Path (Host DTO — additive `JobResult.dynamic_trace`;
  projection from `DynamicExecResult` / Fake path)
- Priority: P1
- Initial planning size: `M`
- Current planning size: `M`
- Owner / agent: Cursor (Grok)
- Program: [ADR 0198](../architecture/adr/0198-dynamic-jobresult-composition.md)
  Follow-up item 1
- Parent: [ADR 0198](../architecture/adr/0198-dynamic-jobresult-composition.md)
  (**Accepted** 2026-08-09)
- Depends on: ADR 0198 (Accepted); LISS-0022 / LISS-0046 Host JobResult
  additive precedent; LISS-0077 `DynamicExecResult` vocabulary
- Related: [LISS-0383](LISS-0383-dynamic-fake-executor-wire.md) (may ship
  Fake-only first); [LISS-0028](LISS-0028-dynamic-qpu-lane.md)
- Blocks: none strictly
- Branch: `feature/liss-0384-dynamic-jobresult-trace`
- GitHub Issue / PR: pending (this Completion)

## Intent

Implement ADR 0198 Decisions 1–4 on the Host boundary:

1. Mid-circuit Controllers / tokens must **not** appear as
   `JobResult.measurements` / `MeasurementEnvelope`.
2. Add additive field **`dynamic_trace`** (trailing after `observations`)
   typed as **`DynamicTraceReport | None`**.
3. Sibling composition with Static terminal `measurements` when both exist.
4. Preserve `physical_execution_claimed` honesty for Fake.

## Explicitly out of scope

- FakeDynamicExecutor AST wire (LISS-0383) unless a thin projection-only
  helper is needed for Red fixtures.
- Qubit reuse/reset (ADR 0199 / LISS-0385).
- WorkflowReport / CLI pretty-print.
- Live provider result mapping.
- Removing `DYNAMIC_*` compile rejection.

## Acceptance reference

[`staqex-dynamic-jobresult-trace.md`](../specs/staqex-dynamic-jobresult-trace.md)
(Plan-locked 2026-08-09).

## Plan-locked decisions (Adjudicator 2026-08-09)

1. **Nested type:** single frozen dataclass `DynamicTraceReport` (not a
   bare tuple of ad-hoc reports).
2. **LISS-0383:** may ship Fake-only (`DynamicExecResult`) first; need not
   wait for this Issue's Green before Plan/Red on Fake wire.
3. **Default for Static Jobs:** `dynamic_trace is None`.

## AI planning record (size M)

- Status: **complete** (Completion approved 2026-08-09)
- Authoring environment: Cursor (Grok 4.5), 2026-08-09
- Size: `M` — Host DTO + projection helper + Red tests; no language surface
  change.
- Route: AT-TDD Phase 1 Red after explicit phase approval.
- Assumptions: projection helper can live beside `host.py` / Fake module
  without Semantic IR imports.
- Confidence: high after Plan lock.
- Revision links: none yet.

## Exit criteria

- [x] Plan approval + Host Gherkin locked.
- [x] Phase 1 Red: failing tests for Plan-locked scenarios.
      File: `tests/test_liss_0384_dynamic_jobresult_trace_red.py`
      (expected Red: missing `DynamicTraceReport` /
      `project_dynamic_trace` / `JobResult.dynamic_trace`).
- [x] Phase 2 Green: Host DTO + `project_dynamic_trace`; Red tests pass
      without editing assertions (2026-08-09).
- [x] Phase 3 Refactor: immutable `MappingProxyType` bindings; module
      docstring; spec status sync. Behavior unchanged.
      Full suite (2026-08-09): `.venv/bin/pytest tests/` → **1366 passed**.
- [x] Completion approval before merge (Adjudicator 2026-08-09).
