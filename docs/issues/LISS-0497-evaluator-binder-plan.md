# LISS-0497: Evaluator binder runtime-plan family

| Field | Value |
|---|---|
| Status | **phase-3-refactor-complete** |
| Phase | phase-3-refactor-complete |
| Parent | [WP-0107](../work-plans/WP-0107-scientific-semantic-core.md) |
| Predecessor | [LISS-0496](LISS-0496-evaluator-evolution-plan.md) |
| Design authority | [Scientific Semantic Consumer Migration](../specs/staqex-scientific-semantic-consumer-migration.md#liss-0497-binder-runtime-plan-family) |
| Scope approval | User approved continuation on 2026-09-01 |
| Architecture approval | Existing LISS-0493 runtime-plan boundary; no new boundary decision |
| Phase 1 Red approval | User approved 2026-09-01 |
| Implementation permission | Phase 2 Green and Phase 3 refactor approved by user |
| Next approval | Next semantic-family Phase 1 Red |

## [DESIGN CHECK]

- **Scope and expected behavior:** define a canonical runtime-plan family for
  `Sigma`/`Pi` and other `OpBinder` nodes, preserving domain, body, output,
  source identity, provenance, authority, and realization status.
- **Specifications and files inspected:** WP-0107, LISS-0493–0496, the
  consumer-migration and language Specs, canonical binder metadata, evaluator
  runtime-plan projection, implementation readiness, and process lessons.
- **Component boundaries:** canonical Semantic IR owns binder meaning and
  provenance; Runtime Plan projects it; a later evaluator executor consumes
  only the plan. Finite binder lowering and QPU/QASM realization remain
  consumer boundaries.
- **Applicable constraints:** Phase 1 Red only; no provider/QPU/AWS, Rust,
  implicit enumeration, hidden finiteization, or production implementation.
- **Decisions and ambiguities:** this slice covers canonical operator binders
  with an explicit source domain and body. Classical numeric binders,
  symbolic/unbounded domains, multi-binder constraints, target realization,
  and callable/dynamic forms remain separate.
- **Verification plan:** add root Red tests for family classification,
  source/provenance conservation, dedicated executor routing, and the absence
  of implicit target realization.

## Acceptance scenarios for Phase 1 Red

1. Given a compiled `Operator H = Sigma (...) { ... }`, when a runtime plan is
   built, then its family is `binder`.
2. Given that plan, when its binder node is inspected, then domain/body/output
   source IDs, authority, provenance, and realization status are conserved.
3. Given a canonical binder program, when execution runs, then a dedicated
   binder executor is selected and the legacy AST body is not entered.
4. Given a binder without source-visible `Realize`, when its plan is built,
   then no implicit target finite artifact is created.

## Phase boundary

Phase 1 creates only the failing acceptance contract. Phase 2 will add the
minimum canonical binder projection and bounded local executor. Classical and
symbolic binder semantics, finite target lowering, QASM, and provider execution
remain separate work.

## Phase 1 Red result

- Added `tests/test_liss_0497_evaluator_binder_plan_red.py`.
- Red verification: **3 failed, 1 passed**, with no collection errors. The
  failures expose missing binder-family classification, binder source/provenance
  fields, and the dedicated executor.
- No production implementation was changed for this issue.

Human review of the Red contract is required before Phase 2 Green.

## Phase 2 Green result

- Added `RuntimeBinderNode` and `RuntimeExecutionPlan.binders` with binder
  source, domain, body, output, authority, provenance, and realization status.
- Canonical plans containing `OpBinder`/`Sigma`/`Pi` nodes are classified as
  `binder` unless a more specific already-migrated runtime family owns the
  program.
- Added `_execute_binder_plan` for the bounded local State/Measure slice. The
  compile-time Operator binder is removed from the deferred runtime payload;
  no finite enumeration or target artifact is introduced.
- LISS-0497 **4 passed**; related runtime-plan tests **21 passed**;
  `py_compile`, manual canonical execution, and `git diff --check` passed.
- Classical numeric binders, symbolic/unbounded domains, multi-binder
  constraints, finite target lowering, QASM, and provider execution remain
  out of scope.

## Phase 3 result

- Extracted the shared `_unit_without_operator_declarations` helper used by
  both binder and evolution runtime routes.
- Reused one canonical node lookup map while projecting runtime families,
  without changing source identity, family precedence, or execution behavior.
- Same-context review found no blocking findings; unsupported symbolic,
  classical, target, and provider paths remain explicitly bounded.
- Verification: LISS-0497 and related runtime-plan tests **21 passed**;
  `py_compile` and `git diff --check` passed.

Process review: no operating-contract deviation or operational problem found.

Issue complete. The next safe action is a new semantic-family Phase 1 Red
contract.
