# LISS-0439: example equation fidelity and compile readiness

## Metadata

- Status: **final-review-ready / independently reviewed READY (2026-08-17)**
- Type: Feature / Architecture bounded example slice
- WorkPlan: [WP-0101](../work-plans/WP-0101-example-equation-fidelity.md)
- Related: [LISS-0437](LISS-0437-explicit-evolution-surface.md)
- Specification: [explicit evolution surface](../specs/staqex-explicit-evolution-surface.md)
- ADR: [ADR 0210](../architecture/adr/0210-formal-limit-finite-realization-policy.md)

## Objective

Make official examples recoverable as blackboard mathematics: named operators,
formula structure, parameters, approximation claims, and semantic boundaries
must be visible in source and the examples must remain compile-checkable.

## Included

- S01 fuel `until` grammar correction.
- A11 relative import correction.
- B08 documentation/source alignment.
- S01 day2 Suzuki/exponential claim alignment.
- Explicit naming/documentation for selected hidden meanings in A02, A04,
  A05, A07, and S01 route.
- Focused and full example verification.

## Excluded

- S02 numerical migration or baseline changes.
- live QPU submission, provider SDK, credentials, and network behavior.
- Compiler or target-lowering redesign.
- Unrelated example restyling or deletion.

## Acceptance

- The changed source compiles under the current grammar.
- The source or its comments accurately identifies exact versus approximate
  evolution and does not claim unused Suzuki parameters.
- No implicit `Limit` realization is added.
- Any new finite QPU example uses all explicit `Realize` policy fields.
- Existing user changes remain intact.

## Completion evidence

- Runnable example entrypoints: `31/31` check pass.
- Spec verification: `161/161` pass.
- Focused evolution/Realize regression: pass.
- Final independent review: `READY / COMPLETE`.
- Non-blocking residual: S01 fuel may reach `EVOLVE_UNTIL_MAX_STEPS_ERROR`

## Completion gate

- Final review approval: user-approved 2026-08-17
- Completion PR: not yet opened
- Until a PR number is recorded, this Issue remains `final-review-ready`.
  at the selected seed/parameters; its source grammar and compile boundary are
  valid, and the example explicitly documents the bounded dynamic lane.
- Review record: [2026-08-17 LISS-0439 review](../collaboration/reviews/2026-08-17-liss-0439-example-equation-fidelity-review.md)
