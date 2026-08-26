# ADR 0189: Quantum mental model and observation contract

## Status

**Accepted** (2026-08-04) — direction approved by the Adjudicator. Follow-up
specifications and implementation remain separately gated.

**Superseded in part by [ADR 0190](0190-s02-selection-boundary-and-mix-control.md)**
(Accepted; Phase 2 implementation approved 2026-08-04): the compatibility
wording in §2 and the related Consequences bullet below, which treated
`when` as remaining valid until a future migration decision, is superseded.
ADR 0190 is the accepted decision: `mix` (not `superpose`) is the canonical
non-collapsing probabilistic/classified alternative spelling, `controlled`/
`Ctl` is reserved for coherent control, `superpose` is reserved for coherent
phase-preserving semantics only, and `when` is retired with no compatibility
alias. The historical text below is preserved as the original decision
record; it is not the current accepted rule.

## Design check

- **Scope and expected behavior:** Define the top-level language direction for
  scientific symbol spelling, quantum state composition, and observations.
- **Specifications and files inspected:** `AGENTS.md`,
  `staqex-language-axioms.md`, `adjudicator-language-vision.md`,
  `staqex-language-specification.md`, DEC-0002, DEC-0003,
  `runtime/joint.py`, `runtime/evaluator.py`, `runtime/mixed_state.py`, and
  the current specification verification inventory.
- **Component boundaries, ports/adapters, and VO/DTO candidates:** The
  language meaning belongs to the Kernel semantic model. Backend capability is
  represented separately by an Observation Contract and target profiles.
  Candidate semantic values are `State<T>`, `DensityState<T>`,
  `Observable<T>`, `Projection<T>`, and `Observation<T>`; the Host result
  remains a separate `JobResult` DTO.
- **Applicable constraints:** Physicist-first spelling, ideal-form-first
  design, Never Leave the State, terminal collapse, fail-closed execution, and
  one Staqex meaning across Python and future Rust implementations.
- **Decisions, assumptions, and unresolved ambiguities:** This ADR proposes a
  contextual scientific lexicon and a future `superpose` spelling. The exact
  reserved-name inventory, migration timing, and complete observation algebra
  remain open until the Adjudicator accepts the direction.
- **Included and omitted AI context:** Included current language axioms,
  canonical decision themes, normative specification, and the shipping Kernel
  state/measurement implementation. Omitted provider SDKs, QPU-specific
  lowering details, and historical ADR narratives because this is a semantic
  direction decision.
- **Task routing (model/assistant/tool):** Strong reasoning review for the
  architecture decision; deterministic repository inspection for current
  implementation claims.
- **Input/output evidence contract when AI output is involved:** Proposed
  rules must be traceable to this ADR and the cited current documents; no
  generated claim is implementation evidence until a conformance test or
  deterministic inspection supports it.
- **Verification plan:** Review this ADR before any grammar, lexer, parser,
  evaluator, or example changes. Later implementation must add conformance
  scenarios for each accepted observation and migration rule.

## Context

Staqex is intended to make a programmer hold a physical state and its formula
in mind at the same time. The project therefore asks the programmer to update
the classical programming mental model rather than merely adding quantum
operations to a conventional scalar language.

The current accepted surface already rejects classical `if`, ordinary loops,
implicit exceptions, and premature measurement. It also defines `State<T>`,
`DensityState<T>`, `when`, `evolve`, `expect`, `inspect`, `project`, and
terminal `measure`.

The shipping Kernel is a meaningful first implementation: it stores finite
worlds with complex amplitudes, supports amplitude coalescing and some
interference, applies selected unitaries and Hamiltonians, supports limited
density-state paths, and preserves terminal measurement. It is not yet a
general Hilbert-space or complete observable-calculus implementation. The
language direction must be explicit about this distinction rather than
allowing implementation shortcuts to define the ideal semantics.

## Decision proposal

### 1. Scientific symbols are a language facility, not ordinary identifiers

Staqex will provide a contextual scientific lexicon for physicist-facing
notation. Common symbols such as `psi`/`ψ`, `phi`/`φ`, `rho`/`ρ`, `H`, and `U`
may be written through stable ASCII aliases when Unicode input is inconvenient.
The aliases are part of the language vocabulary and are preserved in the
syntax/semantic representation as scientific names.

This does **not** make every Greek letter a globally reserved keyword or give
`psi` a hidden classical value. A scientific name still denotes a declared
state, field, operator, or formula according to its typed context. The exact
inventory and shadowing rules require a follow-up surface specification.

The purpose is to reduce keyboard friction while keeping the source close to
the blackboard. ASCII aliases are an input affordance, not a second semantics.

### 2. Quantum state composition must not share the classical meaning of `when`

The current `when` construct is semantically state-preserving, but its name is
strongly associated with classical branching in languages such as Kotlin. The
future canonical spelling should therefore distinguish quantum composition
from classical case selection.

> **Superseded (see Status):** the illustrative pattern and naming below
> predate ADR 0190. The "all positively weighted arms remain, no sampling"
> behavior described here is the `mix` lane, not `superpose`, under the
> accepted taxonomy; `superpose` is reserved for coherent, phase-preserving
> composition. The "compatibility form" sentence is also superseded — `when`
> is retired with no compatibility alias.

