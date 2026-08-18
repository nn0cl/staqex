# Staqex explicit evolution surface — acceptance specification

## Status and authority

- Status: **Accepted; bounded explicit-transform and finite Realize target
  slices complete** (2026-08-17) — direct `Limit` remains source-preserving
  and rejected unless converted through explicit `Realize`.
- Parent WorkPlan: [WP-0100](../work-plans/WP-0100-explicit-evolution-surface.md)
- Local Issue: [LISS-0437](../issues/LISS-0437-explicit-evolution-surface.md)
- ADR: [ADR 0209](../architecture/adr/0209-explicit-blackboard-evolution-surface.md)
- Related accepted context: ADR 0195 (real \(\hbar\) Hamiltonian dynamics),
  LISS-0414 (bracketed `Evolve { … }.run()` syntax), and the physicist-first
  language vision §2.2.

## Problem

The current Hamiltonian form

```staqex
State psi_t = Evolve { psi under H for t }.run()
```

denotes \(e^{-iHt/\hbar}\lvert\psi\rangle\), but the source does not show
the generator, the exponential, or the state/operator application. This
makes `Evolve` appear to be the place where the physics is invented rather
than the place where an explicitly written evolution is executed.

The language must preserve the physicist's written derivation while still
allowing the compiler to lower it to a simulator or QPU target.

## Proposed canonical surface

The user writes the evolution operator and its application explicitly:

```staqex
Operator exponent = -i * H_obj * dur / hbar
Operator U_t = exp(exponent)

State evolvedState = Evolve() {
    U_t * psi_sel
}.run()
```

The preferred compact form, when the derivation is intentionally written as
one expression, is:

```staqex
State evolvedState = Evolve() {
    exp(-i * H_obj * dur / hbar) * psi_sel
}.run()
```

`Evolve()` does not infer `H`, `t`, `\hbar`, an exponential, a time step, or a
gate decomposition. It accepts a body whose final expression already denotes
an evolution from an input State to an output State.

## S02 blackboard-to-source correspondence

S02's intended physics is:

\[
|\psi_0\rangle
\rightarrow
|\psi_{sel}\rangle=\frac{P_F|\psi_0\rangle}{\|P_F|\psi_0\rangle\|}
\rightarrow H_{obj}
\rightarrow U_t=e^{-iH_{obj}t/\hbar}
\rightarrow |\psi_{final}\rangle=U_t|\psi_{sel}\rangle.
\]

The corresponding target source is:

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

For a physicist who wants to write the derivation all the way from the
infinitesimal step, the source may instead contain:

```staqex
Operator U_dt = I - i * H_obj * dt / hbar
Operator U_t = Limit N -> Infinity {
    (I - i * H_obj * dur / (N * hbar)) ^ N
}
```

The MVP accepts the `exp(Operator)` form as executable. A QPU target may
realize it only when the target boundary supplies an accepted finite Suzuki
policy; the source does not contain or imply that approximation choice. With
no target policy, the QPU path is rejected before allocation. The `Limit` form
is source-preserving but target-rejected until a finite realization policy is
attached; it is never silently rewritten to `exp`.

## Frozen semantic and dimensional boundary

The visible source denotes the following sequence:

\[
I \to I - iH\,dt/\hbar
\to \lim_{N\to\infty}(I-iHt/(N\hbar))^N
\to e^{-iHt/\hbar}
\to U(t)\lvert\psi(0)\rangle.
\]

The internal compiler may represent the final expression as an
`Evolution<T>` IR value, but `Evolution<T>` is not required as a user-facing
annotation. A bare `State<T>` is not an evolution value.

Normative typing intent:

```text
State<T>                  ordinary state
Operator                  operator / generator / propagator
Operator * State<T>       state-transform expression
Evolve { state-transform }
  .run()                  State<T>
```

`Evolve() { psi }.run()` is rejected when `psi` is only a `State<T>`; the
compiler must not silently reinterpret identity as time evolution.

The explicit form is a third, discriminated `Evolve` mode. It is distinct
from `Evolve (seeds) times N { ... }` (repeated pure pushforward) and
`Evolve (seeds) for dt { ... }` (one pure pushforward). The current bracketed
`Evolve { psi under H for t }.run()` is migration-only and emits
`EVOLVE_HAMILTONIAN_SHORTCUT_RETIRED` as a compatibility diagnostic during
the bounded Phase 2 corpus migration. It is not an implicit alias for the
explicit mode. A future strict migration/profile gate must promote this
diagnostic to a hard compile rejection before broad migration is complete.

