# Staqex S02 Example Blackboard/Realization Boundary Specification

| Field | Value |
|---|---|
| Status | **proposed** |
| Issue | [LISS-0452](../issues/LISS-0452-s02-example-boundary-alignment.md) |
| WorkPlan | [WP-0115](../work-plans/WP-0115-s02-example-boundary-alignment.md) |
| Authority | WP-0105; LISS-0449–0451 proposed contracts |

## [DESIGN CHECK]

- Scope: audit representative S02 examples and their four semantic stages.
- Lenses: researcher readability, blackboard/source conservation, explicit
  realization, capability honesty, and documentation consistency.
- Exclusions: broad numerical migration, providers, live QPU, solver, syntax.

## Normative direction

Examples distinguish: blackboard equation, ideal source/meaning, explicit
finite realization, and QPU/QASM projection or rejection.

## Acceptance

- Researchers can recover equation structure and assumptions from source.
- `Realize(method, order, steps, error_budget)` is explicit where required.
- Unsupported target behavior does not delete the ideal formula.
- Each example is classified with evidence as supported, partial, unsupported,
  or intentional scope.

## Phase 1 Red audit cases

- `main_selection.sqx` has a recoverable blackboard equation;
- ideal source and finite `Realize` parameters are distinguishable;
- QPU scope/rejection is documented without deleting the ideal formula;
- README, source, and verification inventory agree on the same stage boundary.
