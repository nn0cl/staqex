# Staqex Scientific Semantic IR Meaning Preservation Specification

| Field | Value |
|---|---|
| Status | **proposed** |
| Issue | [LISS-0450](../issues/LISS-0450-semantic-ir-meaning-preservation.md) |
| WorkPlan | [WP-0113](../work-plans/WP-0113-semantic-ir-meaning-preservation.md) |
| Authority | ADR 0211, [ADR 0212](../architecture/adr/0212-ideal-meaning-and-finite-realization-boundary.md); adjudicator language vision |

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

## Meaning-family decomposition

The XL scope is decomposed into independently reviewable slices:

1. `Coin`/`Mix`/`when` mixture and branch meaning (LISS-0448);
2. operator products, tensor structure, and non-unitary meaning;
3. continuous and open-system state/operator meaning;
4. measurement and terminal-collapse boundaries.

The common IR contract is designed first. No family slice may claim completion
for another family, and each slice requires its own Red/Green acceptance.

## Acceptance

- Source structure, state kind, branch relations, parameters, dimensions,
  exactness, and provenance are inspectable.
- Target consumers consume canonical IR only.
- Missing QPU projection does not imply missing ideal meaning.
- ADR 0211 changes require architecture approval.

## Phase 1 Red cases

- `Coin/Mix` produces a structural mixture node, not a unitary gate node;
- branch conditions and child source identities are preserved;
- non-unitary `product` remains a mathematical/operator meaning;
- absent QPU projection does not remove the ideal semantic result;
- source provenance and state/mixture role survive projection.
