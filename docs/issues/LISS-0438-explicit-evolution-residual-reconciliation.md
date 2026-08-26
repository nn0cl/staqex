# LISS-0438: explicit evolution residual reconciliation

## Metadata

- Local issue ID: LISS-0438
- Status/phase: **complete**
- Completion evidence: PR #554, CI run 32115995867 passed Repository sanity,
  Kernel root suites, and Spec verification.
- Type: Architecture Path follow-up
- Parent WorkPlan: [WP-0100](../work-plans/WP-0100-explicit-evolution-surface.md)
- Related Issue: [LISS-0437](LISS-0437-explicit-evolution-surface.md)
- Specification: [explicit evolution surface](../specs/staqex-explicit-evolution-surface.md)
- ADR: [ADR 0210](../architecture/adr/0210-formal-limit-finite-realization-policy.md)
- Acceptance Spec: [residual reconciliation](../specs/staqex-explicit-evolution-residual-reconciliation.md)
- WorkPlan: [WP-0104](../work-plans/WP-0104-explicit-evolution-residual-reconciliation.md)
- Design trace: [2026-08-18 intake](../collaboration/traces/2026-08-18-liss-0438-design-intake.md)
- Design review: [2026-08-18 review 02](../collaboration/reviews/2026-08-18-liss-0438-design-review-02.md)
- Phase 2 review: [2026-08-18 Phase 2 Green review](../collaboration/reviews/2026-08-18-liss-0438-phase2-green-review.md)
- Phase 3 trace: [2026-08-18 Phase 3 refactor](../collaboration/traces/2026-08-18-liss-0438-phase3-refactor.md)

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

- No implementation beyond the bounded Phase 2 Green slice recorded in the
  approval and trace is authorized by this Issue; Phase 3 and scope expansion
  require a separate approval.
- No live QPU submission.
- No provider SDK, credentials, network, or adapter work.
- No change to ADR 0210's source-visible `Realize` boundary.
- No automatic insertion of `Realize`, fixed `N`, order, duration, or error
  budget.

## Required gates before work

1. An acceptance specification and design note for the selected residual
   slice.
2. Independent review of that specification.
3. Explicit user/Adjudicator Phase 2 implementation approval after the Red
   review (recorded); independent Green re-review is complete.
4. Fixed-seed, benchmark, provenance, and scope-boundary verification plan.

The bounded LISS-0438 slice is complete. S02 numerical migration, live QPU,
provider SDK, and broader corpus migration remain separate future work.
