# Staqex Ideal Expression and Finite Realization Boundary Specification

| Field | Value |
|---|---|
| Status | **proposed** |
| Issue | [LISS-0449](../issues/LISS-0449-ideal-expression-realization-boundary.md) |
| WorkPlan | [WP-0112](../work-plans/WP-0112-ideal-expression-realization-boundary-review.md) |
| Authority | ADR 0209, ADR 0210, ADR 0211 |

## [DESIGN CHECK]

- Scope: separate ideal semantic representation from finite QPU realization.
- Lenses: physicist-first source meaning, canonical authority, exactness, and
  realization boundary.
- Exclusions: provider/live QPU, S02 migration, solver, syntax, implementation.

## Normative direction

Ideal `Limit`, exact exponential, and `Evolve` forms remain representable and
source-owned. `Realize` explicitly introduces finite target policy. A target
may reject the realization without deleting the ideal semantic form.

## Acceptance

- Source preserves equation structure and realization parameters.
- No implicit finiteization occurs.
- QPU diagnostics identify missing or unsupported realization provenance.
- Any ADR conflict is resolved before Phase 1 Red.
