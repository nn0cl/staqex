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

## Attempt 25 — Unit D Phase 2 Green

- Date: 2026-09-19
- Approval: `WP-0163 / LISS-0566-D Phase 2 Green / Implementation 承認`
- Result: moved the reviewed call-binding/frame implementation into
  `runtime/evaluation/calls.py`, added explicit target/function/method binding
  entrypoints, removed `Evaluator._legacy_bind_call`, and preserved the
  private `_bind_call` compatibility identity through the existing bridge.
  The cross-family `_run_legacy_ast_body` dispatcher remains intentionally in
  the facade.
- Measurement: `runtime/evaluator.py` is **4,003 lines** and
  `runtime/evaluation/calls.py` is **529 lines**.
- Verification: Unit D **8 passed**, adjacent **42 passed**, targeted runtime
  regressions **19 passed**, and full blocking pytest **2,155 passed**.
- Lifecycle: removed the `LISS-0566-D` Active-Red entry after Green.
- Scope: no Semantic IR, QASM projection, parser/typechecker, provider SDK,
  network, credential, or live-QPU behavior changed.
- Next approval: `WP-0163 / LISS-0566-D Phase 3 Refactor 承認`.

## Attempt 26 — Unit D Phase 3 Refactor

- Date: 2026-09-19
- Approval: `LISS-0566-D Phase 3 Refactor 承認`
- Result: separated call compatibility installation from evolution
  compatibility, made `calls.py` consume explicit environment/frame callbacks,
  and removed the obsolete `_legacy_bind_call` protocol contract. The private
  `_bind_call` alias remains as an explicit compatibility boundary.
- Verification: Unit D/adjacent **42 passed**, targeted runtime regressions
  **19 passed**, full blocking pytest **2,155 passed**, Spec Verification
  **161/161**, compileall, lifecycle, document, coverage-ledger, and diff
  checks passed.
- Scope: no assertion, fixture, Semantic IR, QASM, provider, network,
  credential, or live-QPU behavior changed.
- Next approval: `WP-0163 / LISS-0566-D Phase 3 最終レビュー 承認`.

## Attempt 27 — Unit D Phase 3 final review

- Date: 2026-09-19
- Approval: `LISS-0566-D Phase 3 最終レビュー 承認`
- Result: no blocker found across compatibility wiring, context/state
  ownership, private-consumer preservation, structure budget, or behavior
  preservation. LISS-0566-D and WP-0163 were marked complete.
- Process review: no operating-contract deviation or operational problem
  found.
- Remaining boundary: `_bind_call` remains as a documented private
  compatibility alias; retirement requires a separate consumer decision.

## Attempt 24 — Unit D Phase 1 Red test review

- Date: 2026-09-19
- Approval: `WP-0163 / LISS-0566-D Phase 1 Red テストレビュー承認`
- Review route: `same_context`, weaker than `separate_context`.
- Findings: no blocker. Eight bounded contracts were accepted; the focused
  result is **4 failed, 4 passed**, with four intentional structural gaps and
  four passing boundary/characterization contracts.
- Verification: Active-Red lifecycle passed with one owned entry and
  `git diff --check` passed.
- Result: Phase 1 Red review accepted; no production implementation started.
- Next approval: `WP-0163 / LISS-0566-D Phase 2 Green / Implementation 承認`.

## Attempt 20 — Unit D architecture design intake

- Date: 2026-09-19
- Request: Unit D facade/structure audit design intake after LISS-0566-C
  completion.
- Path: Architecture Path; no implementation authorized.
- Measurement: `runtime/evaluator.py` is **4,491 lines** with **110 methods**;
  largest methods are `_legacy_bind_call` (491 lines) and
  `_run_legacy_ast_body` (414 lines).
- Design boundary: inventory public/private/dynamic consumers, classify the
  remaining evaluator responsibilities, preserve one mutable state owner, and
  define the first successor Phase 1 Red contract before moving source.
