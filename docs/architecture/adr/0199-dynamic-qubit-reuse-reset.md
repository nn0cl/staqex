# ADR 0199: Dynamic-lane qubit reuse and reset model

## Status

**Accepted** (2026-08-09) — Architecture approval by the Adjudicator.
Implements [ADR 0197](0197-dynamic-mid-circuit-feed-forward.md) Follow-up #3
and the remaining reuse portion of [LISS-0028](../../issues/LISS-0028-dynamic-qpu-lane.md)'s
"Timing, qubit reuse, controller values, and JobResult composition"
acceptance item (timing already shipped via ADR 0193 / LISS-0381;
controllers via ADR 0197 / LISS-0382). Acceptance approves Decisions 1–5
below with **Option B declined at original Accept** (no new `reset`
keyword) — **superseded by the 2026-08-10 Amendment below**, which adds
the `reset` keyword. It does **not** by itself authorize Kernel
implementation — see "Acceptance boundary" and "Follow-up work required".

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

## Amendment (Accepted, 2026-08-10): `reset` keyword (Option B, revisited)

**Status: Accepted** — Architecture approval by the Adjudicator.
Revises Decision 3 (no new surface keyword) only; Decisions 1–2 / 4–5 are
**not** reopened, per this ADR's own Follow-up item 4. Does not itself
authorize Kernel implementation — a Feature Path Issue is required
separately.

### Design check

- **Scope and expected behavior:** Decision 3 declined a new `reset`
  keyword because, at the time, no profile could honestly exercise it —
  the Dynamic lane had no real Kernel execution at all. That blocker is
  now resolved: [ADR 0200](0200-dynamic-lane-real-kernel-execution.md) /
  [LISS-0387](../../issues/LISS-0387-dynamic-real-mid-circuit-measure.md)
  shipped real mid-circuit execution, and
  [LISS-0388](../../issues/LISS-0388-dynamic-reuse-capability-followup2.md)
  already repurposed the reuse side of the same capability law for
  simulator-class profiles. This Amendment does the same for reset,
  **and** adds the honest surface spelling Decision 3 withheld — per the
  Adjudicator's direction (2026-08-10): a language must let physicists
  write the straightforward form; declining to implement something
  because it is only reachable through a clever combination of existing
  constructs is the wrong call, and repurposing existing syntax to avoid
  a new keyword is worse than adding one when the physics genuinely
  differs.
- **Specifications and files inspected:** this ADR's original Decisions
  1–5 and Rejected Alternatives (Option B); ADR 0200 Decisions 1–3;
  `compiler/staqex/runtime/joint.py` (`Joint.trace_out` — Born partial
  trace, already shipped, ADR 0173 lineage); `compiler/staqex/runtime/evaluator.py`
  `_run_dynamic_qpu_block` (LISS-0387) and `_bind_names`'s `KetLit`
  preparation path (`state x = |0>`); `hir.py`
  `_verify_static_uncompute_bind` / `_require_uncompute_zero`
  (LISS-0114 F) — **confirmed by direct read** that the Static Kernel's
  existing same-name `state q = |0>` idiom means "verify this wire is
  already computationally |0⟩" (an assertion), not "force it to |0⟩
  regardless of current state" (an operation). Reusing that spelling for
  Dynamic-lane reset would make identical source mean two different
  physics depending on lane — rejected below as a candidate, in favor of
  a distinct keyword. `ast_nodes.py` `MatchStmt` (`"match is a contextual
  soft keyword (not a global hard keyword)"` — precedent this Amendment
  follows for `reset`); grep confirmed no existing `reset` identifier
  usage in `examples/` or `compiler/staqex/stdlib/` (low collision risk
  even as a hard keyword, though contextual is still preferred for
  lane-locality, matching `match`).
- **Component boundaries, ports/adapters, VO/DTO candidates:** Language
  surface (new `reset wire` statement, dynamic-lane-local) + Kernel
  evaluator (reuses `Joint.trace_out` + the existing `KetLit` |0⟩
  preparation path — no new Joint primitive) + `hir.py` linear-use
  extension + `dynamic_capability.py` inference + `dynamic_qpu.py`
  capability law. No new port, no provider SDK, no JobResult DTO change.
- **Applicable constraints:** Static Kernel NLTS / terminal `measure`
  unaffected — `reset` is rejected outside `dynamic qpu`, mirroring
  mid-circuit `measure`'s lane restriction (ADR 0197 Decision 1). No
  revival of `observe` / method-chain / classical `branch` (ADR 0193,
  still standing). `physical_execution_claimed` stays `False` for every
  profile this Amendment covers — this is local-simulator honesty, not a
  live-hardware claim.
