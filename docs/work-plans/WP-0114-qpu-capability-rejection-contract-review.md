# WP-0114: QPU Capability Rejection Contract Review

| Field | Value |
|---|---|
| Status | **proposed** |
| Phase | **phase-0-design** |
| Size | M |
| Issue | [LISS-0451](../issues/LISS-0451-qpu-capability-rejection-contract.md) |
| Specification | [QPU Capability Rejection Contract](../specs/staqex-qpu-capability-rejection-contract.md) |
| Related authority | ADR 0085, ADR 0210, ADR 0211 |
| Depends on | WP-0112 and WP-0113 design directions |
| Branch | `codex/liss-0438-residual-reconciliation` (design intake only) |

## Objective

Define one honest contract for expressions that are meaningful in the ideal
language but cannot be represented by a finite QPU circuit.

## Boundaries to review

- formal `Limit` without `Realize`;
- non-unitary `product` and mathematical transforms;
- `evolve ... until` and dynamic/measurement-dependent evolution;
- continuous operators and unsupported discretization;
- qudit and unsupported local dimensions;
- resource budget overflow;
- unresolved parameters, angles, or target capabilities.

## In scope

- Classification: ideal-supported, simulator-supported, finite-realizable,
  QPU-capability-rejected, or intentionally out of scope.
- Diagnostic codes and provenance requirements.
- Atomic rejection envelope: no QASM, gates, instructions, allocation, or
  partial program after rejection.
- Pre-allocation resource checks and target-boundary observability.

## Out of scope

- Adding target capabilities.
- Provider SDK, live QPU, credentials, and network.
- Numerical S02 migration and solver work.

## Acceptance conditions for design

- Rejection applies to the finite target transition, not to the ideal meaning.
- Every rejection names the unsupported realization/capability and source
  provenance.
- No implicit AST, unitary, Suzuki, or discretization fallback remains.
- Existing resource preflight guarantees remain intact.

## Verification and gates

- Rejection matrix and artifact-envelope tests designed before implementation.
- Independent review of capability honesty and safety boundaries.
- No phase or implementation authorization is implied by this WP.
