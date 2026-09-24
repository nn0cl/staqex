# AI Work Trace: Evaluator evolution-family decomposition

## Decision boundary

- Parent: WP-0168.
- Proposed issue: LISS-0575.
- Current phase: Architecture Path design intake.
- Requested approval: `WP-0168 / Unit A evolution-family decomposition
  Architecture Path scope approval`.
- Implementation permission: none.

## Evidence and inventory

- Target: `runtime/evaluation/evolution.py`, 1,106 lines / 21 def
  declarations.
- Direct consumers: binding, calls, execution, observation, and compatibility
  wiring; direct tests cover explicit evolution, unitary/QFT, CNOT/C-apply,
  tuple-coordinate Hamiltonians, and grid evolution.
- Candidate successors: unitary operations, evolution orchestration, and
  Hamiltonian/grid evolution.
- State boundary: Evaluator owns mutable maps, Joint lifecycle, provenance,
  and runtime DTO identity.

## Applicable process lessons

- `evaluator-state-ownership`: no copied mutable state or second Joint owner.
- `private-consumer-inventory`: enumerate private hooks before body removal.
- `decomposition-callback-boundary`: promote implicit runtime entrypoints to
  explicit context callbacks.
- `compatibility-baseline`: preserve actual runtime exports and private hook
  compatibility until separately retired.

## Architecture Path scope approval

- Approval: `WP-0168 / Unit A evolution-family decomposition Architecture Path
  scope approval` (2026-09-22).
- Scope accepted for design refinement only; Phase 0 acceptance and
  implementation remain unauthorized.
- Candidate A1/A2/A3 boundaries are accepted for deterministic measurement;
  exact split and callback contracts remain unresolved until Phase 0.
- Next approval: `WP-0168 / LISS-0575 Phase 0 acceptance 承認`.

## Phase 0 acceptance

- Approval: `WP-0168 / LISS-0575 Phase 0 acceptance 承認` (2026-09-22).
- Closed the method-family inventory at 1,106 lines / 21 def declarations.
- Decided A1 unitary operations, A2 evolution orchestration, and A3
  Hamiltonian/grid evolution as the implementation units.
- Evaluator remains the mutable state/provenance owner; successors receive
  explicit context callbacks and retain no copied state.
- Direct consumers and allowed paths are recorded in LISS-0575. No tests or
  production implementation were added.
- Next approval: `WP-0168 / LISS-0575 Phase 1 Red 承認`.

## Phase 1 Red

- Approval: `WP-0168 / LISS-0575 Phase 1 Red 承認` (2026-09-23).
- Added the bounded Red suite and active-Red ledger entry only; no production
  implementation was added.
- The initial suite declared five structural gaps and six behavior
  characterizations. Review found its facade-retirement check was vacuous and
  its compatibility check only searched for names.

## Phase 1 Red test review — 2026-09-23

- Replaced the facade check with source symbol ownership contracts, and
  compatibility substring matching with AST imports from each successor.
- Added positive characterizations for C-apply, bounded explicit evolution,
  tuple-coordinate Hamiltonian evolution, and precomputed-grid evolution.
- Corrected bounded run: **5 failed, 10 passed**. The five expected failures
  are three family ownership gaps, compatibility successor wiring, and the
  missing context callback; all ten characterizations passed.
- Active-Red lifecycle, document lifecycle, coverage-ledger consistency, and
  `git diff --check` passed. No production code changed.
- Review result: accepted. Isolation: `same_context`, weaker than
  `separate_context`. Next gate: Phase 2 Green / Implementation approval.

## Phase 2 Green / Implementation — 2026-09-23

- Approval: `WP-0168 / LISS-0575 Phase 2 Green / Implementation 承認`.
- Moved A1 unitary operations, A2 explicit/bounded evolution orchestration,
  and A3 Hamiltonian/tuple/grid operations into their approved successor
  modules. `compatibility.py` wires existing Evaluator hook names to those
  implementations. `evolution.py` retains import compatibility in 27 lines.
- Added live state and callback declarations to `EvaluatorContext`. Runtime
  maps, `Joint` lifecycle, and evolution provenance remain owned by Evaluator;
  successors do not import or instantiate the Evaluator facade.
- The reviewed Red file was unchanged. Focused suite: **15 passed**. Consumer
  import/hook smoke passed. Adjacent suites: **46 passed**. Spec verification:
  **161/161 passed**.
- Baseline all-blocking run before implementation: **2,227 passed** on the
  same base SHA and Python 3.14.6 environment, excluding the then-active Red
  file. The first post-Green full run had **2,241 passed, 1 failed** because
  compatibility.py did not retain the expected `ExplicitPropagator` import.
  Restored the import; final all-blocking run passed **2,242 tests in 308.09s**
  using `.venv/bin/python -m pytest tests/ -q`.
- Other checks: active-Red lifecycle `entries=0`, document lifecycle,
  coverage-ledger consistency, `py_compile`, and `git diff --check` passed.