- Open decisions: split boundaries for call binding versus AST body execution;
  classical value evaluation coupling; and any future private-alias retirement.
- Result: created `LISS-0566-D-facade-structure-audit.md`; awaiting typed
  Architecture Path scope/design approval.

## Attempt 21 — Unit D Phase 0 design evidence

- Date: 2026-09-19
- Approval: `WP-0163 / LISS-0566-D Architecture Path scope/design 承認`
- Evidence: measured `Evaluator` at 4,491 lines and 110 methods; static
  `runtime.evaluator` consumer inventory at 105 files in source/test/tool/
  example roots; reviewed compatibility assignments and existing calls/values
  delegation wrappers.
- Design result: `_run_legacy_ast_body` remains a cross-family dispatcher and
  must not be moved wholesale. The first candidate is a bounded call-binding/
  frame slice behind `evaluation/calls.py`, with receiver restoration,
  dispatch, diagnostics, and single-state-owner Red contracts.
- Verification: document lifecycle and `git diff --check` passed; no source or
  test implementation changes were made.
- Next approval: `WP-0163 / LISS-0566-D Phase 0 acceptance 承認`.

## Attempt 15 — Unit C Phase 1 Red

- Date: 2026-09-19
- Approval: `WP-0163 / LISS-0566-C Phase 1 Red 承認`
- Result: added `tests/test_liss_0566_unit_c_red.py` with nine structural and
  characterization contracts; registered `LISS-0566-C` in
  `docs/testing/active-red-tests.toml`.
- Expected Red contract: focused execution should report **4 failed, 5
  passed**. Structural failures cover missing extracted entrypoints, bodies
  still present on `Evaluator`, missing narrow operator callbacks, and
  compatibility hooks not yet wired to `evaluation/operators.py`.
- Scope discipline: no production source or reviewed assertion changed; the
  no-facade dependency and four existing operator/factory/binder/method
  characterization contracts remain passing.
- Next approval: `WP-0163 / LISS-0566-C Phase 1 Red テストレビュー承認`.

## Attempt 16 — Unit C Phase 1 Red test review

- Date: 2026-09-19
- Approval: `WP-0163 / LISS-0566-C Phase 1 Red テストレビュー承認`
- Review route: `same_context`, weaker than `separate_context`.
- Result: accepted the intentional structural Red contract and added two
  explicit characterization nodes for set-projector tree lowering and
  Jordan-Wigner second-quantized binding; the suite now has **4 failed, 7
  passed**.
- Verification: focused Red run completed with the expected exit code 1;
  active-Red lifecycle passed with one entry; `git diff --check` passed.
- Findings: no Phase 1 test-review blocker. No production source, provider
  boundary, Semantic IR authority, or reviewed assertion was changed.
- Next approval: `WP-0163 / LISS-0566-C Phase 2 Green / Implementation 承認`.

## Attempt 14 — Unit C acceptance/design intake

- Date: 2026-09-19
- Approval: `WP-0163 / LISS-0566-C acceptance/design intake 承認`
- Scope: operator-name/RHS classification, top-level operator resolution,
  merged finite-array context, nested Operator calls and recursive tree
  resolution, set-comprehension lookup, finite-binder/operator lowering,
  Operator-returning function factories, Operator-returning class methods,
  and typed second-quantized binding.
- Measurement: current `runtime/evaluator.py` is **4,957 lines**; the Unit C
  manifest is **11 methods / 507 physical lines**. Existing pure source-arg
  conversion and projector-sum helpers remain in `evaluation/operators.py`.
- Decisions: `Evaluator` remains the sole mutable state owner; factory locals
  and method receiver state remain call-local; compatibility aliases remain
  installed until Unit D; recursive tree resolution remains the canonical
  runtime pass; Semantic IR and provider/QPU boundaries are unchanged.
- Process lessons applied: private-consumer inventory, exact compatibility
  ownership checks, explicit single-state-owner callbacks, named compatibility
  bridge, and positive/negative neighboring-form characterization.
