# ADR 0204: Mid-program `Continuous` type — Lane B ship shape

## Status

**Accepted** (2026-08-10) — Adjudicator Architecture approval. Per
[staqex-v1-continuous-lane-b-expressiveness-scenarios.md](../../specs/staqex-v1-continuous-lane-b-expressiveness-scenarios.md)
§7 ("Next gates (not authorized by this doc)"): opening Lane B required
"Architecture Path + ship ADR only" — this ADR is that gate. Acceptance
authorizes the type/gate/op/port/LINEAR decisions below as an architecture
boundary. **It does not itself authorize Feature Path Red** — a separate
Feature Plan (new `LISS-*`) and Issue-Level Plan approval remain required
per `CLAUDE.md` "Claude Code Issue-Level and Work-Plan Autonomy," same as
ADR 0185 required LISS-0313 before any Lane A Kernel code.

Companions:

- [ADR 0126](0126-continuous-pdf-design-boundary.md) — design boundary.
  Decision 1 ("Continuous PDF is not a Kernel value type") is **proposed for
  partial amendment** by this ADR (see Consequences) — under hard gates,
  `Continuous` becomes a Kernel type, but still never a `measure`/QPU/Joint
  carrier, so ADR 0126's *physics* intent (no continuous value reaches
  collapse or hardware) is preserved, only its *type-existence* clause
  narrows.
