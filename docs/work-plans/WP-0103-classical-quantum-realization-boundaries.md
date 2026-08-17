# WP-0103: classical, mathematical, quantum, and realization boundaries

| Field | Value |
|---|---|
| Status | **final-review-ready — Phase 3 inventory verified; no example rewrite required** |
| Purpose | Make source-level distinctions visible between classical values, mathematical notation, quantum meaning, finite realization, and Host-side experiment control. |
| Local Issue | [LISS-0441](../issues/LISS-0441-classical-quantum-realization-boundaries.md) |
| Related specification | [Explicit evolution surface](../specs/staqex-explicit-evolution-surface.md) |
| Related ADR | [ADR 0209](../architecture/adr/0209-explicit-blackboard-evolution-surface.md), [ADR 0210](../architecture/adr/0210-formal-limit-finite-realization-policy.md) |
| Related WP | [WP-0100](WP-0100-explicit-evolution-surface.md), [WP-0101](WP-0101-example-equation-fidelity.md), [WP-0102](WP-0102-namespace-execution-boundary.md) |
| Planning size | **M** |
| Approval state | Phase 1 Red approved 2026-08-17; Phase 2 implementation approved by user 2026-08-17. Broad language-surface expansion remains outside this WP. |
| Excluded | General ODE/PDE solver commitment, full classical physics library, provider SDK, live QPU submission, S02 numerical migration, and automatic finiteization. |

## [DESIGN CHECK]

- **Scope and expected behavior:** Define and document five semantic roles: classical value, mathematical binder/expression, quantum state/operator/transform, finite target realization, and Host execution control. Phase 1 tests only roles and bridges already represented by the shipping grammar and contracts. A mathematical binder is not silently treated as a Host loop; `steps` and `shots` are not silently treated as physics parameters.
- **Specifications and files inspected:** `AGENTS.md`; `docs/architecture/adjudicator-language-vision.md` §§2–3; `docs/collaboration/independent-review-perspectives.md`; `docs/specs/staqex-language-specification.md`; `docs/specs/staqex-explicit-evolution-surface.md`; `docs/specs/staqex-v1-qpu-capability-honesty.md`; WP-0100; WP-0101; ADR 0209; ADR 0210; official Q# type, namespace, operation, iteration, and submission guidance.
- **Component boundaries, ports/adapters, and VO/DTO candidates:** Classical values and physical parameters remain typed values. Mathematical expressions/binders remain semantic AST nodes. `State<T>`, `Operator`, `Observable`, and explicit state transforms remain Kernel semantic values. Existing realization plans retain their current ADR 0210 contract. Host `Job` and `JobResult` remain outside Kernel source syntax; no new Host block, `Sweep`, or realization result type is introduced by Phase 1.
- **Applicable constraints:** Physicist-first source; source denotes the same blackboard physics; Never Leave the State; terminal `measure`; no silent Host emulation; no hidden Limit-to-exp or gate rewrite; unsupported target behavior is explicit and fail-closed; adapters do not contain physics policy.
- **Decisions, assumptions, and unresolved ambiguities:** The first design separates roles semantically without adding new blocks. Existing `Sigma`/`Pi` binders, existing `evolve` modes, terminal `measure`, and existing provider-neutral Host contracts are the Phase 1 evidence. `Host { ... }`, `FiniteEvolution`, and a new realization-result schema are deferred because they are not current shipping source contracts.
- **Included and omitted AI context:** Included existing evolution/Realize contracts, QPU honesty, official examples, learning-path documents, and Q# comparison. Omitted provider-specific lowering, external credentials, and unrelated classical-language features.
- **Task routing (model/assistant/tool):** Architecture/design review for the semantic taxonomy and bridge rules; deterministic type/effect and negative tests for the Red phase; implementation only after acceptance review and Phase approval.
- **Input/output evidence contract when AI output is involved:** Every proposed rule must show a source example, its semantic role, allowed bridge, forbidden implicit conversion, diagnostic behavior, and verification evidence. Claims about Q# or other languages must cite primary documentation; no hidden reasoning is recorded.
- **Independent review lenses selected and why:** Source-to-domain fidelity; type/dimension/validity closure; realization and fail-closed behavior; state and physics safety; contract completeness; migration/regression safety; evidence/context hygiene. These lenses identify accidental classicalization and hidden finiteization.
- **Verification plan:** Build a source-role inventory for representative
  examples; add Red tests only for wrong-domain operations and implicit bridges
  already expressible in the current grammar; do not make Realize diagnostic
  catalog synchronization a Phase 1 requirement; defer new Host syntax and
  result schemas; run focused regression and independent review.