The proposed canonical spelling is `superpose`, subject to surface review. It
expresses that all positively weighted arms remain part of the resulting state
and that the construct is not a short-circuit branch. The existing `when`
spelling remains a compatibility form until a migration decision is accepted;
it must not acquire classical `when`/`else` semantics.

Illustrative future form:

```staqex
state ψ = superpose(control) {
    0 -> evolve ψ under H₀ for t,
    1 -> evolve ψ under H₁ for t
}
```

This spelling is not intended to claim that every state composition is a
simple probabilistic mixture. The semantic distinction between classical
mixture, coherent superposition, controlled unitary evolution, and dynamic
feed-forward must be represented by types or lane contracts in the follow-up
specification.

### 3. Observation is a first-class semantic family

Observation is not limited to a single destructive `measure`. Staqex will
model observations as typed operations over states, with explicit physical
meaning and explicit execution capability.

| Operation | Semantic role | State collapse | Typical result |
|---|---|---:|---|
| `expect` | Expectation of an observable | No | scalar expectation value |
| `project` | Apply a projector and retain the resulting state | No implicit sampling | `State<T>` / vacuum |
| `inspect` | Non-destructive structural or amplitude view | No | diagnostic state view |
| `trace_out` | Partial trace over a subsystem | No sampling | reduced state |
| `measure` | Born sampling / physical observation | Yes | classical outcome and post-state contract |
| `tomography` | Repeated experiment protocol for state reconstruction | Repeated observations | Host observation report |

The first four are semantic Kernel operations. `measure` is the terminal
collapse operation in the Static Kernel. `tomography` is a Host/protocol
operation because it requires repeated executions and classical estimation;
its protocol status must not be confused with a single-shot state operation.

An operation may be semantically valid yet unsupported by a target. Such a
target must reject explicitly or report a documented capability boundary. A
backend must not replace an unavailable observation with a classical fake or a
silent early collapse.

### 4. Input and output have explicit boundary roles

Source text, parameter bindings, and device job metadata are classical
boundary representations. They do not imply that the program's internal
values are classical.

Inside the object language, intermediate values remain state, operator,
observable, projection, or observation-plan values. Classical values may be
introduced only by an explicitly typed Host boundary, a permitted expectation
projection, or terminal measurement according to the lane contract.

The Host `JobResult` is not the semantic state. It is a classical envelope
containing measured outcomes, observations, diagnostics, and execution
metadata.

## Consequences

- Physicists can use keyboard-friendly scientific names without making the
  language a collection of hidden classical variables.
- New surface design will no longer rely on `when` carrying both a familiar
  classical name and a non-classical meaning.
- Observation semantics can grow independently of backend support and can be
  checked before a live QPU provider exists.
- `tomography`, dynamic measurement, general POVMs, arbitrary density
  operators, and complete Hilbert-space operations remain staged capabilities,
  not claims of the current Kernel.
- Existing `when` programs remain valid during migration, but new canonical
  examples should wait for acceptance of the replacement spelling rather than
  silently changing current syntax. **Superseded by ADR 0190 (see Status):**
  `when` is retired with no compatibility alias and a hard diagnostic; it does
  not remain valid pending migration.
- The Python Kernel and future Rust implementation must share the observation
  contracts; neither implementation may define a narrower surface as the
  language ideal.

## Rejected alternatives

### Make all scientific symbols globally reserved

Rejected for now. It would consume ordinary identifier space, make modules
harder to compose, and confuse a symbol spelling with a pre-existing value.
Contextual scientific names provide the keyboard and notation benefit with a
smaller compatibility cost.

### Keep `when` and explain that it is different

Rejected as the long-term surface direction. Documentation can explain the
current meaning, but the collision with classical branching is a persistent
teaching and reading cost. Compatibility is useful; it is not sufficient as a
design horizon.

### Define every observation as a classical output

Rejected. `expect`, `inspect`, `project`, and `trace_out` can preserve a state
or expose a non-destructive projection. Treating all of them as classical
outputs would reintroduce the scalar mental model the language is intended to
replace.

### Promise that every observation runs on every target

Rejected. Semantic expressibility and target executability are separate
contracts. Capability profiles, lowering diagnostics, and explicit rejection
are required.

## Follow-up work required after acceptance

1. Define the scientific-name inventory, ASCII/Unicode aliases, token classes,
   declaration contexts, and shadowing rules.
2. Compare `superpose` with alternative quantum-specific spellings and define
   the migration path from `when`.
3. Specify the observation type family and its relationship to
   `State<T>`, `DensityState<T>`, `Observable<T>`, and Host `JobResult`.
4. Add conformance scenarios for non-destructive observation, terminal
   measurement, capability rejection, and no implicit collapse.
5. Reconcile the current finite Joint/limited density implementation with the
   semantic IR boundary for general Hilbert-space and observable operations.

## Acceptance boundary

Acceptance of this ADR approves the direction and follow-up specification
work. It does **not** authorize grammar changes, implementation changes,
breaking migration, or QPU-provider selection. Those require their own
reviewed specification and phase approval.