`exp` in this specification is operator exponentiation, not scalar
exponentiation. `i` is dimensionless, `hbar` has the existing Energy*Time
dimension, and an operator exponent must be dimensionless. A Hamiltonian
generator therefore has Energy dimension and `dur` has Time dimension.
`Operator * State<T>` is valid only when the left operand is an Operator and
the right operand is a State with a compatible register/domain; it returns a
state-transform expression, not an ordinary scalar product. Operator powers
are valid only for a dimensionally valid repeated product and an integer or
explicitly supported exponent; their resulting dimension is checked before
`exp`. Identity and zero generators are valid explicit operators and produce
an identity propagator;
they do not authorize a bare State body. Non-Hermitian expressions remain
writable, but a unitary/QPU profile must reject them unless an accepted
realization proves the required unitary transform.

## EARS acceptance scenarios

### A — explicit propagator is preserved

**Given** a typed Hamiltonian `H`, duration `t`, and state `psi0`

**When** the source writes `exp(-i * H * t / hbar) * psi0` inside `Evolve()`

**Then** the compiler preserves the explicit operator-exponentiation and
state-application meaning through the semantic IR.

### B — intermediate derivation remains writable

**Given** a physicist writes `generator`, `U_t`, and `psi_t` as separate
bindings

**When** those bindings are used as the final expression of `Evolve()`

**Then** the program has the same denotation as the one-line expression and
the intermediate names remain visible to diagnostics and provenance.

### C — identity is not silently promoted

**Given** `psi0: State<T>` and no operator or evolution expression

**When** the source writes `Evolve() { psi0 }.run()`

**Then** compilation fails closed with a dedicated diagnostic explaining that
an explicit state-transforming evolution expression is required.

### D — explicit infinitesimal construction is representable

**Given** a source expression using `I - i * H * dt / hbar` and an explicit
finite product or limit representation

**When** the source contains that representation

**Then** the compiler preserves the written construction and does not replace
it with a hidden `under H for t` form. In the MVP, a formal `Limit` is
source-preserving but target-rejected with `EVOLUTION_REALIZATION_REQUIRED`.

### E — target lowering is separate from source meaning

**Given** an explicit `exp(-i * H * t / hbar)` expression

**When** a simulator or QPU profile is selected

**Then** the compiler either lowers that same meaning using an accepted exact
or approximate realization, or rejects it with a target-capability diagnostic.

### F — approximation policy is explicit

**Given** a formal propagator that requires Trotter/Suzuki realization

**When** the source or target profile supplies an explicit order/step policy

**Then** the target-neutral lowering records exact/approximate status, the
policy, order/steps or error budget, and a resource estimate; it must not
silently clamp or invent any of them. Rejection produces no executable
circuit or partial program.

### G — S02 remains blackboard-readable

**Given** S02's `H_obj`, `dur`, and `psi_sel`

**When** the source writes `U_t = exp(-i * H_obj * dur / hbar)` and applies it
to `psi_sel`

**Then** the program denotes the same \(\lvert\psi_{sel}(t)\rangle\) as the
current real-\(\hbar\) Hamiltonian path.

### L — bounded explicit evolution remains visible

**Given** an explicitly defined propagator `U_dt` and a State `fuel`

**When** the source writes:

```staqex
State result = Evolve() {
    U_dt * fuel
    until converged(fuel)
    max 64
}.run()
```

**Then** the source denotes the stepwise sequence

\[
\mathrm{fuel}_0\xrightarrow{U_{dt}}\mathrm{fuel}_1
\xrightarrow{U_{dt}}\cdots
\xrightarrow{U_{dt}}\mathrm{fuel}_k,
\qquad 1\leq k\leq64,
\]

with `converged(fuel_k)` evaluated after each transform. The predicate is
pure, non-measuring, non-RNG, non-mutating, and non-collapsing. The same
explicit transform is reapplied to the single live State carrier; it is not
replaced by one `U_dt`, by an inferred Hamiltonian, or by `U_dt^64`.

The `until` and `max` clauses are inside the `Evolve()` body and `.run()` is
after the closing brace. This is a third mode, distinct from both
`Evolve (seeds) times N { block }` and `Evolve (seeds) for dt { block }`.

### M — bounded iteration and failure contract

`max` is a required positive integer literal in this first slice. `max 0`,
negative values, dynamic expressions, and implicit bounds are rejected. The
initial State is not tested; the predicate is evaluated only after a
transform. If no post-transform State satisfies the predicate before `max`,
the compiler/runtime emits `EVOLVE_UNTIL_MAX_STEPS_ERROR` and publishes no
partially evolved State to later statements or terminal `Measure`.

