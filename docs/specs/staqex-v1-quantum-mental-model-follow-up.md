# Staqex v1 quantum mental-model follow-up specification

| Field | Value |
|---|---|
| Status | **Proposed specification** (2026-08-04) |
| Parent | [ADR 0189](../architecture/adr/0189-quantum-mental-model-and-observation-contract.md) |
| Work plan | [WP-0092](../work-plans/WP-0092-quantum-mental-model-follow-up.md) |
| Follow-up Issues | [LISS-0480](../issues/LISS-0480-scientific-lexicon-contract.md), [LISS-0481](../issues/LISS-0481-observation-contract.md), [LISS-0482](../issues/LISS-0482-observation-semantic-mapping.md), [LISS-0483](../issues/LISS-0483-observation-lexicon-conformance.md) |
| Scope | scientific lexicon, quantum composition surface, observation contracts |
| Implementation status | bounded slices shipped: scientific aliases `psi/ψ`、`phi/φ`、`rho/ρ`, `DiagnosticView<T>` and observation mappings, Static Kernel tomography rejection, and conformance evidence report; public `Observable<T>`/`Projection<T>`/`Observation<T>`, general observation families, POVM/tomography execution, and provider/QPU support remain proposed |

## 1. Purpose

This document translates the accepted mental-model direction into acceptance
boundaries. It remains a proposal for grammar, public type spelling, and
unimplemented observation families. The approved `DiagnosticView<T>` compiler
classification is recorded here as shipped evidence, without changing the
normative v1 grammar.

The language must let a programmer read a source program as a physical state
and its transformation, while keeping the classical Host boundary explicit.
The source surface must not make a state-preserving operation look like a
classical short-circuit branch or make a non-destructive observation look like
a collapsed scalar.

## 2. Semantic vocabulary

The follow-up surface uses these candidate semantic categories:

| Category | Meaning | Classicalization |
|---|---|---|
| `State<T>` | Pure or mixed state carrier in the object-language joint | Never implicit |
| `DensityState<T>` | Density-operator state carrier | Never implicit |
| `Observable<T>` | Quantity whose expectation or measurement is requested | Operation-specific |
| `Projection<T>` | State-transforming subspace restriction | No sampling by itself |
| `Observation<T>` | Typed request/result contract for an observation | Explicit operation |
| `JobResult` | Host execution envelope | Classical boundary |

These names are semantic candidates, not necessarily final surface spellings.
The implementation may use different internal DTOs as long as the denotation
is preserved. The first shipped boundary classifies `inspect(state)` as
`DiagnosticView<T>` in the compiler type layer; it preserves the existing
identity-bind path to terminal `measure` and does not make `DiagnosticView`
a new public annotation.

## 3. Scientific lexicon acceptance boundary

### 3.1 Compact-input law

Staqex prioritizes compact blackboard notation. When a Unicode symbol is
shorter and physically clearer, the symbol is the canonical spelling. An
ASCII alias exists only to make the same notation practical on keyboards that
cannot conveniently enter the symbol.

The alias rules are:

- prefer the Unicode symbol in canonical formatting and documentation;
- prefer short, recognizable ASCII aliases, normally 2–5 letters;
- do not require verbose English names for a mathematical symbol;
- aliases are lexical equivalents, never a second semantic operation;
- a symbol token may be a name, operator, delimiter, or binder according to
  its typed syntactic context;
- symbols with common classical meanings (`x`, `p`, `H`, `U`, `i`) are
  contextual scientific tokens rather than globally unavailable identifiers.

### 3.2 Candidate aliases

The first inventory is deliberately compact:

| Blackboard | Compact ASCII alias | Candidate role |
|---|---|---|
| `ψ` | `psi` | state / wavefunction name |
| `φ` | `phi` | state / test-state name |
| `ρ` | `rho` | density-state name |
| `H` | `H` | Hamiltonian / Hermitian operator name |
| `U` | `U` | unitary operator name |
| `ℏ` | `hbar` | reduced Planck constant |
| `†` | `dag` | adjoint / dagger operator |
| `⊗` | `tp` | tensor product |
| `⊕` | `dsum` | direct sum |
| `∂` | `d` | partial derivative in a calculus context |
| `∇` | `nab` | nabla / gradient operator |
| `Δ` | `del` | delta / Laplacian context |
| `Σ` | `sum` | finite sum binder |
| `Π` | `prod` | finite product binder |
| `⟨A⟩` | `ex(A)` | expectation notation |
| `[A,B]` | `cm(A,B)` | commutator |
| `{A,B}` | `ac(A,B)` | anticommutator |
| `|ψ⟩` | `ket(psi)` | ket notation when Unicode is unavailable |
| `⟨ψ|` | `bra(psi)` | bra notation when Unicode is unavailable |

