# LISS-0437 Phase 3 design reinforcement

## Approval and boundary

- Date: 2026-08-14
- Approval received: Phase 3 design reinforcement and implementation-preparation
- Implementation permission: **Not granted by this record**
- Confirmed Phase 2 baseline: bounded explicit `until` minimum slice is READY
- Design scopes kept separate: formal `Limit`, QPU realization, S02/corpus
  migration, and final closeout

## Design rule

The source remains the physics statement. A target may realize the written
meaning exactly, realize it under an explicitly declared approximation policy,
or reject it before allocation. No Phase 3 work may replace a formal
`Limit` with `exp`, replace a product with one exponential, or infer a QPU
policy from source syntax.

## Workstream A — formal `Limit`

Accepted source meaning:

```staqex
Operator U_dt = I - i * H_obj * dt / hbar
Operator U_t = Limit N -> Infinity {
    (I - i * H_obj * dur / (N * hbar)) ^ N
}
State psi_final = Evolve() { U_t * psi_sel }.run()
```

Design boundary:

- Parser/semantic representation must preserve `Limit`, `N`, `Infinity`, the
  step operator, exponent, and source span.
- MVP simulator and QPU execution remain target-rejected unless a finite
  realization policy is explicitly attached.
- `Limit` must not silently lower to `exp`, a fixed `max`, or one transform.
- The required diagnostic must identify that a finite realization policy is
  missing and must not publish a partial State or circuit.

Required pre-implementation evidence: AST/IR provenance probe, invalid-bound
and missing-realization tests, target rejection test, and an architecture
decision if a finite realization policy is proposed.

## Workstream B — binder-aware QPU realization

Design boundary:

- QPU lowering consumes provider-neutral evolution IR and a target profile;
  it does not interpret arbitrary binder policy in an adapter.
- The profile must declare supported operator family, register mapping,
  Suzuki order/steps or exactness, resource budget, and approximation/error
  budget.
- Unsupported binder, dynamic dimension, missing profile, or exceeded budget
  rejects before allocation with no partial circuit.
- The written finite product remains a product; it cannot be collapsed into a
  single exponential unless the source/target contract explicitly permits the
  equivalence and records the error budget.

Required pre-implementation evidence: provider-neutral capability DTO,
canonical IR example for a bound Pauli sum, rejection matrix, and resource /
approximation provenance contract. Provider SDK integration remains out of
scope.

The typed stage contract is `ExplicitEvolution AST → EvolutionIR → TargetPlan
→ Circuit | TargetRejection`. `EvolutionIR` preserves source span, transform,
state shape, binder witness, and realization request. `TargetPlan` adds target
facts without rewriting source meaning. Missing provenance fails as
`EVOLUTION_PROVENANCE_LOST`; an over-budget resource estimate returns a
rejected envelope before any allocation.

## Workstream C — S02 and corpus migration

S02 is the first numerical migration fixture, not a bulk rewrite template.
The source must expose:

```text
I → I - i H_obj dt / hbar
  → Limit N → Infinity { (I - i H_obj dur / (N hbar)) ^ N }
  → exp(-i H_obj dur / hbar)
  → U_t * psi_sel
  → psi_final
```

Migration gates:

- preserve `H_obj`, `dur`, `psi_sel`, real `hbar`, host arrays, and terminal
  `Measure psi_final` semantics;
- compare fixed-seed distributions and benchmark metrics with the baseline;
- record any intentional numerical tolerance and approximation policy;
- migrate one representative family at a time and do not bulk-rewrite
  Hamiltonian, grid, Lindblad, or discrete `times N` examples;
- require a separate Phase 3 implementation approval after the migration Red
  tests and independent review.

## Cross-workstream acceptance matrix

| Boundary | Design evidence | Implementation gate |
|---|---|---|
| Source meaning | Blackboard/source correspondence and provenance fields | Red test approval |
| Target realization | Exact/approximate/reject decision is explicit | Architecture + target approval |
| Failure safety | No partial State/circuit on rejection or exhaustion | Runtime/QPU Red and Green |
| Numeric equivalence | Fixed-seed baseline and tolerance report | S02 implementation approval |
| Scope isolation | `times`, legacy `for`, bounded explicit, and `Limit` remain distinct | Full regression |

## Independent-review focus

Reviewers must specifically inspect: hidden rewrite risk; provenance loss at
AST→IR→target boundaries; whether adapter code contains physics policy; finite
realization and approximation claims; State linearity and terminal measurement;
S02 source/readout correspondence; and whether a residual is being silently
promoted to implementation scope.

## Next gate

This document authorizes design refinement and independent pre-implementation
review only. It does not authorize Red test creation, production code, S02
migration, QPU implementation, or Phase 3 closeout. Each workstream requires
its own reviewed acceptance specification and explicit phase approval.