`converged(state)` compares the full logical State against the immediately
preceding State using the kernel's declared norm-difference tolerance. It is
not a basis-support test and does not perform measurement. The tolerance and
numeric comparison are part of simulator provenance; QPU approximation must
not claim equivalence without a declared total error policy.

### N — target boundary for bounded iteration

The simulator may execute the bounded loop. QPU lowering rejects any
predicate-dependent early termination before allocation and emits no partial
circuit. A finite `max` does not make dynamic termination statically
equivalent. Fixed-count repetition remains the separate `times N` pushforward
mode; it is not introduced by adding `until` to the explicit mode. No QPU
target may silently lower bounded explicit evolution to a single transform or
to a fixed `max`-step circuit while claiming the predicate-controlled result.

### O — bounded grammar and numeric contract

The normative grammar for the first slice is:

```ebnf
bounded_explicit_evolve ::=
    "Evolve" "(" ")" "{" evolve_let* explicit_transform
    "until" convergence_predicate "max" positive_integer
    "}" "." "run" "(" ")"

explicit_transform      ::= operator_expression "*" state_expression
convergence_predicate   ::= "converged" "(" state_reference ")"
positive_integer        ::= decimal_integer /* value >= 1 */
evolve_let              ::= let_binding /* existing Evolve body binding */
operator_expression     ::= operator_primary operator_tail*
state_expression        ::= state_reference | "(" state_expression ")"
state_reference         ::= identifier /* live State carrier in this body */
operator_primary        ::= identifier | "exp" "(" operator_expression ")"
operator_tail           ::= operator_binary operator_primary
operator_binary         ::= "*" | "+" | "-" | "/" | "^"
```

The referenced `let_binding` and operator precedence are the existing language
grammar; this bounded form adds only the fixed `until`/`max` clause and does
not introduce a second expression grammar. Type checking narrows the final
expression to `Operator * State`.

`until` and `max` are part of the explicit bounded-evolution form, not a
general suffix for `times` or `for`. The initial State is not tested. The
predicate is evaluated after each `explicit_transform`, and the successful
iteration count is in `[1, max]`. The grammar rejects an omitted `max`, a
non-literal bound, `max 0`, negative bounds, and `until` attached to a
`times`/`for` pushforward.

For the MVP simulator, `converged(state)` means the absolute L2 norm of the
full logical State difference from the immediately preceding State is at most
`1e-9`, using finite `Float64` amplitudes. This is a non-measuring read-only
comparison; it is not a basis-support test, marginal measurement, or RNG
operation. The tolerance is fixed by this contract for the first slice and is
not silently changed by an adapter.

The bounded-evolution provenance record must preserve at least:

```text
source_transform
predicate = "converged"
metric = "full_state_l2_difference"
numeric_type = "Float64"
tolerance = 1e-9
iteration_count
max_steps
stop_reason = "predicate" | "max_exhausted" | "target_rejected"
realization = "simulator_exact_step" | "unsupported_qpu"
```

For every explicit evolution that crosses AST → semantic IR → target
lowering, the compiler uses the same target-neutral provenance envelope. The
envelope has these required fields:

```text
source_span
source_transform
state_shape
realization_kind = "exact" | "approximate" | "rejected"
realization_policy
approximation_order_or_null
approximation_steps_or_null
error_budget_or_null
resource_estimate_or_null
capability_rejection_or_null
```

Binder-aware lowering adds a closed capability witness rather than allowing an
adapter to invent policy:

```text
binder_kind
binder_domain
bound_symbols
acting_register
operator_family
register_mapping
```

Every bound symbol must resolve to a finite declared domain before QPU
allocation. Missing domain, unsupported binder/operator family, missing
register mapping, absent approximation policy, or exceeded resource budget
rejects with no circuit or partial program.

The target profile supplies register mapping as a typed field:

```text
register_mapping: Map<acting_register, logical_register_span>
```

For the accepted finite-binder slice, a mapping such as
`{"Sigma": "q[0..7]"}` is the explicit witness that the binder is target
supported. An absent or incomplete mapping is a capability rejection; it must
not be inferred from the source binder name or from the resource estimate.

Formal-to-finite conversion is explicit in source. A formal operator and its
realized approximation are different typed values:

