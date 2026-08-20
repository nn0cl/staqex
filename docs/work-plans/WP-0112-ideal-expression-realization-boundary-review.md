# WP-0112: Ideal Expression and Finite Realization Boundary Review

| Field | Value |
|---|---|
| Status | **proposed** |
| Phase | **phase-1-red** |
| Size | XL |
| Issue | [LISS-0449](../issues/LISS-0449-ideal-expression-realization-boundary.md) |
| Specification | [Ideal Expression and Finite Realization Boundary](../specs/staqex-ideal-expression-realization-boundary.md) |
| Related authority | ADR 0209, ADR 0210, ADR 0211 |
| Depends on | none |
| Branch | `codex/liss-0438-residual-reconciliation` (design intake only) |

## Objective

Ensure that ideal blackboard expressions remain writable and source-owned even
when a QPU target cannot execute them. Separate the language/semantic boundary
from the finite realization boundary.

## Questions to resolve

- Can formal `Limit` and exact exponential expressions be represented in the
  ideal semantic IR without being accepted by QPU lowering?
- Is `Realize` an explicit target transition rather than a prerequisite for
  expressing the ideal equation?
- Which exact expressions are CPU/simulator-executable, symbolic-only, or
  QPU-capability-rejected?
- How are exactness, approximation method, order, steps, and error budget
  preserved from source to target diagnostics?

## In scope

- Issue/Spec/ADR design for ideal expression versus finite realization.
- `Limit`, `exp(-iHt/ℏ)`, `Evolve`, `Realize`, Suzuki, and target diagnostics.
- Source-to-IR provenance and explicit transition records.
- Blackboard/source examples and acceptance matrix.

## Out of scope

- Provider SDK, live QPU submission, credentials, and network.
- S02 numerical migration and solver implementation.
- Syntax implementation, parser changes, and production code.

## Acceptance conditions for design

- Ideal expressions can be represented without implicit finiteization.
- QPU lowering requires an explicit finite realization policy where needed.
- Direct target rejection does not erase the ideal semantic representation.
- Any architecture change is recorded in an accepted ADR before implementation.

## Verification and gates

- Independent design review using physicist-first, canonical-authority, and
  realization-boundary lenses.
- Phase 1 Red approval only after the acceptance Spec is accepted.
- No implementation approval is implied by this WP.

## Red preparation gate

Before Phase 1 Red, the acceptance suite must cover ideal `Limit`, exact
exponential structure, explicit `Realize` provenance, and atomic target
rejection as listed in the Specification.

## Fixed Phase 1 Red inventory

- `tests/test_liss_0449_ideal_realization_boundary_red.py`;
- fixtures `tests/fixtures/ideal_realization/ideal_limit.sqx` and
  `tests/fixtures/ideal_realization/explicit_realize.sqx`;
- cases `limit_preserved_before_target_rejection`,
  `exact_exponential_preserved_without_gates`, and
  `realize_provenance_is_source_owned`.

Given/When/Then cases:

- Given an ideal `Limit`, when the QPU lane is invoked without `Realize`, then
  `EVOLUTION_REALIZATION_REQUIRED` is returned and no target artifact exists.
- Given exact exponential source, when no finite target policy exists, then
  structure remains in semantic IR and no gates are created.
