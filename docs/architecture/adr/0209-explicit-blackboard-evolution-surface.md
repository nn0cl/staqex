# ADR 0209: explicit blackboard evolution surface and target realization

## Status

**Accepted** (2026-08-14) — Architecture approval recorded from the
Adjudicator's approval of the explicit blackboard-evolution boundary and the
bounded explicit-iteration design amendment. The bounded minimum slice has
completed its reviewed Red and Phase 2 Green gates. QPU realization, formal
`Limit` execution, broad migration, and Phase 3 closeout remain outside this
ADR's completed implementation scope.

Related records:

- [LISS-0437](../../issues/LISS-0437-explicit-evolution-surface.md)
- [WP-0100](../../work-plans/WP-0100-explicit-evolution-surface.md)
- [Explicit evolution acceptance specification](../../specs/staqex-explicit-evolution-surface.md)
- ADR 0195: real \(\hbar\) Hamiltonian dynamics
- LISS-0414: bracketed `Evolve { … }.run()` syntax

## Context

The current Hamiltonian form is physically meaningful:

```staqex
State psi_t = Evolve { psi under H for t }.run()
```

Under ADR 0195 it denotes

\[
\lvert\psi(t)\rangle=e^{-iHt/\hbar}\lvert\psi(0)\rangle.
\]

However, the source hides the derivation that a physicist may write on the
blackboard: the identity operator, the infinitesimal generator, the finite
product or exponential, and the application of the propagator to the State.
The language therefore makes `Evolve` appear to create the physics rather
than execute a physics expression already written by the user.

This conflicts with the accepted physicist-first rule that source must denote
the same physics narrative as the blackboard. It also prevents a target
reviewer from seeing what part is mathematical meaning and what part is QPU
realization.

## Decision

### 1. `Evolve` accepts an explicit state-transforming expression

The canonical shape becomes:

```staqex
Operator exponent = -i * H_obj * dur / hbar
Operator U_t = exp(exponent)

State evolvedState = Evolve() {
    U_t * psi_sel
}.run()
```

The one-expression form is also valid:

```staqex
State evolvedState = Evolve() {
    exp(-i * H_obj * dur / hbar) * psi_sel
}.run()
```

`Evolve()` is an execution boundary for the explicit transformation. It does
not infer `H`, `t`, `hbar`, `exp`, a time step, an approximation order, or a
gate decomposition.

### S02 canonical derivation and source shape

The representative S02 program must expose the same sequence as its
blackboard derivation:

\[
|\psi_0\rangle
\rightarrow
|\psi_{sel}\rangle=\frac{P_F|\psi_0\rangle}{\|P_F|\psi_0\rangle\|}
\rightarrow H_{obj}
\rightarrow U_t=e^{-iH_{obj}t/\hbar}
\rightarrow |\psi_{final}\rangle=U_t|\psi_{sel}\rangle.
\]

The target source shape is:

```staqex
State psi_projected = project psi_0 onto P_F
State psi_sel = psi_projected / ||psi_projected||

Operator H_obj = scale * objective_hamiltonian(
    weights, n, activity_w, selectivity_w
)
Time dur = 0.6.fs

Operator exponent = -i * H_obj * dur / hbar
Operator U_t = exp(exponent)

State psi_final = Evolve() {
    U_t * psi_sel
}.run()

Measure psi_final
```

The fully expanded source form may also write the construction before the
exponential:

```staqex
Operator U_dt = I - i * H_obj * dt / hbar
Operator U_t = Limit N -> Infinity {
    (I - i * H_obj * dur / (N * hbar)) ^ N
}
```

The `Limit` form and the `exp` form must denote the same mathematical
propagator when their preconditions hold. `Evolve()` receives the completed
`U_t * psi_sel` transform; it must never receive a bare `psi_sel` and infer a
propagator.

### 2. Identity is not evolution

The following is not an evolution expression:

```staqex
Evolve() { psi_sel }.run()
```

when `psi_sel` is an ordinary `State<T>`. It must fail closed with a dedicated
diagnostic. The compiler must not promote an identity or bare State into a
Hamiltonian evolution.

