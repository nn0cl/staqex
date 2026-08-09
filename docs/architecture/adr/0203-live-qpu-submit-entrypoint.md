# ADR 0203: Separate live QPU submit entrypoint (async, not `submit_source`)

## Status

**Accepted** (2026-08-10) — Architecture approval by the Adjudicator.
Resolves the design question surfaced while investigating how to wire
[ADR 0202](0202-aws-braket-provider-adapter.md)'s AWS Braket adapter into
Host submission: `submit_source` is structurally local-only and
synchronous; live QPU submission is fundamentally asynchronous. Recorded
as its own ADR rather than resolved inline, per this agent's Hard Stop
obligation when an unanticipated design decision surfaces. Acceptance
approves Decisions 1–4 below.

## Design check

- **Scope and expected behavior:** Define a Host entrypoint for
  submitting a compiled program through a live `QpuSubmitPort` adapter
  (ADR 0127/0083, concretely AWS Braket per ADR 0202) — separate from
  `submit_source`, which stays local-only.
- **Specifications and files inspected:** `compiler/staqex/host.py`
  `submit_source` (**confirmed by direct read**: docstring says "Submit
  source to the **local** adapter"; `job_id` is hardcoded
  `f"local-{uuid4().hex}"`; returns a `Job` wrapping a fully-computed,
  synchronous `JobResult` — the entire function is shaped around
  immediate local Joint evaluation, not queued external work);
  `compiler/staqex/qpu_submit.py` (`QpuSubmitPort.submit` already returns
  `ProviderJobId`, not a result — the existing port design already models
  submission as fire-and-forget, separate from `QpuJobPort.status/wait/result/cancel`);
  `compiler/staqex/backend/qasm/emitter.py` (`QASM3Emitter`, Static QPU
  QASM text source) and `compiler/staqex/backend/qasm/dynamic_emitter.py`
  (`emit_dynamic_qpu_qasm3`, ADR 0201, Dynamic-lane QASM text source) —
  both already produce QASM3 text, the natural `QpuArtifact.qasm` payload
  for a live submit call.
- **Component boundaries, ports/adapters, VO/DTO candidates:** New Host
  function (candidate name `submit_live_qpu`, `compiler/staqex/host.py`
  or a new `compiler/staqex/live_submit.py` — exact module placement is
  Feature Issue detail) that: compiles source, emits QASM3 (Static or
  Dynamic-lane, selected by whether the unit has a `dynamic qpu` block),
  builds a `QpuArtifact`/`QpuSubmitRequest`, and calls an **injected**
  `QpuSubmitPort.submit(...)`. Returns `ProviderJobId` directly — never a
  `Job`/`JobResult`. No new port; reuses `QpuSubmitPort`/`QpuArtifact`/
  `QpuSubmitRequest`/`ProviderJobId` exactly as shipped.
- **Applicable constraints:** Must not change `submit_source`'s
  signature, return shape, or synchronous local behavior in any way —
  this ADR is purely additive. Must not claim a completed result:
  returning `ProviderJobId` (not `JobResult`) is itself the honesty
  mechanism — callers cannot mistake "submitted" for "finished" the way a
  `Job`-shaped return might invite. `physical_execution_claimed` is not a
  field this entrypoint sets at all (it lives on `DynamicTraceReport`,
  ADR 0198, a local-Fake-path concept) — a live submission's only claim
  is "a request was sent to the named provider adapter," which the
  `ProviderJobId.provider` field already states plainly.
- **Decisions, assumptions, unresolved ambiguities:** Exact module
  placement and whether Dynamic-lane vs. Static QASM selection is
  automatic (unit shape) or an explicit caller flag are Feature Issue
  detail, not resolved here (mirrors this session's repeated precedent of
  deferring exact code shape to Feature Path once the boundary is
  Accepted).
- **Included and omitted AI context:** Included direct reads of
  `submit_source`, `QpuSubmitPort`, and both QASM emitters. Omitted any
  polling/retry/backoff strategy for `QpuJobPort.wait` — that already
  exists as a separate port method and is unaffected by this ADR.
