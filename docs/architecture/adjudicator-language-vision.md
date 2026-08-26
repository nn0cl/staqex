# Adjudicator language vision (normative orientation)

| Field | Value |
|---|---|
| Status | **Accepted** (Adjudicator, 2026-07-31; **§2.2 Accepted 2026-08-08**) — normative orientation for language design and agent behavior |
| Authority | Adjudicator (human architect); not superseded by agent preference |
| Companions | [ADR 0095](decision-themes/dec-0003-language-surface-and-physicist-first-dx.md), [physicist-dx-harmony](physicist-dx-harmony.md), [axioms](staqex-language-axioms.md), [friction ledger](physicist-source-friction-ledger.md), [minimal dialect (Accepted)](physicist-minimal-dialect.md), [destructive simplification sketch](staqex-destructive-simplification-sketch.md), [ADR 0106](decision-themes/dec-0003-language-surface-and-physicist-first-dx.md), [ADR 0071](decision-themes/dec-0006-host-qpu-and-external-ports.md), [ADR 0111](decision-themes/dec-0006-host-qpu-and-external-ports.md) |
| Spec entry | [`staqex-language-specification.md`](../specs/staqex-language-specification.md) §1.1 |

This document captures the Adjudicator’s **orientation, ideals, and design
horizon** for Staqex. Agents must treat it as binding context when proposing
or changing language surface, semantics, diagnostics, examples, or ADRs.
Chat convenience, “what other quantum SDKs do,” or shortest-path-to-green
must not override it.

## 1. Audience and priority

**Staqex is a language for physicists.**

1. **Primary:** research physicist mental model — blackboard equations, states,
   operators, experiments, honest capability boundaries.
2. **Secondary, non-optional:** programmer DX (Clean Architecture / DDD,
   modules, visibility, ports) so large programs stay maintainable.

When (1) and (2) conflict, **prefer (1)**. DX must have a physics reading; it
must not rewrite chalk into enterprise or gate-DSL ceremony.
See [physicist-dx-harmony](physicist-dx-harmony.md).

## 2. Design horizon (ideal form first)

Per [ADR 0095](decision-themes/dec-0003-language-surface-and-physicist-first-dx.md):

- Aim at the **correct final form** of the language, not the shortest path to
  something that runs.
- **Machine convenience never shapes the surface** (term counts, circuit depth,
  compile time, simulation cost are not grounds to *restrict or rewrite* what
  a physicist may **write** on the language surface).
- Classify failures as **bug / documented deferral / genuine design gap**
  before using them as design evidence.
- “It runs” is not acceptance.

### 2.1 What “machine convenience never shapes the surface” does **not** mean

This rule is about **notation and meaning**, not about promising that every
writable program executes on every device.

| Allowed / required | Forbidden |
|---|---|
| Physicist writes the blackboard form | Truncating or reshaping chalk so the compiler is happier |
| Target/profile rejects unsupported work **explicitly** | Silent success, Host fake-emulation, or “close enough” lowering |
| Cost, depth, qubit count as **diagnostics / capability checks** | Using those costs to ban or rename the surface spelling |

**Writeable ≠ executable on a chosen target** separates **meaning** from
**realization**. It does **not** mean “Staqex programs are non-executable,”
and it does not weaken §2.2: when a target can realize the written meaning, it
must realize *that* meaning; when it cannot, it rejects explicitly without
rewriting the chalk. Feasibility is enforced by fail-closed compilation,
capability profiles, and Host submission contracts
([ADR 0106](decision-themes/dec-0003-language-surface-and-physicist-first-dx.md),
[ADR 0071](decision-themes/dec-0006-host-qpu-and-external-ports.md),
[ADR 0111](decision-themes/dec-0006-host-qpu-and-external-ports.md)) — not by
bending the surface into a gate-DSL. Physics-facing feedback should name the
capability or law that failed (diagnostic codes / Job results), not fail
silently.

A separate “executability ADR” is **not** required to accept this vision; those
boundaries are already accepted. New ADRs are needed only when a *new* rejection
or feedback shape is proposed.

