# ADR 0198: JobResult composition for Dynamic QPU runs

## Status

**Accepted** (2026-08-09) — Architecture approval by the Adjudicator.
Implements [ADR 0197](0197-dynamic-mid-circuit-feed-forward.md) Follow-up #2 /
Decision 5 principle. Acceptance approves Decisions 1–4 below; it does
**not** by itself authorize Host or Kernel implementation — see
"Acceptance boundary" and "Follow-up work required".

## Design check

- **Scope and expected behavior:** Specify how Host `JobResult` (and related
  Host DTOs) compose outcomes of a **Dynamic QPU lane** run so that
  mid-circuit `Controller` / outcome tokens are never silently treated as
  Static terminal `measure` payloads, while remaining compatible with the
  existing additive `JobResult` shape (LISS-0022 / LISS-0046 / ADR 0091).
- **Specifications and files inspected:** ADR 0197 Decision 5; LISS-0028
  remaining JobResult item; `compiler/staqex/host.py` (`JobResult`,
  `MeasurementEnvelope`); LISS-0046 / ADR 0091 observation integration;
  LISS-0066 QPU observation projector; `compiler/staqex/dynamic_qpu.py`
  (`DynamicExecResult`, `physical_execution_claimed`); vision §2.2 / §3.1;
  ADR 0071 fail-closed Host honesty.
- **Component boundaries, ports/adapters, VO/DTO candidates:** Host DTO /
  Job boundary only. Accepted preferred additive field name:
  `dynamic_trace` (immutable structured report, **not** folded into
  `measurements`). Nested report DTO shape is Feature Issue Plan detail.
  No new provider SDK. No Fake-exec wire in this ADR (Follow-up #4 /
  LISS-0383).
- **Applicable constraints:** Additive DTO evolution (positional
  constructors for pre-observation fields remain stable — LISS-0046
  precedent). Mid-circuit tokens ≠ terminal measurement envelopes
  (ADR 0197 Decision 5). Fake / live paths must not claim physical
  feed-forward unless an accepted live-provider ADR says so. Static Kernel
  JobResult behavior for ordinary `measure` unchanged.
- **Decisions, assumptions, unresolved ambiguities:** Nested DTO types and
  CLI/WorkflowReport display remain Feature Issue / follow-up. WorkflowReport
  redesign is deferred. Field name preference locked at Accept:
  `dynamic_trace`.
- **Included and omitted AI context:** Included Host DTO and ADR 0197/0028
  reads. Omitted vendor result schemas, Braket/IBM payloads, credential
  ports beyond existing CredentialPort honesty.
- **Task routing:** Architecture review; deterministic DTO inspection.
- **Evidence contract:** N/A — no AI runtime output.
- **Verification plan (after Accept + Feature Issue):** (a) Static programs
  still populate only `measurements` / `observations` as today; (b) Fake
  dynamic runs expose mid-circuit bindings via the new additive channel,
  never as silent `MeasurementEnvelope` substitutes; (c)
  `physical_execution_claimed` / metadata honesty preserved; (d) positional
  `JobResult` construction remains compatible.

## Context

ADR 0197 Accepted mid-circuit / feed-forward **language meaning** and Kernel
IR witnesses (LISS-0382 complete). Decision 5 only stated a principle:

> Mid-circuit `Controller` bindings and outcome tokens are **not** the same
> object as Static terminal `measure` payloads on `JobResult`.

Today's Host surface (`JobResult`) has:

- `measurements: tuple[MeasurementEnvelope, …]` — terminal collapse report;
- additive `observations: tuple[ObservationReport, …]` (LISS-0046);
- `diagnostics`, `metadata`, `status`.

LISS-0077's `DynamicExecResult` already carries controller bindings and
`physical_execution_claimed=False` for Fake-supplied outcomes, but it is
**not** wired into `Job` / `JobResult`. Without an Architecture decision,
Feature Path cannot decide whether Fake-exec (LISS-0383) should invent a
JobResult shape, overload `measurements`, or keep results only on a
side-channel DTO.

## Decision proposal

### 1. Separation law (normative)

Mid-circuit `Controller<T>` values, `OutcomeToken`s, and match/merge
correlation records **must not** be written into
`JobResult.measurements` as if they were Static terminal `measure`
envelopes.

