# LISS-0594: Unitarity判定familyの責務分離

- Local issue ID: LISS-0594
- GitHub issue: none; local planning
- Status: in_progress — GU supplement verification after Active-Red renewal accepted through `75d24931`; main decomposition remains Phase 1 Red
- Phase: Phase 1 Red
- Type: behavior-preserving source decomposition
- Priority: WP-0175 candidate 4; ordering is inventory guidance, not an implementation commitment
- Initial / current planning size: L / L; no reclassification
- Owner: Codex host / Adjudicator
- Parent: WP-0175
- Depends on: accepted core decomposition; delivered LISS-0590–0593
- Blocks: no unrelated work
- Related branch: `codex/liss-0594-unitarity-family-design`
- Specification: [accepted U01–U10](../specs/unitarity-check-family-separation.md)
- Design intake / trace: [2026-10-23](../collaboration/traces/2026-10-23-liss-0594-unitarity-family-design.md)

## Scope and decision boundary

The approved continuation is limited to investigating and specifying a safe
decomposition of `compiler/staqex/unitarity_check.py`. The file is a 933-line
static pipeline pass, not a Parser or runtime evaluator. Its entry point is
called by `pipeline_legacy._analyze_unit`; the public `check_unitarity` name,
diagnostic dictionaries, ordering, and all established behavior remain in
scope as compatibility constraints.

This Phase 0 proposes separating cohesive implementation responsibilities
behind the existing entry point. The exact module split and family ownership
remain a design choice to be accepted before Phase 1. The design must consider
lineage classification, expression traversal and diagnostics, closed-evidence
transparency for `Evolve times N`, static Operator matrix/Hermiticity checks,
and small closed-expression helpers. It must explicitly disposition the
classical-scalar measurement check rather than silently relocating or changing
it. No line-count reduction target is imposed; implementation bodies must
actually move behind a thin facade if a split is accepted.

Out of scope: changing any unitarity/isometry/Hermiticity criterion, numeric
tolerance, whitelist, fail-closed boundary, diagnostic code/text/span/order,
operator resolution, parser/typechecker behavior, runtime semantics, standards,
or public API; deleting behavior; broadening proof claims; changing fixtures or
tests in Phase 0; implementation, commit, push, PR, or merge. Existing quirks
are characterization targets, not implicit bug-fix authority.

## Current consumer and contract evidence

- Production direct import: `compiler/staqex/pipeline_legacy.py`; the
  `_analyze_unit` pass appends `check_unitarity(unit)` diagnostics before
  TypeChecker diagnostics. `HARD_CODES` classifies the emitted error codes.
- Direct tests import `check_unitarity` in
  `tests/test_liss_0411_static_operator_resolution_red.py`. Additional tests
  exercise compiler diagnostics, including LISS-0436 and the operator
  characteristics/spec-verification suites. Static search is not proof of all
  dynamic, external, or serialized consumers.
- Existing semantic authorities include ADR 0045/0052 and relevant operator
  specifications; LISS-0411 and LISS-0436 own specific historical safeguards.
  This refactor must not supersede them.
- The accepted inventory records 933 physical lines, 803 function-span-union
  lines, 23 functions and a 225-line `_check_expr_unitarity`. These are
  measurements, not behavioral scope or structure-budget waivers.
- Shared state is passed through mutable maps for quantum/strict lineage,
  Operators, scalar coefficients, resolved objects, and diagnostics. Any new
  family boundary must preserve mutation timing and alias/recursion behavior.

## Phase 0 acceptance U01–U10

| ID | Accepted condition |
|---|---|
| U01 | Pin an immutable delivered source/test base and capture exact hashes for the target, public facade, pipeline caller, and all touched consumers before Phase 1. Reconcile any drift from the 2026-10-15 inventory. |
| U02 | Map each moved function and private import/call edge to one implementation owner. Record direct, facade, test, dynamic-search limitations; preserve `check_unitarity` import and call contract. |
| U03 | Define the accepted responsibility/module map, including the expression walker, lineage/evidence helpers, matrix and Hermitian checks, classical scalar/measure behavior, and shared AST traversal. No helper-only facade or duplicate live implementation. |
| U04 | Preserve exact diagnostic list behavior: codes, text, line/column, emission order, multiplicity, early returns, and `HARD_CODES` handling on named positive and negative examples. |
| U05 | Preserve lineage maps, lexical Operator scope, scalar collection, object resolution and recursive expression/function traversal, including mutation timing and memoization/cycle behavior. |
| U06 | Preserve numerical behavior: `_EPS = 1e-8`, matrix construction, wire-count handling, Fock/grid paths, coefficient witnesses, and the current fail-closed/quiet exception outcomes. No tolerance or mathematical-policy changes. |
| U07 | Preserve LISS-0411 static struct-coefficient resolution and its positive/negative safety cases, plus LISS-0436 transparent `Evolve times N` behavior; map inherited suites to explicit owner/caller smoke coverage. |
| U08 | Declare explicit in/out scope for classical measurement eligibility (`_check_measure_target`, `_expr_is_classical_scalar`) and AST child walking; any discovered independent behavior change returns to design. |
| U09 | Specify Phase 1 tests only after acceptance: structure/unique-owner checks plus actual pipeline and direct consumer smoke, existing focused tests, adjacent regressions, and inherited blocker comparison. No blanket hash or public-import-only proof. |
| U10 | Record structure-budget disposition for source modules and implementation bodies; final Phase 2/3 gates require focused, consumer, adjacent, and all-blocking verification at the final committed SHA/environment per verification policy. Human review remains separate. |

