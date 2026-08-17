# Staqex classical, mathematical, quantum, and realization boundaries

| Field | Value |
|---|---|
| Status | **Accepted scope — final-review-ready** |
| Issue | [LISS-0441](../issues/LISS-0441-classical-quantum-realization-boundaries.md) |
| WorkPlan | [WP-0103](../work-plans/WP-0103-classical-quantum-realization-boundaries.md) |
| Authority | Adjudicator language vision, explicit evolution surface, QPU honesty, and finite Realize policy; Phase 2 implementation and Phase 3 review approved 2026-08-17 |

## Semantic roles

| Role | Examples | Meaning |
|---|---|---|
| Classical | `Int`, `Float`, `Parameter`, `shots` | Values and control data |
| Mathematical | `Sigma`, `Pi`, indexed equations | Blackboard structure, not execution loops |
| Quantum | `State<T>`, `Operator`, `Evolve` | Physical state and transformation |
| Realization | `Realize(source, method, order, steps, error_budget)` | Explicit finite target plan |
| Host | existing Host `Job`/`JobResult` contracts | Experiment and job orchestration |

## Boundary rules

1. Classical values and physical quantities follow the existing Type-First,
   literal-lift, and coefficient-lift contracts.
2. State/classical interaction follows the existing Type-First and lift
   contracts; this specification introduces no new conversion rule.
3. Observation/measurement is the explicit quantum-to-classical boundary.
4. Mathematical binders are not rewritten into Host loops in source meaning.
5. `evolve times N` is quantum-transform repetition; Host sweeps remain Host.
6. Existing `Realize` remains governed by ADR 0210; its row below is a
   contract reference, not a Phase 1 fixture. Diagnostic catalog
   synchronization and a new result schema are deferred.
7. Exact and approximate realizations remain distinguishable.
8. Unsupported bridges reject explicitly without partial or silent fallback.

## Conceptual source example (not a Phase 1 fixture)

```staqex
Parameter J : Energy
Operator H = Sigma (i In sites) { J[i] * Z[i] * Z[i + 1] }
Operator U_exact = exp(-i * H * duration / hbar)

State psi_final = Evolve() {
  U_exact * psi_initial
}.run()

measure psi_final
```

Finite realization and Host submission remain separate existing contracts;
this specification does not introduce `Host {}`, `Sweep`, or `FiniteEvolution`
syntax.

## Coverage declaration

The first implementation target is minimum expression capability, not a full
scientific solver library. Numbers, units, parameters, finite linear algebra,
existing `Sigma`/`Pi` binders, quantum operators, explicit evolution, and the
already shipped realization policy are in scope. A new Host block, a new
`FiniteEvolution` result type, general ODE/PDE solving, complete
electromagnetism, thermodynamics, continuous Monte Carlo, provider submission,
and S02 numerical migration remain partial, unsupported, or intentionally out
of scope until a separate approved Issue defines them.
