# WP-0100: explicit blackboard evolution surface and target realization

| Field | Value |
|---|---|
| Status | **final-review-ready — Phase 3 finite Realize/Suzuki closeout (2026-08-17)** |
| Purpose | Let physicists write the construction of a quantum evolution explicitly, while keeping `Evolve` as the execution boundary rather than a hidden Hamiltonian shorthand. |
| Local Issue | [LISS-0437](../issues/LISS-0437-explicit-evolution-surface.md) |
| Proposed ADR | [ADR 0209](../architecture/adr/0209-explicit-blackboard-evolution-surface.md) |
| Acceptance specification | [staqex explicit evolution surface](../specs/staqex-explicit-evolution-surface.md) |
| Branch | `codex/wp-0100-explicit-evolution-surface` |
| Planning size | **L** |
| Current phase | Approved finite target-realization slice complete; residual reconciliation is separated into LISS-0438 |
| Implementation permission | **Approved for Phase 2 Green and previously named Phase 3 migration slices (2026-08-14)** |
| Post-review requirement | Yes; Adjudicator review after Phase 1 and before Phase 2 |

### Mode-specific approval state

| Mode | Design status | Red status | Implementation status |
|---|---|---|---|
| `Evolve() { transform }.run()` | Accepted | Completed/reviewed for the existing slice | Phase 2 Green approved and implemented |
| `Evolve (seeds) times N { block }` / `for dt` | Existing separate modes | Existing coverage | Existing implementation; migration permission is slice-scoped |
| `Evolve() { transform until converged(state) max N }.run()` | Design amendment accepted | Completed/reviewed | Phase 2 Green implemented; post-implementation review required |

The Phase 3 migration permission in the first two rows does not authorize the
third row. The third row has its own Red and implementation gates, which are
now completed for the bounded minimum slice.

## [DESIGN CHECK]

- **Scope and expected behavior:** The source must be able to express the
  blackboard path \(I\to I-iHdt/\hbar\to e^{-iHt/\hbar}\to U\psi\), and
  `Evolve()` must accept only an explicitly state-transforming result. Target
  lowering may realize or reject the same meaning, but may not silently invent
  or rewrite the physics.
- **Specifications and files inspected:** `AGENTS.md`; `agent-quickstart.md`;
  `adjudicator-language-vision.md` §2–§6; `physicist-dx-harmony.md`;
  `staqex-language-specification.md` §§4–6; `staqex-ast-design.md`;
  `staqex-runtime-execution-model.md`; ADR 0195; LISS-0414;
  ADR 0084/0085/0106/0111; S02 `main_selection.sqx` and README;
  WP-0093 and WP-0095.
- **Component boundaries, ports/adapters, and VO/DTO candidates:** The
  parser/AST represents explicit operator algebra; the typechecker validates
  operator/state application and dimensions; a semantic `Evolution<T>` IR
  preserves source provenance and transform structure; a target capability
  profile selects exact/approximate realization; simulator and QPU adapters
  implement ports and do not contain business/physics policy. Candidates:
  `Evolution<T>`, `EvolutionPlan`, `Propagator`, `RealizationPolicy`,
  `CapabilityWitness`, and `EvolutionProvenance` (names are provisional).
- **Applicable constraints:** Physicist-first source; same blackboard meaning;
  Never Leave the State; terminal `Measure`; `mix` not classical `if`;
  fail-closed unsupported targets; no provider SDK in the Kernel; no hidden
  lowering policy in adapters; real \(\hbar\) and dimensioned Energy/Time.
- **Decisions, assumptions, unresolved ambiguities:** The reviewed contract
  freezes `exp(Operator)` and `Operator * State<T>` as the canonical surface;
  explicit `Evolve()` is a distinct mode; bare `State` is invalid; formal
  `Limit` is source-preserving but target-rejected in the MVP; and the current
  Hamiltonian spelling is migration-only with a dedicated diagnostic. Exact
  AST/IR node names remain implementation details. QPU realization metadata
  is a later target contract, not a Phase 1 Red assertion.
