# AI Work Trace: evaluator stateful evolution/operator successor

## Attempt 1 — Architecture Path Phase 0

- Date: 2026-09-19
- Approval: `Architecture Path / Phase 0 acceptance / evaluator stateful
  evolution and operator lowering successor 承認`
- Scope: profile the residual LISS-0562 evaluator stateful surface and define
  the successor issue/work-plan boundaries.
- Evidence: `evaluator.py` measured at 5,921 lines and 136 definitions; 25
  evolution/operator legacy methods remain. The measured bodies are grouped
  into evolution execution (~800 lines), unitary/gate application (~225
  lines), and operator resolution/lowering (~513 lines).
- Decisions: `Evaluator` remains the mutable-state owner; extracted functions
  use explicit callbacks/context; no new provider or semantic authority is
  introduced; Phase 1 must characterize fixed-seed and QASM behavior before
  production extraction.
- Result: created LISS-0566 and WP-0163 design artifacts. No production source
  or tests were changed.
- Next approval: typed Phase 1 Red approval for the named successor scope.

## Attempt 2 — Feature Path Phase 1 Red

- Date: 2026-09-19
- Approval: `Feature Path / Phase 1 Red / LISS-0566 stateful evolution and
  operator lowering successor 承認`
- Result: added six structural/characterization contracts in
  `tests/test_liss_0566_evaluator_stateful_successor_red.py`; registered the
  active Red ownership in `docs/testing/active-red-tests.toml`.
- Verification: focused pytest **3 failed, 3 passed**, the expected Red result
  for missing successor entrypoints, undecomposed stateful implementation
  bodies, and undeclared callback contracts. No production source changed.
- Next action: Phase 1 Red test review, then a separate Phase 2 Green approval
  for one named decomposition unit.

## Attempt 3 — Phase 1 Red test review

- Date: 2026-09-19
- Approval: `Feature Path / Phase 1 Red テストレビュー / LISS-0566 stateful
  evolution and operator lowering successor 承認`
- Result: the six-test Red contract and its intentional `3 failed, 3 passed`
  evidence were accepted. Active-Red ownership remains registered until Green.
- Scope decision: Phase 2 is narrowed to Unit A, evolution execution and
  Hamiltonian loops. Unit B and Unit C require separate implementation gates.
- Next approval: `Feature Path / Phase 2 Green / LISS-0566 Unit A evolution
  execution implementation 承認`.

## Attempt 4 — Phase 2 Green, Unit A

- Date: 2026-09-19
- Approval: `Feature Path / Phase 2 Green / LISS-0566 Unit A evolution
  execution implementation 承認`
- Result: physically moved ten evolution execution methods into
  `runtime/evaluation/evolution.py`; compatibility aliases continue to expose
  the established private evaluator names.
- Measurement: `evaluator.py` decreased from 5,921 to 5,164 lines; 757 lines
  were removed from the facade. Unit B and Unit C were not changed.
- Verification: focused `6 passed`, adjacent `58 passed`, full blocking
  pytest `2,129 passed`, public-symbol baseline passed, compileall passed,
  and lifecycle/diff checks passed.
- Lifecycle: removed the LISS-0566 active-Red entry after the accepted
  contract became green.
- Next approval: `Feature Path / Phase 3 Refactor / LISS-0566 Unit A evolution
  execution 承認`.

## Attempt 5 — Phase 3 Refactor, Unit A

- Date: 2026-09-19
- Approval: `Feature Path / Phase 3 Refactor / LISS-0566 Unit A evolution
  execution 承認`
- Result: renamed the ten extracted Unit A functions from legacy extraction
  names to responsibility-oriented names and added explicit
  `EvaluatorContext` annotations.
- Compatibility: `evaluation/compatibility.py` continues to install the
  evaluator's established private hooks; no consumer-facing or semantic/QASM
  boundary changed.
- Measurement: `evaluator.py` remains 5,164 lines; `evolution.py` is 861
  lines.
- Verification: focused/adjacent characterization `12 passed`, full blocking
  pytest `2,129 passed`, public-symbol baseline, compileall, active-Red and
  document lifecycle checks, coverage-ledger consistency, and diff checks
  passed.
- Next approval: `Feature Path / Phase 3 最終レビュー / LISS-0566 Unit A
  evolution execution 承認`.

## Attempt 6 — Phase 3 Final Review, Unit A

- Date: 2026-09-19
- Review route: `same_context` (weaker than `separate_context`)
- Scope: Unit A refactor, compatibility wiring, state ownership, verification,
  and documentation synchronization.
- Findings: no implementation blocker. The canonical decomposition table had
  a stale pre-extraction `runtime/evaluator.py` line count; it was synchronized
  from 6,926 to the measured 5,164 lines and the concentration description was
  narrowed to the remaining facade families.
- Verification at SHA `b1806fb3a3a1f0135214c9ab6b25b02ca87b753b`:
  full blocking pytest `2,129 passed`, focused/adjacent characterization
  `12 passed`, Spec Verification `161/161`, public baseline, compileall,
  active-Red lifecycle, document lifecycle, coverage-ledger consistency, and
  diff checks passed.
- Disposition: recommend acceptance; no implementation changes requested.
- Next approval: `LISS-0566 Phase 3 最終レビュー 承認`.

## Attempt 7 — Final approval and status synchronization

- Date: 2026-09-19
- Approval: `LISS-0566 Phase 3 最終レビュー 承認`
- Result: LISS-0566 Unit A marked `done`; WP-0163 keeps Units B/C/D gated and
  in progress.
- Process review: no operating-contract deviation or operational problem
  found.

## Attempt 8 — Unit B acceptance/design intake

- Date: 2026-09-19
- Approval: `WP-0163のUnit B acceptance/design intake承認`
- Scope: unitary resolution, QFT family matrix generation, multi-wire
  `apply`, controlled `capply`, and the tightly coupled argument splitter.
- Measurement: four evaluator methods, approximately 250 body lines; current
  `runtime/evaluator.py` size is 5,164 lines.
- Boundary: `Evaluator` remains the single mutable state owner; extracted code
  receives a typed context and retains no copied maps. Compatibility aliases,
  Semantic IR authority, QASM/diagnostic behavior, and provider exclusions are
  explicit acceptance constraints.
- Phase 1 Red contract: structural ownership, narrow context reads, private
  consumer compatibility, fixed-seed local behavior, QASM3, QFT, capply
  polarity, identity, and rejection diagnostics.
- No tests or production implementation were changed.
- Next approval: `WP-0163 / LISS-0566-B Phase 1 Red 承認`.

## Attempt 9 — Unit B Phase 1 Red

- Date: 2026-09-19
- Approval: `WP-0163 / LISS-0566-B Phase 1 Red 承認`
- Result: added seven Unit B acceptance contracts and registered active-Red
  ownership under `LISS-0566-B`.
- Red evidence: focused `tests/test_liss_0566_unit_b_red.py` reports **4
  failed, 3 passed** with no collection errors. Structural failures cover
  extracted entrypoints, facade ownership, narrow context callbacks, and
  compatibility wiring. QFT and controlled-gate characterization passes.
- Scope discipline: no production source or reviewed assertion was changed;
  Unit C and provider/QPU concerns remain excluded.
- Next approval: `WP-0163 / LISS-0566-B Phase 1 Red テストレビュー承認`.
