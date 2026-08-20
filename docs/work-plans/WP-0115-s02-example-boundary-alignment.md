# WP-0115: S02 Example and Blackboard/Realization Boundary Alignment

| Field | Value |
|---|---|
| Status | **proposed** |
| Phase | **phase-0-design** |
| Size | M |
| Issue | [LISS-0452](../issues/LISS-0452-s02-example-boundary-alignment.md) |
| Specification | [S02 Example Blackboard/Realization Boundary](../specs/staqex-s02-example-boundary-alignment.md) |
| Related authority | WP-0105, WP-0112, WP-0113, WP-0114 |
| Depends on | WP-0112–WP-0114 design decisions |
| Branch | `codex/liss-0438-residual-reconciliation` (design intake only) |

## Objective

Audit representative S02 examples so a researcher can recover the blackboard
equation, ideal program meaning, explicit finite realization, and QPU scope
from the source and accompanying documentation.

## Required example presentation

Each selected example must distinguish:

1. Blackboard equation and assumptions.
2. Ideal Staqex expression and semantic state.
3. Explicit finite realization, including method/order/steps/error budget.
4. QPU/QASM projection and its exact supported scope or rejection reason.

## In scope

- `main_selection.sqx` and representative S02 examples.
- Classical/mathematical/quantum/finite labels and provenance.
- Example README/source consistency.
- Compile/spec verification inventory and gap classification.

## Out of scope

- Broad S02 numerical migration unless separately approved by WP-0106.
- Provider SDK, live QPU, credentials, and network.
- New language syntax or hidden example-specific lowering.

## Acceptance conditions for design

- Source never implies that QPU execution is available when only ideal or CPU
  execution exists.
- Finite realization appears explicitly in code and documentation.
- Unsupported target behavior is explained without deleting the ideal formula.
- Every example is classified supported, partial, unsupported, or intentional
  scope with evidence.

## Verification and gates

- Read-only corpus audit first.
- Independent review focused on researcher readability and boundary honesty.
- Any source change requires its own reviewed Spec and phase approval.

## Red preparation gate

The corpus audit must first establish the equation/source/realization/QPU
four-stage mapping for `main_selection.sqx` and selected S02 examples. It must
not change source files during the audit.

## Design audit deliverable

The first deliverable is a read-only inventory and trace, not a Red test or
source change. It must map `main_selection.sqx` and selected examples to the
four stages and record README/source/verification mismatches before any Phase
1 Red request.
