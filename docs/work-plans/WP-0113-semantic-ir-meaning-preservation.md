# WP-0113: Classical/Quantum Meaning Preservation in Scientific Semantic IR

| Field | Value |
|---|---|
| Status | **proposed** |
| Phase | **phase-0-design** |
| Size | L |
| Related Issue | New Issue required before Phase 1 Red |
| Related authority | ADR 0211 and the physicist-first language vision |
| Depends on | WP-0112 design direction |
| Branch | `codex/liss-0438-residual-reconciliation` (design intake only) |

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
