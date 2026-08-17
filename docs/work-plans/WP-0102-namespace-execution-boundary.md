# WP-0102: namespace declaration and execution boundary

| Field | Value |
|---|---|
| Status | **final-review-ready — Phase 3 inventory verified; no example rewrite required** |
| Purpose | Define a language boundary in which `namespace` contains declarations, while executable behavior begins at an explicit `pub fn main(...) -> Unit` or a named callable invoked from it. |
| Local Issue | [LISS-0440](../issues/LISS-0440-namespace-execution-boundary.md) |
| Related specification | [Staqex language specification](../specs/staqex-language-specification.md) |
| Related ADR | [ADR 0209](../architecture/adr/0209-explicit-blackboard-evolution-surface.md), [ADR 0210](../architecture/adr/0210-formal-limit-finite-realization-policy.md) |
| Related WP | [WP-0100](WP-0100-explicit-evolution-surface.md), [WP-0101](WP-0101-example-equation-fidelity.md) |
| Planning size | **M** |
| Approval state | Phase 1 Red approved 2026-08-17; Phase 2 implementation approved by user 2026-08-17. Example migration remains outside this phase. |
| Excluded | Provider SDK, live QPU submission, S02 numerical migration, new storage or deployment architecture. |

## [DESIGN CHECK]

- **Scope and expected behavior:** `namespace` is a declaration and name-resolution boundary under the existing grammar. It must not execute statements, mutate global state, measure, submit jobs, or depend on declaration order for side effects. The existing compilation-unit `pub fn main(...) -> Unit` entry contract remains unchanged; this WP does not add namespace-qualified entry selection.
- **Specifications and files inspected:** `AGENTS.md`; `docs/architecture/agent-quickstart.md`; `docs/specs/staqex-language-specification.md` §§6 and 8; `docs/architecture/adjudicator-language-vision.md`; `docs/architecture/physicist-dx-harmony.md`; Q# namespace guidance; WP-0100; WP-0101; ADR 0209; ADR 0210.
- **Component boundaries, ports/adapters, and VO/DTO candidates:** Parser/AST represents namespace declarations and main/callable bodies separately. Type checking validates declaration purity and entry signatures. Runtime starts only from a selected entry callable. Candidate semantic categories are `Declaration`, `Callable`, `EntryPoint`, and `GlobalConstant`; no mutable global `State` or runtime job object is introduced. Adapters remain outside the namespace semantics.
- **Applicable constraints:** Physicist-first source; Never Leave the State; terminal `measure`; no top-level executable statements; fail-closed diagnostics; no hidden execution in namespace initialization; no business or physics policy in adapters; preserve current `main` contract.
- **Decisions, assumptions, and unresolved ambiguities:** Phase 1 is limited to existing declaration forms and diagnostics. A global `State<T>`, mutable binding, measurement, `Evolve().run()`, QPU submission, or Host job action is not a declaration and belongs in a callable/entry boundary. New top-level `Parameter`, `Operator`, `Realize`, or namespace-qualified `main` forms are deferred unless a separate language-surface decision accepts them.
- **Included and omitted AI context:** Included current grammar, parser namespace handling, entry-point rules, example catalog, and Q# namespace comparison. Omitted provider implementations, unrelated language features, and the full example corpus.
- **Task routing (model/assistant/tool):** Architecture/design review for the boundary; deterministic parser/typecheck tests for the Red phase; implementation only after typed Phase approval.
- **Input/output evidence contract when AI output is involved:** Outputs must identify the exact grammar/spec rule, accepted and rejected source examples, diagnostic code, and deterministic verification. No hidden reasoning or unsupported language claims may be recorded.
- **Independent review lenses selected and why:** Contract and acceptance completeness; architecture and boundary integrity; source-to-domain fidelity; state and physics safety; migration and regression safety; phase and approval discipline. These lenses detect accidental top-level execution, mutable global state, and divergence from the accepted entry-point contract.
- **Verification plan:** Design consistency and `git diff --check`; Phase 1
  tests are limited to existing namespace parse behavior and compilation-unit
  entry handling; global State policy is deferred. Phase 2 parser/typechecker/
  runtime verification and Phase 3 example migration require separate gates.