- Verification scope is split into focused, consumer smoke, adjacent,
  specification, and all-blocking evidence. Static Phase 0 inventory remains
  the source of truth for binding/calls/execution/observation private consumers;
  dynamic import mechanisms were not separately discovered beyond that
  recorded inventory.
- Working tree is dirty on `codex/liss-0575-evolution-family`, based on
  `e8e63ec25420660a28556eeab5ba3a605ef45812`, macOS / Python 3.14.6. The final
  full-suite window was approximately 2026-09-23 18:30:38–18:35:46 +09:00.
  Evidence is provisional until a commit SHA is established and every blocking
  suite is rerun against it.
- Next approval: `WP-0168 / LISS-0575 Phase 3 Refactor 承認`.

## Phase 3 Refactor — 2026-09-23

- Approval: `WP-0168 / LISS-0575 Phase 3 Refactor 承認`.
- Re-read the accepted explicit-evolution specifications, LISS-0575, WP-0168,
  the Phase 1 review, runtime routing, source-quality and verification policy,
  and the current runtime consumers before refactoring.
- Split Hamiltonian one-step execution into named duration normalization,
  operator resolution, legacy single-Pauli execution, and non-qubit-basis
  helpers. Largest function decreased from 326 to 137 lines; the module is
  467 lines. Consolidated bounded-evolution provenance construction.
- Review found no unresolved behavior or ownership issue. Assertions and
  tests were not modified. A transient bare-Identity apply return-indentation
  regression surfaced as three specification-suite failures; corrected it,
  then reran the spec suite and all blocking tests successfully.
- Verification: focused+adjacent **63 passed**, consumer smoke passed,
  spec **161/161**, full blocking **2,242 passed in 316.58s**. Lifecycle,
  document lifecycle, coverage ledger, compileall and diff checks passed.
- Environment: macOS / Python 3.14.6; base/tested commit
  `e8e63ec25420660a28556eeab5ba3a605ef45812`, working tree dirty. Full-suite
  window 2026-09-23 19:54:06–19:59:22 +09:00. Evidence is provisional until
  commit SHA and required post-commit rerun.
- Isolation: `same_context`, weaker than `separate_context`; no configured
  enabled large-change review override. `review-change.py` could not report
  current dirty-tree metrics, so that structural measurement remains an
  explicit gap; source-file/function counts were inspected directly.
- Final review approval received: `WP-0168 / LISS-0575 Phase 3 最終レビュー
  承認` (2026-09-23). The review is accepted; commit and SHA-specific
  blocking rerun remain before issue closure.

## Post-merge closeout — 2026-09-25

- User request: reconcile the stale LISS-0575 / WP-0168 completion ledger and
  consolidate WP-0167, then commit, push, and merge the documentation update.
- Current phase: documentation closeout on the already-approved WP-0168 scope;
  no source implementation or new architecture decision.
- Evidence: PR #596 is merged at `66da78c824b5e5ce97fdf35b0ff9c79d7eec9df3`;
  its implementation head is `fbe5e768301f514b99824c4211bb63883076d5b6`.
  GitHub workflow run `35873796171` for that head completed successfully.
  PR evidence records 2,242 blocking tests, 63 focused/adjacent tests, and
  spec verification 161/161 on the implementation SHA.
- Process finding: issue/work-plan status remained open after merge. The
  existing `status-drift` lesson and Definition of Done directly apply; this
  closeout applies them by synchronizing the Issue, both WPs, and current
  decomposition measurements. No new lesson or template-feedback record is
  needed.
- Current `main` remeasurement was checked at
  `9b2e2e0f8e56399ba8cbd662bbc3bf6d569cb7b7`: evaluator 1,867 lines / 82
  direct methods; observation 768; operators 619; typecheck 4,678; parser
  3,679.
- Included: LISS-0575, WP-0167/WP-0168, decomposition spec, PR #596 merge and
  CI evidence, and the applicable status-drift lesson.
- Omitted: unrelated evaluator successor work and unmerged feature branches.
- Routing: host agent for documentation review; GitHub and local deterministic
  tools for commit, verification, PR, CI, and merge. No private context or
  credentials included.
- Closeout verification on initial commit `bea1fd8f`: full blocking suite
  **2,249 passed in 320.17s**; spec **161/161**; document lifecycle, coverage
  consistency, active-Red lifecycle (0 entries), execution-batch records (20),
  and `git diff --check` passed. Current-main source measurements matched the
  updated specification.
- This trace synchronization changes the final closeout commit SHA, so rerun
  the full blocking suite against that final SHA before push/merge. PR CI on
  the final head remains the merge gate.
- Changed files: LISS-0575, WP-0167, WP-0168, decomposition specification,
  and this representative trace.
- Next safe action: commit this verification-record update, rerun blocking
  checks on its final SHA, and open the documentation closeout PR against the
  current `main`.
