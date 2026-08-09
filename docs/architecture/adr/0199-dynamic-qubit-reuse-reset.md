# ADR 0199: Dynamic-lane qubit reuse and reset model

## Status

**Accepted** (2026-08-09) — Architecture approval by the Adjudicator.
Implements [ADR 0197](0197-dynamic-mid-circuit-feed-forward.md) Follow-up #3
and the remaining reuse portion of [LISS-0028](../../issues/LISS-0028-dynamic-qpu-lane.md)'s
"Timing, qubit reuse, controller values, and JobResult composition"
acceptance item (timing already shipped via ADR 0193 / LISS-0381;
controllers via ADR 0197 / LISS-0382). Acceptance approves Decisions 1–5
below with **Option B declined** (no new `reset` keyword in this Accept).
It does **not** by itself authorize Kernel implementation — see
"Acceptance boundary" and "Follow-up work required".

## Design check

- **Scope and expected behavior:** Define language **meaning** and capability
  law for mid-circuit qubit **reset** and **reuse** after dynamic-lane
  measurement/feed-forward, without inventing silent Host emulation, without
  weakening Static NLTS, and without claiming physical execution.
- **Specifications and files inspected:** ADR 0197 Decisions 1, 6–7;
  LISS-0028; LISS-0077 / `dynamic_qpu.py` (`DynamicCapabilityDemand.needs_reset`
  / `needs_reuse`, P0 feedback-only profiles reject on demand);
  ADR 0193 timing intent (orthogonal opaque `within`); vision §2.2 / §3.1;
  ADR 0071 fail-closed.
- **Component boundaries, ports/adapters, VO/DTO candidates:** Language
  surface meaning + capability demand vocabulary (align with existing Fake
  DTO flags). First Kernel slice: demand flags + stable diagnostics suffice;
  a distinct QSem Region is **not** required by this Accept (optional later).
- **Applicable constraints:** P0 Fake profiles today reject reset/reuse
  demands. No Host silent re-initialization of wires. Physicist-first:
  reuse/reset must read as physics operations (or explicit capability
  gaps), not as hidden allocator tricks. Timing-intent vocabulary remains
  ADR 0193 Follow-up #2 (closed names deferred).
- **Decisions locked at Accept:** Fail-closed capability law; reuse after
  mid-circuit measure is **not** automatic (`match` alone does not prepare
  the wire); **no new surface keyword** (Option B declined). Future
  blackboard `reset` spelling needs a separate Accept / Issue.
- **Included and omitted AI context:** Included Fake demand flags and
  ADR 0197/0028. Omitted vendor reset pulse schedules, OpenQASM `reset`
  emission details (LISS-0097-E), live provider quirks.
- **Task routing:** Architecture review; deterministic Fake module read.
- **Evidence contract:** N/A.
- **Verification plan (after Accept + Feature Issue):** (a) programs that
  demand reset/reuse against feedback-only profiles still fail closed with
  stable diagnostics; (b) Static programs gain no mid-program reset escape;
  (c) demand inference / diagnostics remain inspectable and not silently
  dropped.

## Context

After ADR 0197 / LISS-0382, mid-circuit measure and finite `match`
feed-forward have meaning and IR witnesses, but qubit **reuse after
measure** and explicit **reset** remain only as Fake capability **reject**
flags (`needs_reset`, `needs_reuse`) on P0 feedback-only profiles.

LISS-0028 still lists reuse under a partial acceptance bullet. Without an
Architecture decision, Feature Path must not invent:

- automatic wire recycling after `Controller = measure`;
- a new `reset` keyword or method-chain; or
- Host-side state scrubbing that pretends to be hardware reset.

## Decisions

### 1. Reuse/reset are Dynamic-lane capability demands, not Static escapes

Any qubit reset or post-measure reuse that would re-introduce a classical
or vacuum wire into continuing quantum narrative is **Dynamic-lane only**,
subject to the same lane + capability profile rules as ADR 0197 Decision 1.

