# LISS-0437 bounded explicit evolution design intake

## [DESIGN CHECK]

- **Scope and expected behavior:** Make bounded repetition of an explicit
  propagator visible as `Evolve() { U_dt * state until converged(state) max
  N }.run()`. The loop must remain distinct from one
  `exp(-i * H * t / hbar)` application and from the legacy Hamiltonian
  shortcut `under H for t until ...`.
- **Specifications and files inspected:** LISS-0437 explicit-evolution
  Spec, ADR 0209, WP-0100, ADR 0079/LISS-0012 `until` contract,
  `main_fuel_search.sqx`, LISS-0344, `test_evolve_until_runtime_red.py`,
  QPU IR/lowering diagnostics, and the physicist-first language vision.
- **Component boundaries:** Parser/AST must represent the explicit transform
  and bounded repetition separately. Typechecking validates a State result,
  a pure convergence predicate, and a positive compile-time bound. Runtime
  owns bounded iteration and predicate evaluation. QPU lowering remains a
  capability boundary and must reject predicate-dependent bounded evolution
  before allocation in this slice.
- **Applicable constraints:** No hidden Hamiltonian, duration, step count, or
  approximation policy. `until` must not collapse the State. The predicate
  cannot measure, use RNG, or mutate Host state. No silent replacement with a
  single exponential or Suzuki approximation.
- **Decisions, assumptions, and unresolved ambiguities:** The accepted source
  shape is an explicit propagator plus an in-body bounded execution clause:
  `Evolve() { U_t * fuel until converged(fuel) max 64 }.run()`. `until` and
  `max` are inside the body, `.run()` follows the closing brace, and the mode
  is distinct from `times` and `for`. `max` is a required positive integer
  literal; the predicate is post-transform-only and compares the full logical
  State by absolute L2 difference using finite Float64 amplitudes and a fixed
  `1e-9` tolerance. Simulator execution is in scope;
  predicate-dependent QPU lowering is fail-closed before allocation.
  Provenance must retain the source transform, predicate, metric, numeric
  type, tolerance, iteration count, max, stop reason, and realization.
  The existing legacy source remains migration-only and cannot be treated as
  the shipped explicit outcome. Remaining work is acceptance-test design and
  fresh independent review; implementation is not authorized by this intake.
- **Included and omitted AI context:** Included only the explicit-evolution
  contract, legacy `until` runtime contract, fuel example, and target
  capability boundary. Omitted unrelated showcase sources and provider
  integrations.
- **Task routing:** Architecture review for grammar and semantic boundary;
  deterministic Red tests for parser/type/runtime/QPU behavior; implementation
  only after the acceptance contract is reviewed and approved.
- **Verification plan:** Add Red tests for explicit bounded syntax, predicate
  purity, positive max bound, repeated propagator execution, terminal measure,
  and QPU rejection without a finite profile. Then migrate
  `main_fuel_search.sqx` and run its regression, the explicit-evolution suite,
  the 161-case spec gate, and source-corpus checks.

## Proposed semantic shape

The source must denote:

```text
U_t = exp(-i * X * dur / hbar)
fuel_0 -- U_t --> fuel_1 -- U_t --> ... -- U_t --> fuel_k
```

where `k <= max` and the pure predicate is evaluated after each transform.
The target does not get to replace this with one application or infer a
finite Suzuki policy.

## Stopping condition

This design intake is **not implementation approval**. The accepted-grammar
and predicate-contract decisions are now recorded in the Spec and ADR. The
the required fresh independent review of those amendments completed with
`READY` and no P0/P1 findings. The next gate is separate Red phase approval;
tests and implementation remain unauthorized until that approval.