Terminal `MeasurementEnvelope` remains the Host report for **terminal**
collapse (Static `measure`, or an explicitly designated dynamic-lane
terminal outcome if a future Accept adds one — not invented here).

### 2. Additive Host channel `dynamic_trace` (Accepted)

Extend `JobResult` with an **additive** immutable field named
**`dynamic_trace`** that carries a structured dynamic run report, for
example:

- lane id / profile id;
- controller bindings (name → classical tag);
- consumed outcome token ids;
- selected match arms / merge satisfaction summary;
- capability demand echoes and related diagnostics already mirrored in
  `diagnostics` when useful;
- `physical_execution_claimed: bool` (must remain `False` for Fake).

Nested report type(s) are Feature Issue Plan detail under
[LISS-0384](../../issues/LISS-0384-dynamic-jobresult-trace.md). Prefer
**additive last-field** placement so existing positional construction of
pre-observation fields stays compatible (LISS-0046 precedent). Keyword-only
adoption is acceptable for the new field.

### 3. Composition with Static terminal measure in the same program

When a program contains both `dynamic qpu { … }` and a later Static
terminal `measure`, a completed Job **may** populate:

- the additive dynamic report from the dynamic region; and
- `measurements` from the Static terminal measure;

as **sibling** channels. Dynamic mid-circuit data must not replace or
shadow the terminal envelope.

Until Fake-exec / Host wiring Issues are approved, compile-time capability
rejection may still prevent any Job from running such programs — this ADR
defines the **envelope meaning**, not execution authorization.

### 4. Metadata honesty

`JobResult.metadata` may record lane/profile keys for Host tooling, but
must not be the sole structured home for controller bindings if that would
encourage ad-hoc string protocols. Prefer the typed `dynamic_trace` field.

### 5. Out of scope for this ADR

- Removing `DYNAMIC_*` rejection or wiring FakeDynamicExecutor (LISS-0383).
- Qubit reuse/reset full model (ADR 0199).
- Live provider result schema mapping (LISS-0100 lineage).
- WorkflowReport redesign; ObservationReport substitution for controllers.
- Changing Static NLTS or mid-circuit surface spelling (ADR 0197).

## Consequences

Positive:

- Feature Path (Fake-exec / Host submit) has a non-guessable JobResult law.
- Physicist-facing honesty: mid-circuit classical tags are not mislabeled as
  terminal measurement.

Negative / residual open:

- Nested `dynamic_trace` DTO types and projection from `DynamicExecResult`
  remain Feature Issue detail ([LISS-0384](../../issues/LISS-0384-dynamic-jobresult-trace.md)).
- WorkflowReport / CLI pretty-print of the new channel is follow-up.

## Rejected alternatives

### Fold Controllers into `measurements`

Rejected — violates ADR 0197 Decision 5; confuses terminal collapse with
feed-forward tags.

### Overload `observations` for Controllers

Rejected — observations are LISS-0044/0046 checkpoint reports, not dynamic
match tokens; would overload two different Host meanings.

### Redesign JobResult from scratch

Rejected — breaks LISS-0022/0046 additive contract without necessity.

## Follow-up work required after acceptance

1. Feature Path Local Issue: additive Host DTO `dynamic_trace` + projection
   from `DynamicExecResult` (or Fake path) into `JobResult`, with Red tests
   for separation from `measurements`.
   **Filed:**
   [LISS-0384](../../issues/LISS-0384-dynamic-jobresult-trace.md)
   (awaiting Plan approval; no Red yet).
2. Coordinate with [LISS-0383](../../issues/LISS-0383-dynamic-fake-executor-wire.md)
   so Fake-exec Plan either projects into `dynamic_trace` or keeps
   `DynamicExecResult`-only until LISS-0384 lands.
3. Optional CLI/REPL display Issue for the additive channel.

## Acceptance boundary

Acceptance of this ADR approves the **Host composition law** (Decisions
1–4). It does **not** authorize implementation, Fake-exec, live QPU submit,
or removal of dynamic-lane capability rejection.

## Dependency Adoption Evidence

N/A — no new external dependency.