## Goal

Make the source structure communicate whether a construct defines meaning or
executes a program. A reader should be able to identify the entry point without
guessing whether a namespace body runs during module loading.

## Conceptual shape (not a Phase 1 fixture)

```staqex
namespace QuantumOscillator {

  Parameter m : Mass
  Parameter omega : AngularFrequency

  Operator H =
      p^2 / (2 * m)
    + (m * omega^2 * x^2) / 2

  fn evolve_once(psi: State<WaveFunction>, t: Time)
      -> State<WaveFunction> {
    Operator U = exp(-i * H * t / hbar)
    return U * psi
  }

}

pub fn main() -> Unit {
  State psi_t = evolve_once(psi_initial, duration)
  measure psi_t
}
```

The following shapes remain invalid:

```staqex
namespace Invalid {
  H(q)
  measure q
  submit(program)
  State mutable_global = evolve(...)
}
```

## Design rules

1. A namespace contributes names; it does not create an execution sequence.
2. Global declarations must be immutable and side-effect free.
3. A `State<T>` is not a global mutable variable. State creation and
   transformation occur in a callable or entry body.
4. `measure`, `Evolve().run()`, Host submission, and mutable assignment are
   executable statements and require an execution boundary.
5. `pub fn main(...) -> Unit` remains the canonical compilation-unit entry;
   namespace-qualified entry selection is deferred.
6. Named functions and quantum transformations may be declared in a namespace,
   but their bodies execute only when called.
7. Import and namespace resolution must not depend on runtime initialization.
8. Library units without `main` remain valid but are not runnable programs.

## Proposed acceptance matrix

| Source shape | Expected result |
|---|---|
| Namespace with an existing accepted declaration or pure callable | Accept |
| New top-level `Operator`, `Equation`, or `Parameter` declaration | Deferred; not a Phase 1 fixture |
| Namespace with an unrecognized executable member | Observe existing `PARSE_ERROR`; no new namespace diagnostic in Phase 1 |
| Mutable global `State` policy | Deferred; no new global-state diagnostic in Phase 1 |
| Compilation unit with existing `pub fn main() -> Unit` | Accept as runnable entry |
| Library namespace without `main` | Accept as non-entry compilation unit |
| Namespace-qualified entry selection | Deferred; not introduced by this WP |
| Host submission embedded in namespace initialization | Deferred; Phase 1 does not add a Host boundary diagnostic |

## Planned phases

### Phase 0 — design and inventory

- Confirm current parser, AST, typechecker, runtime, and example behavior.
- Identify any examples that rely on namespace execution or implicit global state.
- Maintain the linked Issue and acceptance specification as the Red authority.

### Phase 1 — Red

- Add failing tests for accepted declaration forms.
- Add a Red fixture for existing namespace parse rejection, if not already
  covered. Do not add a new diagnostic contract.
- Add compilation-unit entry and library-unit acceptance cases.

### Phase 2 — Green

- Implement only the accepted declaration/entry boundary.
- Preserve existing `pub fn main` behavior and diagnostics.
- Do not introduce a new global runtime or module initialization mechanism.

### Phase 3 — Refactor and review

- Migrate only examples shown by the inventory to depend on the explicit
  boundary.
- Verify imports, source readability, and terminal measurement rules.
- Run an independent context review before any broader example migration.

## Acceptance conditions

- Namespace bodies contain only existing grammar members.
- Unrecognized namespace members fail with existing parser behavior.
- No new mutable-global or implicit-initialization semantics are introduced.
- Existing library imports and `pub fn main(...) -> Unit` remain compatible.
- The source clearly distinguishes definition from execution.
- Phase 1 Red remains limited to existing grammar and diagnostics. New entry
  selection or global declaration forms require a separate Issue/Spec.
