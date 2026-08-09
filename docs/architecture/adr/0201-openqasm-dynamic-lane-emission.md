# ADR 0201: OpenQASM emission for the Dynamic QPU lane

## Status

**Accepted** (2026-08-10) — Architecture approval by the Adjudicator.
Investigates the deferred item every Dynamic-lane ADR in this lineage has
named without resolving: ADR 0197 Follow-up #4 ("OpenQASM dynamic
emission"), ADR 0199 Out of scope, ADR 0200 verification plan omission —
all citing `LISS-0097-E` / the `staqex-v1-dynamic-qpu-plan.md` "Slice E
(portable dynamic artifact)" as deferred follow-up. Acceptance approves
Decisions 1–5 below, **including Decision 4 Option 2** (emission requires
only successful compilation, independent of any Fake profile gate).

## Design check

- **Scope and expected behavior:** Decide whether and how a `dynamic qpu`
  program (mid-circuit `measure`, `match` feed-forward, `reset` — all
  Kernel-complete as of this session: ADR 0197/0382, ADR 0199
  Amendment/LISS-0390) can be emitted as OpenQASM 3 text, and what that
  emission does and does not claim about physical execution.
- **Specifications and files inspected:**
  `compiler/staqex/backend/qasm/emitter.py` (`QASM3Emitter`,
  `emit_unit`/`emit_qpu_program` — **confirmed by direct read: zero
  references to `DynamicQpuStmt`, `MatchStmt`, `MeasureExpr`, `ResetStmt`
  anywhere in this module**); `compiler/staqex/backend/qasm/lower.py`
  (`lower_unit_to_circuit`, "Prefer structural AST patterns" — built
  entirely around Static QPU / Parametric circuit patterns: `forEach`
  register loops, `evolve`/Trotter, gate `apply` calls; no Controller,
  match, or mid-circuit measure handling); `compiler/staqex/backend/qasm/circuit.py`
  (`Circuit`/`Gate` IR — **confirmed by direct read: a flat gate list,
  `GateName` literal has no `"reset"` entry, no conditional/branching
  representation of any kind** — QASM3's `if`/`else` has no IR
  counterpart today); `compiler/staqex/host.py` (`prepare_parametric_qasm`
  — **confirmed the QASM emission path and the Dynamic-lane
  `submit_source` execution path are structurally disjoint**: QASM
  emission never touches `dynamic_fake_wire.py` / `dynamic_qpu.py` /
  the evaluator's `_run_dynamic_qpu_block`, and vice versa); ADR 0071
  (fail-closed Host honesty, no silent emulation); ADR 0197 Decision 3
  (`Controller<T>` — phase-local classical carrier, cannot enter Theory /
  alter shape / select deployment); `staqex-v1-dynamic-qpu-plan.md` §7
  (explicit non-goal: "Live QPU feed-forward (LISS-0100)" kept separate
  from "portable dynamic artifact").
- **Component boundaries, ports/adapters, VO/DTO candidates:** A new
  Dynamic-lane-specific lowering path (name TBD at Feature Issue,
  candidate `lower_dynamic_unit_to_circuit`) — **not** a small patch to
  the existing Static `lower_unit_to_circuit`, which is structurally
  built for a different program shape (straight-line gates, no
  conditional/classical-bit control). `Circuit`/`Gate` IR needs two
  additions: a `"reset"` `GateName` entry, and **some** representation of
  finite classical-conditioned blocks (QASM3 `if`/`else`) that does not
  exist in the flat gate-list model today — exact shape (nested block
  IR vs. flat gate list with jump/label annotations) is a Feature Issue
  design question, not resolved here. No new port; no provider SDK; no
  network. This ADR does **not** touch `JobResult`/`dynamic_trace`
  (ADR 0198) or the local Fake/evaluator execution path (ADR 0200) —
  emission is a **separate, additive** output channel from the same
  compiled AST, not a replacement or an alternate execution route.
- **Applicable constraints:** `physical_execution_claimed` semantics
  (ADR 0071/0197) must not be weakened: **emitting QASM3 text is not
  executing it.** This ADR defines a text artifact's meaning, the same
  way `prepare_parametric_qasm` already does for the Static QPU surface
  — it does not submit anything, does not contact a provider, and does
  not require `CredentialPort` (ADR 0161). What a physicist or Host tool
  does with the emitted text **outside** Staqex (hand it to a real QASM
  simulator or hardware) is explicitly out of this ADR's authority, the
  same way emitting the existing Static QASM output today carries no
  execution claim either — this is not a new category of honesty risk,
  it is the same one the Static QPU surface has already carried since
  `LISS-0097`. `Controller<T>`'s phase-locality (ADR 0197 Decision 3)
  must have a faithful QASM counterpart: a genuine classical `bit`
  register is the natural match (QASM3 bits are classical, matching
  "cannot enter Theory" directly) — not a workaround.
- **Decisions, assumptions, unresolved ambiguities:** Whether emission
  should be gated behind the same `dynamic_fake_profile` Host setting
  that gates local execution, or available whenever the program compiles
  (since emission makes no execution claim at all) is **not resolved
  here** — flagged as Decision 4's open question for the Adjudicator.
  Exact Circuit-IR conditional-block representation is Feature Issue
  detail (mirrors ADR 0197's own precedent of deferring exact AST/IR
  shape to Feature Path).
- **Included and omitted AI context:** Included direct reads of the QASM
  emitter/lowering/circuit modules and `host.py`'s two disjoint
  submission paths. Omitted live provider QASM dialects/vendor
  extensions (still ADR 0127 territory, not reopened here).
- **Task routing:** Architecture proposal; deterministic source
  inspection.
- **Evidence contract:** N/A — no AI runtime output.
- **Verification plan (after Accept + Feature Issue):** (a) a Dynamic-lane
  program with `measure`/`match`/`reset` emits QASM3 text using genuine
  `bit`, `measure`, `if`/`else`, and native `reset` statements — not a
  flattened or silently-approximated form; (b) `physical_execution_claimed`
  is untouched by this ADR everywhere it already appears (ADR 0198's
  `dynamic_trace`, ADR 0200's evaluator path) — emission does not set or
  read that flag at all, since it makes no execution claim; (c) Static
  QPU emission (`prepare_parametric_qasm`, existing) is byte-for-byte
  unaffected; (d) unsupported Dynamic-lane shapes (if any surface during
  Feature Issue design) reject explicitly, per ADR 0071, rather than
  silently dropping structure.

## Context

Every ADR in this session's Dynamic-lane lineage has named the same
deferred item without resolving it:

- ADR 0197 Follow-up #4: "OpenQASM dynamic emission" listed alongside
  live provider work, both still separate.
- ADR 0199 Out of scope: "OpenQASM `reset` emission; live provider."
- `staqex-v1-dynamic-qpu-plan.md` §4: "E portable dynamic artifact /
  target metadata — follow-up; unlocks LISS-0097 dynamic emission,"
  explicitly forbidden until "later approvals" alongside provider SDKs.

Investigation for this ADR found the reason it kept sliding: it is not a
small addition to the existing QASM path. The existing emitter/lowering/
circuit modules were built for the **Static QPU / Parametric circuit
surface** (`forEach` register loops, gate `apply`, `evolve`/Trotter) — a
different lane with a different AST shape than `dynamic qpu`'s
Controller/match/measure/reset constructs, and the two submission paths in
`host.py` are already structurally disjoint. Nothing in the Circuit IR
represents classical-conditioned branching or a reset gate today.

Separately, QASM3 (the target language itself) already has native syntax
for exactly this physics — `bit c; c = measure q;`, `if (c == 1) { x q;
}`, and a literal `reset q;` statement — so the *target* is not the
blocker; the *Staqex-side lowering path* is.

## Decision proposal

### 1. Emission is additive and separate; it does not touch Fake/evaluator execution

QASM3 emission for `dynamic qpu` programs is a **new, separate output
channel** from the same compiled AST — parallel to, not replacing or
routing through, the local Fake/evaluator execution path (ADR 0200) or
`JobResult`/`dynamic_trace` (ADR 0198). It changes neither.

### 2. `physical_execution_claimed` is untouched; emission is not execution

Emitting QASM3 text makes **no execution claim of any kind** — the same
boundary `prepare_parametric_qasm` already holds for the Static QPU
surface. This ADR does not set, read, or reason about
`physical_execution_claimed` anywhere. Submitting the emitted text to a
real QASM-capable target (simulator or hardware) outside Staqex remains
entirely ADR 0127 / live-provider territory, not reopened here.

### 3. Faithful mapping, reusing QASM3's own native vocabulary (no invented dialect)

A future Feature Issue implementing this ADR must map:

- `Controller<T> c = measure wire` → a genuine classical `bit c; c =
  measure wire;` — `Controller`'s phase-locality (ADR 0197 Decision 3)
  has a direct, honest QASM3 counterpart in a classical bit, not a
  workaround.
- `match c { 0 => {…} 1 => {…} }` → QASM3 `if (c == 0) { … } if (c == 1)
  { … }` (or `if`/`else` for the two-arm case) — Staqex's `match` is
  already finite/closed (ADR 0197 Decision 3), the same shape QASM3's
  conditional already expects; this is a faithful re-expression in the
  target language, not new Kernel control flow (vision §2.2 — the
  physics narrative is preserved, only the concrete syntax changes for
  the target).
- `reset wire` → QASM3's own native `reset wire;` statement — a direct
  1:1 correspondence. (This mapping is part of why the Adjudicator's
  2026-08-10 direction to add a genuine `reset` keyword rather than
  reusing `state x = |0>` was the right call for expressiveness: the
  distinct keyword has a clean, honest target-language counterpart that
  a repurposed idiom would not have had.)

No new Staqex surface syntax is proposed by this Amendment — this
Decision is about the **Kernel-to-target lowering**, not the language.

### 4. Resolved (Adjudicator, 2026-08-10): Option 2

QASM emission requires only successful compilation — **independent of any
`dynamic_fake_profile` Host gate**. Emission makes no execution claim
(Decision 2), so it needs no capability profile; gating it behind the
same setting local Fake execution needs would conflate "can this
simulator run it" with "can this text be produced," which are different
questions. (Option 1 — gating emission behind the same profile setting as
local execution — was considered and not chosen.)

### 5. Out of scope for this ADR

- Live provider submission of emitted QASM (ADR 0127 boundary, untouched).
- Vendor-specific QASM dialects / pulse-level extensions.
- Circuit IR's exact conditional-block representation (Feature Issue
  design detail).
- Any change to the Dynamic-lane language surface, Kernel semantics, or
  capability law (ADR 0197/0199/0200 all stand unchanged).

## Consequences

Positive:

- Closes a five-ADR-old deferred item with a concrete, grounded design
  rather than leaving it as permanent scope debt.
- QASM3's own native vocabulary (`measure`, `if`, `reset`) maps
  faithfully with no invented dialect — low semantic risk once Circuit
  IR is extended.
- Validates the `reset` keyword decision (ADR 0199 Amendment): a direct
  target-language correspondence a repurposed `state x = |0>` idiom
  would not have had.

Negative / residual open:

- Genuinely larger implementation than "add reset to the emitter" —
  requires a new lowering path and a Circuit IR extension (conditional
  blocks), not a small patch.
- Decision 4 (profile gating) is left open; a Feature Issue cannot
  proceed against this ADR alone without that choice.

## Rejected alternatives

### Route Dynamic-lane emission through the existing `lower_unit_to_circuit`

Rejected — that function is structurally built for straight-line Static
QPU circuits (confirmed by direct read); forcing Controller/match/reset
through it would either silently drop structure or require rewriting it
beyond recognition. A separate, purpose-built lowering path is more
honest and lower-risk.

### Treat emitted QASM as claiming physical execution

Rejected — would weaken ADR 0071 / ADR 0200's carefully-maintained
`physical_execution_claimed=False` discipline for no reason; emission is
a text transformation, not a submission.

### Invent a QASM dialect extension instead of native `if`/`reset`

Rejected — QASM3 already has native syntax for exactly this physics;
inventing an alternate encoding would violate vision §2.2's "same
denoted physics" principle for no benefit.

## Follow-up work required after acceptance

1. Feature Path Issue: Circuit IR extension (`"reset"` GateName,
   conditional-block representation) + new Dynamic-lane lowering path +
   `QASM3Emitter` wiring, with Red tests for the three mapping rules in
   Decision 3, gated per Decision 4 (compilation success only).
2. Optional later Issue: CLI/REPL surface for requesting Dynamic-lane
   QASM output (mirrors `prepare_parametric_qasm`'s existing surface).

## Acceptance boundary

Acceptance of this ADR approves the **emission boundary and mapping
rules** in Decisions 1–5. It does not itself authorize Kernel/Host
implementation — a Feature Path Issue is required. It does not select a
live QPU provider or change any Dynamic-lane language surface or
capability law.

## Dependency Adoption Evidence

N/A — no new external dependency. Targets OpenQASM 3, already the
existing emission target for the Static QPU surface.
