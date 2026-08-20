# LISS-0450: Scientific Semantic IR Meaning Preservation

| Field | Value |
|---|---|
| Status | **open** |
| Phase | **phase-0-design** |
| Type / priority | architecture / P0 |
| Initial size | XL |
| Current size | XL |
| WorkPlan | [WP-0113](../work-plans/WP-0113-semantic-ir-meaning-preservation.md) |
| Specification | [Scientific Semantic IR Meaning Preservation](../specs/staqex-semantic-ir-meaning-preservation.md) |
| Dependencies | [LISS-0449](LISS-0449-ideal-expression-realization-boundary.md) design direction |
| Related authority | ADR 0211, [ADR 0212](../architecture/adr/0212-ideal-meaning-and-finite-realization-boundary.md); adjudicator language vision |
| Implementation approval | not granted |

## Objective

Make the Scientific Semantic IR preserve blackboard meaning before any target
projection, including meanings that are not currently QPU-executable.

## Acceptance direction

- `Coin`, `Mix`, `when`, `interfer`, `product`, continuous/open-system
  constructs, and measurement boundaries remain semantically identifiable.
- Mixture is not silently rewritten as unitary superposition.
- Source structure, parameters, dimensions, exactness, state kind, branch
  relationships, and provenance remain inspectable.
- All target consumers use the canonical IR and never re-read AST meaning as a
  hidden fallback.

## Exclusions

Gate synthesis, provider SDK, live QPU, S02 migration, solver, and syntax
redesign are excluded.

## Approval boundary

Because this may change ADR 0211's canonical data model, architecture review
and a reviewed acceptance Spec are required before Phase 1 Red.