## Goal

A reader should be able to inspect a source file and answer all of the
following without relying on compiler folklore:

- Is this a classical parameter or a quantum state?
- Is this a mathematical sum or an execution loop?
- Is this an ideal quantum evolution or a finite approximation?
- Is this a QPU resource parameter or a physical parameter?
- Is this operation part of the physics or Host-side experiment management?

## Semantic roles

### Classical values (conceptual, not a Phase 1 fixture)

```staqex
Parameter mass : Mass
Parameter duration : Time
Int shots = 1000
Float error_budget = 1e-3
```

Physical parameters may participate in quantum equations. `shots` and
`error_budget` are execution controls and must not be confused with physical
quantities.

### Mathematical expressions (conceptual, not a Phase 1 fixture)

```staqex
Operator H =
  Sigma (i In sites) { J[i] * Z[i] * Z[i + 1] }
```

The binder denotes a mathematical sum. It is not automatically a mutable
classical loop and must preserve its source domain and provenance.

### Quantum meaning (existing LISS-0437 contract; not a new Phase 1 fixture)

```staqex
Operator U_exact = exp(-i * H * duration / hbar)

State psi_final = Evolve() {
  U_exact * psi_initial
}.run()
```

`State`, `Operator`, `Observable`, and state-transform expressions are
quantum/physical semantics, not ordinary mutable classical variables.

### Finite realization (existing ADR 0210 contract; not a new result type)

```staqex
Realize(
  source = U_exact,
  method = suzuki,
  order = 2,
  steps = 16,
  error_budget = error_budget
)
```

`steps`, `order`, and `error_budget` describe realization. They must not be
inferred from the ideal equation or silently inserted by an adapter. Exact
diagnostic catalog synchronization is deferred; Phase 1 adds no new code.

### Host control

Host `Job`/`JobResult` contracts remain outside the Kernel source syntax. Host
iteration manages experiments and jobs; it is not part of the quantum equation.

## Boundary rules

1. Classical values and physical quantities follow the existing Type-First,
   literal-lift, and coefficient-lift contracts; this WP introduces no new
   conversion restriction.
2. State/classical interaction follows the existing Type-First and lift
   contracts; this WP introduces no new State-to-classical conversion rule.
3. A quantum observation crosses to a classical result only through an
   explicit observation/measurement operation.
4. `Sigma` and `Pi` are mathematical binders, not Host loops.
5. Static `forEach` may elaborate a declared finite quantum register, but its
   role must remain distinct from Host iteration.
6. `evolve times N` represents quantum-transform repetition, not parameter
   sweeping.
7. `evolve until` represents a bounded semantic evolution mode and remains a
   static-QPU capability rejection where the target cannot represent it.
8. Existing `Realize` retains its current source transform, method, parameters,
   error evidence, and resource evidence; a new result schema is deferred.
9. Exact simulator execution, approximate simulator execution, and QPU gate
   realization must remain distinguishable in results and provenance.
10. Unsupported bridges reject explicitly; the compiler must not replace a
    mathematical or quantum construct with an easier classical computation.

## Proposed acceptance matrix