- **Included and omitted AI context:** Included only the relevant language,
  runtime, QPU boundary, ADR, S02, and work-plan excerpts. Omitted unrelated
  examples, private data, provider credentials, and full repository exports.
- **Task routing (model/assistant/tool):** Strong reasoning agent for the
  architecture and ADR boundary; code assistant for Phase 1 acceptance tests
  after review; deterministic tools for parser/typecheck/conformance/QPU IR
  verification.
- **Input/output evidence contract when AI output is involved:** Input is the
  accepted specification plus named architecture excerpts. Output must be a
  structured design/patch limited to named files, with source examples,
  diagnostics, provenance, target capability behavior, and deterministic
  verification evidence. No hidden reasoning or ungrounded provider claims.
- **Verification plan:** Phase 0 uses document consistency and `git diff
  --check`. Phase 1 adds failing parser/type/semantic/lowering tests only.
  Phase 2 implements the smallest accepted surface. Phase 3 verifies source
  readability, S02 meaning, simulator/QPU provenance, full regression, spec
  verification, and corpus checks.

## Goal

Change the meaning of `Evolve` from “implicitly construct and execute a hidden
Hamiltonian exponential” to “execute an explicitly written state evolution.”
The physics expression remains visible in the source; `Evolve` marks the
execution boundary and does not supply missing physics.

## Approval record

- Approval type: **Architecture approval**
- Approved scope: ADR 0209, the accepted explicit-evolution Spec, S02
  blackboard/source correspondence, and the separated QPU realization
  boundary.
- Implementation permission: **No**
- Phase 1 permission: **Red tests only, approved 2026-08-14**
- Phase 2 implementation permission: **Approved by user 2026-08-14** for
  LISS-0437 minimum Green scope; no QPU deployment or broad corpus migration.
- Phase 3 migration-slice permission: **Approved by user 2026-08-14**; B08
  tuple-carrier semantics and the B08 official-example migration were the
  first executed migration slice. This permission covers only the named
  migration/compatibility slices. Remaining families require their own bounded
  verification and must not be bulk-rewritten.
- Bounded explicit-iteration design approval: **Approved by user 2026-08-14**
  for the Spec/ADR design amendment, followed by the separately approved Red
  and Phase 2 Green gates. Those gates are now complete for the minimum slice.
- Post-implementation review: required before Phase 3 closeout.
- Phase 3 design reinforcement approval: **Approved by user 2026-08-14**;
  implementation remains separately gated per workstream.
- Phase 3 Red approval: **Approved by user 2026-08-14 for all three
  workstreams** (`Limit`, binder-aware QPU, and S02 migration boundary).
- Phase 3 Green implementation: **Not approved by this record**.

## Current implementation and impact inventory

This inventory was completed before design execution. It records the current
shipping Kernel rather than assuming that the proposed `Evolution<T>` already
exists.

### Phase 2 implementation slice

- Added `Evolve() { transform }.run()` as a distinct explicit-transform mode
  in the AST/parser; empty-seed `Evolve()` is no longer parsed as a seed.
- Added type rules for `Operator * State`, operator `exp`, `i`, real `hbar`,
  Hamiltonian Energy dimensions, and dimensionless exponents.
- Added explicit-state-transform and migration diagnostics.
- Preserved `times N` and `for dt` pushforward paths.
- Added the minimum `Limit ... -> Infinity { ... }` source-preserving parser
  surface and target-realization diagnostic; finite realization is deferred.

### Current parser and AST

- The following baseline inventory is historical evidence from before Phase 2
  Green: `compiler/staqex/parser.py::_evolve_expr` recognized the three
  baseline families `times`, `for`, and legacy Hamiltonian evolution.