- Result: added the bounded Unit C issue and detailed work-plan design. No
  Phase 1 Red tests, production source, or active-Red lifecycle entry were
  created.
- Next approval: `WP-0163 / LISS-0566-C Phase 1 Red 承認`.

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

## Attempt 10 — Unit B Phase 1 Red test review

- Date: 2026-09-19
- Approval: `WP-0163 / LISS-0566-B Phase 1 Red テストレビュー承認`
- Review route: `same_context`, weaker than `separate_context`.
- Findings: the Red scope is bounded to Unit B; QFT and controlled-gate
  characterization pass; four structural gaps fail for the expected pre-Green
  reasons. The compatibility assertion was strengthened to require exact
  evaluator-to-extracted-function assignments.
- Verification: focused suite `4 failed, 3 passed`, active-Red lifecycle
  passed with one owned entry, and diff check passed.
- Disposition: accepted; no production implementation permission is implied.
- Next approval: `WP-0163 / LISS-0566-B Phase 2 Green / Implementation 承認`.

## Attempt 11 — Unit B Phase 2 Green

- Date: 2026-09-19
- Approval: `WP-0163 / LISS-0566-B Phase 2 Green / Implementation 承認`
- Result: extracted Unit B unitary/gate mechanics and narrow read-only context
  callbacks; compatibility hooks remain installed.
- Measurement: `evaluator.py` decreased from 5,164 to 4,953 lines; extracted
  `evolution.py` is 1,092 lines.
- Verification: Unit B focused `7 passed`, adjacent QFT/apply/capply/QASM/S01
  regression `20 passed`, full blocking pytest `2,136 passed`, public
  baseline, Spec Verification, compileall, lifecycle, coverage-ledger, and
  diff checks passed.
- Lifecycle: removed the LISS-0566-B active-Red entry after Green.
- Scope: Unit C, Semantic IR, provider SDK, network, credentials, and live QPU
  behavior were not changed.
- Next approval: `WP-0163 / LISS-0566-B Phase 3 Refactor 承認`.

## Attempt 12 — Unit B Phase 3 Refactor

- Date: 2026-09-19
- Approval: `WP-0163 / LISS-0566-B Phase 3 Refactor 承認`
- Result: clarified Unit B type/doc contracts, callback documentation,
  duplicate operator lookup, and compatibility formatting without changing
  behavior or assertions.
- Measurement: `evaluator.py` is 4,957 lines; `evolution.py` is 1,106 lines.
- Verification: focused/adjacent `27 passed`, full blocking `2,136 passed`,
  Spec Verification `161/161`, public baseline, compileall, lifecycle,
  coverage-ledger, and diff checks passed.
- Next approval: `WP-0163 / LISS-0566-B Phase 3 最終レビュー 承認`.

## Attempt 13 — Unit B final review and completion

- Date: 2026-09-19
- Approval: `WP-0163 / LISS-0566-B Phase 3 最終レビュー 承認`
- Review route: `same_context`, weaker than `separate_context`.
- Findings: no implementation blocker. One stale Issue next-approval pointer
  was corrected to the final-review record.
- Verification at SHA `c3eb3e26cc2c5bc671aafd3a9192b5c9046e5d24`:
  full blocking pytest `2,136 passed`, focused/adjacent `27 passed`, Spec
  Verification `161/161`, public baseline, compileall, lifecycle,
  coverage-ledger, document lifecycle, and diff checks passed.
- Result: LISS-0566-B marked `done`; WP-0163 keeps Unit C and Unit D gated.
- Process review: no operating-contract deviation or operational problem
  found.

## Attempt 17 — Unit C Phase 2 Green

- Date: 2026-09-19
- Approval: `WP-0163 / LISS-0566-C Phase 2 Green / Implementation 承認`
- Result: extracted the eleven Unit C operator-resolution/lowering methods into
  `runtime/evaluation/operators.py`; added explicit context callbacks for live
  environments, finite-array lookup, receiver/assignment state, and recursive
  evaluation; retained established compatibility aliases in
  `evaluation/compatibility.py`.
