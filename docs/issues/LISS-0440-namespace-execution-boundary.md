# LISS-0440: namespace declaration and execution boundary

| Field | Value |
|---|---|
| Status/phase | **complete** — Phase 3 inventory verified; no example rewrite required |
| WorkPlan | [WP-0102](../work-plans/WP-0102-namespace-execution-boundary.md) |
| Specification | [Namespace execution boundary](../specs/staqex-namespace-execution-boundary.md) |
| Scope approval | User approval recorded 2026-08-17 |
| Phase approval | Phase 1 Red approved by user 2026-08-17 |
| Implementation approval | Phase 2 approved by user 2026-08-17; existing implementation satisfies the approved boundary |
| Completion PR | **PR #553** |

Status/phase: **complete**

## Objective

Make `namespace` a declaration/name-resolution boundary and keep executable
behavior behind `pub fn main(...) -> Unit` or an explicitly invoked callable.

## In scope

- namespace declaration contents and imports;
- existing immutable/declaration forms;
- named callable declarations and the existing compilation-unit `main` entry;
- rejection of unrecognized namespace members using existing parser behavior;
  mutable global State policy is deferred;
- parser, AST, typecheck, diagnostics, tests, and narrowly affected examples.

## Out of scope

- new runtime module initialization;
- provider SDK, credentials, network, or live QPU submission;
- S02 numerical migration;
- unrelated namespace, class, or visibility redesign.

## Acceptance outline

- Declaration-only namespace bodies are accepted.
- Unrecognized namespace execution members use existing parser behavior;
  measurement/submission and mutable global State policies are deferred.
- Existing compilation-unit `pub fn main(...) -> Unit` remains the runnable
  entry contract; namespace-qualified entry selection is deferred.
- Library units without `main` remain valid and non-runnable.
- No execution order or side effect is inferred from declaration order.