- The current shipping parser also has the explicit-transform mode
  `Evolve() { transform }.run()` and checks its final body result as
  `Operator * State`. Bounded explicit iteration is implemented for the
  accepted `until`/positive-literal-`max` minimum slice.
- `compiler/staqex/ast_nodes.py::EvolveExpr` is a tagged-shape record, not a
  generic transformation node. Its fields are `seeds`, `times`, `body`,
  `duration`, `hamiltonian`, `until_predicate`, `max_steps`, and `suzuki`.
  `body` and `hamiltonian` are mutually meaningful modes in current code.
- `EvolveBody` contains only `let` bindings plus one final expression. It is
  currently a repeated pushforward block, not a user-visible evolution plan.
- `Operator` expressions use a separate operator AST family (`OpBin`,
  `OpPow`, `OpPauli`, `OpBinder`, `OpCall`, etc.) from ordinary `Expr`. The
  proposed `Operator exp(...)` and `Operator * State` therefore require an
  explicit cross-domain contract; they are not a missing parser token only.

### Current compiler pipeline consumers

An `EvolveExpr` is inspected by multiple independent compiler stages:

1. parser construction and retired-keyword handling;
2. early-collapse / nested-`mix` traversal;
3. `TypeChecker._infer_evolve` for seed types, duration dimensions, Suzuki
   policy, and `until` purity/bounds;
4. `physical_axioms.py` for `COIN_IN_EVOLVE_ERROR` and evolution-body walks;
5. HIR linear-use analysis for seed introduction, consumption, tuple binds,
   and trace/discard obligations;
6. `unitarity_check.py` for Hamiltonian checks and the separate LISS-0436
   transparency rule on `times N` blocks;
7. `ir/dag.py`, which currently emits one generic `evolve` DAG node with
   `times`, optional `under`, duration, and body-result inputs;
8. `qpu_ir.py`, which only projects existing `EvolveExpr` instances and
   Suzuki metadata; it has no generic propagator/evolution provenance model;
9. runtime evaluation and QASM lowering.

This means a new explicit mode cannot be implemented safely only in the
parser or evaluator. Every traversal must preserve the new expression and
must keep `times N` and Hamiltonian evolution distinct.

### Current runtime realization

`runtime/evaluator.py::_bind_evolve` first branches on
`expr.hamiltonian`:

- Hamiltonian mode binds seed wires, validates real Time units, canonicalizes
  duration to seconds, then calls `_hamiltonian_evolve_one_step`.
- The Hamiltonian path has separate runtime branches for single Pauli gates,
  Fock/site-basis operators, Position grids, tuple-valued selection
  coordinates, and multi-wire sparse Pauli Hamiltonians.
- Dense paths call `runtime/matrix.py::expm_ih`; sparse paths call
  `runtime/sparse_pauli.py::expm_ih_apply`. Both directly implement
  \(e^{-iHt/\hbar}\) using the ADR 0195 real-\(\hbar\) contract.
- `until` repeats the Hamiltonian step and evaluates a restricted pure
  predicate. It is not supported by the static QPU IR.
- Non-Hamiltonian `times`/`for` mode first creates working coordinates,
  executes local pushforwards, repeats the body, and traces dead local axes at
  the boundary. Calls to gate/walk primitives and user functions have special
  runtime paths.

There is currently no runtime operation that evaluates a general operator
  exponential AST and then applies that propagator to a State. There is also
  no internal `Evolution<T>` value in the shipping runtime.

### Current QPU realization

- `backend/qasm/lower.py` recognizes a State binding only when its expression
  is an `EvolveExpr` with `hamiltonian is not None`.
- QASM lowering resolves the Hamiltonian into sparse Pauli terms and requires
  an explicit Suzuki policy. A plain Hamiltonian evolve is rejected with
  `QASM_TROTTER_STEPS_REQUIRED`; step counts are not silently invented.
- `backend/qasm/trotter.py` is deliberately specialized for
  `evolve ... under H for t`; it does not lower a generic `Operator U` or
  `Operator * State` expression.