The same rule applies to `I * psi_sel`: it is an explicit identity operation,
not a time evolution, unless the source also supplies a non-identity
generator or propagator.

### 3. User-facing `Evolution<T>` is not required

The compiler may construct an internal `Evolution<T>` semantic IR value from
an explicit state-transforming expression. Users do not need to annotate that
type. The visible type distinction is:

```text
State<T>                  ordinary state
Operator                  generator or propagator
Operator * State<T>       state-transform expression
Evolve() { transform }
  .run()                  State<T>
```

An already materialized `State<T>` is not re-wrapped as an evolution.

### 4. Blackboard derivation remains expressible

The source may show the derivation explicitly:

\[
I
\rightarrow I-\frac{iHdt}{\hbar}
\rightarrow
\lim_{N\rightarrow\infty}
\left(I-\frac{iHt}{N\hbar}\right)^N
\rightarrow e^{-iHt/\hbar}
\rightarrow U(t)\lvert\psi\rangle.
\]

Whether a formal `Limit` is executable is a target decision. Its source
meaning must not be discarded merely because a selected QPU cannot execute a
formal limit.

### 5. Target realization is a separate phase

The compiler may lower the same explicit meaning to:

- exact matrix or sparse simulation;
- an accepted finite product;
- Trotter/Suzuki decomposition with explicit order and steps;
- provider-neutral QPU IR and supported gate operations.

If the selected profile cannot realize the expression, it returns an explicit
capability or realization diagnostic. It must not silently replace the
equation, invent a step count, or change `H`, `t`, or \(\hbar\).

For QPU deployment, the source meaning ends at the explicit propagator
application. The target realization then has a separately reported boundary:

```text
U_t = exp(-i H_obj dur / hbar)
  -> exact simulator exponential, or
  -> explicit Suzuki/Trotter policy
  -> Pauli rotations
  -> provider-neutral QPU IR
  -> target gate set
  -> terminal Measure
```

The QPU path must report whether it is exact or approximate, the order and
step count (or accepted error policy), resource estimates, and rejected
capabilities. This is a realization of the written equation, not a rewrite of
the source equation.

### 6. Existing `times N` evolution remains separate

`Evolve (seeds) times N { block }` is a repeated pure State pushforward. It is
not reinterpreted as Hamiltonian exponentiation and is not merged with the
explicit propagator surface by this ADR.

### 7. Bounded explicit evolution is a distinct visible mode

The accepted bounded form is:

```staqex
State result = Evolve() {
    U_dt * fuel
    until converged(fuel)
    max 64
}.run()
```

Its blackboard denotation is:

\[
\mathrm{fuel}_0\xrightarrow{U_{dt}}\mathrm{fuel}_1
\xrightarrow{U_{dt}}\cdots\xrightarrow{U_{dt}}\mathrm{fuel}_k,
\quad 1\leq k\leq64,
\]

where the pure predicate is evaluated after every transform. The initial
State is not checked. The same explicit transform is reapplied to the one
live State carrier; this mode is not one application, `U_dt^64`, an inferred
Hamiltonian evolution, or the existing `times N`/`for dt` pushforward.

For the first slice, `max` is a required positive integer literal. Zero,
negative, dynamic, and omitted bounds are rejected. `converged(state)` is a
non-measuring, non-RNG, non-mutating, non-collapsing comparison of the full
logical State with the immediately preceding State using the declared kernel
norm-difference tolerance. Failure to converge by `max` emits
`EVOLVE_UNTIL_MAX_STEPS_ERROR` and publishes no partial State.

The simulator owns this loop. QPU lowering rejects predicate-dependent early
termination before allocation and emits no partial circuit. A finite `max`
does not authorize fixed unrolling or a single-step replacement. `until` is
not added to `times` or `for` by this decision. Approximate realization
metadata must report iteration count, realization policy, and total error
budget where applicable.

The first-slice grammar is fixed as:

```ebnf
bounded_explicit_evolve ::= "Evolve" "(" ")" "{" evolve_let*
    explicit_transform "until" convergence_predicate "max" positive_integer
    "}" "." "run" "(" ")"
explicit_transform ::= operator_expression "*" state_expression
convergence_predicate ::= "converged" "(" state_reference ")"
evolve_let ::= let_binding /* existing Evolve body binding */
operator_expression ::= operator_primary operator_tail*
state_expression ::= state_reference | "(" state_expression ")"
state_reference ::= identifier /* live State carrier in this body */
operator_primary ::= identifier | "exp" "(" operator_expression ")"
operator_tail ::= operator_binary operator_primary
operator_binary ::= "*" | "+" | "-" | "/" | "^"
```

`let_binding` and operator precedence refer to the existing language grammar;
the bounded form adds no second expression grammar. Type checking requires the
final expression to denote `Operator * State`.

`max` is a positive decimal integer literal. The first simulator contract
uses full-logical-State absolute L2 difference, finite Float64 amplitudes, and
an absolute tolerance of `1e-9`. The predicate is evaluated only after each
transform. Bounded provenance records the source transform, predicate,
metric, numeric type, tolerance, iteration count, max, stop reason, and
realization. These details are source/semantic contracts; adapters may not
replace them with a basis-support test or a different tolerance.

On `max` exhaustion, the diagnostic and execution trace must expose the
complete provenance record with these exact required fields:
`source_transform`, `predicate`, `metric`, `numeric_type`, `tolerance`,
`iteration_count`, `max_steps`, `stop_reason`, and `realization`. No
intermediate/final State, State amplitudes, or resumable handle may be
published, rebound, resumed, or sent to terminal `Measure`.

## Consequences

### Positive

- S02 can show `U_t = exp(-i * H_obj * dur / hbar)` directly.
- A physicist can write the derivation and the program with the same narrative.
- Source provenance can retain generator, exponent, propagator, and State
  application nodes.
- Simulator and QPU lowering become visible realization choices rather than
  hidden meaning changes.
- Unsupported target capabilities fail honestly.

### Costs and risks

- Operator `exp`, complex `i`, operator powers, and dimensionless exponent
  checking need a precise language contract.
- The parser, AST, typechecker, semantic IR, simulator lowering, QPU IR, and
  diagnostics all cross the same feature boundary.
- Formal limits may be writable but not executable on an MVP target.
- Existing linear-use analysis may need a shared-expression/DAG treatment for
  blackboard equations; no-cloning rules must not be weakened to solve this.
- Existing Hamiltonian syntax needs an explicit migration decision.

## Boundaries and non-goals

- No vendor SDK, credential, datastore, or live QPU provider is selected.
- No new dynamic QPU semantics are introduced.
- No automatic Hamiltonian discovery from a bare State is introduced.
- No silent natural-unit fallback is introduced; ADR 0195 remains authoritative.
- No user-facing `Evolution<T>` ceremony is required.
- No change is made to terminal `Measure`, `RngPort`, or the Static Kernel
  prohibition on early collapse and classical `if`/`while`/bare `for`.

## Proposed diagnostics

The following diagnostic names are frozen for the acceptance contract:

- `EVOLVE_REQUIRES_EXPLICIT_TRANSFORM`
- `OPERATOR_EXP_DOMAIN_ERROR`
- `EVOLUTION_DIMENSION_ERROR`
- `EVOLUTION_TARGET_UNSUPPORTED`
- `EVOLUTION_REALIZATION_REQUIRED`
- `EVOLUTION_APPROXIMATION_POLICY_MISSING`
- `EVOLUTION_PROVENANCE_LOST`
- `EVOLVE_UNTIL_MAX_STEPS_ERROR`

`EVOLVE_HAMILTONIAN_SHORTCUT_RETIRED` is a migration diagnostic for the
current hidden Hamiltonian spelling during the bounded Phase 2 compatibility
window. A future strict migration/profile gate must promote it to a compile
error before broad migration. It is never an alias for explicit mode. A rejected target
must return no executable circuit or partial program. Target-neutral realization metadata
must include exact/approximate status, policy, order/steps or error budget,
resource estimate, and capability rejection when applicable.

### Phase 3 design amendment: closed provenance and binder capability witness

