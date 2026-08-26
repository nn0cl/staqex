# LISS-0447 Design Intake Trace

- Scope approval: user approved continuation for the three residual LISS-0445
  contracts; design intake only.
- Target: AlgorithmPlan canonical projection, H1 early-return authority, and
  ordinary QASM fallback retirement.
- Excluded: LISS-0446 redesign, provider/live QPU, S02, solver, syntax changes,
  and Limit/Realize semantic changes.
- Initial independent review: `NOT READY`.
- Accepted corrections: field mapping and rejection contract, H1 authority
  choice, fallback decision table, atomic artifact envelope, and fixed Red
  case IDs. The follow-up review also required explicit canonical
  `realize_source_node_id` and `finite_realization_record` ownership plus
  fixed fixture inputs; these were added without implementation.
- Production implementation: not started.
- Final design review: `NOT READY` because the fixed fixtures are Phase 1 Red
  outputs and cannot be created before that phase is approved. The remaining
  contract was fixed to one exact error code with deterministic reason values.
- Next condition: typed Phase 1 Red approval; only then create the fixed Red
  tests and fixtures.
- Phase 1 Red result after approval: **6 failed, 0 passed, no collection
  errors**; no production files were changed.
- Red evidence correction added a separate mismatched plan/projection test;
  the focused result is now **7 failed, 0 passed, no collection errors**.
- Phase 1 baseline had pre-existing dirty production changes from LISS-0444 /
  LISS-0445 / LISS-0446 work. LISS-0447 Phase 1 changed only its new test,
  fixture, and documentation paths; no existing production file was edited.
- Next condition: independent Phase 1 Red review, then separate Phase 2 Green
  implementation approval.
