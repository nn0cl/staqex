# Staqex Ideal Expression and Finite Realization Boundary Specification

| Field | Value |
|---|---|
| Status | **proposed** |
| Issue | [LISS-0449](../issues/LISS-0449-ideal-expression-realization-boundary.md) |
| WorkPlan | [WP-0112](../work-plans/WP-0112-ideal-expression-realization-boundary-review.md) |
| Authority | ADR 0209, ADR 0210, ADR 0211, [ADR 0212](../architecture/adr/0212-ideal-meaning-and-finite-realization-boundary.md) |

## [DESIGN CHECK]

- Scope: separate ideal semantic representation from finite QPU realization.
- Lenses: physicist-first source meaning, canonical authority, exactness, and
  realization boundary.
- Exclusions: provider/live QPU, S02 migration, solver, syntax, implementation.

## Normative direction

Ideal `Limit`, exact exponential, and `Evolve` forms remain representable and
source-owned. `Realize` explicitly introduces finite target policy. A target
may reject the realization without deleting the ideal semantic form.

## Meaning/realization acceptance matrix

| Form | Ideal semantic IR | Exact/symbolic inspection | Finite QPU projection |
|---|---|---|---|
| `Limit` | preserve structure and provenance | allowed where evaluator contract supports it | reject unless explicit `Realize` supplies a finite policy |
| `exp(-iHt/ℏ)` | preserve operator/exponential structure | allowed where exact/symbolic contract supports it | reject unless a meaning-preserving finite realization exists |
| `Evolve` | preserve state/operator/duration relation | allowed in the exact/symbolic lane | finite only through explicit realization policy |
| `Realize` | preserve method/order/steps/error budget | inspectable as a target transition | eligible for capability and resource checks |

No row permits hidden finiteization or AST-pattern substitution.

## Acceptance

- Source preserves equation structure and realization parameters.
- No implicit finiteization occurs.
- QPU diagnostics identify missing or unsupported realization provenance.
- Any ADR conflict is resolved before Phase 1 Red.

## Phase 1 Red cases

- ideal `Limit` is retained in the semantic result while QPU output rejects;
- exact exponential structure is retained without creating finite gates;
- explicit `Realize` provenance contains method/order/steps/error budget;
- rejection leaves QASM, gates, allocation, and partial program empty.