### 2.2 Source must denote the same thing as the blackboard

What a physicist writes while thinking on the blackboard — including the
intermediate forms of that thought process — must remain the **same denoted
physics** when expressed as a Staqex program. The program is not a loose
translation into a different dialect; it is the blackboard’s **canonical
written form** under one meaning.

**Same meaning** means: reading the source recovers the same physics narrative
the chalk expressed (states, operators, expansions, juxtapositions, and
attached intent such as lane markers or region attributes). It does **not**
require glyph-for-glyph identity with a particular chalkboard rendering
(presentation affordances such as ASCII source spelling remain allowed when
they preserve semantics — see ADR 0191 / ADR 0189).

**Intentional transform has priority.** When the physicist deliberately
rewrites — expands a sum, substitutes an equivalent operator, factors a term,
or chooses a lane-appropriate spelling (for example an explicit circuit form)
— that intentionally written form becomes the new blackboard and therefore the
new program positive. Machine- or DX-driven forced rewrites that change the
denoted narrative without that intent are forbidden. Intentional transform
never authorizes violating §3 axioms (Never Leave the State, `when` not `if`,
terminal `measure`, and related laws).

**Composition stability (corollary).** Expanding, rewriting, or combining
independently well-formed blackboard fragments must not silently drop enclosing
structure or attached intent, and must not force a flatten-to-gates or a new
grammar category *only* so fragments can sit together. Unsupported composition
fails closed with an explicit diagnostic and, when still open, is recorded in
the friction ledger / Issues — not papered over in official examples.

| Layer | What “same” requires |
|---|---|
| **Meaning (source ↔ blackboard)** | Same denoted physics narrative and attached intent |
| **Realization (target / profile)** | Realize that meaning when capable; otherwise explicit reject — never a silent different meaning |

This clause forbids the §4 anti-pattern (equation → broken DSL → QPU port) at
the surface. It does not invent open lane semantics by implication, and it
does not promise every composition runs on every device (§2.1).

## 3. Non-negotiable physics laws (object language)

From axioms and the normative spec:

- **Never Leave the State** — mid-program values stay in the joint; collapse
  only at terminal `measure` in the Static Kernel lane.
- **`mix` not `if`** — classical short-circuit control is rejected so unitary /
  mixture narratives stay honest.
- **No classical `while` / bare `for` as Joint control** inside the Static
  Kernel — state update uses `evolve` (and related pure Joint transformers).
- Fail-closed diagnostics; no silent “success” for unsupported realization.

These are **physics-protecting** disciplines, not programmer pedantry.

### 3.1 Outer vs Kernel vs lane surfaces (do not conflate)

Vision §3 applies to the **Static Kernel object language**. It does **not**
mean “all repetition in the product is `evolve`” or “no iteration exists
anywhere.”

| Layer | Role | Repetition / control (normative sketch) |
|---|---|---|
| **Static Kernel** | NLTS Joint evolution; terminal `measure` | `evolve`; `mix`; **no** classical `if` / `while` / bare `for` |
| **Static QPU / Hilbert surface** | Explicit register factors | Static **`forEach`** elaboration over `QubitRegister<N>` ([ADR 0069](decision-themes/dec-0005-quantum-operations-and-runtime.md)) — not a classical loop over measured bits |
| **Parametric lane** | Symbolic gate parameters | `Param<T>` + Host binding ([ADR 0070](decision-themes/dec-0006-host-qpu-and-external-ports.md)) |
| **Dynamic QPU lane** | Feed-forward / mid-circuit (capability-gated) | Separate `dynamic qpu` surface; unsupported → reject ([ADR 0071](decision-themes/dec-0006-host-qpu-and-external-ports.md)) |
| **Host / Outer** | Jobs, sweeps, workflow, classical orchestration **outside** NLTS | Host lifecycle, parameter sweeps, algorithm drivers ([ADR 0065](decision-themes/dec-0006-host-qpu-and-external-ports.md), ADR 0106 `workflow`) — classical iteration belongs **here**, not smuggled into Kernel `if`/`for` |

