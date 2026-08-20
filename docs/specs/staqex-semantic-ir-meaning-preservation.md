# Staqex Scientific Semantic IR Meaning Preservation Specification

| Field | Value |
|---|---|
| Status | **proposed** |
| Issue | [LISS-0450](../issues/LISS-0450-semantic-ir-meaning-preservation.md) |
| WorkPlan | [WP-0113](../work-plans/WP-0113-semantic-ir-meaning-preservation.md) |
| Authority | ADR 0211; adjudicator language vision |

## [DESIGN CHECK]

- Scope: preserve ideal classical, mathematical, quantum, and mixed meaning in
  the canonical IR before target projection.
- Lenses: physicist-first source, mixture/unitary distinction, provenance,
  projection conservation, and no hidden fallback.
- Exclusions: gate synthesis, providers, live QPU, S02, solver, syntax.

## Normative direction

`Coin`, `Mix`, `when`, `interfer`, `product`, continuous/open-system meaning,
and measurement boundaries remain identifiable in Scientific Semantic IR.
Mixture is never silently rewritten as unitary superposition.

## Acceptance

- Source structure, state kind, branch relations, parameters, dimensions,
  exactness, and provenance are inspectable.
- Target consumers consume canonical IR only.
- Missing QPU projection does not imply missing ideal meaning.
- ADR 0211 changes require architecture approval.