```staqex
Operator U_formal = Limit N -> Infinity {
    (I - i * H * dur / (N * hbar)) ^ N
}
Operator U_qpu = Realize(
    U_formal,
    method = "suzuki",
    order = 2,
    steps = 8,
    error_budget = 1e-6
)
```

The compiler must preserve the relation between `U_formal` and `U_qpu`, and
must not insert `Realize`, choose `N`, or replace the formal expression with
`exp` implicitly. A formal `Limit` passed directly to a target remains
`EVOLUTION_REALIZATION_REQUIRED`.

The provenance envelope is a typed stage contract, not an optional metadata
map:

```text
AST ExplicitEvolution
  -> EvolutionIR { source_span, source_transform, state_shape,
                   operator_shape, binder_witness, realization_request }
  -> TargetPlan { realization_kind, realization_policy, approximation,
                  error_budget, resource_estimate, capability_witness }
  -> Circuit | TargetRejection { envelope, no_allocation = true }
```

Each arrow preserves the source span, transform, state shape, binder witness,
and realization request. `TargetPlan` may add target facts but may not remove
or rewrite them. A missing required field is `EVOLUTION_PROVENANCE_LOST` and
stops lowering before allocation.

When `stop_reason = "max_exhausted"`, the diagnostic and execution trace must
publish the complete provenance record, including `predicate`,
`iteration_count = max_steps`, metric, numeric type, tolerance, source
transform, stop reason, and realization. They must not publish the
intermediate or final `State`, bind it for later statements, or pass it to
terminal `Measure`.

### P — bounded acceptance scenarios

**P1 — one or more post-step checks**

Given a State `state0`, a propagator `U_dt`, and a predicate that becomes true
after the second application, when the bounded form runs with `max 4`, then
the simulator applies exactly two transforms, evaluates the predicate only
after each transform, returns the second State, and records
`iteration_count = 2` and `stop_reason = "predicate"`.

**P2 — no initial-State short circuit**

Given an initial State that already satisfies the convergence relation, when
the bounded form runs, then it still applies one transform before evaluating
the predicate and reports an iteration count of at least one.

**P3 — bound exhaustion is atomic**

Given a predicate that remains false through `max 3`, when the simulator runs,
then it emits `EVOLVE_UNTIL_MAX_STEPS_ERROR`, records
`stop_reason = "max_exhausted"`, and publishes neither the third intermediate
State nor a result binding to later statements or terminal `Measure`.
The diagnostic may expose only the provenance record required by scenario O,
not State amplitudes or a resumable intermediate value.

**P4 — predicate is a non-collapsing read**

Given a tuple or entangled State with phase information, when `converged(state)`
is evaluated, then no measurement or RNG operation occurs, amplitudes and
phases remain available to the next transform, and the live State carrier is
not duplicated or consumed by the predicate.

**P5 — target boundary is fail-closed**

Given a bounded explicit form with a predicate-dependent stop, when a QPU
target is selected, then lowering fails before allocation with a capability
diagnostic, emits no partial circuit, and never replaces the form with one
transform or a fixed `max`-step circuit.

**P6 — existing modes remain distinct**

Given `Evolve (seeds) times N { block }` or `Evolve (seeds) for dt { block }`,
when the source is compiled, then those forms retain their existing
pushforward semantics and are not parsed as bounded explicit evolution.

**P7 — formal Limit remains visible**

Given `Limit N -> Infinity { (I - i * H * dur / (N * hbar)) ^ N }`, when a
target has no explicit finite realization policy, compilation preserves the
Limit provenance and rejects before allocation with
`EVOLUTION_REALIZATION_REQUIRED`. It must not emit `exp`, choose a fixed `N`,
or return a partial circuit.

For a target that is explicitly authorized to execute the formal `Limit`, the
source must contain a finite realization policy through `Realize(source=...)`:

```text
method       = "suzuki" | "product"
order        = positive integer, when method is suzuki
steps        = positive integer, or an explicit bounded step policy
error_budget = explicit tolerance, when approximation is used
```

The target plan retains these fields, resource estimates, and approximation
evidence. Missing, malformed, or budget-exceeding policy is rejected before
allocation. The compiler must not infer `N`, order, duration, Hamiltonian, or
error budget, and must not rewrite the written `Limit` to `exp`.

The bounded QPU realization slice accepts explicit Suzuki plans as
provider-neutral finite gate plans. The written finite `product` is not treated
as a unitary QPU gate sequence and is rejected with an explicit capability
diagnostic. Diagnostic/rejection evidence is distinct from target-plan
provenance. A missing or malformed policy may retain diagnostic evidence, but
resource-budget rejection leaves no gates, allocation, partial program, or
target-plan provenance envelope.

