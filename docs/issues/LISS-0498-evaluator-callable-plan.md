# LISS-0498: Evaluator callable/object runtime-plan family

| Field | Value |
|---|---|
| Status | **phase-3-refactor-complete** |
| Phase | phase-3-refactor-complete |
| Parent | [WP-0107](../work-plans/WP-0107-scientific-semantic-core.md) |
| Predecessor | [LISS-0497](LISS-0497-evaluator-binder-plan.md) |
| Design authority | [Scientific Semantic Consumer Migration](../specs/staqex-scientific-semantic-consumer-migration.md#liss-0498-callableobject-runtime-plan-family) |
| Scope approval | User approved continuation on 2026-09-01 |
| Architecture approval | Existing LISS-0493 runtime-plan boundary; no new boundary decision |
| Phase 1 Red approval | User approved continuation on 2026-09-01 |
| Implementation permission | Phase 2 Green and Phase 3 refactor approved by user |
| Next approval | Next semantic-family Phase 1 Red |

## [DESIGN CHECK]

- **Scope and expected behavior:** define a canonical runtime-plan family for
  free functions, class declarations, method calls, receiver identity, and
  return flow.
- **Specifications and files inspected:** WP-0107, LISS-0493–0497, the
  consumer-migration and language Specs, canonical `FunDecl`/`ClassDecl`/
  `Call`/`Attr` nodes, evaluator callable mechanics, readiness, and process
  lessons.
- **Component boundaries:** canonical Semantic IR owns callable structure and
  provenance; Runtime Plan projects it; evaluator later consumes the plan.
  AST objects may remain payload mechanics but not authority.
- **Applicable constraints:** Phase 1 Red only; no provider/QPU/AWS, Rust,
  finiteization, solver policy, or public runtime API change.
- **Decisions and ambiguities:** this slice covers a local class construction
  and method invocation with terminal State/Measure. Recursion, cross-module
  dispatch, dynamic lanes, binder/operator resolution, and target realization
  remain separate.
- **Verification plan:** add root Red tests for family classification,
  declaration/invocation/receiver provenance, dedicated executor routing, and
  absence of implicit target realization.

## Acceptance scenarios for Phase 1 Red

1. Given a local class declaration and method invocation, when a runtime plan
   is built, then its family is `callable`.
2. Given that plan, when callable nodes are inspected, then declaration,
   invocation, receiver, output, authority, provenance, and execution status
   are conserved.
3. Given canonical execution of the local callable program, when execution
   runs, then a dedicated callable executor is selected and the legacy AST body
   is not entered.
4. Given a callable program without source-visible `Realize`, when its plan is
   built, then no implicit target finite artifact is created.

## Phase boundary

Phase 1 creates only the failing acceptance contract. Phase 2 will add the
minimum callable projection and bounded local executor. Recursive,
cross-module, dynamic-lane, binder/operator, and target realization behavior
remain separate work.

## Phase 1 Red result

- Added `tests/test_liss_0498_evaluator_callable_plan_red.py`.
- Red verification: **3 failed, 1 passed**, with no collection errors. The
  failures expose missing callable-family classification, callable
  declaration/invocation/receiver fields, and the dedicated executor. No
  production implementation is authorized in this phase.

Human review of the Red contract is required before Phase 2 Green.

## Phase 2 Green result

- Added `RuntimeCallableNode` and `RuntimeExecutionPlan.callables` with
  declaration, invocation, receiver, output, authority, provenance, and
  execution status evidence.
- Canonical plans containing local `FunDecl`/`ClassDecl` declarations and
  `Call` nodes are classified as `callable`.
- Added `_execute_callable_plan` for the bounded local callable/object
  State/Measure slice, preserving existing local call mechanics behind the
  canonical plan boundary.
- LISS-0498 **4 passed**; related runtime-plan tests **21 passed**; manual
  canonical execution, `py_compile`, and `git diff --check` passed.
- Recursive/cross-module dispatch, dynamic lanes, binder/operator resolution,
  target realization, and provider execution remain out of scope.

## Phase 3 result

- Extracted callable projection into `_build_runtime_callable_nodes`, keeping
  family construction readable and separate from the main plan builder.
- Added an explicit eligibility boundary: closed local callable execution uses
  the dedicated plan route, while class construction remains on the existing
  compatibility path until its mechanics have a dedicated contract.
- Same-context review found no blocking finding after correcting and testing
  the compatibility boundary.
- Verification: LISS-0498 plus related runtime-plan and namespace/class tests
  **23 passed**; `py_compile` and `git diff --check` passed.

Process review: no operating-contract deviation or operational problem found.

Issue complete. The next safe action is a new semantic-family Phase 1 Red
contract.
