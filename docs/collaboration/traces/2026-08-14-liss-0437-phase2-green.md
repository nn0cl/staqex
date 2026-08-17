# LISS-0437 Phase 2 Green implementation trace

## Approval and scope

- Date: 2026-08-14
- Issue: LISS-0437
- Phase: Phase 2 Green
- Approval: user approved the reviewed Red tests and Phase 2 Green
  implementation
- Scope: bounded explicit evolution minimum slice only
- Excluded: QPU execution, formal `Limit` realization, broad corpus migration,
  and Phase 3 closeout

## Implemented contract

The accepted source form is:

```staqex
State result = Evolve() {
    U_dt * fuel
    until converged(fuel)
    max 64
}.run()
```

The simulator reapplies the explicit `Operator * State` transform, then
evaluates the pure post-transform convergence predicate. `converged` uses the
full logical-State absolute L2 difference with Float64 tolerance `1e-9`.
`max` is a required positive integer literal. Exhaustion raises
`EVOLVE_UNTIL_MAX_STEPS_ERROR` without publishing a partial State.

The bounded provenance records `source_transform`, `predicate`, `metric`,
`numeric_type`, `tolerance`, `iteration_count`, `max_steps`, `stop_reason`,
and `realization`. QPU lowering rejects predicate-dependent bounded evolution
before circuit allocation and does not substitute a single transform or a
fixed circuit.

## Changed implementation areas

- Parser and AST bounded-body shape and validation handoff.
- Typechecker positive-literal bound and predicate contract.
- Simulator loop, full-State L2 convergence, exhaustion diagnostics, and
  provenance.
- Host metadata propagation and local-simulator continuation past QPU-only
  capability diagnostics.
- QPU lowering fail-closed rejection before allocation.
- Reviewed Red test suite for syntax, bounds, runtime, exhaustion, linearity,
  QPU safety, and `times`/`for` separation.

## Verification evidence

- `python3 tests/test_liss_0437_explicit_evolution_surface_red.py` — PASS
- `python3 tests/test_evolve_until_runtime_red.py` — PASS
- `python3 tests/test_qpu_ir_lowering_red.py` — PASS
- `python3 tests/spec_verification/run_all.py` — PASS, 161/161
- `python3 -m py_compile ...` for touched Python modules — PASS
- `git diff --check` — PASS
- `pytest` was not used because the environment has no pytest module.

## Remaining gate

The implementation is complete for the approved Phase 2 bounded minimum
slice. Independent post-implementation review is required before declaring
the broader work plan complete or starting excluded target/migration work.