- `qpu_ir.py` projects existing `EvolveExpr`/Suzuki data, but does not retain
  a source-level exponent, propagator, finite product, or realization graph.
- Provider-neutral QPU IR and OpenQASM are therefore affected, but vendor
  adapters and credentials remain outside this scope.

### Current source and test footprint

A deterministic source inventory found:

- official/example sources: 22 Hamiltonian-form `Evolve` sites across 20
  files, plus 3 `times` block sites across 3 files;
- test sources: 158 Hamiltonian-form sites, 19 `times` sites, and 2 `for`
  block sites across 80 files (textual inventory, including dedicated Red
  fixtures and specification suites);
- the official Hamiltonian examples include S02, S01's multiple disaster
  paths, B04/B07/B08/B16, A03/A05/A06/A10/A11, and the quantum-matter
  showcase;
- the official `times` examples are B06, B09, and A02. These must remain on
  the discrete pushforward path and must not be migrated as Hamiltonian
  exponentials.

### Confirmed current behavior of the proposed surface

Read-only compile probes confirmed:

- current `Evolve { psi under H for dur }.run()` reaches the existing compiler
  pipeline (subject to the normal source-level semantic obligations);
- `Evolve() { psi }.run()` is not parsed as a new evolution form;
- `Evolve() { apply(H, psi) }.run()` is likewise not parsed as a new form;
- `Operator U = exp(-i * H * dur / hbar)` currently reaches the existing
  second-quantized/operator algebra diagnostics rather than an operator
  exponential implementation;
- ordinary `apply(H, psi)` is a separate supported unitary-transform path and
  currently resolves only the existing named/operator unitary vocabulary, not
  a general `Operator * State` expression.

### Impact classification

| Area | Impact | Required design work |
|---|---|---|
| Lexer / parser | High | Add and disambiguate `Evolve()` body syntax; define operator `exp`, `i`, `hbar`, powers, and application precedence. |
| AST | High | Preserve existing modes and add an explicit-transform representation or a lossless generalized `EvolveExpr` mode. |
| Type system | High | Separate `State`, `Operator`, propagator, transform, and internal `Evolution<T>`; enforce dimensionless exponent and reject identity-only bodies. |
| Linear / HIR | High | Model shared input references as one Joint/DAG transform without weakening no-cloning or silently duplicating State roots. |
| Physical axioms | Medium | Walk new transform bodies; keep entropy, measurement, and classical-control prohibitions. |
| Unitarity | High | Replace syntactic allowlists with semantic transform obligations; distinguish proof, writable meaning, and target executability. |
| Runtime simulator | High | Add explicit operator-exponential/application realization or a semantic bridge to existing exact paths. |
| Physics/DAG IR | High | Retain generator, exponent, propagator, application, approximation, and source provenance. |
| QPU IR / QASM | High | Lower explicit propagators and policies; retain current fail-closed Suzuki behavior. |
| Examples | Medium/High | Migrate 22 Hamiltonian sites intentionally; leave 3 discrete `times` sites unchanged. |
| Tests/spec verification | Very high | Update ~158 Hamiltonian test sites plus parser, type, runtime, QPU, provenance, and negative cases. |
| Documentation | High | Update normative grammar, AST, type system, runtime, QPU, vocabulary, ADR 0195 relationship, and friction ledger. |

### Design correction resulting from the inventory

The earlier proposal treated `Evolve() { U_t * psi }` as if `Operator * State`
and `exp(Operator)` already existed. They do not. The implementation plan must
therefore sequence the work as a language/IR capability first, not as a syntax
migration. The current Hamiltonian runtime can be reused as one exact
realization after semantic normalization, but it cannot be called directly
from the new surface without losing the explicit source structure.

## Design principles

1. **Blackboard derivation is source-positive.** The user may write the
   generator, infinitesimal step, finite product, limit, exponential, and
   state application as separate expressions.