Adjudicator explicitly accepted this exact dedicated issue/spec and U01–U10
Phase 0 criteria on 2026-10-23. The acceptance does not authorize Phase 1,
implementation, commit, or remote delivery.

## Review / approval state

- Scope / Phase 0 design-start authority: continuation of the user's
  instruction to proceed after LISS-0593 closeout; only Phase 0 investigation
  and design were initially authorized.
- Phase 0 acceptance: explicitly received 2026-10-23 for this dedicated
  issue/spec and exact U01–U10 criteria.
- Phase 1 Red execution approval: explicitly received 2026-10-25 for
  test-only work under accepted U01–U10.
- Implementation allowed: no.
- Phase 1 Red execution allowed: yes, only for the authorized test/fixture and
  active-Red lifecycle artifacts; production implementation is not allowed.
- Post-review requirement: human acceptance of the exact spec and any
  boundary/structure dispositions; if a new architecture decision is needed,
  record and obtain its approval separately.

## AI planning record

### AIP-0594-001 — proposed

- Status: proposed; planning only, not accepted for execution
- Authoring agent/environment: Codex host, local repository
- Model/reasoning as displayed: N/A (not exposed in the task context)
- Created: 2026-10-23
- Planning size: L
- Intended route: host for bounded Phase 0; same-context review if required by
  routing; no implementation routing requested yet
- Estimated token range: 6,000–12,000 task tokens; midpoint 9,000
- Estimation basis: one substantial design/spec pass with legacy evidence and
  acceptance matrix; excludes Red test authoring and implementation
- Confidence: medium; exact next decomposition boundary is not yet accepted
- Actual token use: N/A (not available to the agent)
- Revisions: none

## Adjudicator decision points

1. Review and accept the exact failing test cohort and baseline comparison.
   No later phase approval is implied.

## Phase 1 Red execution checkpoint — 2026-10-25

- Reviewed artifact is the new test module
  `tests/test_liss_0594_unitarity_family_red.py`, SHA-256
  `d85d28f37a30317a959eced12d16f348e45c4093ddd92033fca4edd282db408f`.
- U01 source/consumer pins at this checkpoint: `unitarity_check.py`
  `5b143ef91ee4513ed9514f915935f6f72b823bff04d28253cb7e7160d335c3ea`;
  `pipeline_legacy.py`
  `58c1cc721d0f0fbc625d2930a70571cf5fbc6c81026cd91dc559ca88cfb07405`;
  public `pipeline.py`
  `76a801834a1bce5bff07d6105610e7adcecfb532bd4e864f33b8a17ed0d5bf72`;
  direct consumers LISS-0411 `833d1802ddb208985eaa25fe4ec749f6fcd3096a3e7a93f6594fab1cb35cec66`,
  LISS-0436 `0dfd7fb6cd2252a87f3362dd098109dbac7eb45efe2aff59cd5df219033cf3b5`,
  LISS-0376 `4df5f27ae1b9848abdc83552ea522341618da39e261e0f02d2a98433bfe98f39`,
  SV-23 `6aefd0cd3ecb04a28a4ed7ec30857bebc5c2712f2493e3189d147318696f0bf7`,
  SV-30 `5b3ba9eca29d01a1e18db4b410f3838f6fd00791306f7a1ffae19882494ab147`.
