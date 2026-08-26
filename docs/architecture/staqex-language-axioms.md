# Staqex Language Axioms

These axioms are **immutable product law** for Staqex (Quantum-Probabilistic
Executable). Agents and humans must not reintroduce deterministic scalar
programming as the default mental model.

Audience and design priority: Staqex is a language **for physicists**;
programmer DX is secondary. See
[Adjudicator language vision](adjudicator-language-vision.md) and
[physicist-dx-harmony](physicist-dx-harmony.md).

Normative decisions: ADR 0013 (axioms), ADR 0014 (MVP Discrete PMF),
ADR 0017 / **0024** (surface vocabulary — `mix` / `class` / packages).

These axioms say what Staqex *means*. What Staqex is *aiming at* — the ideal
final form of a language for generalized quantum computers, rather than the
shortest path to something that runs — is
[ADR 0095](decision-themes/dec-0003-language-surface-and-physicist-first-dx.md). Where an older
document's "MVP" framing appears to set a lower target than these axioms
imply, ADR 0095 governs: that framing is historical scope, not end-state.

## Axiom 1 — Every value is a probability distribution (joint store)

There is no classical “certain scalar” as a first-class runtime value.
Literals such as `10` denote a distribution (in MVP: a Dirac Discrete PMF
concentrated on `10`), not a bare integer. The runtime store is a **joint**
distribution on the product of declared variable supports, not a map from
names to independent scalars (see formal semantics sketch).

## Axiom 2 — Every operation is a probabilistic operation

`A + B`, `A - B`, and `A * B` are operations on distributions (convolution or
pushforward), never plain numeric ALU ops on collapsed scalars.

## Axiom 3 — Superposition via `mix` (not classical `if`)

Classical `if` is rejected (jump + discard ≈ early collapse narrative).
`mix (c) { … }` keeps all positively weighted arms in a mixture / linear span
controlled by condition state `c` (former surface `span`; ADR 0024).
**Kernel PoC A/B do not require `mix` yet.**

## Axiom 4 — Evolution via `evolve` (not classical loops)

Classical `while` / bare `for` loops are rejected in the Static Kernel. Pure
multi-step state update uses `evolve`, including bounded `evolve … until … max N`
(ADR 0079). Terminal `return` in an ordinary `fn` is a **pure value boundary**
(ADR 0068), not a classical loop or observation.

**Kernel PoC A/B do not require `evolve` yet.**

## Axiom 5 — Collapse only at measurement

Distributions remain uncollapsed through pure computation. Sampling /
collapse to a single outcome occurs only at an observation boundary
(`measure` in current surface; ADR 0017). Side-effecting report of a measured
outcome uses `MeasureSinkPort`; it must not silently collapse earlier
expressions.

## MVP enforcement scope (Adjudicator-approved)

| Topic | Status |
|-------|--------|
| Discrete PMF values (joint store) | In scope (ADR 0014, semantics sketch) |
| Arithmetic `+`, `-`, `*` | In scope |
| `measure` collapse | In scope (terminal sampling only) |
| `mix` / `evolve` | Syntax baseline (ADR 0017 → 0024); Kernel PoC A/B not required |
| `if` / `while` / bare `for` | **Rejected** as surface (use `mix` / `evolve`) |
| `return` in ordinary `fn` | **Allowed** as pure terminal value (ADR 0068) |
| `evolve … until` | **Shipped** bounded repetition (ADR 0079) |
| Continuous / sample bags | Non-decision |
| Amplitude / QPU IR | Stance (a): lift later (ADR 0016) |

## Axiom 6 — No exceptions (failure is a world-line)

`throw` / `try` / `catch` are rejected. Encode failure as orthogonal basis
labels (`Success` / `Error`) under `mix`; discard arms with `project`
(ADR 0025).

Do **not** conflate world-line labels with Host `JobResult` failures or QPU
capability rejects. Shared glossary: [ADR 0175](decision-themes/dec-0003-language-surface-and-physicist-first-dx.md)
(**Accepted**).

## Axiom 7 — No threads (concurrency is the model)

`Thread` / `async` / `await` are rejected in the object language. Simultaneous
evolution is `mix` and joint product; engines may parallelize invisibly
(ADR 0028).

## Forbidden reasoning patterns

- Treating `state x = dirac(10)` as binding a classical `i64`.
- Implementing `+` as integer addition of collapsed samples unless the
  specification explicitly describes a measure-then-operate path (MVP does
  not).
- Collapsing inside arithmetic “for convenience”.
- Classical short-circuit `if` that discards the other branch’s mass.