2. **Identity is not evolution.** `I * psi` and `psi` are identity operations;
   they cannot be promoted to time evolution by `Evolve`.
3. **No user-facing `Evolution<T>` ceremony.** The compiler may infer an
   internal evolution IR from an explicit state-transforming final expression.
4. **One meaning, multiple realizations.** Exact simulator, matrix
   exponential, Trotter/Suzuki, and QPU gate synthesis are realizations of the
   written expression, not alternate source meanings.
5. **Explicit target limits.** A target rejects unsupported formal expressions
   or requests an explicit approximation policy; it never silently changes the
   equation.
6. **Separate block evolution from Hamiltonian evolution.** `Evolve() { … }`
   for an explicit transform must not be conflated with `Evolve (...) times N`
   pure repetition or with a time-dependent Hamiltonian integrator.

## Target source shape: S02

The intended S02 shape is:

```staqex
Operator H_obj = scale * objective_hamiltonian(
    weights, n, activity_w, selectivity_w
)
Time dur = 0.6.fs

Operator exponent = -i * H_obj * dur / hbar
Operator U_t = exp(exponent)

State evolvedState = Evolve() {
    U_t * psi_sel
}.run()

Measure evolvedState
```

The one-expression form is also accepted if it preserves the same source
meaning:

```staqex
State evolvedState = Evolve() {
    exp(-i * H_obj * dur / hbar) * psi_sel
}.run()
```

The complete S02 time-evolution passage is intentionally visible:

```text
I → I - i H_obj dt / hbar
  → Limit N → Infinity { (I - i H_obj dur / (N hbar)) ^ N }
  → exp(-i H_obj dur / hbar)
  → U_t * psi_sel
  → psi_final
```