- [ADR 0162](0162-continuous-host-bridge-first.md) — Host/Bridge-first
  evolution path; Decision 4 names this exact gate ("A mid-program
  `Continuous` type still requires a **future** ship ADR").
- [ADR 0185](0185-kernel-continuous-value.md) — Lane A `finiteize`, shipped
  and unchanged in its existing uniform-args form; extended (Decision 4
  below) to also accept a `Continuous` value, additively.
- [ADR 0074](0074-explicit-discretization-contract.md) — discretization
  provenance contract, reused unchanged.
- [Continuous / Lane B expressiveness scenarios](../../specs/staqex-v1-continuous-lane-b-expressiveness-scenarios.md)
  (LISS-0315/0316, frozen baseline 2026-08-03) — CH-field-compose §2A is the
  concrete Ideal-form driver for this proposal; its §2A.11 "Ship ADR
  checklist" is the backbone of the Decision section below.
- Host substitute already Runtime-proven:
  `examples/showcase/S01_quantum_disaster_response/host/field_compose_inject.py`
  (LISS-0317) — its `weight`/`mask`/`damage`/`flood`/`fire`/`impassable`
  Python functions are the concrete semantics this ADR lifts into typed
  Kernel ops.

## Context

The Lane B expressiveness scenarios doc scores `CH-field-compose` (K-ku
overnight damage/flood/fire risk → masked risk → tonight zone bins) as
**weak**: the Ideal form (§2A) requires named, multi-step continuous
carriers (`damage`, `risk`, `masked`) as first-class mid-program values
before finiteization, but today that algebra only exists as untyped Python
in a Host script. The seat cannot score **Y** until a ship ADR exists
(§2A.10, §4 P0 finding: "Mid-program Continuous type world (blocked)...
Opening is Architecture Path + ship ADR only").

The Adjudicator selected "Continuous PDF Lane B" as the first reopened-
backlog item to work through this session (2026-08-10), instructing work to
proceed through the remaining items "上から" (in the order presented). This
ADR is the required first step for that item — investigation and proposal,
not implementation.

## Decision

### 1. `Continuous<T>` type world + hard gates

- New Kernel type `Continuous<T>`, `T` a classical payload tag (mirrors
  `State<T>`'s existing convention; MVP tag: `Field` — e.g.
  `Continuous<Field>`). Declared via `state`-keyword binds exactly like
  `State<T>` today (`Continuous damage = …` — bare-name inference, same as
  `state x = …`, per DEC-0003 blackboard-spelling precedent), not a new
  binding keyword.
- **Runtime representation is an opaque Host-backed handle** — never a
  Joint `World`, never amplitude-bearing. The Kernel never evaluates the
  underlying continuous function; only Host code (behind the port in
  Decision 2) does. This matches ADR 0162 Decision 1 ("Continuous carriers
  ... are not Kernel mid-program values" in the Joint-eval sense) even
  though `Continuous` becomes a **typed** Kernel value.
- **Hard gates (TypeChecker / hir.py — compile-time rejection, not just
  documentation):**
  - `Continuous` may never appear as the operand of `measure`.
  - `Continuous` may never appear in an `evolve` block, a `Joint`-forming
    expression (`|ψ⟩`, `Coin`, tensor, etc.), or any QPU/QASM emission
    path.
  - The **only** operations a `Continuous` value may enter are: the ops
    named in Decision 3, and `finiteize` (Decision 4). Any other use is a
    new hard diagnostic, e.g. `CONTINUOUS_ESCAPE_ERROR`.

### 2. Host injection port

- New port `ContinuousFieldPort` (mirrors the existing `RngPort`/
  `HostInputPort` shape — provider-neutral, Host-owned): a single method
  returning an opaque handle plus provenance, e.g.
  `def field(self, source: str, domain: str, provenance: Mapping[str, Any]) -> ContinuousFieldHandle`.
  The Kernel never imports a concrete field-definition adapter; a Host
  adapter (analogous to `field_compose_inject.py`'s Python functions, now
  behind a port) supplies the real function.
- Kernel-callable surface: `field_from_host(source, domain, provenance =
  {…}) -> Continuous<Field>`, routed through this port — mirrors the
  `finiteize`/`HostMonteCarloPort` precedent (ADR 0163) of a thin Kernel
  Call dispatching to a Host port, no Kernel-side numerics.

### 3. MVP continuous ops — exactly two, both already Host-proven

Per §2A.11 item 2 ("MVP continuous ops for this seat: inject, weight, mask
— or smaller set that still yields ≥2 steps"):

- `weight(Continuous, Continuous[, Continuous]) -> Continuous` — pointwise
  composition (lifts `field_compose_inject.py`'s `weight(damage, flood,
  fire)` unchanged in meaning).
- `mask(Continuous, Continuous) -> Continuous` — pointwise suppression
  (lifts `mask(risk, impassable)` unchanged).
- No other continuous ops in MVP. `clip`, `normalize_field`,
  `support_restrict` (named as "optional later Ideal" in §2A.5) are
  explicitly **not** in this ship — a later additive ADR, not blocking
  this one.
- Both ops are pure Kernel-side bookkeeping over opaque handles (compose a
  new handle referencing its inputs + operation name for provenance); the
  actual pointwise math still lives Host-side, evaluated only when
  `finiteize` (Decision 4) forces a concrete sampling/discretization pass.

### 4. `finiteize` accepts a `Continuous` first argument

- Extend the shipped Lane A grammar
  (`finiteize(lo, hi, n_bins, n_samples[, seed])`, unchanged, still valid)
  with a second overload: `finiteize(continuous, bins = N, interval = …,
  label_mode = …)` where `continuous` is a `Continuous<Field>` value.
  Exact keyword-argument shape is Feature Red material (per §2A.6's own
  disclaimer that its Ideal spelling is not final grammar), not fixed here.
- Backend for the `Continuous`-argument overload is a Host-side
  discretization pass over the composed handle chain (evaluates
  `weight`/`mask`/`field_from_host` lazily, in order, then buckets),
  reusing `EqualWidthHistogramMonteCarlo`'s existing bucketing machinery
  (ADR 0163) rather than inventing new numerics.
- Provenance carries `discretization` (ADR 0074 shape, unchanged) plus
  `continuous_pipeline` (the op-name chain — already the exact shape
  `field_compose_inject.py` produces today, now generated from the real
  Kernel call chain instead of hand-written Host book-keeping).

### 5. LINEAR / discard story for `Continuous` roots

- `Continuous` roots are tracked by the **same** linear-use checker
  (`hir.py`) machinery as `State` roots (`introduced`/`consumed`), not a
  parallel system.
- **The only consuming operation in this MVP is `finiteize`.** `weight`
  and `mask` are non-consuming transforms that return a **new** named
  root (the input roots become dead after use, same as any other Call
  whose result is bound to a new name — ordinary move semantics, no
  special case).
- No separate "explicit continuous discard" form is introduced in this
  MVP — every named `Continuous` root must reach `finiteize` exactly once,
  or `LINEAR_IMPLICIT_DISCARD` fires, identically to an unmeasured `State`
  root today.
- **Known, explicitly out-of-scope limitation:** a `Continuous` root can be
  consumed by `finiteize` **at most once** under this rule. `CH-field-fork`
  (one continuous root, two independent `finiteize` calls at different
  resolutions) is therefore **not** satisfied by this ADR — the
  expressiveness scenarios doc already scores CH-field-fork as "park until
  compose Ideal Y needed" (§3.1), so this is a deliberate, disclosed
  sequencing choice, not an oversight. A future amendment would need to
  either permit non-linear (shared/aliased) `Continuous` reads or introduce
  an explicit duplication op.

### 6. Constellation sample path, not spine rewrite

- No change to `examples/showcase/S01_quantum_disaster_response/main_disaster_response.sqx`
  or any other shipped example. A Lane B `CH-field-compose` demo, once
  built, is a **new** constellation/pre-inject example file, per the
  expressiveness scenarios doc's own "Spine purity" gate (§2A.10, §4 P2).

## Non-goals

- `CH-field-fork` (dual finiteize of one shared root) and `CH-field-theory`
  (Theory `continuous_operator` vocabulary unification) — both explicitly
  parked by the expressiveness scenarios doc (§3 inventory); this ADR does
  not attempt either.
- CFD, continuous seismic waveforms, city-wide continuous optimum QC —
  permanent-out per the locked scenario and this ADR's own scope.
- Joint rational masses (ADR 0125) and CUDA Deferred workers — unrelated
  reopened-backlog items, not touched here.
- Any change to `submit_source`, the Dynamic QPU lane, or the AWS Braket
  lineage (all unrelated, already shipped this session).
- Live/cloud Monte Carlo SDK selection inside the Kernel (ADR 0162
  Non-goals, still standing).

## Rejected alternatives

### Make `Continuous` a Joint-compatible / amplitude-bearing carrier

Rejected — this would directly reopen ADR 0126 Decision 1's physics intent
(no continuous value reaches collapse), not merely its type-existence
clause. Every seat in the expressiveness doc requires `measure`/QPU to stay
finite-only forever; a Joint-compatible `Continuous` would blur that line
by construction, not just by discipline.

### Allow unlimited (non-linear) reads of a `Continuous` root

Rejected for this MVP — would immediately need to answer `CH-field-fork`'s
harder question (independent resolutions from one shared source, each with
its own provenance) inside the same ADR that is trying to ship the
smaller, already-scored `CH-field-compose` seat. Deferred per Decision 5's
disclosed limitation, matching the expressiveness doc's own sequencing.

### Reuse `HostMonteCarloPort` instead of a new `ContinuousFieldPort`

Rejected — `HostMonteCarloPort.sample_to_finite` is shaped around
*sampling a distribution to a finite bucket*, i.e. it already assumes the
finiteization step. A `Continuous` field injection (Decision 2) needs to
return an *opaque, still-continuous* handle, which is a different contract
shape; conflating the two ports would make `HostMonteCarloPort`'s existing,
shipped, Lane-A-tested contract do double duty for an unrelated concern.

## Consequences

- **Amends ADR 0126 Decision 1** from "Continuous PDF is not a Kernel value
  type in this ADR" to "Continuous PDF is a Kernel value type only under
  the hard gates in this ADR's Decision 1" — the *never reaches
  measure/QPU/Joint* physics intent is explicitly preserved and now
  compiler-enforced rather than true only by absence.
- Unblocks `CH-field-compose` scoring **Y** once Green (currently frozen
  at **weak** per LISS-0319).
- Sizeable Feature Path surface once accepted — likely a multi-Issue batch,
  not one Issue: new AST bind shape (or `StateBind`-style reuse with
  `ty.name == "Continuous"`, TBD at Feature Plan time), `hir.py` hard-gate
  diagnostics, `TypeChecker` type-world entries, a new
  `ContinuousFieldPort` + Host adapter, evaluator handle representation,
  `weight`/`mask` Call dispatch, and the `finiteize` overload. This ADR
  does not size or order that batch — a Feature Plan investigation
  (mirroring this session's LISS-0387 batch-investigation precedent) would
  do that separately, after Architecture approval.
- `CH-field-fork` and `CH-field-theory` remain scored **weak**/blocked
  after this ADR ships — explicitly not resolved here (see Non-goals).

## Acceptance boundary

Acceptance of this ADR authorizes the type/gate/op/port/LINEAR decisions in
Decisions 1–6 above as an architecture boundary, and authorizes the ADR
0126 Decision 1 amendment stated in Consequences. It does **not** authorize:

- Technology selection (none required — the new port stays provider-neutral
  and adapter-agnostic, same as every other Host port in this project).
- Feature Path Red or any Kernel code change.
- Any wording change to ADR 0126 beyond the single Decision 1 amendment
  named above.
- A decision on `CH-field-fork`/`CH-field-theory` (both remain open,
  unaddressed reopened-backlog rows).

A Feature Plan investigation (new `LISS-*`, produced under this session's
Issue-Level Autonomy work-plan-investigation process) is required before any
Red, exactly as ADR 0185 required LISS-0313.

## Implementation permission

| Item | Status after Accept |
|---|---|
| Architecture (type/gate/op/port/LINEAR shape) | **granted** 2026-08-10 |
| Technology selection | not required |
| Feature Plan (work-plan investigation) | **requested separately** |
| Phase 1 Red / Kernel code | **forbidden** until Feature Plan investigation + batch or Issue-level Plan approval |

## Decision history

| Date | Event |
|---|---|
| 2026-08-10 | Proposed — Architecture Path investigation into the Continuous PDF Lane B reopened-backlog item |
| 2026-08-10 | Adjudicator Architecture approval → **Accepted** |
