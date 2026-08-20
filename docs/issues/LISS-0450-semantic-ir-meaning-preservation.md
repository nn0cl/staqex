# LISS-0450: Scientific Semantic IR Meaning Preservation

| Field | Value |
|---|---|
| Status | **final-review-ready** |
| Phase | **phase-3-refactor** |
| Type / priority | architecture / P0 |
| Initial size | XL |
| Current size | XL |
| WorkPlan | [WP-0113](../work-plans/WP-0113-semantic-ir-meaning-preservation.md) |
| Specification | [Scientific Semantic IR Meaning Preservation](../specs/staqex-semantic-ir-meaning-preservation.md) |
| Dependencies | [LISS-0449](LISS-0449-ideal-expression-realization-boundary.md) design direction |
| Related authority | ADR 0211, [ADR 0212](../architecture/adr/0212-ideal-meaning-and-finite-realization-boundary.md); adjudicator language vision |
| Implementation approval | granted for Phase 2 Green; Phase 3 not granted |

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

The broad family inventory is not a blanket implementation approval. For this
phase, only the accepted Coin/when meaning preservation, ExactExponential
metadata, ideal fingerprint, and canonical consumer boundary are included.
The behavior-preserving Phase 3 Refactor is complete for this bounded slice;
additional meaning families require separate approval. The result is ready
for the completion PR and final Adjudicator review.

Approval evidence: `docs/collaboration/traces/2026-08-20-liss-0449-0451-phase2-green.md`.
Phase 3 evidence: `docs/collaboration/traces/2026-08-21-liss-0449-0451-phase3-refactor.md`.