- On dirty working tree at HEAD `93a2548ae168a70a3c3340bf79533de95828dc39`,
  macOS 27.0.1 arm64, CPython 3.12.6, pytest 9.0.3:
  `python3.12 -m pytest tests/test_liss_0594_unitarity_family_red.py tests/test_liss_0411_static_operator_resolution_red.py tests/test_liss_0436_evolve_times_block_transparency_red.py tests/test_liss_0376_unitarity_superpose_dispatch_red.py -q`
  produced 23 passed / 1 expected structural Red. The failing node is
  `test_phase1_structure_moves_recursive_walker_out_of_public_module`;
  the body currently remains in the public module. Diagnostic ordering,
  spans/messages, classical measurement, positive/negative transforms, and
  existing LISS-0411/0436/0376 consumers passed.
- `python3.12 tests/spec_verification/run_all.py`: 161/161 PASS.
- `python3.12 scripts/check-test-lifecycle.py --as-of 2026-10-25`: PASS,
  one active-Red entry.
- `python3.12 -m pytest tests/ -q --ignore=tests/test_liss_0594_unitarity_family_red.py`:
  3,583 passed / 6 failed in 451.88s. All six failures arise from the same
  exact-path assertion in inherited LISS-0591/0592/0593 guards:
  `tests/test_liss_0594_unitarity_family_red.py` is an unrecognized added test
  path. The affected nodes are LISS-0591 P10, LISS-0592 R06, and LISS-0593
  F09 pre/post and G07 pre/post. These are induced by the new test path; no
  comparable pre-addition root run was captured, so no unrelated baseline
  failure is claimed.
- No production code or prior guard was edited. Changing the exact allowed
  test-path cohort in predecessor guard support is outside the currently
  accepted LISS-0594 test specification. Do not loosen snapshots or path
  assertions. Phase 1 review/acceptance is not ready until the Adjudicator
  chooses whether to authorize a bounded compatibility supplement design.
- Next requested decision: Scope approval / Phase 0 design-start for a bounded
  LISS-0594 test-path guard-compatibility supplement covering only the exact
  new test-path allowance required by predecessor guards. No such repair is
  authorized yet.
- `git diff --check`: PASS. No commit, Phase 2, or delivery permission.

## Guard compatibility supplement — Phase 0 accepted (2026-10-26)

- Scope approval / Phase 0 design-start: explicitly received 2026-10-26 for
  investigating and specifying the exact test-path compatibility boundary
  described here. This does not authorize Red test edits, guard changes,
  acceptance of the proposed clauses, or any implementation.
- Phase 0 acceptance: Adjudicator explicitly accepted GU01–GU09 on 2026-10-26.
  This accepts the bounded supplement specification only; it does not
  authorize Phase 1 Red execution or any guard-support implementation.
