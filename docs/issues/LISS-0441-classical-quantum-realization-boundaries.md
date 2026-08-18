# LISS-0441: classical, mathematical, quantum, and realization boundaries

| Field | Value |
|---|---|
| Status/phase | **complete** — Phase 3 inventory verified; no example rewrite required |
| WorkPlan | [WP-0103](../work-plans/WP-0103-classical-quantum-realization-boundaries.md) |
| Specification | [Classical/quantum/realization boundaries](../specs/staqex-classical-quantum-realization-boundaries.md) |
| Scope approval | User approval recorded 2026-08-17 |
| Phase approval | Phase 1 Red approved by user 2026-08-17 |
| Implementation approval | Phase 2 approved by user 2026-08-17; existing implementation satisfies the approved boundary |
| Completion PR | **PR #553** |

Status/phase: **complete**

## Objective

Ensure that source code distinguishes classical values, mathematical
expressions, quantum meaning, finite realization, and Host experiment control.

## In scope

- typed classical parameters and physical quantities;
- existing `Sigma`/`Pi` mathematical binders and indexed expressions;
- `State<T>`, `Operator`, `Observable`, and explicit state transforms;
- explicit `Realize` policies and provenance;
- existing Host-side `Job`/`JobResult`, shots, and submission boundaries;
- representative example documentation; new implicit-bridge rules, diagnostic
  catalog synchronization, and new provenance/result schemas are deferred.

## Out of scope

- a complete classical physics library;
- general ODE/PDE solver commitment;
- automatic finiteization or hidden gate synthesis;
- provider SDK, credentials, network, or live QPU submission;
- S02 numerical migration.

## Acceptance outline

- `Sigma`/`Pi` remain mathematical binders, not implicit Host loops.
- `State<T>` cannot silently become a classical scalar.
- Existing `Realize` policy is the visible boundary to finite execution;
  result-type redesign is deferred.
- existing exact/approximate realization evidence remains distinguishable;
  new result schemas are deferred.
- minimum classical mathematics/physics coverage is recorded as supported,
  partial, unsupported, or intentional scope.
