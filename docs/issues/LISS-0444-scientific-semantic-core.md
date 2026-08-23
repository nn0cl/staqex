# LISS-0444: Scientific Semantic Core and IR authority

| Field | Value |
|---|---|
| Status/phase | **Phase 2 Green bounded consumer migration complete — consumer-wide migration pending** |
| WorkPlan | [WP-0107](../work-plans/WP-0107-scientific-semantic-core.md) |
| Specification | [Scientific Semantic Core](../specs/staqex-scientific-semantic-core.md) |
| ADR | [ADR 0211](../architecture/adr/0211-scientific-semantic-core-and-ir-authority.md) |
| Predecessors | [LISS-0440](LISS-0440-namespace-execution-boundary.md), [LISS-0441](LISS-0441-classical-quantum-realization-boundaries.md), [LISS-0437](LISS-0437-explicit-evolution-surface.md) |
| Approval status | Architecture, Phase 1 Red, representative Phase 3 slice, consumer-wide migration Phase 1 Red, and bounded Phase 2 Green approved; consumer-wide migration remains pending |

Status/phase: **Bounded Phase 2 Green complete — consumer-wide migration pending**

## Objective

Design a durable language-semantic foundation in which blackboard mathematics,
classical expressions, quantum meaning, evolution relations, and finite
realization are represented structurally and traceably from source to each
consumer. The design is based on implementation reality, not on preserving
existing DTOs or minimizing the first patch.

## Audit basis

The current implementation contains multiple partially overlapping models:
operational AST and `OpExpr`, soft `Physics IR`, generic `Symbolic IR`,
caller-injected `EquationNode` values with string expressions, HIR, Quantum
Semantic IR, Algorithm Plan IR, and a large evaluator with repeated semantic
dispatch. `EquationNode` is not produced by the parser, and Physics IR is not
the authoritative execution meaning. These are design facts to resolve, not
assets to preserve by default.

## In scope

- canonical source-to-semantic representation and ownership;
- structural expression/equation nodes with type, dimension, phase, and
  provenance;
- explicit classical, mathematical, quantum, evolution, simulator, and
  finite-realization roles;
- relationship between parser, typecheck, HIR, semantic IR, simulator, and
  `Realize`/Algorithm Plan projections;
- migration or retirement criteria for existing Physics/Symbolic/Equation DTO
  paths;
- independent review of implementation reality, source fidelity, and future
  language debt.

## Out of scope

- provider SDKs, credentials, network, or live QPU submission;
- solver implementation, automatic differentiation, or automatic integration;
- S02 numerical migration;
- broad example rewrites before the canonical semantic contract is accepted;
- implementation phases before Architecture approval and a reviewed Spec.

## Completion condition for design intake

An accepted ADR, reviewed Spec, and WP define one authoritative semantic model,
the migration/deprecation boundary, the first Red phase, and the explicit
review request below. No implementation is authorized by this Issue alone.
