# LISS-0438: explicit evolution residual reconciliation

## Metadata

- Local issue ID: LISS-0438
- Status: **Planned / not approved for implementation**
- Type: Architecture Path follow-up
- Parent WorkPlan: [WP-0100](../work-plans/WP-0100-explicit-evolution-surface.md)
- Related Issue: [LISS-0437](LISS-0437-explicit-evolution-surface.md)
- Specification: [explicit evolution surface](../specs/staqex-explicit-evolution-surface.md)
- ADR: [ADR 0210](../architecture/adr/0210-formal-limit-finite-realization-policy.md)

## Purpose

Track work that remains after the bounded finite `Realize`/Suzuki target slice
was completed and independently reviewed under LISS-0437. This Issue exists
to prevent residual migration and corpus work from being mistaken for an
approval to change the compiler or deploy to a QPU.

## Candidate future scope

- Reconcile the S02 `main_selection.sqx` source with the accepted explicit
  `Realize` surface.
- Perform the required fixed-seed and benchmark comparison against the
  pre-migration baseline.
- Assess broader example/corpus migration only after a separate acceptance
  specification and phase approval.
- Update the roadmap and completion evidence after those activities.

## Explicit exclusions

- No implementation is authorized by this Issue.
- No live QPU submission.
- No provider SDK, credentials, network, or adapter work.
- No change to ADR 0210's source-visible `Realize` boundary.
- No automatic insertion of `Realize`, fixed `N`, order, duration, or error
  budget.

## Required gates before work

1. An acceptance specification and design note for the selected residual
   slice.
2. Independent review of that specification.
3. Explicit user/Adjudicator phase and implementation approval.
4. Fixed-seed, benchmark, provenance, and scope-boundary verification plan.

Until those gates are recorded, LISS-0438 remains a roadmap item only.