The source may use either the expanded `Limit` construction or the already
derived `exp` construction. In both cases, `Evolve()` receives the explicit
state-transform expression, never a bare State. This is the intended S02
design and is not a request to preserve the current hidden `under H for t`
form as the canonical spelling.
```

For the full blackboard derivation, the source may additionally express the
infinitesimal and finite-product construction. The MVP must preserve it in
the semantic representation even if a particular QPU profile cannot execute
the formal limit.

## Work units

### 0 — Architecture decision and contract freeze

1. Review and accept/reject the companion specification.
2. Freeze a bounded compatibility period for `Evolve { psi under H for
   t }.run()` with diagnostic `EVOLVE_HAMILTONIAN_SHORTCUT_RETIRED`; strict
   migration/profile gate is required to reject it before broad migration,
   and it is never an alias.
3. Freeze the distinction between `State<T>`, `Operator`, state-transform
   expression, and internal `Evolution<T>`.
4. Freeze exact domains and dimensional rules for operator `exp`, `i`,
   `hbar`, operator powers, `Limit`, and `Operator * State<T>`.
5. Record the accepted boundary in a new ADR or accepted amendment to the
   appropriate DEC theme.
6. Confirm the S02 blackboard/source correspondence; formal `Limit` is
   source-preserving but target-rejected in the MVP.

**Gate:** Architecture approval; no implementation permission implied.

### 1 — Phase 1 Red: source and semantic acceptance tests

Tests only:

1. Red-test explicit `U_t = exp(...)` and `U_t * psi` parsing.
2. Red-test the multi-line blackboard derivation with named intermediate values.
3. Red-test bare `Evolve() { psi }.run()` with the dedicated diagnostic.
4. Red-test the old Hamiltonian spelling's migration diagnostic.
5. Red-test operator-domain and dimensionless-exponent diagnostics.
6. Red-test formal `Limit` source preservation and MVP target rejection.
7. Red-test that `times N` remains separate and that measurement/classical
   control protections remain active.
8. Keep S02 source shape as a text/parse fixture only; numerical equivalence,
   provenance shape, QPU resources, and official S02 migration belong to later
   phases. The Red suite must not add a semantic equivalence oracle against
   the current real-\(\hbar\) path.

**Gate:** Adjudicator reviews Red tests before Green.

### 2 — Phase 2 Green: minimum Kernel implementation

Only after Phase 1 review:

1. Extend AST/parser for the accepted explicit operator expressions.
2. Add type/dimension checking for operator exponentiation and State
   application.
3. Build internal `Evolution<T>` semantic IR with source spans and
   provenance; do not expose it as mandatory source syntax.
4. Make `Evolve()` accept only an explicit state-transform result and reject
   identity-only bodies.
5. Keep existing `times N` block repetition separate.
6. Route exact simulator realization through the existing real-\(\hbar\)
   primitive without duplicating the physics formula in adapters.

**Gate:** deterministic tests, spec verification, and review; no QPU provider
selection is authorized by this WorkPlan.

### 3 — Phase 2/3 target realization slice

1. Project the internal evolution IR to existing provider-neutral QPU IR.
2. Support only already-accepted exact or explicitly parameterized
   Trotter/Suzuki policies.
3. Require an explicit typed acting-register mapping at the target boundary,
   for example `{"Sigma": "q[0..7]"}` for
   `Sigma (i In 0..7) { Z[i] }`; the lowering must never infer this mapping
   from binder names.
4. Emit provenance: source equation, realization, approximation order/steps,
   estimated resources, and capability decisions.
5. Reject formal limits, unsupported operator exponentials, insufficient qubits,
   or unavailable gates with physics-facing diagnostics.
6. Distinguish missing/incomplete register mapping from resource-budget
   exhaustion, and reject both before allocation with no partial circuit.
7. Verify no adapter invents Hamiltonians, durations, or step counts.

This unit is a target/lowering slice, not a vendor integration. Real QPU
submission remains behind existing Host/QPU ports and is out of scope here.

### 3A — bounded explicit iteration Phase 2 slice

The accepted source shape is:

```staqex
Evolve() {
    U_dt * state
    until converged(state)
    max 64
}.run()
```

The blackboard meaning is stepwise `state_(k+1) = U_dt * state_k`, with a
post-transform pure convergence check and a positive literal bound. The
simulator owns the loop; predicate-dependent QPU lowering rejects before
allocation. `times N` and `for dt` remain separate modes. Exhaustion emits
`EVOLVE_UNTIL_MAX_STEPS_ERROR` without publishing a partial State.

This design slice has been implemented in Phase 2 Green. The simulator runs
the bounded step loop and retains the specified provenance; predicate-
dependent QPU lowering rejects before allocation; exhaustion publishes only
the required diagnostic metadata. A post-implementation independent review
remains required before Phase 3 closeout.

The existing Phase 3 migration permission above must not be read as permission
for this new bounded-iteration mode; its Red and implementation approvals are
separate.

### Red-entry documentation checklist

Before requesting Red phase approval, the acceptance artifacts must retain the
following concrete contract:

- grammar: `Evolve() { operator * state until converged(state) max positive_literal }.run()`;
- post-transform-only predicate evaluation, with no initial-State check;
- full logical-State absolute L2 difference, Float64, tolerance `1e-9`;
- `EVOLVE_UNTIL_MAX_STEPS_ERROR` with no partial-State publication;
- provenance for `source_transform`, `predicate`, `metric`, `numeric_type`,
  `tolerance`, `iteration_count`, `max_steps`, `stop_reason`, and
  `realization`;
- simulator execution only; predicate-dependent QPU lowering rejected before
  allocation; `times` and `for` remain separate.

The Red suite should verify these observable contracts, not internal AST names
or an unapproved QPU resource estimate.

### Bounded acceptance matrix

| Case | Observable assertion | Target |
|---|---|---|
| Syntax | In-body `until`/`max` followed by `.run()` parses as bounded explicit mode | parser/typechecker |
| Bound validation | Missing, zero, negative, dynamic, or non-literal `max` fails closed | typechecker |
| Step semantics | Same `Operator * State` transform is reapplied; predicate is post-step-only | simulator |
| Convergence | Full-State L2/Float64/`1e-9` contract is used without measurement or RNG | simulator/runtime |
| Exhaustion | `EVOLVE_UNTIL_MAX_STEPS_ERROR`; no partial State reaches later code or `Measure` | runtime/diagnostics |
| Linearity | Tuple/entangled State remains one live carrier across iterations | HIR/runtime |
| Provenance | `source_transform`, `predicate`, `metric`, `numeric_type`, `tolerance`, `iteration_count`, `max_steps`, `stop_reason`, and `realization` are retained | IR/provenance |
| QPU safety | Predicate-dependent form is rejected before allocation with no partial circuit | QPU IR/lowering |
| Mode isolation | `times N` and `for dt` preserve existing pushforward behavior | regression |

Failure provenance is required as diagnostic/trace metadata on
`max_exhausted` and must include: `source_transform`, `predicate`, `metric`,
`numeric_type`, `tolerance`, `iteration_count`, `max_steps`, `stop_reason`,
and `realization`. State amplitudes, an intermediate State, and any resumable
handle are excluded.

This matrix is the reviewed acceptance contract for the bounded Phase 2
implementation. The Red suite is now green; it remains the regression
contract for subsequent refactors and target work.

### 4 — S02 migration and corpus review

1. Rewrite S02 only after the source surface and semantic contract are
   accepted.
2. Preserve `H_obj`, `dur`, `psi_sel`, real \(\hbar\), host arrays, and all
   terminal measurement semantics.
3. Compare simulator output and benchmark metrics against the current
   baseline with fixed seeds.
4. Review representative Hamiltonian, Pauli, grid, Lindblad, and discrete
   `times N` examples to ensure no accidental semantic conflation.
5. Verify that S02's measured distribution and benchmark metrics remain
   equivalent under fixed seeds, while the source exposes the complete
   time-evolution derivation.

### 5 — Phase 3 closeout

1. Refactor for readable responsibility boundaries.
2. Update normative grammar, AST, type-system, runtime, QPU, and vocabulary
   documents.
3. Update friction ledger and open-work register.
4. Record migration notes and reviewer-empathy summary.
5. Set Issue/WP/trace to `final-review-ready`; do not claim completion before
   the completion packet and final review requirements are satisfied.

## QPU realization contract

| Source meaning | Simulator realization | QPU realization | Failure behavior |
|---|---|---|---|
| `exp(-iHt/hbar) * psi` | Exact matrix/sparse exponential where supported | Pauli/gate decomposition or accepted Suzuki policy | Explicit unsupported-target diagnostic |
| finite product of infinitesimal steps | Execute the written product or documented equivalent | Gate sequence for each explicit step | No silent replacement with one exponential |
| formal `Limit` | Symbolic or exact profile only | Not executable without a declared discretization | Reject with required-realization diagnostic |
| `U * psi` with known `U` | Apply operator | Map to provider-neutral QPU IR | Reject if register/gate capability is insufficient |
| bare `psi` | Identity value | Not an evolution submission | `EVOLVE_REQUIRES_EXPLICIT_TRANSFORM` |

The QPU target profile owns `register_mapping` as typed target input; it does
not alter the source equation. An empty or incomplete mapping is a mapping
capability rejection, while a complete mapping that exceeds the declared
resource budget is a distinct budget rejection. Both failures publish typed
provenance and resource metadata and start no allocation.

### Phase 3 Green bounded implementation record

The target-boundary slice implements the contract above for finite binder
operators and explicit `Realize` formal-Limit sources. It performs a
source-preserving preflight, returns typed capability evidence where required,
and emits an empty provider-neutral circuit with zero allocation on mapping,
non-unitary-product, or budget rejection. Direct `Limit` remains rejected;
Suzuki finite synthesis is provider-neutral. This does not implement S02
numerical migration, live QPU submission, or provider SDK integration.

### Accepted formal `Limit` realization follow-up

ADR 0210 is Accepted and its bounded finite realization slice is implemented
and independently reviewed. A target profile supplies capability facts, but
the source must contain the explicit `Realize` conversion boundary. Direct
formal `Limit` remains the source-preserving `EVOLUTION_REALIZATION_REQUIRED`
rejection.

The accepted boundary is now source-visible: finite realization is written as
`Realize(U_formal, method, order, steps, error_budget)`. A target profile may
provide capability facts, but it may not insert this conversion implicitly.
Parser/type/semantic Red tests for `Realize` are a prerequisite to any
implementation.

## Ports and adapters

- `EvolutionLoweringPort`: accepts semantic evolution IR and target profile;
  returns a provider-neutral realization or a typed rejection.
- `QpuCapabilityPort`: reports supported operator families, qubits, gates,
  parameter binding, approximation policies, and resource limits.
- Existing `RngPort` and `MeasureSinkPort`: unchanged; measurement remains
  terminal.
- Existing Host/QPU job ports: unchanged; this WorkPlan does not add a vendor
  adapter or credential path.

No physics policy belongs in a QPU adapter. Adapters consume a validated
provider-neutral plan and report target facts.

## Diagnostics to design

- `EVOLVE_REQUIRES_EXPLICIT_TRANSFORM`: body returns a State without an
  explicit state-transforming evolution expression.
- `OPERATOR_EXP_DOMAIN_ERROR`: `exp` applied to a non-Operator or unsupported
  operator domain.
- `EVOLUTION_DIMENSION_ERROR`: exponent is not dimensionless.
- `EVOLUTION_TARGET_UNSUPPORTED`: selected target cannot realize the written
  evolution.
- `EVOLUTION_REALIZATION_REQUIRED`: a formal limit or symbolic expression
  needs an explicit finite realization policy.
- `EVOLUTION_APPROXIMATION_POLICY_MISSING`: target lowering requires order or
  step count and none was supplied.
- `EVOLUTION_PROVENANCE_LOST`: internal lowering would discard source
  equation structure; this is a compiler invariant failure, not a user fix.

Exact names remain provisional until Architecture approval.

## Verification matrix

| Stage | Evidence |
|---|---|
| Design | accepted spec, ADR decision, issue/WP synchronized |
| Phase 1 | Red parser/type/semantic/QPU-boundary tests only — completed |
| Phase 2 | Green acceptance tests; S02 compile; `times N` and Hamiltonian regression slices; no adapter policy — completed |
| Phase 3 closeout | Focused finite-realization regression, provenance/budget checks, independent review, and `git diff --check` — completed |
| Residual reconciliation | S02 fixed-seed/benchmark comparison and broader corpus migration — separate LISS-0438, not approved |
| Final review | final-review-ready trace, completion packet, and explicit residual risks |

## Context ledger

### Included

- Physicist-first language vision and DX harmony.
- Current AST/spec/runtime treatment of `Evolve`.
- ADR 0195 real-\(\hbar\) dynamics.
- LISS-0414 bracketed syntax.
- Existing Suzuki/Trotter and provider-neutral QPU IR boundaries.
- S02 `main_selection.sqx`, README, WP-0093, WP-0095.

### Omitted

- Vendor SDK details and credentials.
- Unrelated examples and private data.
- Dynamic QPU lane implementation details except the existing boundary.
- Exact AST node names and precedence tables, which are implementation
  details constrained by the accepted surface contract.

## Approval request

Architecture and Phase 1 approvals are recorded. The user approved Phase 2
Green implementation and Phase 3 design reinforcement for LISS-0437 on
2026-08-14, followed by the bounded finite-realization implementation and
closeout approval. The independent correction loop completed `READY` on
2026-08-17. QPU deployment, provider SDK work, S02 numerical migration, and
broader corpus reconciliation require the separate LISS-0438 workstream and
new phase approval.
