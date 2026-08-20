# LISS-0445 consumer-wide migration design review 02

| Field | Value |
|---|---|
| Trigger | Approved continuation after LISS-0444 bounded Phase 2 Green |
| Scope | LISS-0445, WP-0108, consumer migration Spec, open-work synchronization |
| Context | Fresh independent read-only context; no implementation or approval |
| Result | **READY / COMPLETE** for design intake |
| Next gate | Typed Phase 1 Red approval; not granted by this review |

## Review result

The design now separately inventories `physics_ir`, `physics_equation`/
`EquationNode`, `OpExpr`, HIR, Quantum Semantic IR, both Algorithm Plan
representations, `symbolic_ir`, evaluator, QASM/QPU, binder, H1 early-return,
continuous, and host/provider paths. Each has a disposition, owner boundary,
planned phase, and exit or deferral evidence.

The design fixes the single canonical binder build boundary and requires the
shared `CompileResult.scientific_semantic_ir` identity, explicit consumer
rejection fields, and a concrete ordinary-QASM fixture/retirement milestone.
The Phase 1 Red file and fixture directory are fixed and production changes
are prohibited.

## Disposition

- Previous inventory, binder-boundary, rejection-matrix, and fallback-exit
  findings: accepted and corrected in the Spec/WP.
- No unresolved P0/P1/P2 findings remain.
- Provider SDK/live QPU, S02, solver, implicit finiteization, and ADR-0211
  changes remain excluded.

## Reusable lenses

Canonical authority; projection conservation; contract completeness;
realization/fail-closed behavior; migration safety; phase/approval discipline;
evidence hygiene.

## Terminal state

`COMPLETE` for the design review. This record does not approve Phase 1 Red,
Phase 2 Green, implementation, deletion, or any technology choice.