The aliases are lexical conveniences. They do not inject hidden runtime
values, measure a state, or create an alternative type system.

The table is a proposal, not yet the final reserved inventory. In particular,
`d`, `del`, `sum`, and `prod` require context-sensitive parsing so that
ordinary identifiers and mathematical binders do not collide.

### 3.4 LISS-0480 v1 lexicon contract

The following matrix is the accepted v1 contract for the first lexicon slice.
`canonical` is the semantic spelling used by the AST and Scientific Semantic
IR; `written` is the exact source spelling retained for diagnostics and source
maps. A display alias is accepted only in the listed context and must produce
the same semantic identity as its canonical spelling.

| Canonical | Display alias(es) | Token class | Accepted context | Collision rule | Version | Unsupported spelling diagnostic |
|---|---|---|---|---|---|---|
| `psi` | `ψ` | scientific name | quantum state binding/reference | ordinary local name may shadow only in a nested scope; duplicate binding in one scope is `LEXICON_COLLISION` | v1 | `LEXICON_UNSUPPORTED_SPELLING`, suggest `psi` or `ψ` |
| `phi` | `φ` | scientific name | quantum state/test-state binding/reference | same canonical identity across source spellings; duplicate binding in one scope is deterministic | v1 | `LEXICON_UNSUPPORTED_SPELLING`, suggest `phi` or `φ` |
| `rho` | `ρ` | scientific name | density-state binding/reference | same canonical identity across source spellings; duplicate binding in one scope is deterministic | v1 | `LEXICON_UNSUPPORTED_SPELLING`, suggest `rho` or `ρ` |
| `H` | — | contextual scientific name | Hamiltonian/Hermitian operator position | remains an identifier outside operator position; no global reservation | v1 | `LEXICON_UNSUPPORTED_SPELLING` only for a rejected operator spelling |
| `U` | — | contextual scientific name | unitary operator position | remains an identifier outside operator position; no global reservation | v1 | `LEXICON_UNSUPPORTED_SPELLING` only for a rejected operator spelling |
| `hbar` | not active in v1 | scientific constant name | physics expression | ordinary local shadowing follows declaration scope when activated | v1 | `LEXICON_UNSUPPORTED_SPELLING`, suggest `hbar` |
| `dag` | not active in v1 | postfix operator | adjoint expression | cannot be used as a declaration name when activated | v1 | `LEXICON_UNSUPPORTED_SPELLING`, suggest `dag` |
| `tp` | not active in v1 | infix operator | tensor-product expression | cannot be used as a declaration name when activated | v1 | `LEXICON_UNSUPPORTED_SPELLING`, suggest `tp` |
| `cm` | `[A,B]` | operator expression | commutator position | square brackets are disambiguated by syntactic position; `cm(A,B)` is not a second semantic operation | v1 | `LEXICON_UNSUPPORTED_SPELLING`, suggest `cm(A,B)` |
| `controlled` | `Ctl` | reserved operation word | coherent control expression | reserved in operation position; never aliases `Mix`/`mix` | v1 | `LEXICON_UNSUPPORTED_SPELLING`, suggest `controlled` |
| `superpose` | `Superpose` | reserved operation word | coherent phase-preserving operation | reserved operation position; never aliases `Mix`/`mix` | v1 | `LEXICON_UNSUPPORTED_SPELLING`, suggest `superpose` |

The v1 matrix deliberately does not reserve `d`, `del`, `sum`, `prod`,
`dsum`, `nab`, `ex`, `ket`, or `bra` globally. They remain proposal-level,
context-sensitive candidates until a separate grammar decision specifies their
binder/operator ownership. An implementation must not silently accept an
unlisted spelling as a new dialect: it either preserves an ordinary identifier
role or emits the actionable diagnostic above with the canonical suggestion.

Each accepted alias test must expose both `canonical_spelling` and
`written_spelling`; comparing only rendered text is insufficient evidence that
the alias preserved meaning.

