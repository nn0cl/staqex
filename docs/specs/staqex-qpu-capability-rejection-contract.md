# Staqex QPU Capability Rejection Contract Specification

| Field | Value |
|---|---|
| Status | **proposed** |
| Issue | [LISS-0451](../issues/LISS-0451-qpu-capability-rejection-contract.md) |
| WorkPlan | [WP-0114](../work-plans/WP-0114-qpu-capability-rejection-contract-review.md) |
| Authority | ADR 0085, ADR 0210, ADR 0211 |

## [DESIGN CHECK]

- Scope: classify and enforce finite-target capability boundaries.
- Lenses: capability honesty, atomic rejection, pre-allocation safety,
  provenance, and ideal/target separation.
- Exclusions: new QPU capabilities, providers, live submit, S02, solver.

## Normative direction

Rejection applies to the finite target transition, not to ideal source meaning.
Cases include `Limit`, non-unitary `product`, `until`, continuous operators,
qudits, unresolved parameters, and resource budgets.

## Acceptance

- Every rejection has deterministic code and source provenance.
- No QASM, gates, instructions, allocation, or partial program remains.
- Resource overflow is detected before gate/bit allocation.
- The classification matrix distinguishes ideal, simulator, finite, QPU, and
  intentional-scope status.
