# ADR 0197: Dynamic-lane mid-circuit measurement and classical feed-forward

## Status

**Accepted** (2026-08-09) — Architecture approval by the Adjudicator.
Extends [LISS-0028](../../issues/LISS-0028-dynamic-qpu-lane.md)'s unchecked
item "Mid-circuit measurement and classical feed-forward have explicit
semantics distinct from terminal `measure`". Acceptance approves Decisions
1–7 below; it does **not** by itself authorize Kernel-touching
implementation, and it does not make the dynamic QPU lane executable — see
"Acceptance boundary" and "Follow-up work required" below. It does **not**
revive `observe` / classical `branch` (ADR 0193 Decision 5).

## Design check

- **Scope and expected behavior:** Define how mid-circuit measurement and
  finite classical feed-forward are denoted and mean, as a **Dynamic QPU
  lane** surface distinct from Static Kernel terminal `measure` (NLTS),
  without inventing method-chain or retired keywords, and without silently
  Host-emulating unsupported hardware. Align language meaning with the
  already-shipped Fake DTO contract ([LISS-0077](../documentation-compression-map.md)
  / [`staqex-v1-dynamic-qpu-plan.md`](../../specs/staqex-v1-dynamic-qpu-plan.md))
  and the existing QSem markers (`DynamicMeasurementRegion`,
  `DynamicControlRegion`).
- **Specifications and files inspected:** LISS-0028; ADR 0071 / 0106 D2
  (DEC-0006 theme + archived ADR text); ADR 0193 Decision 5; ADR 0069;
  `staqex-dynamic-qpu-lane.md`; `staqex-v1-dynamic-qpu-plan.md`;
  `compiler/staqex/dynamic_qpu.py` (Fake executor + verifier);
  `quantum_semantic_ir.py` (DynamicMeasurementRegion /
  DynamicControlRegion / TimingRegion); `typecheck.py` unconditional
  `DynamicQpuStmt` rejection; vision §2.2 / §3.1; language axioms Axiom 5
  (collapse at measure — Static reading).
- **Component boundaries, ports/adapters, VO/DTO candidates:** Language
  surface + Quantum Semantic IR meaning only. Reuse existing Fake DTOs
  (`ControllerValue`, `OutcomeToken`, `MatchPlan`, `MergeObligation`,
  `DynamicCapabilityDemand`, …) as the **semantic vocabulary** for a
  future Feature Path wire. No new Host/QPU provider SDK. No JobResult
  DTO redesign in this ADR (principle paragraph only).
- **Applicable constraints:** Physicist-first / vision §2.2 (source denotes
  blackboard; intentional transform priority). Static Kernel NLTS and
  terminal `measure` must not be weakened. Fail-closed; no Host silent
  emulation (ADR 0071). `observe` / method-chain / open classical `branch`
  remain rejected (ADR 0193). Timing intent remains ADR 0193 / LISS-0381
  (`within <name>` opaque for now).
- **Decisions, assumptions, unresolved ambiguities:** Surface spelling of
  mid-circuit collapse (Decision 2) is the primary Adjudicator choice —
  this ADR **recommends** lane-local `measure` that yields
  `(Controller<T>, post-measure State)` rather than a new keyword.
  Exact parser spelling of `dynamic qpu` vs `dynamic qpu fn` remains an
  implementation Issue detail under Decision 1's lane rule. Qubit reuse /
  reset full model and JobResult composition DTOs stay follow-up ADRs.
- **Included and omitted AI context:** Included LISS-0028/0077/0193 and
  live Kernel refusal/Fake/QSem reads. Omitted vendor pulse dialects,
  OpenQASM dynamic emission (LISS-0097-E), live provider submit
  (LISS-0100).
- **Task routing:** Architecture review; deterministic source inspection;
  no external model call required for acceptance.
- **Evidence contract:** N/A — no AI runtime output.
- **Verification plan (after Accept + Feature Issue):** (a) Static programs
  retain terminal-measure-only collapse; (b) well-formed dynamic mid-circuit
  programs parse into QSem DynamicMeasurement/Control markers (or fail with
  stable diagnostics if still capability-rejected); (c) Controller escape
  attempts reject with the LISS-0077 code family; (d) lane remains
  non-executable until a separate, named execution Issue is approved —
  **or**, if the Adjudicator chooses Decision 7 Option B, Fake-backed
  execution is gated by an explicit Feature Issue listed in Follow-up.

## Context

After ADR 0193 / LISS-0381, timing *intent* has a grammar and IR witness, but
LISS-0028's first unchecked acceptance item remains:

> Mid-circuit measurement and classical feed-forward have explicit semantics
> distinct from terminal `measure`.

