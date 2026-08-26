# WP-0113: Classical/Quantum Meaning Preservation in Scientific Semantic IR

| Field | Value |
|---|---|
| Status | **bounded Coin/when slice complete; follow-up slices open** |
| Phase | **phase-3-refactor complete for the approved bounded slice** |
| Size | XL |
| Issue | [LISS-0450](../issues/LISS-0450-semantic-ir-meaning-preservation.md) |
| Specification | [Scientific Semantic IR Meaning Preservation](../specs/staqex-semantic-ir-meaning-preservation.md) |
| Related authority | ADR 0211 and the physicist-first language vision |
| Depends on | WP-0112 design direction |
| Branch | Merged through PRs #557, #558, and #559 |

## Objective

Make the Scientific Semantic IR preserve the blackboard meaning of classical,
mathematical, quantum, and mixed expressions before any QPU projection.

## Candidate semantic families

- `Coin`, `Mix`, and `when` mixtures;
- `interfer`, phase, and branch relationships;
- `product`, tensor products, and non-unitary mathematical operators;
- continuous operators and discretization markers;
- `DensityState` and Lindblad/open-system expressions;
- measurement status and terminal-collapse boundaries.

## In scope

- Meaning categories and canonical IR data model requirements.
- Preservation of source structure, operators, parameters, exactness,
  dimensions, state kind, branch/mix semantics, and provenance.
- Distinction between ideal semantic execution and QPU projection.
- Capability-independent inspection and diagnostics.

## Execution decomposition

1. Define and review the common semantic-role/provenance contract only.
2. Complete the `Coin`/`Mix`/`when` slice through LISS-0448.
3. Design separate follow-up slices for product/tensor, continuous/open-system,
   and measurement boundaries; do not implement them implicitly in this WP.
4. Reconcile each slice with the common contract through independent review.

The WP is XL because the inventory is broad, but no single phase may claim all
families are implemented.

## Fixed Phase 1 Red inventory

- `tests/test_liss_0450_semantic_ir_meaning_red.py`;
- fixture `tests/fixtures/semantic_meaning/mixture_and_product.sqx`;
- common-field cases for role, state kind, child identity, dimensions,
  exactness, intent, and provenance;
- separate family markers so `Coin/Mix` completion cannot imply product,
  continuous, open-system, or measurement completion.

Given/When/Then cases:

- Given `mixture_and_product.sqx`, when semantic IR is built, then mixture and
  product roles remain distinct structural nodes.
- Given the same source, when a target projection is unavailable, then the
  semantic result retains child identity, role, and provenance.

## Out of scope

- QPU gate synthesis itself.
- Provider SDK, live submission, S02 migration, solver, and syntax redesign.
- Choosing a particular numeric approximation without a separate decision.

## Acceptance conditions for design

- `Coin/Mix` are not forced into a gate interpretation at the semantic layer.
- A source expression remains inspectable even when QPU projection is absent.
- Semantic IR does not silently collapse classical mixture into unitary
  superposition.
- Every target projection consumes the canonical IR and never re-reads AST
  meaning as a hidden fallback.

## Verification and gates

- Representative blackboard/source pairs for each semantic family.
- Independent review for meaning conservation and physicist readability.
- Phase 1 Red and implementation require a reviewed acceptance Spec.

## Phase 2/3 evidence

- Phase 2 Green implementation and regression: trace
  `docs/collaboration/traces/2026-08-20-liss-0449-0451-phase2-green.md`.
- Phase 3 Refactor, verification, and independent READY review: trace
  `docs/collaboration/traces/2026-08-21-liss-0449-0451-phase3-refactor.md`.
- Completion state: the approved bounded Coin/when/ExactExponential and
  canonical-consumer slice is merged through PRs #557–#559. Final CI recovery
  run #1181 passed all three checks.
- Follow-up product/tensor, continuous/open-system, and measurement slices are
  not completed by this work plan and require separate design/approval.