The commutator keeps `[A,B]` as its canonical blackboard spelling. Square
brackets are not rejected merely because other languages use them for lists or
indexing. The parser and type checker must distinguish an operator expression
from a list/index expression by syntactic position and expected type. `cm(A,B)`
is the compact ASCII fallback for an ambiguous or keyboard-constrained
context; a long spelling such as `commutator(A,B)` is not required.

### 3.3 Acceptance scenarios

```gherkin
Feature: keyboard-friendly scientific names

  Scenario: ASCII alias names a declared quantum state
    Given a quantum scope with `psi` as a scientific-name token
    When the source declares `State<Qubit> psi = |+>`
    Then the semantic binding is a State named `ψ`
    And no measurement occurs

  Scenario: Unicode and ASCII aliases have one meaning
    Given `ψ` and `psi` are accepted aliases in the same scientific context
    When equivalent programs use either spelling
    Then their semantic representations and execution meaning are identical

  Scenario: scientific names do not inject classical values
    Given a declaration `State<Qubit> psi = |+>`
    When `psi` is used before terminal measurement
    Then it remains a State value
    And it cannot be used as a classical branch condition

  Scenario: unrelated Greek names remain available by explicit policy
    Given a name is outside the accepted scientific inventory
    When it is used as an ordinary identifier
    Then the lexer and type checker follow the ordinary identifier policy
    And the implementation does not reserve every Greek letter implicitly
```

Open specification decisions: the complete inventory, whether `H` and `U`
are contextual tokens or ordinary identifiers with scientific metadata,
whether `ket(psi)` / `bra(psi)` are parser sugar or ordinary library calls,
and shadowing rules for nested scopes.

## 4. Quantum composition acceptance boundary

### 4.1 Meaning

The canonical future composition form must preserve all positively weighted
arms. It must not perform classical short-circuit selection, discard an arm
because another arm matched, or sample its control state.

[ADR 0190](../architecture/adr/0190-s02-selection-boundary-and-mix-control.md)
(Accepted; Phase 2 implementation approved for S02, 2026-08-04) has already
settled the taxonomy this section was investigating: `mix` is the canonical
non-collapsing, state-valued probabilistic/classified alternative
transformation; `controlled`/`Ctl` is reserved for coherent control and is
not an alias for `mix`; `superpose` is reserved for coherent, phase-preserving
semantics and must not be used for convex mixture; and `when` is removed from
the canonical surface with no compatibility alias and a hard diagnostic. This
section restates that accepted taxonomy for the general-language follow-up
rather than proposing a new one.

The pattern below preserves all positively weighted arms with no
interference and no sampling — under ADR 0190's taxonomy this is the `mix`
lane, not `superpose`:

```staqex
state ψ₂ = mix(control) {
    0 -> evolve ψ under H₀ for t,
    1 -> evolve ψ under H₁ for t,
}
```

`superpose` remains reserved for a distinct, not-yet-active grammar that
preserves relative phase; it is not demonstrated by this pattern. Existing
`when` programs are not the target surface: per ADR 0190, `when` is retired
without a compatibility alias. This retirement is **already implemented and
shipped** (PR #337, commit `321de3a`, under the ADR 0190/WP-0093 Phase 2
approval), not a pending implementation slice: `when` fails lexing with a
`RETIRED_KEYWORD` diagnostic naming `mix`, and `mix` is the active grammar for
this lane. `superpose`'s grammar/type boundary and `controlled`'s call-form
execution are both now shipped (see §4.3); only `superpose`'s coherent
execution math and a possible `controlled` block form remain open.

### 4.2 Acceptance scenarios

```gherkin
Feature: state-preserving quantum composition

  Scenario: all positive-weight arms survive
    Given `control` has support on two outcomes
    When a state composition combines two valid arms
    Then both arms remain in the resulting state
    And the evaluator consumes no measurement randomness

  Scenario: composition is not classical case selection
    Given two arms are valid for the control support
    When one arm is evaluated
    Then the other arm is not discarded merely because the first arm exists
    And the result remains a State value

  Scenario: mixture and coherent control are not conflated
    Given a composition request identifies a mixture, coherent control, or
      dynamic feed-forward lane
    When the program is type-checked
    Then the selected meaning is explicit in the type or lane contract
    And the implementation does not silently choose a different meaning

  Scenario: target capability is checked after semantic elaboration
    Given a valid state composition is not supported by a target
    When the program is lowered for that target
    Then lowering fails with an explicit capability diagnostic
    And the source meaning is not rewritten into a classical branch
```