Static Kernel programs must not gain mid-program reset/reuse as a way
around NLTS or terminal `measure`.

### 2. Fail-closed when the profile cannot provide the demand (normative)

If a dynamic program (or its lowered demand DTO) sets `needs_reset` or
`needs_reuse` and the selected profile does not advertise support, the
run **rejects** with stable diagnostics (existing LISS-0077 codes /
`DYNAMIC_*` family as applicable). Host must **not** silently emulate
reset/reuse (ADR 0071).

P0 Fake feedback-only profiles remain reject-on-demand until a later
Accept or Feature Issue extends a profile.

### 3. No new surface keyword (Accepted; Option B declined)

This Accept **does not** introduce a new hard keyword (e.g. `reset`) or
revive retired forms. Until a Fake/profile Issue is approved to **exercise**
supported reset/reuse:

- capability demand may be inferred from IR/lowering analysis or explicit
  future surface approved separately; and
- the absence of a physicist-facing reset spelling is an honesty gap
  recorded here, not permission to invent Host scrubbing.

**Option B (declined at this Accept):** lane-local `reset q` inside
`dynamic qpu`. A future Architecture Accept may revisit Option B without
reopening Decisions 1–2 / 4–5.

### 4. Timing intent remains orthogonal

`dynamic qpu within <name>` (ADR 0193) does **not** imply reset or reuse.
Latency windows (`needs_latency`) stay a separate demand flag; closed
timing-name vocabulary remains deferred.

### 5. Relation to mid-circuit measure

Mid-circuit `measure` (ADR 0197) produces a controller token and a
post-measure joint. **Reuse** of the measured wire for further gates is a
**distinct** demand from producing the token. Feed-forward `match` does not
by itself authorize treating the wire as freshly prepared.

### 6. Out of scope

- JobResult composition (ADR 0198 / LISS-0384).
- Fake-exec AST wire (LISS-0383) beyond preserving reject-on-demand.
- OpenQASM `reset` emission; live provider reset semantics.
- Closed timing-intent vocabulary (ADR 0193 Follow-up #2).

## Consequences

Positive:

- Reuse/reset cannot be silently invented during Fake-exec wiring.
- Aligns with shipped LISS-0077 demand flags.

Negative / residual open:

- Physicists still lack a writeable reset spelling until a future Option B
  Accept or surface Issue.
- Profile matrices for which targets support reset/reuse remain future
  adapter work.

## Rejected alternatives

### Silent Host re-init after mid-circuit measure

Rejected — ADR 0071; hides missing hardware capability.

### Static Kernel `reset` as NLTS workaround

Rejected — destroys Static terminal-measure law.

### Treat `within` timing names as implying reuse windows

Rejected — orthogonal concerns; timing names are still opaque (ADR 0193).

### Accept Option B (`reset q`) in this same Accept

Declined — keep capability law without new surface until a profile can
honestly exercise it; revisit as a separate Accept.

## Follow-up work required after acceptance

1. Feature Path Issue: diagnostics + demand inference without enabling
   unsupported profiles (no new `reset` keyword in that Issue's default
   Plan).
   **Filed / Plan approved:**
   [LISS-0385](../../issues/LISS-0385-dynamic-reuse-reset-demand.md)
   (2026-08-09; awaiting Phase 1 Red).
2. Optional profile extension Issue for Fake reset/reuse under supplied
   outcomes (`physical_execution_claimed=False`).
3. Coordinate with [LISS-0383](../../issues/LISS-0383-dynamic-fake-executor-wire.md)
   so Fake-exec retains reject-on-demand unless a profile Issue lands first.
4. Optional later Architecture Accept for Option B surface spelling.

## Acceptance boundary

Acceptance approves the **capability / lane law** (Decisions 1–5; Option B
declined). It does **not** authorize Kernel Red by itself, does not make
the dynamic lane executable, and does not select live QPU reset semantics.

## Dependency Adoption Evidence

N/A — no new external dependency.