Discrete algorithms (e.g. QFT / Grover-style iteration) are expressed with the
**lane-appropriate** surface (`forEach`, parametric circuits, dynamic lane when
accepted, or Host-outer drivers) — **not** by forcing every discrete step into
Hamiltonian `evolve`. Agents must not “fix” Outer or QPU-lane needs by
warping Kernel axioms, nor “fix” Kernel physics by importing classical loops.

## 4. What Staqex refuses (industry anti-pattern)

Agents must not recreate:

> beautiful equation → awkward / broken DSL spelling → port to QPU and call it done.

Equation-breaking workarounds in samples (hardcoded Hamiltonians beside unused
parameter packs, literal-only couplings because named `J` falsely trips LINEAR,
gate tourism as showcase) are **defects or sample debt**, not style.

Honest gaps: [physicist-source-friction-ledger](physicist-source-friction-ledger.md).
Coefficient elaboration vs LINEAR: [ADR 0114](decision-themes/dec-0002-state-first-semantics-and-measurement.md)
(**Accepted**; implement via LISS-0121 after phase approval).

## 5. Tone and claims

- Do **not** use marketing slogans (“apologize-free for senior programmers,”
  “dual-excellence” hype) as north-star copy.
- State the **joint professional standard** in plain terms: research-grade
  physics reading **and** Clean Architecture / DDD discipline under one meaning.
- Prefer precise diagnostics and ledgers over aspirational adjectives.

## 6. Agent obligations

When designing or changing language-affecting work, agents must:

1. Read this file (and ADR 0095 + physicist-dx-harmony) on Architecture Path
   and on Feature Path that touches language surface, semantics, diagnostics,
   or official examples.
2. In `[DESIGN CHECK]`, state whether the proposal preserves physicist-first
   spelling or intentionally diverges (divergence requires Adjudicator
   Architecture approval).
3. Prefer fixing Kernel/spec honesty over teaching workarounds in `examples/`.
4. **Stop and ask** only when a change would make the **language surface or
   semantics** less like the blackboard **for machine or DX convenience**
   (warping chalk to fit gates, silencing fail-closed, classical control inside
   Kernel, etc.). This does **not** forbid proposing optimizations, lowering
   strategies, capability checks, Host-outer designs, or performance work that
   **preserve** the surface and fail-closed honesty — put those in the design
   note; do not treat every engineering idea as an automatic hard stop.

### 6.1 Friction ledger and Adjudicator response (operations)

When ideal (blackboard) and reality (compiler / simulator / QPU profile) diverge:

1. **Record** the gap in
   [physicist-source-friction-ledger](physicist-source-friction-ledger.md)
   and/or a local Issue (class A–E as in that ledger).
2. **Do not** paper over the gap in official examples.
3. **Continue** non-blocked work when the gap is classified and does not
   require inventing surface meaning; state the classification in the design
   note or handoff.
4. **Stop for Adjudicator** when choosing among design options, accepting a
   deferral that would force later breakage, or changing axioms / vision /
   accepted ADR premises.

Numeric “SLA” for Adjudicator turnaround is **out of scope** for this vision
file; process cadence lives in collaboration docs. The obligation here is
**honest recording + correct stop vs continue**, not silent drift.

## 7. Relationship to other documents

| Document | Role |
|---|---|
| This file | Adjudicator vision / priority / anti-patterns / boundary clarifications (living; agents bind here), including §2.2 blackboard↔source sameness |
| `staqex-design-philosophy.md` | Historical archive of design intent; defer to this file + ADR 0095 on conflict |
| ADR 0095 | Ideal-form operational rules |
| ADR 0106 / 0069 / 0070 / 0071 / 0111 | Lanes, capability rejection, delivery honesty (executability ≠ surface folding) |
| physicist-dx-harmony | DX ↔ physics reading table |
| Language axioms + normative spec | Immutable laws and conformance |
| Friction ledger | Honest current gaps (not permission to ignore vision) |
| Agent contracts (`AGENTS.md`, `CLAUDE.md`, mirrors, Cursor rules) | Must point here so all agent families inherit the same orientation |
