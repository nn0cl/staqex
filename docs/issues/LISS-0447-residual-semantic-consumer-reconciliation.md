# LISS-0447: Residual Semantic Consumer Reconciliation

| Field | Value |
|---|---|
| Status | **Phase 3 Refactor final-review-ready** |
| Discovered in | LISS-0445 related regression and LISS-0446 closeout |
| Specification | [Residual Semantic Consumer Reconciliation](../specs/staqex-residual-semantic-consumer-reconciliation.md) |
| WorkPlan | [WP-0110](../work-plans/WP-0110-residual-semantic-consumer-reconciliation.md) |
| Authority | [ADR 0211](../architecture/adr/0211-scientific-semantic-core-and-ir-authority.md) |

## Objective

Reconcile the three remaining semantic-consumer contracts that still fail the
canonical Scientific Semantic IR boundary, without reopening completed QASM
public-entry work or changing the language/realization architecture.

## Bounded subcontracts

1. **AlgorithmPlan:** replace the temporary `scientific_semantic_ir.AlgorithmPlan`
   DTO as an executable consumer input with one compatible projection into
   `algorithm_plan_ir.AlgorithmPlanModule`, preserving source identity and
   realization policy.
2. **H1 delivery:** remove the `compile_source()` H1 early return that bypasses
   the canonical semantic result, while retaining H1 authoring diagnostics and
   its separate source-language boundary.
3. **Ordinary QASM:** retire the AST fallback for the fixed ordinary-gate
   fixture only after canonical projection coverage proves equivalent output;
   unsupported cases must reject explicitly and atomically.

These are separately testable subcontracts. Completion of one does not imply
completion of the others.

## Exclusions

- no provider SDK, live QPU, network, or credentials;
- no S02 numerical migration or solver;
- no LISS-0446 public-entry redesign;
- no direct `Limit` lowering or implicit finiteization;
- no broad H1 language redesign or example rewrite;
- no removal of compatibility paths without replacement and rollback evidence.

## Current evidence

- `AlgorithmPlan` now uses one `AlgorithmPlanModule` projection with a
  compatibility provenance view; the canonical fields and rejection reasons
  are tested.
- H1 `compile_source()` now builds `ScientificSemanticIR`; H1-specific
  `physics_ir` and state-transform data remain authoring/diagnostic
  projections, while inspection/snapshot use the canonical IR.
- ordinary canonical gates now project preparation, `apply`, `cnot`,
  `capply`, and terminal measurement directly from the compile-owned semantic
  IR; the AST fallback is no longer used for this path.
- unsupported ordinary inputs reject atomically with
  `E_QPU_CANONICAL_PROVENANCE` and no QASM or circuit artifacts.

## Gate

Phase 1 Red is complete and recorded. The AlgorithmPlan Phase 2 Green batch is
implemented under separate approval and passed independent review. The H1
Phase 2 Green batch is also complete after its independent review. The
ordinary-QASM Phase 2 Green batch is complete after its independent review.
The H1 batch passed its post-correction independent review and is complete.
The ordinary-QASM Green implementation passed its independent review. Phase 3
removed the obsolete ordinary AST fallback and is ready for final review.
