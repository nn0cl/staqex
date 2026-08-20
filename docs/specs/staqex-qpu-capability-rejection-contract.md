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

## Rejection code/reason/provenance matrix

| Case | Code | Required reason | Required provenance |
|---|---|---|---|
| ideal `Limit` without finite realization | `E_QPU_CANONICAL_PROJECTION_UNAVAILABLE` | `missing_finite_realization` | `source_node_id`, source span |
| exact exponential without target realization | `E_QPU_CANONICAL_FINITE_EVOLUTION_UNSUPPORTED` | `finite_projection_unavailable` | evolution source node and operator provenance |
| `Coin/Mix` without finite projection | `E_QPU_CANONICAL_PROJECTION_UNAVAILABLE` | `mixture_projection_unavailable` | mixture node, branch children, source span |
| non-unitary `product` | `E_QPU_UNSUPPORTED_CAPABILITY` | `non_unitary_target` | product node and operand provenance |
| `evolve ... until` | `E_QPU_UNSUPPORTED_CAPABILITY` | `until_requires_dynamic_target` | evolve node and predicate provenance |
| resource budget overflow | `E_QPU_RESOURCE_UNSUPPORTED` | `resource_budget_exceeded_before_allocation` | estimate, profile, source nodes |
| unresolved rotation/parameter | `QASM_ROTATION_ANGLE_UNRESOLVED` or existing target-specific code | `parameter_unresolved` | operation node and parameter provenance |

These codes/reasons are the Phase 1 acceptance contract. A new code requires a
Spec/ADR update before implementation.

## Phase 1 Red cases

- ideal `Limit` without finite realization rejects only at QPU projection;
- non-unitary `product` retains ideal meaning and rejects at QPU capability;
- unsupported `until` rejects without partial target artifacts;
- resource overflow is rejected before gate or qubit allocation;
- every rejection records deterministic code, source provenance, and reason.

### Given/When/Then fixtures

- `tests/fixtures/capability_rejection/ideal_limit.sqx`: Given an ideal
  `Limit`, when QPU projection runs without `Realize`, the semantic result
  remains and the target artifact envelope is empty.
- `tests/fixtures/capability_rejection/non_unitary_product.sqx`: Given a
  non-unitary product, QPU projection returns the matrix code/reason before
  allocation.
- `tests/fixtures/capability_rejection/resource_overflow.sqx`: Given an input
  exceeding the target budget, projection allocates no gate or qubit.
