# ADR 0210: explicit finite realization policy for formal Limit

## Status

**Accepted** (2026-08-15) — Architecture approval received from the user.
This ADR accepts the finite-realization boundary. The bounded finite
`Realize`/Suzuki implementation slice is complete and independently reviewed;
this ADR still grants no permission for S02 numerical migration, provider SDK
integration, or live QPU submission by itself.

Related:

- [LISS-0437](../../issues/LISS-0437-explicit-evolution-surface.md)
- [WP-0100](../../work-plans/WP-0100-explicit-evolution-surface.md)
- [ADR 0209](0209-explicit-blackboard-evolution-surface.md)
- [Explicit evolution specification](../../specs/staqex-explicit-evolution-surface.md)

## Context

Staqex permits the physicist to write the formal blackboard construction:

```staqex
Operator U_t = Limit N -> Infinity {
    (I - i * H * dur / (N * hbar)) ^ N
}
```

The source must remain visible and must not be silently rewritten to `exp` or
to a compiler-selected fixed `N`. A target, however, may require a finite
realization before it can execute the written meaning.

## Decision

Keep the formal `Limit` as the semantic source expression. Permit execution
only when the selected target profile supplies an explicit finite realization
policy containing all of:

```text
method       = "suzuki" | "product"
order        = positive integer, when method is suzuki
steps        = positive integer, or an explicit bounded step policy
error_budget = explicit tolerance, when approximation is used
```

The target plan must publish the source provenance, finite realization method,
parameters, estimated resources, and approximation/error evidence. It must
reject before allocation when any required policy field is absent, invalid,
or exceeds the target budget.

The source may make the conversion explicit through a realization expression:

```staqex
Operator U_formal = Limit N -> Infinity {
    (I - i * H * dur / (N * hbar)) ^ N
}
Operator U_qpu = Realize(
    U_formal,
    method = "suzuki",
    order = 2,
    steps = 8,
    error_budget = 1e-6
)
```

`U_formal` and `U_qpu` are distinct typed values. The conversion is visible
in source, and its result must retain a relation to the source transform,
method, parameters, and error evidence. A target profile may supply default
capability facts, but it may not hide this source-level conversion or infer
`N`, order, duration, Hamiltonian, or error budget.

## Consequences

Positive:

- Blackboard meaning remains source-visible.
- Exact symbolic/source-only handling and finite target execution are clearly
  separated.
- Resource and approximation choices are reviewable and reproducible.

Costs and open boundaries:

- A target profile schema and error/resource estimator are required.
- The relation between `steps` and `error_budget` must be validated for each
  operator family.
- Exact simulator realization, Suzuki realization, and QPU gate synthesis
  may require separate capability ports.

## Rejected alternatives

1. **Compiler-selected fixed `N`** — rejected because it hides a physical and
   numerical choice from the source author.
2. **Automatic rewrite to `exp`** — rejected because it erases the written
   infinitesimal construction and violates source/blackboard correspondence.
3. **Adapter-local finiteization** — rejected because it moves physics policy
   into an adapter and prevents provenance/resource review.

4. **Implicit target-profile realization** — rejected because it makes the
   source appear to contain a different operator than the one written on the
   blackboard.

## Required acceptance tests after ADR approval

- Missing policy remains `EVOLUTION_REALIZATION_REQUIRED` with provenance.
- Invalid or incomplete policy is rejected before allocation.
- Explicit `method`, order/steps, and error budget are retained in the target
  plan and provenance.
- No `exp` rewrite or compiler-selected `N` occurs.
- Exact and approximate realization kinds are distinguishable.
- Budget overflow returns no gates, qubits, or partial program.

## Finite realization acceptance boundary

For the first implementation slice:

- `product` executes the written finite product for the declared positive
  `limit_steps`; it does not replace the product with a hidden exponential.
- `suzuki` executes an explicit finite approximation using the declared
  positive `limit_order` and `limit_steps`, and retains the declared positive
  `limit_error_budget` as evidence.
- Both realizations publish `realization_kind = "approximate"`, the method,
  parameters, source transform, and resource estimate.
- Successful `Realize` produces a provider-neutral plan; provider submission
  remains outside this ADR.
- A bare formal `Limit` passed directly to a target remains rejected. The
  source must contain the explicit conversion boundary.
- The bounded QPU slice rejects the non-unitary `product` method explicitly;
  it does not claim that the written product is a unitary gate sequence.
- Invalid policy and resource overflow remain fail-closed with no allocation;
  budget overflow leaves no gates, qubits, partial program, or provenance.

Acceptance artifact:
`tests/test_liss_0437_limit_realization_red.py`.

## Approval record

Architecture approval and the bounded finite-realization implementation review
are complete for this boundary. The independent review record is
[`2026-08-17-liss-0437-limit-realization-review-02.md`](../collaboration/reviews/2026-08-17-liss-0437-limit-realization-review-02.md),
terminal `COMPLETE` / `READY`. This ADR does not approve QPU deployment,
provider SDK integration, or S02 numerical migration.