Present state of the repository:

1. **Static Kernel** — NLTS; collapse only at terminal `measure`
   (axioms / vision §3).
2. **Dynamic lane rejection** — every `DynamicQpuStmt` still emits
   `DYNAMIC_CAPABILITY_REQUIRED_ERROR` and
   `DYNAMIC_UNSUPPORTED_FEATURE_ERROR` (LISS-0028 Phase 3).
3. **LISS-0077 P0** — Fake DTO + verifier + `FakeDynamicExecutor` under
   **supplied** outcomes; not wired from parser/AST; does not claim physical
   execution.
4. **QSem** — `DynamicMeasurementRegion` / `DynamicControlRegion` schemas and
   verifiers exist; **no production lowering** from source builds them
   (tests only).
5. **ADR 0193 Decision 5** — explicitly does **not** introduce mid-circuit
   observation/branch; rejects `observe` revival and classical `branch`.

Without an Architecture decision, Feature Path cannot implement mid-circuit
without guessing surface spelling, Controller laws, and NLTS/lane boundary
wording — all of which ADR 0071 / 0106 left open or deferred.

## Decision proposal

### 1. NLTS is Static-Kernel law; Dynamic lane is a distinct collapse surface

**Never Leave the State** (mid-program values stay uncollapsed) remains
normative for the **Static Kernel** object language (vision §3 / axioms).

The **Dynamic QPU lane** is a separate surface (vision §3.1; ADR 0071 /
0106 D2) that **may** perform mid-circuit collapse **only** when:

- the collapse appears inside an explicit dynamic-lane region
  (`dynamic qpu …` / approved dynamic entry form); and
- a target capability profile admits the demanded dynamic features; and
- unsupported demands fail closed (no Host silent emulation).

Agents must not "fix" Static programs by smuggling mid-circuit collapse
into ordinary `main` without the dynamic lane marker.

### 2. Mid-circuit collapse spelling: lane-local `measure` (recommended)

Inside the dynamic lane, mid-circuit collapse continues to use the keyword
**`measure`**, not a revived `observe`, not a method-chain, and not a new
`branch` keyword.

**Recommended reading (blackboard):**

- Static / terminal: `measure ψ` ends the Static Kernel narrative
  (outcome leaves the joint as a classical report / JobResult path).
- Dynamic / mid-circuit: `measure ψ` **inside** `dynamic qpu …` produces a
  **paired** result: an `OutcomeToken` (finite classical controller seed) and
  a **post-measure** Joint state that remains in-lane for further quantum
  ops — never a silent Static-style terminal exit.

**Rejected for this ADR (already decided elsewhere):**

- Reviving `observe` (ADR 0193; RETIRED → `measure`).
- Kotlin-style `.observe { }.measure { }` method chains (ADR 0193).
- Open classical `if` / `while` / unbounded `branch` as Joint control.

**Adjudicator alternative (not recommended):** introduce a distinct keyword
(e.g. `mid_measure`) solely to avoid overloading `measure`. Rejected as
primary because it doubles collapse vocabulary against physicist-first
"one collapse verb" unless the Adjudicator prefers extreme Static/Dynamic
visual separation.

Exact AST product type / destructuring sugar (`(token, psi') = measure psi`
vs implicit controller bind) is deferred to the Feature Issue under this
Decision's meaning — Implementation must not invent a second collapse verb.

### 3. Classical feed-forward is `Controller<T>` + finite `match` + one merge

Normative dynamic feed-forward (aligning ADR 0106 D2 and LISS-0077):

- **`Controller<T>`** — phase-local classical carrier; **not** `State`;
  cannot enter Theory, alter Static register shape, select
  deployment/provider, or escape the dynamic phase.
- **Finite `match`** over an `OutcomeToken` — only closed, finite arms.
- **Exactly one merge** of the correlated post-measure Joint / token pair
  (`MergeObligation` / QSem pairing laws).

LISS-0077 Fake DTO names (`ControllerValue`, `OutcomeToken`, `MatchPlan`,
`MergeObligation`, `DynamicCapabilityDemand`, …) are adopted as the
**semantic vocabulary** this ADR endorses; parser wire remains a Feature
Path concern after Accept.

### 4. Existing QSem Dynamic regions are the normative IR targets

Future source lowering **shall** target (or extend in a later ADR, not
silently replace):

- `DynamicMeasurementRegion` — mid-circuit collapse marker with
  `required_capability` (today: `DynamicMeasurementFeedback` family);
- `DynamicControlRegion` — feed-forward / match / merge marker paired to a
  measurement region.

`TimingRegion` (ADR 0193) remains an independent intent witness and does
not imply mid-circuit execution.

