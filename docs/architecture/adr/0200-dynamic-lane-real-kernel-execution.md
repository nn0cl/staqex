# ADR 0200: Dynamic-lane real Kernel execution (mid-circuit collapse + reuse)

## Status

**Accepted** (2026-08-09) — Architecture approval by the Adjudicator.
Responds to the Adjudicator's root-cause direction (2026-08-09,
"根本解決をしていかないといつまでもパッチワークが続いている") on the Dynamic
QPU lane reuse/reset lineage (ADR 0197 / 0198 / 0199; LISS-0382–0386).
Acceptance approves Decisions 1–6 below (Kernel execution boundary and
physics reuse). It does **not** by itself authorize Kernel Red — see
"Acceptance boundary" and "Follow-up work required" below.

## Design check

- **Scope and expected behavior:** Decide whether and how the Dynamic QPU
  lane gains **real** Kernel execution for mid-circuit `measure` and
  post-measure wire reuse — i.e. the evaluator actually evolves state for a
  `dynamic qpu` block instead of unconditionally skipping it — so that
  reuse is genuine continued state evolution rather than a capability-flag
  bookkeeping decision layered on top of a block that never runs. Reset
  stays explicitly out of scope (see Decision 4).
- **Specifications and files inspected:**
  [`evaluator.py:369-371`](../../../compiler/staqex/runtime/evaluator.py)
  (`DynamicQpuStmt` unconditionally skipped — confirmed by direct read, not
  inference); `evaluator.py:4894-4933` (`_measure`: terminal-only, samples
  once via `RngPort`, does not project/continue the joint — matches NLTS);
  `runtime/joint.py:219-231` (`Joint.project_coord` — Lüders-style
  world-filter, **already shipped**); `evaluator.py:3960-4019` (`project(psi,
  k)` — existing Static-Kernel surface that already performs conditional
  collapse + renormalize via `project_coord`, precedent this ADR reuses
  rather than inventing new Joint math); ADR 0197 (mid-circuit meaning,
  Decision 2's "paired (OutcomeToken, post-measure Joint)" promise — shipped
  only as IR markers, never as evaluator behavior); ADR 0198 (JobResult
  `dynamic_trace`); ADR 0199 (capability demand law; Option B declined);
  LISS-0382/0383/0384/0385/0386 (all bookkeeping-layer, zero evaluator
  execution); `dynamic_fake_wire.py` `FAKE_BYPASS_HARD_CODES` comment
  (`LINEAR_IMPLICIT_DISCARD` bypassed because the Fake path never actually
  runs the block).
- **Component boundaries, ports/adapters, VO/DTO candidates:** Kernel
  evaluator (`runtime/evaluator.py`, `runtime/joint.py`) only. No new
  Host/QPU port; `RngPort` already exists and already backs terminal
  `measure`. No JobResult DTO shape change (ADR 0198 stays as accepted).
- **Applicable constraints:** Static Kernel NLTS/terminal-measure must not
  change (Decision 1 below is additive to the Dynamic lane only).
  `physical_execution_claimed` must remain `False` for every profile this
  ADR touches — "real execution" here means the **local simulator**
  genuinely evolves state, not that hardware is contacted (ADR 0071). No
  new surface keyword (ADR 0199 Decision 3 unchanged — reset stays out).
  Physicist-first: reuse must read as ordinary continued state evolution on
  a collapsed wire, not a hidden allocator trick (vision §2.2).
- **Decisions, assumptions, unresolved ambiguities:** The central
  assumption requiring Adjudicator confirmation is Decision 3 below — once
  a profile genuinely simulates state, there is no physical constraint left
  to justify rejecting reuse on that profile, which **repurposes** (not
  removes) the ADR 0199 / LISS-0385 / LISS-0386 reject-on-demand behavior
  for simulator-class profiles. This is a deliberate, named consequence,
  not a silent regression — flagged explicitly for sign-off before any
  Feature Issue touches those tests again.
- **Included and omitted AI context:** Included direct reads of the four
  files above (evaluator, joint, ADR 0197/0198/0199, LISS-0382-0386).
  Omitted: live QPU provider semantics, OpenQASM dynamic emission, vendor
  reset pulse schedules — all remain separately deferred.
- **Task routing:** Architecture proposal; deterministic source inspection.
  No external model call involved in reaching this proposal.
- **Evidence contract:** N/A — no AI runtime output evaluated.
- **Verification plan (after Accept + Feature Issue):** (a) Static Kernel
  `main` programs outside `dynamic qpu` are byte-for-byte unaffected
  (regression sweep); (b) a `dynamic qpu` program with mid-circuit `measure`
  under a supplied outcome produces a joint genuinely collapsed via
  `project_coord` + renormalize, not merely a label; (c) applying further
  gates to the measured wire inside a matching arm actually changes
  amplitudes (observable via a second measurement or JobResult trace),
  proving reuse is real, not bookkeeping; (d) `physical_execution_claimed`
  stays `False` throughout; (e) linear/Trace-Out GC accounting for the
  reused wire is genuine (no `LINEAR_IMPLICIT_DISCARD` bypass needed once
  the block actually executes).