- **Decisions, assumptions, unresolved ambiguities:** Exact diagnostic
  code names and whether `reset` is a hard vs. contextual keyword are
  Feature Issue Plan detail once the meaning below is Accepted (following
  ADR 0197's own precedent of leaving exact AST/diagnostic naming to
  Feature Path). The recommendation below is contextual (matching `match`
  precedent), not resolved as binding here.
- **Included and omitted AI context:** Included direct reads of
  `joint.py`, `evaluator.py`'s LISS-0387 additions, `hir.py`'s uncompute
  witness code, and `ast_nodes.py`'s `MatchStmt` docstring. Omitted live
  provider reset pulse schedules (still out of scope, per this ADR's
  original Decision 6 / Out of scope list).
- **Task routing:** Architecture proposal; deterministic source
  inspection.
- **Evidence contract:** N/A — no AI runtime output.
- **Verification plan (after Accept + Feature Issue):** (a) `reset wire`
  outside `dynamic qpu` fails closed with a stable diagnostic, Static
  Kernel behavior unaffected; (b) inside `dynamic qpu`, `reset wire`
  genuinely reinitializes the wire (observable the same way LISS-0387
  proved real collapse: at the Evaluator/Joint boundary, since the wire
  stays block-local); (c) after `reset`, the wire is usable again exactly
  as if freshly introduced (no spurious `LINEAR_DUPLICATE_USE` /
  `LINEAR_IMPLICIT_DISCARD`); (d) `needs_reset` is inferred from source
  (a `ResetStmt` in the block) and no longer rejected on simulator-class
  profiles, symmetric to LISS-0388's reuse treatment.

### Proposed decision (revises Decision 3 only)

1. **New contextual keyword `reset`,** lane-local to `dynamic qpu` (same
   precedent as `match` — not a globally reserved word). Statement form:
   `reset wire` — bare, no binding, since reset produces no classical
   outcome to feed forward (unlike `measure`, which requires
   `Controller<T> c = measure wire`). `wire` must reference a quantum
   wire already introduced earlier in the same `dynamic qpu` block
   (mirrors mid-circuit `measure`'s existing wire-scoping rule).
2. **Kernel meaning:** `reset wire` performs `Joint.trace_out(wire)`
   followed by re-preparing `wire` as `|0⟩` in the same joint — reusing
   the two already-shipped primitives LISS-0387 and ADR 0173 already
   established, not new Joint math. This is a genuinely different
   operation from the Static Kernel's same-name `state x = |0>` idiom
   (verification, LISS-0114 F) — the two are not unified, by design,
   because they denote different physics (see Design check above).
3. **Linear-use law (`hir.py`):** after `reset wire` inside the
   dynamic-lane nested scope, `wire` is treated as freshly introduced
   again (equivalent to a new `state wire = |0>`) — any prior
   "dynamically measured" marking (LISS-0387 Decision 4) is cleared, and
   later statements in the same block may measure/reuse/reset it again
   validly.
4. **Capability law repurposed, symmetric to LISS-0388:** `needs_reset`
   is inferred from source (presence of a `ResetStmt` in the block) and
   is **no longer** unconditionally rejected on simulator-class profiles
   (`SIM0_EXACT`, `CH1_DIGITAL_RESEARCH`) — a real local simulator has no
   physical constraint against trace-out-then-reprepare either, the same
   reasoning LISS-0388 already applied to reuse. `needs_reset` remains
   available as a capability-law hook for any future
   hardware-constrained or live profile that genuinely cannot perform
   fast mid-circuit reset.
5. **Out of scope for this Amendment:** OpenQASM `reset` emission; live
   provider reset pulse schedules; any change to `measure` / `match` /
   the mid-circuit `Controller` model; any change to Static Kernel
   `state x = |0>` semantics.

### Rejected alternative (this session)

**Reuse the existing `state wire = |0>` same-name idiom instead of a new
keyword.** Rejected — confirmed by direct code read that this idiom
already means "verify uncompute to zero" (LISS-0114 F) in the Static
Kernel; overloading it for Dynamic-lane "force reset" would make
identical source denote two different physics depending on lane,
violating vision §2.2 more than adding a distinct keyword would. The
Adjudicator explicitly directed against this kind of surface-avoidance
repurposing (2026-08-10).

### Amendment acceptance boundary

Accepting this Amendment approves the **grammar and Kernel meaning**
above (points 1–5). It does not itself authorize Kernel Red — a Feature
Path Issue is required, per this ADR's own process.