### 5. JobResult principle (detail deferred)

Mid-circuit `Controller` bindings and outcome tokens are **not** the same
object as Static terminal `measure` payloads on `JobResult`. A later ADR
(or LISS-0028 JobResult-composition Issue) must specify the Host envelope
for dynamic runs. This ADR only forbids treating mid-circuit tokens as
silent substitutes for terminal measurement in Static Kernel programs.

### 6. Capability fail-closed (reaffirm)

Dynamic programs that demand reset, reuse, latency windows, or feedback
unsupported by the selected profile reject with stable diagnostics (LISS-0077
codes / existing `DYNAMIC_*` family as applicable). Host must not silently
emulate missing hardware control (ADR 0071).

### 7. Execution authorization is **not** granted by this ADR

Accepting this ADR accepts **meaning and IR targets**. It does **not**:

- remove today's unconditional `DynamicQpuStmt` typecheck rejection; or
- wire parser → FakeDynamicExecutor; or
- claim live QPU feed-forward.

A dedicated Feature Path Issue (Follow-up) is required for any Kernel Red
that changes rejection or execution behavior. Optional later Issue may
connect AST → Fake under supplied outcomes without claiming physical
execution (LISS-0077 honesty).

## Consequences

Positive:

- LISS-0028's mid-circuit acceptance item gains an Architecture answer
  compatible with shipped Fake/QSem assets and ADR 0193 rejects.
- Static NLTS remains crisp; Dynamic collapse is an explicit lane law.
- Feature Path can implement without inventing `observe`/`branch`.

Negative / residual open:

- Surface sugar for packing `(Controller, State)` remains Issue-level.
- JobResult composition and qubit reuse/reset full models still need
  separate ADRs/Issues.
- Lane stays non-executable until a Feature Issue is approved — physicists
  still cannot *run* mid-circuit programs on shipping Kernel after Accept
  alone (honest; matches ADR 0193's timing-intent precedent).

## Rejected alternatives

### Revive `observe` / introduce `checkpoint` / classical `branch`

Rejected — ADR 0193 Decision 5; RETIRED keyword; opens unbounded classical
control inside quantum narrative.

### Treat mid-circuit as Static Kernel exception to NLTS

Rejected — would destroy the Static blackboard law. Dynamic must be a
**named lane**, not a silent Static escape hatch.

### Skip Architecture and wire Fake executor from today's `dynamic qpu { }`

Rejected — would invent surface meaning (Controller production, match/merge
laws) without Adjudicator decision; violates Prime Directive.

### Closed timing-intent vocabulary as part of this ADR

Rejected — belongs to a future adapter-backed ADR (0193 Follow-up #2);
orthogonal to mid-circuit collapse laws.

## Follow-up work required after acceptance

1. File a Kernel-touching Local Issue implementing Decisions 1–4 / 6–7
   boundary: surface sugar for lane-local mid-circuit `measure`, AST/IR
   lowering to `DynamicMeasurementRegion` / `DynamicControlRegion`,
   Controller/match/merge diagnostics aligned with LISS-0077 — **without**
   removing capability rejection unless the Issue explicitly schedules a
   Fake-exec slice approved separately.
   **Shipped (Kernel complete):**
   [LISS-0382](../../issues/LISS-0382-dynamic-mid-circuit-feed-forward.md)
   (`feature/liss-0382-dynamic-mid-circuit-feed-forward`).
2. Separate ADR/Issue for JobResult composition of dynamic runs
   (LISS-0028 remaining item).
3. Separate ADR/Issue for qubit reuse / reset model beyond capability
   reject flags.
4. Later: AST → FakeDynamicExecutor under supplied outcomes (still
   `physical_execution_claimed=False`); OpenQASM dynamic emission;
   live provider (LISS-0097-E / LISS-0100).

## Acceptance boundary

Acceptance of this ADR approves the **semantic boundary and IR targets**
above (Decisions 1–7). It does **not** authorize Kernel implementation,
does not make the dynamic lane executable, does not select a live QPU
provider, and does not decide JobResult DTO shape or concrete timing-name
meanings.

## Dependency Adoption Evidence

Not applicable — no new library, provider SDK, or datastore.

## Enforcement

Code review / agent review should reject:

- Introducing `observe`, method-chain collapse, or unbounded classical
  `branch` as mid-circuit surface after this ADR is Accepted.
- Weakening Static Kernel NLTS / terminal-measure rules to "make dynamic
  easier."
- Kernel Red for mid-circuit execution without a Feature Issue that cites
  this ADR's Follow-up and an explicit phase approval.
- Silently Host-emulating unsupported dynamic capability demands.