### 4.3 Composition lanes (accepted taxonomy, ADR 0190)

The surface must not use one keyword for physically different operations.
The following restates the taxonomy [ADR 0190](../architecture/adr/0190-s02-selection-boundary-and-mix-control.md)
already accepted for S02 and the general language surface it exercises; it is
not a new proposal awaiting approval.

| Lane | Meaning | State treatment | Surface | Status |
|---|---|---|---|---|
| Probabilistic mixture | Push forward a state-valued control through alternatives | All positive-weight arms remain; no sampling | `mix (control) { … }` | Accepted (ADR 0190); shipped v1 grammar |
| Coherent superposition | Combine amplitudes with phase-sensitive linear semantics | Amplitudes interfere; not a classical case split | `superpose (amplitudes) { … }` | **Shipped** ([LISS-0320](../issues/LISS-0320-superpose-formal-grammar.md), PR #345) — parses to `SuperposeExpr`, type-checks to `State<T>`; coherent amplitude/phase *execution* still fails closed with `COHERENT_EXECUTION_UNSUPPORTED` |
| Coherent controlled operation | Apply a unitary conditionally while retaining coherent control | Control and target remain one quantum state | `controlled(ctrl[, …], U, tgt[, …])` | **Shipped** (verified live 2026-08-05) — `runtime/evaluator.py`'s `controlled` op is a real alias of `capply` (`Cⁿ(U)`); executes correctly, not a stub. A distinct `controlled { … }` *block* form (mirroring `superpose`'s arm shape) remains undecided design, not a confirmed gap — a single controlled-unitary application has no per-arm branching to express |
| Dynamic feed-forward | Use a classical measurement result to select a later action | Collapse and classical boundary are explicit | `measure` followed by Host/dynamic lane | Separate lane; never lowered to `superpose` or `mix` |

`superpose` is therefore not an alias for `mix`, and neither is `controlled`.
A valid implementation of `superpose`'s coherent amplitude/phase execution
(distinct from its already-shipped grammar/type boundary) must make the
coefficient/phase contract explicit and must reject a target that cannot
preserve it. `mix` remains the readable v1 spelling for the existing
probabilistic composition behavior and is already shipped in the Kernel
parser.

### 4.4 `when` migration rule (accepted, ADR 0190)

ADR 0190 item 4 already decided the migration rule for `when`:

- `when` is removed from the canonical surface. Backward compatibility is not
  required.
- The compiler must not silently reinterpret `when` as `mix`; retirement is a
  hard diagnostic, not a runtime or parser fallback.
- Any source rewrite from `when` to `mix` belongs to a separate migration
  tool, not the compiler.
- No `when`/`else` classical semantics are introduced under any replacement
  spelling.

