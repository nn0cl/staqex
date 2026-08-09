# LISS-0384: Additive `JobResult.dynamic_trace` for Dynamic QPU runs (ADR 0198)

## Metadata

- Local issue ID: LISS-0384
- Status/phase: **proposed** / `phase-0-design` — awaiting Plan approval
  (Architecture Accept of ADR 0198 done 2026-08-09; no Red until Plan)
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
- Related: [LISS-0383](LISS-0383-dynamic-fake-executor-wire.md) (Fake-exec
  Plan — may soft-depend on this Issue for JobResult projection);
  [LISS-0028](LISS-0028-dynamic-qpu-lane.md)
- Blocks: none strictly (Fake-exec can ship `DynamicExecResult`-only first)
- Branch: TBD at Plan approval
- GitHub Issue / PR: none yet

## Intent

Implement ADR 0198 Decisions 1–4 on the Host boundary:

1. Mid-circuit Controllers / tokens must **not** appear as
   `JobResult.measurements` / `MeasurementEnvelope`.
2. Add additive field **`dynamic_trace`** (last-field / keyword-friendly)
   carrying structured dynamic-run report data.
3. Sibling composition with Static terminal `measurements` when both exist.
4. Preserve `physical_execution_claimed` honesty for Fake.

## Explicitly out of scope

- FakeDynamicExecutor AST wire (LISS-0383) unless Plan merges a thin
  projection-only slice.
- Qubit reuse/reset (ADR 0199).
- WorkflowReport / CLI pretty-print (optional follow-up).
- Live provider result mapping.
- Removing `DYNAMIC_*` compile rejection.

## Acceptance reference

[ADR 0198](../architecture/adr/0198-dynamic-jobresult-composition.md)
Decisions 1–4; Gherkin to be added under Plan approval (Host-facing
scenarios: Static-only unchanged; Fake/dynamic report on `dynamic_trace`
only; sibling channels).

## AI planning record (size M)

- Status: proposed, pre-Plan-approval
- Authoring environment: Cursor (Grok 4.5), 2026-08-09
- Size: `M` — Host DTO + projection + Red tests; bounded by Accepted ADR;
  no language surface change.
- Route: AT-TDD after Plan + Phase approvals.
- Assumptions: nested report DTO can mirror LISS-0077 fields without
  importing Semantic IR builders into Host.
- Confidence: high on separation law; medium on exact nested type shape.
- Revision links: none yet.

## Exit criteria

- [ ] Plan approval + Host Gherkin locked.
- [ ] Phase 1 Red / Phase 2 Green / Phase 3 Refactor.
- [ ] Completion approval before merge.

## Adjudicator decision points (Plan)

1. Nested type name(s) for `dynamic_trace` payload (single frozen dataclass
   vs tuple of smaller reports).
2. Whether LISS-0383 Plan must wait for this Issue's Green before claiming
   JobResult completeness, or may ship Fake-only first.