- **Task routing:** Architecture proposal; deterministic source
  inspection.
- **Evidence contract:** N/A — no AI runtime output.
- **Verification plan (after Accept + Feature Issue):** (a)
  `submit_source`/`submit_path` are byte-for-byte unaffected (no diff);
  (b) the new entrypoint returns `ProviderJobId`, never blocks waiting
  for a result, and never constructs a `JobResult`; (c) tests exercise
  only a fake `QpuSubmitPort`, never a real provider adapter — mirrors
  LISS-0392's own standing constraint.

## Context

ADR 0202 selected AWS Braket as a concrete `QpuSubmitPort` adapter. The
natural next question — "how does a physicist actually reach it from
`submit_source`" — turned out not to have a natural answer:
`submit_source` is local-only and synchronous by construction, while live
submission is fire-and-forget-then-poll. Forcing the two into one
function would either lie about synchronicity (blocking on a real queue,
possibly for a long time, inside what looks like a normal local call) or
force local evaluation to pretend to be async for no reason. Both are
worse than keeping them separate.

## Decision proposal

### 1. New, separate entrypoint — `submit_source` is untouched

A new Host function submits a compiled program through an injected
`QpuSubmitPort` and returns `ProviderJobId` immediately. `submit_source`
and `submit_path` keep their existing local-only, synchronous contract
exactly as shipped.

### 2. Returns `ProviderJobId`, never `Job`/`JobResult`

The return type itself is the honesty mechanism: a caller holding a
`ProviderJobId` cannot mistake it for a finished result. Fetching status
or a result is a **separate**, explicit call through `QpuJobPort`
(already shipped, unchanged).

### 3. QASM source reuses both existing emitters unchanged

The new entrypoint calls `QASM3Emitter.emit_unit` (Static QPU surface) or
`emit_dynamic_qpu_qasm3` (Dynamic-lane, ADR 0201) to build the
`QpuArtifact.qasm` payload — neither emitter changes.

### 4. Out of scope for this ADR

- Any specific polling/retry/backoff policy (already a `QpuJobPort`
  concern, unaffected).
- Cost/budget guardrails before submission — the user's own
  responsibility, per ADR 0202.
- Wiring a CLI/REPL command for this entrypoint (optional follow-up).

## Consequences

Positive:

- Closes the gap ADR 0202 left open without disturbing `submit_source`'s
  well-tested local contract at all.
- The async reality of live submission is honestly reflected in the
  return type, not hidden behind a synchronous-looking call.

Negative / residual open:

- Two Host submission entrypoints to document and teach (local
  synchronous vs. live async) instead of one — an accepted tradeoff, not
  resolved away.

## Rejected alternatives

### Add a `target="aws-braket"` branch inside `submit_source` itself

Rejected — `submit_source` is local-only by contract (docstring, hardcoded
`job_id` prefix, synchronous `JobResult` return); branching it into an
async external call would silently change its meaning for existing
callers and conflate two different execution models in one function
shape.

### Make `submit_source` itself async (return an awaitable)

Rejected — would force every existing local caller to adopt async
calling conventions for no benefit to the local (already synchronous,
already fast) path; the asynchrony belongs to live submission specifically,
not to `submit_source` generally.

## Follow-up work required after acceptance

1. Feature Path Issue: implement the new entrypoint, Red tests using a
   fake `QpuSubmitPort`, confirm `submit_source`/`submit_path` unaffected
   (no diff).

## Acceptance boundary

Acceptance of this ADR approves the **entrypoint shape and honesty
contract** in Decisions 1–4. It does not itself authorize implementation
— a Feature Path Issue is required. It does not authorize any real
submission by this agent (ADR 0202 Decision 5 continues to apply
unchanged).

## Dependency Adoption Evidence

N/A — no new external dependency; reuses ADR 0127/0083's shipped ports.