This specification adopts that rule for the general-language follow-up (not
only the S02 scope). The lexer, parser, and diagnostic changes to retire
`when` are **already implemented and shipped** (PR #337, commit `321de3a`) —
confirmed live: `when (...)` fails lexing with `RETIRED_KEYWORD: retired
\`when\` → use \`mix\``, with no `MIX_FALLBACK` or other silent
reinterpretation. `superpose`'s grammar and `controlled`'s call-form
execution are both shipped (§4.3); the remaining open items under this
work plan are the scientific lexicon beyond `psi`/`phi`/`rho`/`cm`, the
public observation surface, and conformance scenarios.

### 4.5 `superpose` formal-grammar acceptance scenarios (Phase 1 target, LISS-0320)

PR #344 added a **shallow, non-normative** recognition of `superpose` inside
the `H1` authoring heuristic (`Parser._parse_h1_experiment_body`): it tags a
source *line* as `H1Superposition`/`CoherentSuperposition` purely by scanning
for the lexeme `"superpose"`, without parsing a control/arms structure,
without typechecking, and without evaluator semantics. This does **not**
satisfy §4.3's "formal grammar" status; `superpose` remains ordinary-surface
inactive. This subsection defines the acceptance boundary for the next slice:
a real `SuperposeExpr` in the primary grammar/AST/typecheck path, structurally
parallel to (but never unioned with) `WhenExpr`/`WhenArm`.

Explicitly out of scope for this slice: `controlled` grammar (turned out
not to need a separate Issue — its call form was already shipped, see
§4.3's 2026-08-05 note), coherent amplitude/phase execution math, and
QASM/target-profile
lowering. Because a typed-but-unexecutable AST node must not crash with an
unhandled-node exception, this slice includes one fail-closed "not yet
executable" evaluator diagnostic — this is a safety minimum, not the future
target-lowering/capability-rejection work item.

```gherkin
Feature: superpose formal grammar and type boundary

  Scenario: superpose parses to a distinct AST node
    Given source text `superpose(control) { 0 -> a, 1 -> b, }`
    When the program is parsed
    Then the result is a `SuperposeExpr` node
    And it is not a `WhenExpr` node
    And no `H1Superposition` heuristic node is produced outside an H1
      `experiment` block

  Scenario: superpose is not silently accepted as mix
    Given source text `superpose(control) { 0 -> a, 1 -> b, }`
    When the program is type-checked
    Then the result type is `State<T>` matching the arm bodies
    And the diagnostics do not contain a `Mixture` classification
    And the diagnostics do not silently rewrite `superpose` to `mix`

  Scenario: mix and when are unaffected
    Given the existing `mix (control) { … }` and retired `when (control) { … }`
      test fixtures
    When the full regression suite runs
    Then their parse, type, and diagnostic behavior is unchanged from the
      pre-slice baseline

  Scenario: attempting to evaluate superpose fails closed, not open
    Given a well-typed program containing `superpose(control) { … }`
    When the program is evaluated (not merely type-checked)
    Then evaluation fails with one explicit, documented diagnostic
    And the diagnostic is not a Python traceback or unhandled-node error
    And the diagnostic does not silently execute `mix` semantics instead
```

## 5. Observation acceptance boundary

### 5.1 Operation matrix

| Operation | Input | Result | Collapse | Current Kernel posture |
|---|---|---|---:|---|
| `expect` | `Observable<T>`, `State<T>` | expectation projection | no | limited / shipped paths |
| `project` | `Projection<T>`, `State<T>` | `State<T>` or vacuum | no sampling | shipped limited paths |
| `inspect` | `State<T>` | diagnostic view | no | shipped diagnostic path |
| `trace_out` | composite state, subsystem | reduced state | no sampling | shipped limited Joint path |
| `measure` | measurable state / POVM | observed outcome + post-state contract | yes | terminal computational path |
| `tomography` | experiment/job plan | Host reconstruction report | repeated shots | deferred protocol |

The `Current Kernel posture` column is evidence, not a promise that every
listed semantic family is complete. General POVMs, arbitrary density operators,
and tomography remain deferred until their own specifications are accepted.

### 5.3 Proposed semantic type boundary

The first type-layer should be introduced in the semantic IR, not as a new set
of mandatory source annotations. This preserves the physicist-first surface
while preventing the compiler from collapsing all observation forms into one
classical result.

| Semantic type | Denotes | May collapse | Initial exposure |
|---|---|---:|---|
| `State<T>` | pure or mixed quantum carrier | never implicitly | existing surface type |
| `Observable<T>` | quantity/operator eligible for expectation or observation | no | compiler/IR category |
| `Projection<T>` | subspace restriction or reduced-state transform | no sampling by itself | compiler/IR category |
| `Observation<T>` | typed observation intent/result contract with kind and lane | only when its kind is `measure` | compiler/IR DTO |
| `DiagnosticView<T>` | non-destructive view retaining a State lineage | only through terminal `measure` of its underlying state | Host/diagnostic DTO |
| `MeasurementEnvelope<T>` | terminal classical outcome plus post-state metadata | yes | Host result DTO |

The categories have these lowering rules:

- `expect(O, ψ)` elaborates through `Observable<T>` and produces a permitted
  expectation projection. It must not consume or sample `ψ`; whether the
  source-level result remains a scalar projection or becomes an explicit
  `Observation<T>` value is a later surface decision.
- `project(P, ψ)` elaborates through `Projection<T>` and produces
  `State<T>` or vacuum. It is a state transformation, not a sampled outcome.
- `inspect(ψ)` produces `DiagnosticView<T>` and retains the semantic state.
  The view itself never samples; terminal `measure` may explicitly consume the
  retained underlying state, preserving the existing identity-bind surface.
- `trace_out(ψ, subsystem)` produces a reduced `State<T>` and does not create
  a classical result.
- terminal `measure(ψ)` produces `MeasurementEnvelope<T>` and is the only
  Static Kernel operation in this family that samples and collapses.
- `tomography` is an `Observation<T>` protocol request at the Host boundary.
  It requires repeated execution and returns a `JobResult`/`ObservationReport`;
  it is not a Kernel expression and must fail with an explicit capability
  diagnostic when requested from the Static Kernel lane.

`Observation<T>` is deliberately a contract rather than an alias for
`JobResult`: the former preserves semantic intent, while the latter is a
classical Host envelope containing execution metadata. Target capability is
checked after semantic elaboration, so an unsupported target rejects the
request without rewriting it as `State`, `Float`, or an early measurement.

### 5.4 LISS-0481 observation contract matrix

The following matrix is the v1 acceptance contract for observation intent and
result boundaries. `lane` and `provenance` are observable metadata, not
implementation-only annotations.

| Operation | Semantic type | Result contract | Collapse | Sampling | Lane | Required provenance | Unsupported behavior |
|---|---|---|---:|---:|---|---|---|
| `expect(O, state)` | `Observable<T>` | expectation projection | no | no | `StaticKernel` | source ID, operator ID, input state ID | reject with operation and target capability |
| `project(P, state)` | `Projection<T>` | `State<T>` or vacuum | no | no | `StaticKernel` | source ID, projector ID, input state ID, loss marker | reject without fabricated state |
| `inspect(state)` | `DiagnosticView<T>` | non-destructive diagnostic view | no | no | `StaticKernel` | source ID, state lineage ID, exactness | reject without sampling or finite-plan allocation |
| `trace_out(state, subsystem)` | `Projection<T>` | reduced `State<T>` | no | no | `StaticKernel` | source ID, subsystem ID, reduction/projection loss | reject without fabricated reduced state |
| terminal `measure(state)` | `Observation<T>` → `MeasurementEnvelope<T>` | outcome plus post-state metadata | yes | yes | `StaticKernel` | source ID, measurement ID, outcome, post-state ID, collapse boundary | fail before a second implicit measurement |
| `tomography(plan)` | `Observation<T>` → `ObservationReport` | Host reconstruction report | no in Kernel | repeated shots at Host | `HostProtocol` | source ID, job/plan ID, shot policy, target capability | Static Kernel must emit `OBSERVATION_UNSUPPORTED` and no report |

Every accepted operation must preserve its source ID and semantic input
lineage. A diagnostic view or observation report with only rendered text and no
lineage is not a conforming result. Unsupported behavior is a rejection, not a
zero value, empty report, or implicit conversion to `measure`.

### 5.5 LISS-0482 observation-to-IR mapping matrix

The mapping layer is a source-derived projection. It may add consumer-facing
metadata, but it must not replace the Scientific Semantic IR authority or
materialize a finite artifact implicitly.

| Source operation | Scientific Semantic IR role | Lane | Required identity/provenance | Exactness/dimensions | Projection-loss rule | Illegal transition |
|---|---|---|---|---|---|---|
| `expect(O, state)` | `ExpectationProjection` | `StaticKernel` | source ID, observable node ID, state lineage | preserve declared exactness and dimensions | report loss explicitly; never sample | reject classical-only observable or invalid lane |
| `project(P, state)` | `Projection` | `StaticKernel` | source ID, projector node ID, state lineage | preserve dimensions; mark vacuum | record projection loss | reject if projection fabricates state |
| `inspect(state)` | `DiagnosticView` | `StaticKernel` | source ID, state lineage, view node ID | preserve exactness and dimensions | no projection loss or finite allocation | reject if mapped to measurement |
| `trace_out(state, subsystem)` | `ReducedState` | `StaticKernel` | source ID, subsystem ID, parent lineage | preserve remaining dimensions | record reduction loss | reject if treated as terminal outcome |
| terminal `measure(state)` | `Measurement` | `StaticKernel` | source ID, measurement ID, outcome/post-state lineage | boundary-defined outcome exactness | collapse boundary explicit | reject a second implicit collapse |
| dynamic measurement | `DynamicMeasurement` | `DynamicQpu` | source ID, dynamic token, branch lineage | preserve token and branch dimensions | no static projection substitution | reject if lowered to static measurement |
| `tomography(plan)` | `ObservationProtocolRequest` | `HostProtocol` | source ID, plan/job ID, target capability | protocol-defined report exactness | no Kernel finite artifact | reject in StaticKernel with `OBSERVATION_UNSUPPORTED` |

For every row, mapping output must include `role`, `lane`, `source_id`,
`provenance`, `exactness`, and `dimensions`. A missing field is a mapping
contract failure even when a consumer can still render an artifact.

### 5.7 LISS-0484 broader observation algebra design

LISS-0480–0483 establish the lexical, contract, mapping, and bounded
conformance foundations. The next local design slice defines the algebraic
relationships without selecting a storage model or exposing mandatory source
annotations.

| Concept | Input relation | Output relation | Collapse | Required invariant | Current implementation boundary |
|---|---|---|---:|---|---|
| `Observable<T>` | operator/quantity over `State<T>` | expectation or measurement request | no by itself | observable identity and dimensions remain source-derived | compiler/IR category only |
| `Projection<T>` | projector/reduction over `State<T>` | `State<T>` or vacuum | no implicit sampling | projection loss is explicit and no finite artifact is fabricated | compiler/IR category only |
| `Observation<T>` | typed intent with operation and lane | projection, diagnostic view, measurement envelope, or protocol request | only `measure` | operation, lane, lineage, and capability are preserved | compiler/IR DTO candidate |
| `DiagnosticView<T>` | `inspect(State<T>)` | non-destructive view | no | source state lineage remains available | shipped bounded IR metadata |
| `MeasurementEnvelope<T>` | terminal `measure(State<T>)` | classical outcome + post-state metadata | yes | collapse is explicit and terminal | shipped Host result boundary |

The algebra has four required laws: (1) `expect`, `project`, `inspect`, and
`trace_out` are state-preserving or state-transforming but non-sampling; (2)
only terminal `measure` may create a collapse outcome in the Static Kernel;
(3) every result keeps source identity, lane, and provenance; and (4) an
unsupported operation is rejected explicitly rather than coerced into a
different observation kind.

LISS-0484 must decide the vocabulary for operation kind, lane, lineage,
exactness, dimensions, projection-loss, and capability status, plus the
composition rules for `expect(project(P, state))`, `inspect(project(P, state))`,
and repeated observation requests. It must not decide general Hilbert storage,
POVM numerical semantics, tomography shot estimation, provider SDKs, or public
surface annotations. Those are separate ADR/Issue boundaries.

### 5.6 LISS-0483 cross-feature conformance matrix

Conformance is a deterministic proof ledger over accepted source behavior. Each
row names the canonical behavior, the observable proof, and the result that
must be reported when the behavior is deferred. A passing compile alone is not
conformance evidence if the semantic meaning or review metadata is discarded.

| Feature family | Canonical contract | Deterministic proof | Deferred/negative proof | Required evidence |
|---|---|---|---|---|
| scientific names | `psi/ψ`, `phi/φ`, `rho/ρ` share one meaning | lexer/parser token and binding identity test | unlisted spelling has stable actionable diagnostic | canonical/written spelling, source span |
| probabilistic composition | `mix` is non-collapsing composition | semantic role/lane test | no rewrite to `measure` or `superpose` | role, lane, branch provenance |
| coherent composition | `superpose` is distinct from `mix` | AST/IR role test | unsupported execution rejects explicitly | role, rejection code, source ID |
| controlled operation | `controlled`/`Ctl` retains coherent-control meaning | call-form semantic test | no alias to mixture | operation role, control/target provenance |
| migration | `when` is retired; `mix` is canonical | lexer diagnostic test | no compatibility fallback | diagnostic code, replacement, span |
| observation | `inspect`/`project`/`trace_out` do not collapse | observation mapping test | unsupported observation has no fabricated result | kind, collapse, sampling, mapping evidence |
| terminal boundary | only terminal `measure` samples/collapses | measurement envelope test | second implicit collapse rejects | outcome, post-state, collapse boundary |

The conformance runner must return one record per matrix row with `feature`,
`status`, `source_id`, `evidence`, and `diagnostic` (when applicable). A row
without evidence is `inconclusive`, not `passed`. Conformance records prove
language behavior only; they do not imply provider or hardware support.

### 5.2 Acceptance scenarios

```gherkin
Feature: typed observations

  Scenario: expectation does not collapse a state
    Given a valid State and Observable
    When `expect` is evaluated
    Then it returns the declared expectation projection
    And the source State remains available without sampling

  Scenario: projection returns a state or vacuum
    Given a valid projector and State
    When `project` is evaluated
    Then the result is a State or vacuum
    And no single outcome is sampled implicitly

  Scenario: inspect is non-destructive
    Given a valid State
    When `inspect` or `snapshot` is requested
    Then a diagnostic representation is emitted
    And the State's semantic value is unchanged

  Scenario: measure is the explicit collapse boundary
    Given a valid measurable State in the Static Kernel lane
    When terminal `measure` is evaluated
    Then a Born outcome is produced through the measurement boundary
    And the result is represented in the Host measurement envelope

  Scenario: tomography is a Host protocol
    Given a valid experiment plan requiring repeated observations
    When tomography is requested
    Then it is represented as a Host/protocol operation
    And it is not confused with one in-program measurement

  Scenario: unsupported observation fails closed
    Given a semantically valid observation unsupported by a selected target
    When lowering or execution is requested
    Then an explicit capability diagnostic is returned
    And no silent classical approximation or early collapse occurs
```

## 6. Current implementation gap

### Detailed follow-up Issue design

#### LISS-0480 — scientific lexicon and alias contract

Define canonical ASCII spellings, display aliases, token classes, contexts,
shadowing, versioning, and diagnostics. Aliases map to one AST/semantic
meaning and retain written-form provenance. Phase 1 is lexer/parser contract
and fixture inventory; mandatory Unicode migration is excluded.

#### LISS-0481 — observation contract

Define `Observable<T>`, `Projection<T>`, and `Observation<T>` across `expect`,
`project`, `inspect`, `trace_out`, `measure`, and tomography. Inspection is
non-destructive, terminal `measure` is the only collapse boundary, and dynamic
measurement is a distinct lane. General Hilbert storage and POVM/tomography
implementation remain separate decisions.

#### LISS-0482 — observation-to-semantic-IR mapping

Map accepted observation concepts to Scientific Semantic IR roles and lanes,
preserving source IDs, provenance, exactness, dimensions, and projection-loss
diagnostics. Illegal lane transitions reject explicitly; observation never
becomes implicit finite realization.

#### LISS-0483 — observation/lexicon conformance closure

After 0480–0482 are accepted, build one matrix for aliases, `mix`, `superpose`,
`controlled`, `when` retirement, inspection, projection, and terminal measure.
Every proof maps to a deterministic test; deferred forms remain explicit
rejects and do not imply hardware support.

The shipping Kernel currently provides a finite-support Joint with complex
amplitudes, selected unitary and Hamiltonian operations, limited density-state
handling, non-destructive diagnostic paths, and terminal measurement. It does
not yet provide the complete semantic categories or all observation families
listed above.

The implementation gap is classified as a documented design/coverage gap, not
permission to narrow the language ideal. Follow-up lowering may choose finite
representations for a target, but the semantic IR must retain the distinction
between state, operator, projection, observation, and measured result.

## 7. Out of scope for this specification

- Choosing a QPU provider, SDK, numerical library, or storage representation.
- Renaming or deleting `when` before a migration review.
- Implementing general POVMs, tomography, or arbitrary Hilbert-space storage.
- Adding classical control flow to the Static Kernel.
- Changing the current normative v1 specification before this proposal is
  accepted as an amendment.

## 8. Phase 1 review questions

1. Is `superpose` the right canonical word, or should the language use another
   physics-specific composition term?
2. Which scientific names belong in the first reserved/contextual inventory?
3. Should `Observable<T>`, `Projection<T>`, and `Observation<T>` be visible
   surface types, compiler-only semantic categories, or a layered combination?
   **Proposed default:** compiler/IR categories first; expose surface types
   only where the blackboard notation becomes clearer and after conformance
   evidence exists.
4. Is `tomography` correctly placed at the Host/protocol boundary?
5. Which observation scenarios should become the first Phase 1 Red tests?

## 9. Type-boundary review decision required

This proposal is ready for review but does not accept a new public type
surface. The next approval should decide only whether the semantic categories,
collapse matrix, and Host/Kernel separation above are the correct contract.
After that decision, Phase 1 Red tests may cover the selected IR/diagnostic
boundary. Grammar changes, public `Observable<T>` syntax, general POVMs, and
tomography execution remain separately gated.