- Canonical acceptance: [GU01–GU09](../specs/unitarity-check-family-separation.md#guard-compatibility-supplement--phase-0-accepted-gu01gu09).
- Observed failure chain: `tests/liss_0591_guard_support.py::historical_test_paths`
  composes the LISS-0591 path set with
  `tests/liss_0593_guard_support.py::new_test_paths()`. The latter currently
  declares only the LISS-0593 tests/fixtures. LISS-0593's `carrier_after()`
  reconstructs the accepted LISS-0591 support carrier and wires that same
  exact-path reader into copied-root checks. Six reported consumers reject
  the new LISS-0594 test file because it is absent from this explicitly
  composed inventory.
- Accepted narrow model: declare
  `tests/test_liss_0594_unitarity_family_red.py` as a separate exact
  follow-on test path, not as a member of LISS-0593's immutable semantic test
  cohort. Preserve the existing `NEW_TESTS`/`NEW_FIXTURES` composition and its
  accepted 26-path count. Reuse the existing `new_test_paths()` exact-set
  boundary so live and projected historical readers recognize only this
  additional path.
- Phase 1 test-only artifacts: add focused acceptance cases to the
  already declared LISS-0594 test module and update only the copied-root setup
  and explicit expected inventory in
  `tests/test_liss_0593_guard_composition_red.py`. Preserve all prior nodes and
  assertions; do not create another new test path.
- Proposed later support change, only after separate Phase 1 review and Phase
  2 approval: `tests/liss_0593_guard_support.py` declares the separate exact
  follow-on path and includes it in `new_test_paths()`. Do not edit the
  LISS-0591/0592/0593 baselines, evidence snapshots, or carrier source bytes.
- Required proof: exact current-root allow; exact copied pre/post-root allow;
  the LISS-0594 file must physically exist in each tested root; the historic
  set returned by `historical_test_paths()` remains exactly its original
  cohort; missing LISS-0594 artifact, missing historic path, and any unrelated
  added path are rejected. Run the six affected P10/R06/F09/G07 nodes through
  real consumers in both shapes.
- Out of scope: path globs/wildcards, blanket new-test allowance, changing old
  test bytes/assertions, changing the fixed 26-path LISS-0591/0593 cohort,
  regenerating fixtures or digests, changing production compiler code, or
  repairing unrelated existing failures.
- Current phase: supplementary Phase 1 Red authored; human review/acceptance
  pending. Next is Phase 2 Green only after that review and separate
  implementation approval. Implementation permission: no.

### Proposed AI planning record — AIP-0594-002

- Status: proposed; design only
- Authoring agent/environment: Codex host, local repository
- Model/reasoning as displayed: N/A (not exposed in task context)
- Created: 2026-10-26
- Planning size: M
- Intended route: host for bounded test-guard compatibility design; same-context
  review per runtime routing if a review packet is required
- Estimated token range: 3,000–6,000 task tokens; midpoint 4,500
- Estimation basis: one exact path propagation and copied-root evidence
  decision; excludes test authoring and guard modification
- Confidence: medium; existing staged reader/producer dependencies were traced,
  but no compatibility code has been exercised or changed
- Actual token use: N/A (not available to the agent)
- Revisions: none

## Guard compatibility supplement — Phase 1 Red checkpoint (2026-10-26)

- Phase 1 Red execution approval: explicitly received 2026-10-26 for the
  accepted GU01–GU09 test-only scope. No guard/support implementation is
  authorized.
- Test artifacts: `tests/test_liss_0594_unitarity_family_red.py` and the
  copied-root/inventory expectations in
  `tests/test_liss_0593_guard_composition_red.py`. No production, guard,
  fixture-evidence, baseline, or exclusion file was changed.
- The follow-on module remains the exact path
  `tests/test_liss_0594_unitarity_family_red.py`. Its pre-supplement pin was
  SHA-256 `d85d28f37a30317a959eced12d16f348e45c4093ddd92033fca4edd282db408f`;
  the current authored test artifact is SHA-256
  `1d49a7155e269e7e13e24299e1c5c249aa036d677b85f17c12486928bd1ae8f8`.
- Focused supplement cases: 9 failed as expected against the unmodified
  support reader because the exact follow-on path is not yet declared. The
  LISS-0594 characterization plus LISS-0411/0436/0376 consumers produced
  22 passed / 4 failed: the pre-existing structural Red plus three new
  compatibility Reds.
- Full LISS-0593 guard-composition module: 208 passed / 32 failed. All failures
  are inventory-compatibility Reds caused by the same undeclared exact
  follow-on path; no test was skipped and no frozen hash/assertion was loosened.
- The six previously observed inherited consumer nodes were rerun unchanged:
  LISS-0591 P10, LISS-0592 R06, and LISS-0593 F09/G07 pre/post. All six still
  fail at the exact path inventory boundary. A pre-addition full-suite baseline
  was not captured, so no broader unrelated-failure comparison is claimed.
- Same-context reviewer re-read the accepted spec, both changed test modules,
  and deterministic output. The initial synthetic-vs-real copied-root inventory
  probe was corrected to retain the real subprocess function before monkeypatch
  setup. The original LISS-0593 prefix-hash guard and all prior node IDs remain
  intact; review routing is `same_context` and is weaker than separate context.
- Current status at this checkpoint: the corrected Phase 1 Red cohort was
  explicitly re-accepted by the Adjudicator on 2026-10-27. The earlier Phase 2
  implementation authorization covered only the exact singleton support-path
  change; no main unitarity implementation is authorized by that scope.

## Guard compatibility supplement — Phase 1 Red correction and re-review (2026-10-26)

- User authorized correcting and re-reviewing the Phase 1 cohort after the
  first blocking run exposed test-setup defects.
- Corrections preserve GU02/GU05 acceptance tests in the existing LISS-0594
  module. The LISS-0593 module contains only the exact follow-on inventory
  expectation, copied-root setup, and consumer wiring required by GU06–GU08.
  LISS-0591 B08's synthetic inventory adds only the exact singleton; its prior
  bytes are checked against one explicit raw substitution.
- GU07 scopes the synthetic inventory patch and then runs P10/R06 with the real
  copied-root Git inventory. GU08 retains its positive/negative fault sequence
  and includes the exact follow-on path in its injected inventory.
- Same-context review re-read GU01–GU09, changed test files and deterministic
  output. No weakened semantic assertion, wildcard, skipped node, exclusion or
  regenerated historical evidence was found. Isolation is `same_context`,
  weaker than `separate_context`.
- Focused LISS-0594 plus LISS-0411/0436/0376: 25 passed / 1 expected structural
  Red (`test_phase1_structure_moves_recursive_walker_out_of_public_module`).
  LISS-0591 guard migration plus LISS-0593 guard composition: 319 passed.
  CI root suite: 3,589 passed / 0 failed; Spec verification: 161/161 PASS.
  Lifecycle and diff checks passed. Runs used dirty HEAD
  `93a2548ae168a70a3c3340bf79533de95828dc39`, Darwin arm64, CPython 3.12.6,
  pytest 9.0.3; final SHA remains provisional until commit.
- Review disposition: Phase 1 Red re-review passed and the corrected cohort was
  re-accepted by the Adjudicator on 2026-10-27. The exact singleton support
  change is locally Green under the recorded blocking evidence. This does not
  implement the main unitarity decomposition or authorize its source changes.

## Guard compatibility supplement — Phase 1 acceptance and Phase 2 Green (2026-10-27)

- Adjudicator explicitly re-accepted the corrected GU01–GU09 Phase 1 Red cohort
  on 2026-10-27.
- Phase 2 implementation permission had previously been explicitly granted
  for this supplement and was used only to add
  `FOLLOW_ON_TESTS = {"tests/test_liss_0594_unitarity_family_red.py"}` to
  `tests/liss_0593_guard_support.py::new_test_paths()`.
- Verification at dirty HEAD `93a2548ae168a70a3c3340bf79533de95828dc39`,
  Darwin arm64, CPython 3.12.6, pytest 9.0.3: focused LISS-0594 plus adjacent
  LISS-0411/0436/0376 was 25 passed / 1 expected structural Red; inherited
  LISS-0591/0593 suites were 319 passed; CI root suite was 3,589 passed / 0
  failed with the lifecycle-declared Active-Red exclusion; Spec verification
  was 161/161 PASS. Lifecycle and diff checks passed.
- This is provisional local evidence: no commit was made, and final-SHA
  blocking verification remains required after a later commit. The main
  unitarity checker remains unmodified; its structural Red is still open.
- At this 2026-10-27 checkpoint, the next approval was Phase 3 Refactor/review
  for the GU compatibility supplement. No main-source implementation, commit,
  or remote delivery was authorized by that checkpoint.

## Guard compatibility supplement — Phase 3 Refactor/review (2026-10-28)

- Approval: Adjudicator explicitly approved GU compatibility supplement
  Phase 3 Refactor/review on 2026-10-28. Scope is GU01–GU09 only; the main
  `unitarity_check.py` decomposition remains in Phase 1 Red.
- Refactor: corrected the `new_test_paths()` missing-artifact diagnostic from
  the misleading LISS-0593-only wording to the composed-inventory wording.
  Assertions, path membership, fixture bytes and consumer behavior were not
  changed.
- Review route: `same_context` per `runtime-routing.toml`; this is weaker than
  separate-context review. The reviewer re-read the canonical spec, issue,
  trace, source/test changes and deterministic output from disk.
- Findings: no blocking GU-supplement finding remains. The single exact
  follow-on path remains outside the frozen 26-path semantic cohort. Existing
  P10/R06/F09/G07 consumer paths and copied-root checks pass. No assertion was
  weakened or removed. The active-Red manifest excludes only the approved
  LISS-0594 module containing the still-intended main-source structural Red.
- Verification used dirty worktree at HEAD
  `93a2548ae168a70a3c3340bf79533de95828dc39`, macOS arm64, CPython 3.12.6,
  pytest 9.0.3: focused LISS-0594 plus LISS-0411/0436/0376 was 29 passed / 1
  expected structural Red; inherited LISS-0591/0593 suites were 319 passed;
  root blocking pytest was 3,589 passed / 0 failed with the lifecycle-declared
  exclusion; spec verification was 161/161 PASS. Lifecycle, document,
  coverage-ledger, execution-batch, baseline, syntax and diff checks passed.
  These are provisional dirty-tree results, not final-commit evidence.
- Environment comparison: an initial inherited-suite run under the unrelated
  venv Python 3.14.8/pytest 9.1.1 produced 49 AST-baseline failures. The same
  suite passed 319/319 under the CI-compatible Python 3.12.6/pytest 9.0.3;
  one failed node also passed alone in that environment. Treat the first run
  as environment-incompatible evidence, not as a product regression.
- Structure disposition: no production source body changed. The 344-line
  LISS-0594 test module is retained as the single follow-on path required by
  GU08; splitting it would alter the accepted exact-path inventory. The
  existing 668-line LISS-0593 composition test module received only the
  bounded consumer setup/expectation additions required by GU06–GU08. No
  `[source_structure]` budget is configured. Manual worktree accounting found
  1,363 inserted/deleted lines overall and 392 added Python lines, all
  test/support code; production-source additions are zero. `review-change.py`
  cannot report structured implementation-size metrics while the tree is
  dirty. Conditional large-change routing is not enabled, so the configured
  same-context review route applies.
- At the Phase 3 review checkpoint, the next gate was separate final-
  verification approval. That approval was received on 2026-10-28; this review
  approval itself authorized no commit, push, PR or merge.

## Guard compatibility supplement — dirty-tree final verification (2026-10-28)

- Approval: Adjudicator explicitly approved final verification on 2026-10-28.
- State: HEAD `93a2548ae168a70a3c3340bf79533de95828dc39`, dirty worktree;
  macOS arm64, CPython 3.12.6, pytest 9.0.3. No production/test source
  changed after Phase 3; review/status records were updated.
- Focused LISS-0594 plus LISS-0411/0436/0376: 29 passed / 1 intended main-source
  structural Red. Inherited LISS-0591/0593: 319 passed. Root blocking pytest
  with the lifecycle-declared LISS-0594 exclusion: 3,589 passed / 0 failed.
  Spec verification: 161/161. Test/document lifecycle, coverage ledger,
  execution-batch validation (20), behavior-preservation baseline (3 cases),
  Python compilation and diff checks passed.
- Result: GU compatibility supplement passed local final verification; no new
  comparable-environment failures. Main decomposition remains unimplemented,
  and its Phase 1 structural Red remains active.
- Limitation: no commit was authorized or made, so no immutable final SHA is
  verified. Next gate is separate local-commit/actual-SHA approval and a fresh
  all-blocking rerun. This does not authorize push, PR or merge.

## Guard compatibility supplement — committed-SHA verification (2026-10-28)

- Approval: Adjudicator approved local commit and actual-SHA all-blocking
  revalidation on 2026-10-28.
- Commit: `638c8956f8f1ff2d8808ef2cba68e66bd18a5922`, clean worktree at test
  time; macOS arm64, CPython 3.12.6, pytest 9.0.3.
- Focused LISS-0594 plus LISS-0411/0436/0376: 29 passed / 1 intended
  main-source structural Red. Inherited LISS-0591/0593: 319 passed. Root
  blocking pytest with the declared LISS-0594 active-Red exclusion: 3,589
  passed / 0 failed. Spec verification: 161/161.
- Repository sanity: required documents/ADRs (99), shell syntax, lifecycle,
  coverage ledger, execution-batch records (20), baseline (3 cases), Python
  syntax, diff checks and template-copy smoke passed. PR-only traceability is
  not applicable without a PR.
- Result: GU compatibility supplement passed all declared local blocking
  checks at this commit. Main unitarity decomposition remains unimplemented;
  its Phase 1 structural Red is still active. No new failures were found.
- This is a local verification record only; it does not authorize push, PR,
  merge, or acceptance of the main-source decomposition.

## Guard compatibility supplement — final review result accepted (2026-11-02)

- Approval: Adjudicator explicitly accepted the final review result on
  2026-11-02. Accepted scope is GU01–GU09 compatibility supplement only.
- Accepted evidence: committed-SHA verification at
  `2907cf452fac4c7811b35d6ee0c25eb0ddc6cc11`; focused compatibility and
  adjacent suites, inherited consumer suites, full blocking pytest with the
  lifecycle-declared active-Red exclusion, spec/lifecycle/coverage and
  repository sanity checks passed as recorded in the linked Phase 3 review.
- The intentional main-source structural Red remains open. This acceptance
  does not accept or implement the main `unitarity_check.py` decomposition.
- Next gate: separate approval to commit this acceptance/status record and
  rerun all blocking checks at the resulting actual SHA. No push, PR, or merge
  is authorized.

## Acceptance-record committed-SHA verification accepted (2026-11-02)

- Approval: Adjudicator accepted the committed-SHA verification result on
  2026-11-02. Tested commit: `3ab970ad84c5d4637f7734c114ccf2afaaec4735`,
  clean worktree, macOS arm64, CPython 3.12.6, pytest 9.0.3.
- Results: root blocking pytest 3,589 passed; inherited LISS-0591/0593
  consumers 319 passed; focused LISS-0594 plus adjacent tests 29 passed with
  the intended main-source structural Red; spec verification 161/161; CI
  repository sanity and template-copy/configure smoke passed. The focused Red
  matches the already accepted Phase 1 target; no new comparable-environment
  failure was observed.
- This acceptance is limited to the GU compatibility supplement and its
  acceptance record. Main `unitarity_check.py` decomposition remains
  unimplemented and its Phase 1 structural Red remains active.
- Next gate: separate approval to commit this verification-result/status
  record and rerun the blocking suites at the resulting actual SHA. No push,
  PR, or merge is authorized.

## Verification-result record committed-SHA acceptance (2026-11-04)

- Approval: Adjudicator accepted the verification result on 2026-11-04.
- Tested commit: `d152534d5bcd59100d0026aecff1d899bea60434`, clean worktree;
  macOS arm64, CPython 3.12.6, pytest 9.0.3.
- Results accepted: root blocking pytest 3,589 passed; inherited LISS-0591/
  0593 consumer tests 319 passed; focused LISS-0594 plus adjacent tests 29
  passed with the intended main-source structural Red; spec verification
  161/161; CI repository sanity, required documents/ADRs and
  template-copy/configure smoke passed.
- Scope remains GU01–GU09 and its verification record. Main
  `unitarity_check.py` decomposition remains unimplemented; its Phase 1
  structural Red remains active. No comparable-environment new failure was
  observed.
- Next gate: separate approval to commit this acceptance/status record and
  rerun blocking checks at the resulting actual SHA. No push, PR, or merge is
  authorized.

## Active-Red renewal acceptance-record verification accepted (2026-11-18)

- Approval: Adjudicator accepted the verification result on 2026-11-18.
- Tested commit: `75d24931324be40a571d70f7d48978cbb65e28fd`, clean worktree;
  macOS arm64, CPython 3.12.6, pytest 9.0.3.
- Results accepted: Active-Red lifecycle passed with `review_by =
  2026-11-20`; root blocking pytest 3,589 passed; inherited LISS-0591/0593
  consumers 319 passed; focused LISS-0594 plus adjacent tests 29 passed with
  the known main-source structural Red; spec verification 161/161; document
  lifecycle, coverage, baseline, execution-batch, required-file/ADR and
  template-copy checks passed.
- No new comparable-environment failure was observed. Main
  `unitarity_check.py` decomposition remains unimplemented and its Phase 1
  structural Red remains active.
- Next gate: separate approval to commit this acceptance/status record and
  rerun blocking checks at the resulting actual SHA. No push, PR, or merge is
  authorized.

## Active-Red renewal verification acceptance (2026-11-18)

- Approval: Adjudicator accepted the verification result on 2026-11-18.
- Tested commit: `8973aa4874c8a7617cec4c71e22331a6c5030c7f`, clean worktree;
  macOS arm64, CPython 3.12.6, pytest 9.0.3.
- Results accepted: Active-Red lifecycle passed with `review_by =
  2026-11-20`; root blocking pytest 3,589 passed; inherited LISS-0591/0593
  consumers 319 passed; focused LISS-0594 plus adjacent tests 29 passed with
  the known main-source structural Red; spec verification 161/161; document
  lifecycle, coverage, baseline, execution-batch, required-file/ADR and
  template-copy checks passed.
- The main `unitarity_check.py` decomposition remains unimplemented and its
  Phase 1 structural Red remains active. No new comparable-environment
  failure was observed.
- Next gate: separate approval to commit this acceptance/status record and
  rerun blocking checks at the resulting actual SHA. No push, PR, or merge is
  authorized.

## Acceptance-record committed-SHA verification accepted (2026-11-17)

- Approval: Adjudicator accepted the verification result on 2026-11-17.
- Tested commit: `fa1cc39cf63a44e7a5f32bcc0d394773f1dce5e2`, clean worktree;
  macOS arm64, CPython 3.12.6, pytest 9.0.3.
- Results accepted: Active-Red lifecycle passed with `review_by =
  2026-11-20`; root blocking pytest 3,589 passed; inherited LISS-0591/0593
  consumers 319 passed; focused LISS-0594 plus adjacent tests 29 passed with
  the known main-source structural Red; spec verification 161/161; document
  lifecycle, coverage, baseline, execution-batch, required-file/ADR and
  template-copy checks passed.
- No new comparable-environment failure was observed. The main
  `unitarity_check.py` decomposition remains unimplemented and its Phase 1
  structural Red remains active.
- Next gate: separate approval to commit this acceptance/status record and
  rerun blocking checks at the resulting actual SHA. No push, PR, or merge is
  authorized.

## Active-Red renewal verification-record SHA accepted (2026-11-17)

- Approval: Adjudicator accepted the committed-SHA verification result on
  2026-11-17.
- Tested commit: `49bdc21faee237a0ec4e592fed38941470e03a08`, clean worktree;
  macOS arm64, CPython 3.12.6, pytest 9.0.3.
- Results accepted: Active-Red lifecycle passed with `review_by =
  2026-11-20`; root blocking pytest 3,589 passed; inherited LISS-0591/0593
  consumers 319 passed; focused LISS-0594 plus adjacent tests 29 passed with
  the known main-source structural Red; spec verification 161/161; document
  lifecycle, coverage, baseline, execution-batch, required-file/ADR and
  template-copy checks passed.
- No new comparable-environment failures were observed. Main
  `unitarity_check.py` decomposition remains unimplemented, and its Phase 1
  structural Red remains active.
- Next gate: separate approval to commit this result-acceptance record and
  rerun blocking checks at the resulting actual SHA. No push, PR, or merge is
  authorized.

## Active-Red renewal acceptance-record verification accepted (2026-11-17)

- Approval: Adjudicator accepted the final verification result on 2026-11-17.
- Tested commit: `8a364e95a46d07b7913a1b16b18cc2ebd5aa0170`, clean worktree;
  macOS arm64, CPython 3.12.6, pytest 9.0.3.
- Results accepted: Active-Red lifecycle passed with `review_by =
  2026-11-20`; root blocking pytest 3,589 passed; inherited LISS-0591/0593
  consumers 319 passed; focused LISS-0594 plus adjacent tests 29 passed with
  the known main-source structural Red; spec verification 161/161; document
  lifecycle, coverage, baseline, execution-batch, required-file/ADR and
  template-copy checks passed.
- No new comparable-environment failure was observed. The main
  `unitarity_check.py` decomposition remains unimplemented and its Phase 1
  structural Red remains active.
- Next gate: separate approval to commit this acceptance/status record and
  rerun blocking checks at the resulting actual SHA. No push, PR, or merge is
  authorized.

## Active-Red renewal acceptance-record SHA verification accepted (2026-11-17)

- Approval: Adjudicator accepted the committed-SHA verification result on
  2026-11-17.
- Tested commit: `b93361dcb7d94f5dfcde6332ac919744e41ae39b`, clean worktree;
  macOS arm64, CPython 3.12.6, pytest 9.0.3.
- Results accepted: Active-Red lifecycle passed with the renewed
  `review_by = 2026-11-20`; root blocking pytest 3,589 passed; inherited
  LISS-0591/0593 consumers 319 passed; focused LISS-0594 plus adjacent tests
  29 passed with the known main-source structural Red; spec verification
  161/161; document lifecycle, coverage, baseline, execution-batch,
  required-file/ADR and template-copy checks passed.
- Scope is still the GU compatibility supplement and its records. Main
  `unitarity_check.py` decomposition remains unimplemented; its Phase 1
  structural Red remains active. No new comparable-environment failure was
  observed.
- Next gate: separate approval to commit this acceptance/status record and
  rerun blocking checks at the resulting actual SHA. No push, PR, or merge is
  authorized.

## Verification-result acceptance-record SHA accepted (2026-11-04)

- Approval: Adjudicator accepted the latest verification result on 2026-11-04.
- Tested commit: `eb4d23030d78ab354da9d307ad0514d6770ad8fd`, clean worktree;
  macOS arm64, CPython 3.12.6, pytest 9.0.3.
- Results accepted: root blocking pytest 3,589 passed; inherited LISS-0591/
  0593 consumers 319 passed; focused LISS-0594 plus adjacent tests 29 passed
  with the known main-source structural Red; spec verification 161/161; CI
  lifecycle, coverage, baseline, required files/ADRs and template-copy smoke
  passed. The known Red matches the accepted Phase 1 target; no new failure
  appeared.
- Main `unitarity_check.py` decomposition remains unimplemented and its
  structural Red remains active. This acceptance covers only the GU
  compatibility supplement and its records.
- Next gate: separate approval to commit this acceptance record and rerun
  blocking checks at the resulting actual SHA. No push, PR, or merge is
  authorized.

## Active-Red renewal committed-SHA verification accepted (2026-11-16)

- Approval: Adjudicator accepted the verification result on 2026-11-16.
- Tested commit: `5f1111f4181ab83ddecd871f6d9f032aa1cc0e30`, clean worktree;
  macOS arm64, CPython 3.12.6, pytest 9.0.3.
- Results accepted: Active-Red lifecycle passed with one entry and the renewed
  `review_by` of 2026-11-20; root blocking pytest 3,589 passed; inherited
  LISS-0591/0593 consumers 319 passed; focused LISS-0594 plus adjacent tests
  29 passed with the known main-source structural Red; spec verification
  161/161; document lifecycle, coverage, baseline, execution-batch,
  required-file/ADR and template-copy checks passed.
- No new comparable-environment failures were observed. The main
  `unitarity_check.py` decomposition remains unimplemented and its Phase 1
  structural Red remains active.
- Next gate: separate approval to commit this acceptance/status record and
  rerun blocking checks at the resulting actual SHA. No push, PR, or merge is
  authorized.