Before any Phase 3 implementation, all explicit evolution paths share one
target-neutral provenance envelope: source span, source transform, state shape,
realization kind, realization policy, approximation order/steps or error
budget, resource estimate, and capability rejection. Binder-aware QPU lowering
also records binder kind/domain, bound symbols, acting register, operator
family, and register mapping. A target adapter may consume this witness but
may not derive missing physics or approximation policy.

Allocation is forbidden until every binder has a finite declared domain and a
register mapping, and the target profile supplies the required exact or
approximate realization policy. Missing data, unsupported operators, or budget
excess returns a rejected provenance envelope and no circuit.

The target profile contract includes a typed
`register_mapping: Map<acting_register, logical_register_span>` field. The
finite-binder witness `{"Sigma": "q[0..7]"}` is explicit target capability
evidence; mapping is never inferred from binder spelling or resource estimates.
Missing or incomplete mapping is a capability rejection distinct from budget
overflow.

The stage boundary is typed: `ExplicitEvolution AST → EvolutionIR →
TargetPlan → Circuit | TargetRejection`. `EvolutionIR` must retain source span,
source transform, state shape, operator shape, binder witness, and realization
request. `TargetPlan` may add target policy, approximation, error budget, and
resource estimate, but may not remove or rewrite source meaning. Missing
provenance is `EVOLUTION_PROVENANCE_LOST` and fails before allocation.

If the resource estimate exceeds the declared target budget, lowering returns a
rejected envelope containing both estimate and budget, with no allocated qubit,
gate, or partial circuit.

The S02 migration is a separate numerical gate: its completed source/compiler
slice is not equivalent to numerical migration. Fixed-seed distribution and
benchmark comparison must pass before S02 or broad corpus migration is
promoted.

## Alternatives considered

### Keep `Evolve { psi under H for t }` as the canonical surface

Rejected for this proposal: it is compact but hides the mathematical
construction the language is intended to preserve.

### Remove `Evolve` and use only `U * psi`

Deferred: `Evolve` remains useful as an execution/lowering boundary and can
carry realization provenance. Removing it would conflate source expressions
with execution orchestration.

### Require users to write `Evolution<T>` explicitly

Rejected: it adds programming ceremony to a physics expression. The compiler
should infer the internal semantic category from the explicit transform.

### Let `Evolve { psi }` infer the missing Hamiltonian

Rejected: a bare State contains no generator, duration, or physical law from
which a unique evolution can be derived.

## Approval record

- Approval type: **Architecture approval**
- Approved scope: explicit blackboard evolution surface, S02 source
  correspondence, explicit propagator application, and separated target
  realization boundary.
- Accepted surface direction: `Evolve() { explicit-transform }.run()`;
  operator exponentiation and state application are language capabilities to
  be implemented under this ADR.
- Bounded explicit-iteration design: **Accepted by user 2026-08-14**. The
  accepted spelling is
  `Evolve() { U_dt * state until converged(state) max 64 }.run()` with
  post-transform-only pure convergence, positive literal `max`, simulator
  execution, and QPU fail-closed rejection before allocation. Red tests and
  Phase 2 Green implementation are complete for this minimum slice.
- Formal `Limit`: source-preserving capability remains subject to the MVP
  executable/source-only decision recorded in the companion Spec; no target
  may silently rewrite it.
- Implementation permission: **Phase 2 Green minimum slice approved by user
  2026-08-14**
- Approved implementation scope: explicit `Evolve()` parser/AST mode, source
  and type diagnostics, linear-use preservation, S02 source migration, and
  the source-only `Limit` boundary. QPU deployment and broad corpus migration
  are not approved by this record.
- Phase approval: **Phase 1 Red and Phase 2 Green approved** (2026-08-14)
- Phase 1 scope: create and run failing acceptance tests for the frozen
  source/compiler contract only; no production implementation or migration.
- Phase 1 implementation permission: **No**; Phase 2 Green implementation
  permission: **Yes, for the bounded minimum slice**
- Post-review requirement: **Yes**

Architecture approval does not grant Phase 1, Phase 2, or implementation
permission. Those remain separate gates under [WP-0100](../../work-plans/WP-0100-explicit-evolution-surface.md).
