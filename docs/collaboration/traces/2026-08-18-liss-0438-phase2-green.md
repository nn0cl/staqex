# LISS-0438 Phase 2 Green trace

## [DESIGN CHECK]

- Scope and expected behavior: implement the approved S02 residual
  reconciliation. Keep exact `U_t` as the only local simulator propagator;
  add source-visible `U_formal` and `U_qpu = Realize(...)`; expose separate
  exact-local, finite-target, successful provenance, and rejection channels in
  the Host benchmark result.
- Specifications and files inspected: LISS-0438 residual Spec, WP-0104,
  ADR 0210, Phase 1 Red test/review, S02 source, baseline, benchmark report,
  and existing LISS-0437 finite-realization tests.
- Component boundaries, ports/adapters, and VO/DTO candidates: changes are
  limited to the S02 example and Host-side `BenchmarkResult`; target lowering
  is invoked only as a provider-neutral capability check. No provider adapter,
  QPU port, or credential path is introduced.
- Applicable constraints: exact local numerical lane must remain unchanged;
  S02 numerical migration/retuning, live QPU, provider SDK, network, and broad
  corpus migration remain excluded.
- Decisions: the current S02 finite target is honestly recorded as
  `QASM_TROTTER_UNSUPPORTED_H` because the existing QASM lowerer cannot lower
  the factory-backed Hamiltonian. The report retains diagnostic rejection
  evidence only; it does not fabricate a resource estimate or target-plan
  provenance.
- Independent review lenses: contract completeness, source fidelity,
  realization/fail-closed behavior, migration/reproducibility, evidence
  hygiene, and phase discipline.
- Verification plan: compile and run S02 exact-local, run the 20-shot benchmark,
  verify the seed-0 and metric baseline, run LISS-0437 regressions and the
  LISS-0438 suite, then independently review.

## Approved scope

- User approval: `承認` on 2026-08-18, interpreted as Phase 2 Green and
  implementation approval for LISS-0438.
- Changed implementation files: `main_selection.sqx`,
  `host/benchmark_result.py`, `host/benchmark_report.py`.
- Changed verification/process files: the LISS-0438 test, this trace, and
  review/status records.
- Excluded: compiler policy changes, S02 numerical retuning, live QPU,
  provider SDK, credentials, network, and unrelated examples.

## Verification evidence

- `compile_path(main_selection.sqx)`: `ok=True`, no diagnostics.
- Seed-0 exact-local execution: `(0, 1, 1, 1, 1, 1, 0, 0)`, matching the
  pre-migration baseline selection.
- 20-shot benchmark: `feasible`, `infeasible_shots=6`,
  `top_k_overlap=0.3333333333333333`, `reproducibility_verified=True`.
- Finite target capability check: `QASM_TROTTER_UNSUPPORTED_H`; diagnostic
  evidence present, `target_plan_provenance=None`, `partial_program=None`,
  `submitted=False`.
- LISS-0438 test: 5/5 PASS.
- LISS-0437 Realize and Limit regressions: 5/5 and 2/2 PASS.
- Python compilation and `git diff --check`: PASS.

## Gate status

- Phase 2 Green: approved and executed.
- Implementation approval: approved for this bounded scope.
- Phase 3/refactor approval: not granted.
- Independent review: re-review required after the recorded correction.

## Review terminal state

- Review record: [Phase 2 Green independent review](../reviews/2026-08-18-liss-0438-phase2-green-review.md)
- Terminal state: `COMPLETE`.
- Final verdict: `READY` for bounded Phase 2 Green; Phase 3/refactor and scope
  expansion are not approved.
