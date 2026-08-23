# LISS-0452: S02 Example Blackboard/Realization Boundary Alignment

| Field | Value |
|---|---|
| Status | **open** |
| Phase | **phase-0-design** |
| Type / priority | documentation / P1 |
| Initial size | M |
| Current size | M |
| WorkPlan | [WP-0115](../work-plans/WP-0115-s02-example-boundary-alignment.md) |
| Specification | [S02 Example Blackboard/Realization Boundary](../specs/staqex-s02-example-boundary-alignment.md) |
| Dependencies | LISS-0449, LISS-0450, and LISS-0451 |
| Related | WP-0105 and LISS-0442 |
| Implementation approval | not granted |

## Objective

Align representative S02 examples with the full path from blackboard equation
to ideal source, explicit finite realization, and QPU scope.

## Acceptance direction

- Researchers can recover the equation and assumptions from source.
- Ideal meaning is distinct from finite realization and QPU projection.
- `Realize(method, order, steps, error_budget)` is explicit wherever required.
- Unsupported target behavior is documented without deleting the ideal formula.
- Each example is classified supported, partial, unsupported, or intentional
  scope with evidence.

## Exclusions

Broad S02 numerical migration, provider SDK, live QPU, credentials, network,
solver, and syntax redesign are excluded.

## Approval boundary

Begin with a read-only corpus audit. Any source or runtime change requires a
separate reviewed Spec and phase approval.
