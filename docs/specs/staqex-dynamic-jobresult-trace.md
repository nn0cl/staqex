# Staqex Dynamic JobResult `dynamic_trace` (ADR 0198 / LISS-0384)

| Field | Value |
|---|---|
| Status | **Host DTO shipped** (LISS-0384 Phase 3); Fake-exec wire still gated (LISS-0383) |
| Decision | [ADR 0198](../architecture/adr/0198-dynamic-jobresult-composition.md) (**Accepted**) |
| Issue | [LISS-0384](../issues/LISS-0384-dynamic-jobresult-trace.md) |

Normative Host acceptance scenarios for Phase 1–3 on LISS-0384. Assertions
must match these `Then` clauses exactly.

## Plan-locked shape

- Additive field on `JobResult`: **`dynamic_trace`**
- Type: **`DynamicTraceReport | None`**, default **`None`** (Static-only
  Jobs).
- Placement: **trailing field after `observations`** (LISS-0046 additive
  precedent — do not reorder older positional fields).
- Nested carrier: single frozen dataclass **`DynamicTraceReport`** with at
  least: `lane`, `profile_id`, `controller_bindings` (immutable mapping),
  `consumed_token_ids`, `selected_arm`, `physical_execution_claimed`.
  Exact optional extras may mirror LISS-0077 `DynamicExecResult` fields
  without importing Semantic IR builders into Host.
- Mid-circuit Controllers / tokens must **never** appear as
  `MeasurementEnvelope` entries in `measurements`.

## Acceptance scenarios

```gherkin
Feature: Host JobResult dynamic_trace channel (ADR 0198)

  Scenario: Static-only Job leaves dynamic_trace unset
    Given a completed local Job for a Static Kernel program with terminal measure
    When the caller reads JobResult
    Then dynamic_trace is None
    And measurements contain the terminal MeasurementEnvelope as today
    And observations behavior is unchanged

  Scenario: Dynamic Fake report does not pollute measurements
    Given a DynamicExecResult from FakeDynamicExecutor under supplied outcomes
      with physical_execution_claimed False and non-empty controller bindings
    When it is projected into JobResult.dynamic_trace
    Then dynamic_trace is a DynamicTraceReport carrying those bindings
    And dynamic_trace.physical_execution_claimed is False
    And no MeasurementEnvelope is synthesized solely from those controllers

  Scenario: Sibling channels when Static terminal measure coexists
    Given a JobResult that carries both a Static terminal MeasurementEnvelope
      and a DynamicTraceReport
    When the caller inspects measurements and dynamic_trace
    Then both channels are present as siblings
    And dynamic_trace content is not copied into measurements

  Scenario: Positional construction of pre-observation fields remains valid
    Given existing callers that construct JobResult with positional arguments
      for status, measurements, diagnostics, metadata, and observations
    When dynamic_trace is added as a trailing keyword/default field
    Then those positional constructions remain valid
```

## Boundary contract

- `JobResult` remains a Host DTO; no Joint / AST / provider SDK leakage.
- LISS-0383 may ship Fake-exec returning `DynamicExecResult` first without
  waiting for this Issue's Green; projection into `dynamic_trace` may be
  the same Issue or a follow-on slice under Plan.
- WorkflowReport / CLI display remain out of scope for LISS-0384.