| Construct | Semantic role | Implicit bridge | Expected behavior |
|---|---|---|---|
| `Sigma (i In D) { term(i) }` | Mathematical binder | Host loop | No; retain binder structure |
| `forEach q in register` | Static quantum expansion | Dynamic Host loop | No; target-lane expansion only |
| Existing Host `Job`/`JobResult` contract | Classical orchestration | Quantum evolution | No; remain outside Kernel source |
| `evolve times N` | Quantum transform repetition | Host sweep | Existing contract reference; not a new Phase 1 fixture |
| `exp(-i * H * t / hbar)` | Ideal quantum propagator | Gate sequence | Existing explicit-evolution contract reference; not a new Phase 1 fixture |
| Existing `Realize(source, ...)` | Finite realization | Hidden rewrite | Existing ADR contract reference; diagnostic/catalog changes deferred |
| terminal `measure psi` | Quantum→classical boundary | Silent state read | No; explicit terminal observation |
| `Operator H = classical_loop_result` | Mathematical/quantum definition | Mutable global assembly | Deferred; no new binder/constructor contract in Phase 1 |

## Classical mathematics and physics coverage

The goal is minimum expression capability, not an immediate full scientific
solver library.

| Area | Initial target |
|---|---|
| Numbers and units | Int/Float/complex, constants, parameters, dimensions |
| Linear algebra | vectors, matrices, inner/outer products, tensor products, indexed elements |
| Mathematical structure | finite sum/product, indices, equations, substitutions |
| Calculus notation | derivative, partial derivative, integral, variation as explicit semantic forms or documented boundary |
| Classical mechanics | coordinates, momentum, energy, Hamiltonian/Lagrangian expressions |
| Waves/Fourier | wavefunction, mode/index structure, Fourier-related expressions |
| Probability/statistics | finite distributions, expectation, variance, weighted samples |
| Open systems | density state, jump operators, Lindblad coefficients with explicit simulator boundary |
| ODE/PDE | expression of equation, initial/boundary conditions; solver commitment remains separate |
| Field/thermal physics | typed expression and intentional partial boundary before any solver claim |

## Planned phases

### Phase 0 — taxonomy and representative inventory

- Classify representative B, A, S01, and S02 examples by semantic role.
- Record current supported/partial/unsupported/intentional-scope status.
- Identify where classical syntax currently hides quantum meaning or where
  realization metadata is mixed into physics source.
  - Maintain the linked Issue and acceptance specification as the Red authority.

### Phase 1 — Red

- Do not add a new State/classical conversion test; preserve existing
  Type-First and lift tests.
- Add failing tests distinguishing existing mathematical binders from executable
  `evolve`/Host contracts.
- Do not add Realize diagnostic-catalog tests in this phase; catalog
  synchronization is deferred to the existing realization follow-up.
- Do not add tests for new `Host {}` syntax, `FiniteEvolution`, or a new
  realization-result schema.

### Phase 2 — Green

- Implement only the accepted semantic/type/diagnostic rules.
- Preserve existing source spellings where their meaning is already valid.
- Do not introduce broad classical physics solvers or provider integrations.

### Phase 3 — Refactor, examples, and review

- Update representative examples so source roles are visible.
- Add role/provenance output to deterministic diagnostics where required.
- Verify QPU rejection and simulator behavior remain distinct.
- Run independent review focused on accidental classicalization and hidden
  finiteization.

## Acceptance conditions

- Source/document readers can distinguish classical parameters, mathematical
  binders, quantum transforms, finite realization, and Host control.
- No implicit State collapse, Host fallback, or finite QPU conversion occurs.
- `Sigma`, `Pi`, and existing Host contracts have documented semantic roles.
  `evolve` and `Realize` are referenced existing contracts, not new Phase 1
  fixtures. Realize diagnostics remain governed by ADR 0210 and are deferred
  from this Red slice.
- Exact/approximate provenance remains governed by existing ADR 0210; no new
  result DTO is introduced in this WP.
- Minimum classical mathematical/physical expression needs are documented as
  supported, partial, unsupported, or intentional scope.
- Existing explicit-evolution, finite-Realize, QPU honesty, and S02 exclusion
  boundaries remain unchanged.
- Phase 1 Red remains limited to existing grammar and diagnostics. New syntax,
  result schemas, Host blocks, and broader classical-physics coverage require
  a separate Issue/Spec.
