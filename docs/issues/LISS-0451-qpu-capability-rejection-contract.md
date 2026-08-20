# LISS-0451: QPU Capability Rejection Contract

| Field | Value |
|---|---|
| Status | **open** |
| Phase | **phase-0-design** |
| Type / priority | architecture / P1 |
| Initial size | M |
| Current size | M |
| WorkPlan | [WP-0114](../work-plans/WP-0114-qpu-capability-rejection-contract-review.md) |
| Specification | [QPU Capability Rejection Contract](../specs/staqex-qpu-capability-rejection-contract.md) |
| Dependencies | LISS-0449 and LISS-0450 design decisions |
| Related authority | ADR 0085, ADR 0210, ADR 0211 |
| Implementation approval | not granted |

## Objective

Define capability rejection as a boundary on finite target realization, never
as deletion of ideal source meaning.

## Acceptance direction

- Classify ideal-supported, simulator-supported, finite-realizable,
  QPU-rejected, and intentional-scope cases.
- Cover `Limit`, non-unitary `product`, `until`, continuous operators, qudits,
  unresolved parameters, and resource limits.
- Preserve source provenance and use deterministic rejection codes.
- Reject atomically before QASM, gate creation, allocation, or partial program.

## Exclusions

Adding QPU capabilities, provider SDK, live submission, credentials, network,
S02 migration, and solver work are excluded.

## Approval boundary

The rejection matrix is design-only until reviewed. It must not be used to
justify removing ideal-language or semantic-IR support.