## Context

ADR 0197 Decision 2 promised that dynamic-lane `measure` produces "an
`OutcomeToken` ... and a post-measure Joint state that remains in-lane for
further quantum ops" — real continued execution. What shipped instead
(LISS-0382 → LISS-0386) is IR-level meaning plus a Host/Fake **bookkeeping**
layer that:

- never executes a single statement inside `dynamic qpu` (evaluator skips
  the whole block unconditionally);
- represents "the program ran" entirely as caller-`supplied_outcomes` labels
  matched against a `MatchPlan`, with no amplitude ever touched;
- represents "reuse is unsupported" as a static reject-on-demand flag
  (`DynamicCapabilityDemand.needs_reuse`) computed by source-pattern
  matching (LISS-0385), wired into the same never-executing Host path
  (LISS-0383/0386).

Each of LISS-0383/0385/0386 individually closed an honesty gap in that
bookkeeping layer. None of them touched the fact that there is no execution
underneath it — the Adjudicator's "patchwork" diagnosis names exactly this:
the lane has grown paperwork around a void.

Separately, the Static Kernel already ships the primitive this needs: the
surface function `project(psi, k)` performs a genuine Lüders projection
(`Joint.project_coord` + renormalize) as an **explicit, non-terminal**
collapse a physicist can already write and reason about today. Dynamic-lane
mid-circuit `measure` is the same physics with a different surface spelling
and a Controller-typed classical carrier for the outcome — not a new kind of
collapse the Kernel has never modeled.

## Decisions

### 1. `dynamic qpu` blocks execute for real; Static Kernel is unaffected

The evaluator's unconditional `DynamicQpuStmt` skip
(`evaluator.py:369-371`) is replaced with genuine statement execution
**inside the dynamic lane only**. Static `main` bodies outside `dynamic
qpu` keep today's NLTS/terminal-measure behavior byte-for-byte; this
Decision adds a lane, it does not touch the Static evaluation path.

### 2. Mid-circuit `measure` is `project_coord` + renormalize, reusing existing Kernel physics

`Controller<T> c = measure w` inside `dynamic qpu` performs:

1. resolve the collapse outcome — either RNG-sampled via the existing
   `RngPort` (mirroring terminal `_measure`'s `sample_from_marginal`), or
   the Host-`supplied_outcomes` override when present (LISS-0077 honesty
   mode, unchanged contract);
2. `joint.project_coord(w, lambda v: v == outcome)` then renormalize —
   **the same operation** `project(psi, k)` already performs in the Static
   Kernel (`evaluator.py:3996`/`4011`), not new Joint math;
3. bind `c` to the outcome as a `Controller<T>` value (phase-local, cannot
   escape to Theory — ADR 0197 Decision 3, unchanged).

The resulting Joint is the real post-measure state and continues in the
lane.

### 3. Reuse is genuine continued evolution, not a capability flag, for simulator-class profiles

Once Decision 2 ships, further gates applied to `w` inside a `match` arm
(or after) run through the **normal** statement-evaluation loop against the
real post-measure Joint. This makes reuse structurally identical to
ordinary Joint evolution — there is no separate "reuse" operation to gate.

**Consequence (named, not silent):** `DynamicCapabilityDemand.needs_reuse`
reject-on-demand (ADR 0199 Decision 2; LISS-0385 inference; LISS-0386
auto-attach) no longer has a physical justification for **simulator-class**
profiles (`SIM0_EXACT`, and any future profile that is honestly a full local
state-vector simulator) — a real simulator has no hardware constraint
preventing it from continuing to evolve a collapsed wire. The reject-on-demand
law is **repurposed**, not deleted: it continues to apply to
**non-simulator** profile classes (e.g. a future constrained/hardware-modeled
profile tier, or live QPU) where a genuine physical limitation exists. This
ADR does not itself flip LISS-0383/0385/0386's tests — that happens in the
Feature Issue this ADR authorizes, with the Adjudicator's explicit awareness
that it revisits work completed under PR #483/#484.

### 4. Reset stays out of scope (unchanged from ADR 0199)

This ADR does not add a `reset` keyword or any other new surface spelling
(ADR 0199 Decision 3 stands). `needs_reset` remains never-inferred
(LISS-0385) and remains reject-on-demand on every profile. Re-preparing a
wire to a definite state after mid-circuit measure is a **future** Accept,
independent of this one.

### 5. Linear accounting must become real, not bypassed

`dynamic_fake_wire.py`'s `FAKE_BYPASS_HARD_CODES` currently bypasses
`LINEAR_IMPLICIT_DISCARD` because the block never actually runs. Once
Decision 1 ships, the reused/measured wire's linear lifecycle must be
accounted for genuinely by the same Trace-Out GC / linear-type machinery
Static Kernel already uses (ADR 0138/0142/0153/0158 lineage) — the bypass
is removed, not extended.

### 6. `physical_execution_claimed` stays `False`; no live-provider claim

Nothing in this ADR contacts hardware or claims physical execution (ADR
0071 unchanged). "Real execution" means the local simulator genuinely
computes amplitudes; `JobResult.dynamic_trace.physical_execution_claimed`
stays `False` for every profile this ADR covers.

## Consequences

Positive:

- Closes the actual root cause the Adjudicator named: no more capability
  bookkeeping layered on a block that never runs.
- Reuses shipped Kernel physics (`project_coord`, `RngPort`) instead of
  inventing new state math — lower implementation risk than it first
  appears.
- Makes the Dynamic lane physicist-honest: `measure` inside `dynamic qpu`
  means the same kind of thing `project(psi, k)` already means, just with a
  Controller-typed carrier.

Negative / residual open:

- Explicitly revisits and will change tests/behavior shipped under
  LISS-0383/0385/0386 (PR #483/#484) for simulator-class profiles — this is
  a deliberate, disclosed consequence of fixing the root cause, not an
  accidental regression, but it does mean recently "complete" Issues gain a
  documented amendment (as LISS-0383 already did once this session).
  Follow-up Feature Issue(s) must record this explicitly per Adjudicator
  and per `docs/collaboration/definition-of-done.md` Issue Status
  Synchronization.
- Reset remains an open honesty gap (unchanged from ADR 0199) — physicists
  still cannot spell reset until a future Accept.
- Linear/Trace-Out GC integration for the reused wire needs its own careful
  Feature-Issue-level design (this ADR states the requirement, not the
  detailed accounting algorithm).

## Rejected alternatives

### Keep patching the bookkeeping layer (profile-capability model, per-profile advertised-flags registry)

Rejected — this was the previously-proposed "Direction A", explicitly
identified by the Adjudicator as more patchwork; it would add a capability
advertisement model on top of a lane that still never executes, deferring
the same root cause again.

### Full live-hardware-equivalence execution model in this ADR

Rejected — out of scope; conflates "the local simulator genuinely evolves
state" (this ADR) with "a live QPU provider is selected/contacted" (ADR
0127 boundary, still deferred). This ADR claims neither.

### Invent new Joint-level collapse math instead of reusing `project_coord`

Rejected — `project_coord` + renormalize is already shipped, already used
by `project(psi, k)`, and already exercises the same Lüders projection
mid-circuit measurement needs. Inventing a parallel mechanism would violate
vision §2.2 (same physics, not a machine-forced second dialect).

## Follow-up work required after acceptance

1. Feature Path Issue: wire Decisions 1–2 (real mid-circuit `measure` via
   `project_coord`) into the evaluator, gated the same way LISS-0382 gated
   IR lowering (dynamic lane only, Static untouched).
2. Feature Path Issue: reuse falls out of Decision 1 — verify via the
   Verification plan above; explicitly amend LISS-0385/0386's
   simulator-profile reject-on-demand tests per Decision 3's named
   consequence, with its own Issue-level documentation synchronization.
3. Feature Path Issue: linear/Trace-Out GC accounting for the collapsed
   wire (Decision 5), replacing the `LINEAR_IMPLICIT_DISCARD` bypass.
4. Reset remains a separate future Accept (Decision 4) — not filed by this
   ADR.

## Acceptance boundary

Acceptance of this ADR approves the **Kernel execution boundary and
physics reuse** in Decisions 1–6. It does not by itself authorize Kernel
Red — a Feature Path Issue is required per Follow-up above. It does not
decide the detailed linear/Trace-Out GC accounting algorithm (Decision 5)
or any reset surface (Decision 4).

## Dependency Adoption Evidence

Not applicable — no new library, provider SDK, or datastore. Reuses
`RngPort` (already adopted, ADR 0170) and `Joint.project_coord` (already
shipped).

## Enforcement

Code review / agent review should reject:

- Reintroducing capability-flag bookkeeping (profile-advertisement
  registries, reject-on-demand scaffolding) for simulator-class profiles as
  a substitute for real execution once this ADR ships.
- Inventing a second collapse primitive instead of reusing
  `Joint.project_coord`.
- Adding a `reset` keyword or equivalent surface under this ADR (still
  ADR 0199 Decision 3's boundary).
- Claiming `physical_execution_claimed=True` anywhere this ADR's execution
  path is reached.
