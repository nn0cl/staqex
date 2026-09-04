# AI work trace: LISS-0491 `run_unit()` retirement design

- Date: 2026-08-31
- Scope: architecture design for retiring the legacy evaluator entry after
  the canonical semantic execution boundary established by LISS-0490.
- Approval: Adjudicator approved the named design scope; Architecture approval
  and implementation permission remain pending.
- Evidence inspected: evaluator, host/run/CLI entrypoints, LISS-0489,
  LISS-0490, WP-0107, consumer-migration Spec, ADR 0211, readiness and
  collaboration policies, and repository call-site inventory.
- Decision: staged delivery-first migration, observable compatibility lane,
  production-caller inventory guard, and explicit zero-caller removal gate.
  `run_unit()` is not removed in this design task.
- Omitted: provider/QPU/AWS, Rust, solver, release policy, and broad rewrite.
- Applicable lessons: preserve authority and caller evidence separately;
  classify compatibility as non-authoritative; synchronize status on closure.
- Phase 1 result: the fixed Red suite was created and ran with 5 failures and
  no collection errors. Failures identify delivery bypasses, missing
  deprecation metadata, remaining direct production callers, and missing
  result source provenance.
- Review result: same-context review on 2026-09-01 accepted the Red contract;
  see `docs/collaboration/reviews/2026-09-01-liss-0491-phase1-review.md`.
- Phase 2 result: delivery callers migrated, deprecation/source metadata added,
  and the production inventory guard passes; 27 targeted/regression tests,
  `py_compile`, and `git diff --check` passed.
- Phase 2 review: same-context review accepted the bounded implementation;
  see `docs/collaboration/reviews/2026-09-01-liss-0491-phase2-review.md`.
- Phase 3 result: extracted authority-neutral `_execute_unit()` so canonical
  execution no longer traverses public `run_unit()`; 27 tests, `py_compile`,
  and `git diff --check` passed.
- Phase 3 review: same-context review accepted the bounded refactor; see
  `docs/collaboration/reviews/2026-09-01-liss-0491-phase3-review.md`.
- Process review: no operating-contract deviation or operational problem found.
- Next safe action: keep `run_unit()` as compatibility API until a separate
  removal-window decision and broader regression evidence are approved.