- Measurement: `runtime/evaluator.py` is **4,491 lines** and
  `runtime/evaluation/operators.py` is **617 lines**.
- Verification: Unit C focused **11 passed**, adjacent operator/binder/
  second-quantization regressions **29 passed**, combined structural suite
  **17 passed**, affected S02/benchmark/legacy consumers **20 passed**, and
  full blocking pytest **2,147 passed**. `git diff --check` passed after
  whitespace cleanup.
- Lifecycle: removed the LISS-0566-C active-Red entry after Green.
- Scope: no Semantic IR, QASM projection, parser/typechecker, provider SDK,
  network, credential, or live-QPU behavior changed.
- Next approval: `WP-0163 / LISS-0566-C Phase 3 Refactor 承認`.

## Attempt 18 — Unit C Phase 3 Refactor

- Date: 2026-09-19
- Approval: `WP-0163 / LISS-0566-C Phase 3 Refactor 承認`
- Result: behavior-preserving cleanup of `evaluation/operators.py`:
  normalized extracted-function indentation/signatures, removed a duplicate
  local import, restored the missing `LitFloat` import, centralized numeric
  receiver-field extraction, clarified class lookup and host-array merging,
  and formatted long calls.
- Verification: Unit C and adjacent suites **46 passed**, full blocking pytest
  **2,147 passed**, Spec Verification **161/161**, compileall, Active-Red
  lifecycle, document lifecycle, coverage-ledger consistency, and
  `git diff --check` passed.
- Scope: no acceptance assertion, compatibility assignment, Semantic IR,
  QASM, provider boundary, credential, network, or live-QPU behavior changed.
- Next approval: `WP-0163 / LISS-0566-C Phase 3 最終レビュー 承認`.

## Attempt 22 — Unit D Phase 0 acceptance

- Date: 2026-09-19
- Approval: `WP-0163 / LISS-0566-D Phase 0 acceptance 承認`
- Result: accepted the Unit D audit boundary, measured consumer/structure
  evidence, single-state-owner constraint, compatibility role, and bounded
  call-binding/frame successor candidate.
- Scope: Phase 1 Red test/design work only; no production implementation,
  facade retirement, or private-alias removal authorized.
- Next approval: `WP-0163 / LISS-0566-D Phase 1 Red 承認`.

## Attempt 23 — Unit D Phase 1 Red

- Date: 2026-09-19
- Approval: `WP-0163 / LISS-0566-D Phase 1 Red 承認`
- Result: added eight bounded call-binding/frame acceptance contracts and
  registered issue-linked Active-Red ownership for `LISS-0566-D`.
- Expected Red: **4 failed, 4 passed**; structural gaps cover successor
  entrypoints, legacy body ownership, and compatibility wiring. Context,
  no-facade dependency, and existing local call behavior remain green.
- Scope discipline: no production source or reviewed assertion changed.
- Next approval: `WP-0163 / LISS-0566-D Phase 1 Red テストレビュー承認`.

## Attempt 19 — Unit C Phase 3 final review

- Date: 2026-09-19
- Approval: `WP-0163 / LISS-0566-C Phase 3 最終レビュー 承認`
- Review route: `same_context`, weaker than `separate_context`.
- Findings: no blocker. Extracted ownership, single mutable-state ownership,
  compatibility bridge, behavior preservation, and size guardrail were all
  confirmed from the repository artifacts and deterministic checks.
- Verification: Unit C/adjacent **46 passed**, full blocking pytest **2,147
  passed**, Spec Verification **161/161**, compileall, Active-Red lifecycle,
  document lifecycle, coverage-ledger consistency, and `git diff --check`
  passed.
- Result: LISS-0566-C marked `done`; Unit D remains separately gated.
- Process review: no operating-contract deviation or operational problem
  found.