**P8 — binder-aware target rejection**

Given a finite operator binder with a declared domain and no target register
mapping or approximation policy, lowering returns a diagnostic rejection record
and no circuit. That diagnostic record is not a target-plan provenance
envelope. Given a supported capability witness, lowering retains the binder
domain, register mapping, order/steps or error budget, and resource estimate in
the target-neutral result.

**P9 — S02 migration boundary**

The S02 source migration is accepted only after fixed-seed distribution and
benchmark comparison against the pre-migration baseline. The migration keeps
`H_obj`, `dur`, `psi_sel`, real `hbar`, host arrays, and terminal
`Measure psi_final`; it does not authorize bulk migration of other example
families.

**P10 — resource budget rejection**

Given a supported binder and operator family whose estimated qubit or gate
resource exceeds the declared target budget, lowering returns
`EVOLUTION_TARGET_UNSUPPORTED` as a diagnostic rejection. Allocation has not
started and the result contains no gates, qubits, partial circuit, or
target-plan provenance. The requested budget and estimate may appear only in
the transient diagnostic/reporting path, not in a retained provenance object.

### I — S02 exposes the complete time-evolution equation

**Given** S02's selected state, objective Hamiltonian, duration, and real
\(\hbar\)

**When** the source writes `U_t = exp(-i * H_obj * dur / hbar)` and passes
`U_t * psi_sel` to `Evolve()`

**Then** the source visibly denotes the propagator and its application, and
`Evolve()` does not infer either one.

### J — expanded and exponential forms agree

**Given** the infinitesimal/limit form and the exponential form under their
mathematical preconditions

**When** the expanded form has an explicit finite realization policy and both
forms are lowered to a capable exact simulator

**Then** both produce the same propagator denotation within the declared
numeric tolerance, while retaining separate source provenance.

### K — QPU realization boundary is reported

**Given** the explicit S02 propagator application

**When** a QPU target is selected

**Then** the compiler reports the exact or approximate realization, policy,
resource estimate, and capability limitations; it does not silently rewrite
the blackboard equation.

### H — physics laws remain enforced

**Given** an evolution body containing `measure`, classical `if`, or another
forbidden early-collapse/control construct

**When** the source is compiled

**Then** the existing physics-protecting diagnostics remain in force; explicit
evolution does not weaken Never Leave the State or terminal measurement.

## Out of scope

- A QPU vendor SDK, credentials, deployment service, or hardware adapter.
- A new datastore, job persistence scheme, or provider-specific schema.
- Mid-circuit measurement or dynamic feed-forward in the Static Kernel.
- Automatic discovery of a Hamiltonian from a bare State.
- Silent conversion of arbitrary classical expressions into quantum operators.
- Requiring users to write an `Evolution<T>` annotation.
- Removing `Evolve` entirely; its execution boundary remains useful.

## Frozen decisions for Phase 1

1. `exp(Operator)` and `Operator * State<T>` are the canonical spellings;
   `apply(U, psi)` is not a second surface in this issue.
2. The explicit `Evolve() { transform }.run()` mode is distinct from both
   pushforward modes and the old Hamiltonian shortcut.
3. Formal `Limit` is source-preserving and target-rejected in the MVP.
4. Phase 1 Red covers parser, diagnostics, source preservation, mode
   separation, and physics protections only. Numerical equivalence, semantic
   IR shape, QPU resources, and migration of official examples are later
   phases.
5. Exact internal node names and precedence tables are implementation
   details constrained by these observable contracts; they require no new
   user-facing `Evolution<T>` annotation.
6. Bounded explicit iteration uses `Evolve() { transform until predicate max
   positive_literal }.run()`; `until` is not accepted by `times` or `for` in
   this slice.
7. Predicate evaluation is post-transform-only and non-collapsing; the first
   slice defines `converged(state)` as full-State norm-difference convergence
   under the declared kernel tolerance.
8. Unsuccessful exhaustion publishes no State and reports
   `EVOLVE_UNTIL_MAX_STEPS_ERROR`.
9. Predicate-dependent bounded evolution is simulator-only in this slice;
   QPU lowering is fail-closed before allocation. Approximation provenance
   must include iteration count, realization, and total error policy where
   applicable.
10. The first-slice numeric contract is full-State L2 difference, Float64,
    absolute tolerance `1e-9`; provenance fields are normative as listed in
    scenario O.
