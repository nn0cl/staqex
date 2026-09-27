# Specification: Evaluator legacy `when` binding extraction

## Status

Accepted — Adjudicator approved `LISS-0580 Phase 0 acceptance` on 2026-09-27.
Architecture boundary: ADR 0227, accepted 2026-09-27.

## Purpose

Move the existing legacy AST `WhenExpr` binding implementation out of the
large Evaluator facade while preserving all runtime behavior and the existing
single-owner state boundary.

## Scope

In scope:

- the implementation currently in `Evaluator._bind_when`;
- its `_ctrl_masses` and `_pat_match` helpers, if Phase 0 consumer inventory
  confirms they have no independent facade consumers;
- a successor module at
  `compiler/staqex/runtime/evaluation/legacy_control_binding.py`;
- the existing private binder callback and compatibility installation;
- structural and runtime evidence for canonical execution's explicit legacy
  fallback.

Out of scope:

- changing `WhenExpr` or `Mix` syntax or meaning;
- changing canonical Runtime Plan classification or eligibility;
- retiring or narrowing `_run_legacy_ast_body` fallback;
- changing branch selection, probabilities, amplitudes, phases, coalescing,
  errors, or measurement timing;
- nested-control support changes, dynamic-QPU behavior, QASM/QPU/provider
  behavior, parser/typechecker changes, or unrelated Evaluator extraction.

## Normative behavior-preservation requirements

1. Canonical `control_mixture` execution continues to use the dedicated
   deferred State/Measure executor when the main body satisfies the existing
   eligibility predicate.
2. A canonical `control_mixture` plan whose main body does not satisfy that
   predicate continues to enter the existing legacy AST body. Its `WhenExpr`
   binding continues through the `_bind_when` compatibility callback to the
   extracted implementation.
3. Legacy control resolution preserves all current sources and precedence:
   per-world assignments, evaluator objects, evaluator scalars, supported
   literals, and general value evaluation.
4. Branch matching preserves exact matching, numeric cross-type equality, and
   enum variant matching. The first matching non-else arm wins; otherwise the
   first else arm is used. No matching arm produces no output world.
5. Each control mass at or below `EPS` is skipped. Other masses scale input
   amplitudes by the existing complex square-root rule. `Coin`, `KetLit`, and
   ordinary value arms retain their current behavior.
6. Output worlds preserve the source world's coordinate-phase metadata, apply
   the existing probability pruning rule for ket support, and are coalesced
   exactly as before. Vacuum input and empty output remain empty.
7. The extraction does not normalize the complete output or introduce an
   early terminal measurement.
8. The successor must not import or instantiate `Evaluator`, retain mutable
   evaluator state, or create copied long-lived maps. Mutable state remains
   owned by the live Evaluator instance.
9. `_bind_when` remains an explicit compatibility entrypoint until a distinct
   approved consumer-retirement decision proves it unnecessary.

## Acceptance scenarios

### Scenario A: canonical eligible control mixture

Given a compiled single-level control-mixture unit that satisfies the existing
deferred State/Measure eligibility predicate, when it runs through
`run_canonical_unit`, then the canonical control-mixture executor is used and
the legacy AST body is not entered. Existing LISS-0495 evidence is reused;
do not duplicate it without a test gap.

### Scenario B: canonical fallback reaches the extracted binder

Given a canonical control-mixture unit whose main body is not eligible for the
deferred State/Measure path, when it runs through `run_canonical_unit`, then
the established legacy AST path is selected and the installed `_bind_when`
callback resolves to the successor implementation. Result values and
diagnostics match the pre-extraction characterization.

### Scenario C: direct fallback behavior is conserved

Given existing supported control forms (including Coin control, numeric and
enum patterns, else selection, ket arms, ordinary value arms, and zero/empty
branches), when the legacy binder executes, then outcomes, amplitudes,
coordinate phases, coalescing, and errors match the accepted pre-extraction
behavior.

### Scenario D: facade and state ownership are explicit

Given the extracted runtime module, when its structure and live compatibility
installation are inspected, then the implementation body is owned by the
successor, the facade contains no duplicate algorithm, the setup installs the
intended callback, and the live hook is identical to the successor function.

## Consumer and test inventory for Phase 1 planning

- Production dispatch: `runtime/evaluation/binding.py` calls
  `context._bind_when` for `WhenExpr`.
- Canonical route: `runtime/evaluation/orchestration.py` dispatches
  `control_mixture`; its executor uses the deferred executor only when
  `_main_deferred_eligible` passes and otherwise calls
  `_run_legacy_ast_body`.
- Compatibility: `runtime/evaluation/compatibility.py` installs extracted
  family methods; the exact mapping/setup/runtime identity must be asserted if
  this pattern is used.
- Context contract: `runtime/evaluation/context.py` declares `_bind_when`.
- Existing evidence to inspect and reuse: LISS-0495 canonical control tests,
  `tests/test_when_ket_prepare_arms_red.py`,
  `tests/test_liss_0225_when_on_enum_red.py`,
  `tests/test_liss_0375_nested_when_tensor_dispatch_red.py`, and existing
  nested-control rejection/diagnostic tests.
- Phase 1 must search for private imports, monkeypatches, direct helper
  references, and lifecycle-managed tests before removing any body. Search
  results alone do not prove runtime identity or reachability.

Phase 1 test mapping: Scenario A reuses LISS-0495's canonical eligible-path
test. Scenario B reuses the enum-plus-`Inspect` source shape in
`tests/test_liss_0225_when_on_enum_red.py`, which is outside deferred
eligibility; the new LISS-0580 behavior characterization spies on
`execute_control_mixture_plan`, records that its eligibility checks are false,
asserts the executor itself calls `_run_legacy_ast_body`, and confirms
`_bind_when` is reached through the public host path. Scenario C's existing
supported forms are covered by LISS-0225 and the ket-arm suite; Scenario D is
covered by three LISS-0580 structural contracts for successor ownership,
facade-body removal, and compatibility setup/live identity.

## Phase boundaries

- Phase 0: confirm this contract, actual fallback fixture, complete consumer
  inventory, callback shape, allowed paths, and clause-to-test mapping. No
  test or production code changes.
- Phase 1 Red: add only reviewed structural gaps and fallback-path behavioral
  characterization. Report structural failures separately from passing
  behavior characterization.
- Phase 2 Green: move the accepted implementation with minimum changes; do
  not modify reviewed assertions or expand semantics.
- Phase 3 Refactor: improve readability only; confirm the facade body is
  removed and rerun actual consumers and blocking suites on the final commit.

## Verification requirements

For any split, inventory actual consumers including private imports; assert
successor ownership and facade-body absence; test exact compatibility
installer mapping, setup invocation, and runtime hook identity; run consumer
smoke and adjacent regression; report source implementation-body sizes and
structure-budget disposition. No runtime test was executed as part of this
specification acceptance.

## Phase 0 acceptance result

- Approval: `LISS-0580 Phase 0 acceptance`, Adjudicator, 2026-09-27.
- Accepted: retain-and-extract boundary; current behavior and canonical
  fallback are preserved; the specification is authoritative for the bounded
  structural work.
- Phase 0 did not authorize: Phase 1 Red, Phase 2 implementation, or fallback
  retirement. Phase 1 Red was separately approved afterward.
- Next gate: separate Phase 2 Green/Implementation approval. The corrected
  Phase 1 Red test review was accepted by the Adjudicator on 2026-09-27.

## Phase 1 Red record

- Approval: `LISS-0580 Phase 1 Red 承認`, Adjudicator, 2026-09-27.
- Added `tests/test_liss_0580_legacy_when_binding_red.py` and three active-Red
  lifecycle entries. Production code and acceptance assertions were not
  changed.
- Expected structural failures: successor module/algorithm ownership;
  duplicate `_bind_when` implementation still on Evaluator; dedicated
  compatibility installer and live hook identity not yet present.
- Passing characterization: canonical enum `Mix` with `Inspect` dispatches a
  `control_mixture` plan; the executor sees ineligible deferred-path checks,
  calls the legacy AST body, and reaches `_bind_when`.
- Focused result: **3 failed, 1 passed**, no collection errors. The initial
  invalid fixture reused the same state through `Inspect` and `Measure`; it was
  corrected to the established `expect` then `Inspect` shape from LISS-0225,
  and rerun.
- Existing consumers: LISS-0495, LISS-0225, LISS-0138 ket-arm, and LISS-0375
  nested-control suites: **11 passed**. Combined run: **3 expected structural
  failures, 12 passed**.
- Tested base SHA: `98d71df0f553bc3c0b8173d7aeb2310fa40c7184`; working tree dirty
  with design docs and the Phase 1 test/manifest. Environment: macOS 27.0.0
  arm64, Python 3.14.6, repository `.venv`.
- Lifecycle check, `py_compile`, and `git diff --check` passed. Ruff was not
  available at `.venv/bin/ruff`; no alternative lint command was run.
- Next gate at Red completion: Phase 1 Red test review; no implementation was
  authorized at that point.

### Phase 1 Red review correction

- Same-context review initially found that the passing characterization did
  not prove canonical `control_mixture` fallback selection. The test now
  observes the dispatched plan family, the executor's ineligible checks, and
  the legacy-body call made during that executor invocation.
- Re-review verification: focused suite **3 expected failures, 1 pass**;
  adjacent consumer run **3 expected failures, 12 passes**; lifecycle,
  `py_compile`, and `git diff --check` pass.
- Review Summary: `docs/collaboration/reviews/2026-09-27-liss-0580-phase1-red-review.md`.
- Same-context reviewer disposition: no remaining test-contract blockers;
  at the time, Adjudicator approval remained required and Phase 2 had not yet
  been authorized. Separate Phase 2 approval was subsequently granted below.
- Adjudicator accepted `LISS-0580 Phase 1 Red テストレビュー承認` on
  2026-09-27. Phase 2 Green/Implementation remains a separate approval gate.

## Phase 2 Green result

- Approval: `LISS-0580 Phase 2 Green / Implementation 承認`, Adjudicator,
  2026-09-27.
- Extracted `bind_when`, control-mass resolution, and pattern matching into
  `runtime/evaluation/legacy_control_binding.py`. The live Evaluator remains
  the sole state owner; compatibility wiring installs the exact successor
  callable as `_bind_when`.
- Reviewed Phase 1 tests were unchanged during implementation. The three
  structural contracts and canonical fallback characterization pass.
- Focused plus adjacent consumers: **15 passed**. All 2,275 collected pytest
  cases passed across three runs: the initial full run passed 863 before it
  was interrupted in a long benchmark test; that test passed alone, and the
  remaining 1,411 tests passed in a continuation run. No test failures were
  observed. Lifecycle, syntax, coverage-ledger consistency, and whitespace
  checks passed.
- Evidence was run against base SHA
  `98d71df0f553bc3c0b8173d7aeb2310fa40c7184` with a dirty working tree;
  macOS 27.0.0 arm64, Python 3.14.6, pytest 9.1.1. Ruff is unavailable in
  `.venv`.
- Source ownership: the Evaluator definitions are absent; the successor is
  140 physical lines and `evaluator.py` is 1,305 lines. No quantitative
  `[source_structure]` budget is configured; this split is bounded to the
  legacy `when` family and does not claim broader Evaluator decomposition.
- Phase 2 implementation is complete. Phase 3 Refactor was separately
  approved on 2026-09-27; execute only that bounded phase, then obtain its
  review and final review.

## Phase 3 Refactor result

- Approval: `LISS-0580 Phase 3 Refactor 承認`, Adjudicator, 2026-09-27.
- Reviewer-empathy inspection found the extracted implementation already
  separated by responsibility; additional helper layers would add navigation
  without reducing complexity. Added one concise comment explaining the
  non-else-before-else selection invariant. No behavior, tests, or assertions
  changed.
- Consumer inventory was repeated: production dispatch, protocol callback,
  compatibility installer/live hook, and the structural/runtime tests remain
  the only discovered Python consumers. No independent private helper imports
  or monkeypatch consumers were found beyond the approved tests.
- Focused/adjacent consumers: **15 passed**. CI blocking suite
  `.venv/bin/python -m pytest tests/ -q`: **2,275 passed in 314.44s**.
  Lifecycle, coverage-ledger consistency, and `git diff --check` passed.
- Evidence is provisional on base SHA
  `98d71df0f553bc3c0b8173d7aeb2310fa40c7184` with dirty/uncommitted worktree;
  macOS 27.0.0 arm64, Python 3.14.6, pytest 9.1.1. A final committed-SHA
  rerun remains required. Ruff is unavailable in `.venv`.
- Structure: `legacy_control_binding.py` 141 lines, compatibility facade
  289 lines, Evaluator 1,305 lines. No quantitative `[source_structure]`
  budget or enabled large-change review override is configured. The review
  metrics tool cannot represent the current untracked/dirty snapshot; observed
  workspace inventory is 13 changed files (4 tracked-modified, 9 untracked).
- Same-context reviewer disposition: no blocking readability or compatibility
  finding; this is weaker than separate-context review. Final Adjudicator
  approval and tested-final-commit evidence are recorded below.
- Final review approval: `LISS-0580 Phase 3 最終レビュー 承認`, Adjudicator,
  2026-09-27. The approved final review required a commit and full
  blocking-suite rerun; completion evidence follows.
- Final commit verification: `f50f116b7db287ad942d99bc9f4f38e5cb27cfb8`, clean
  worktree; focused/adjacent **15 passed**, full blocking suite **2,275 passed
  in 315.85s**, lifecycle and coverage-ledger checks passed. Environment:
  macOS 27.0.0 arm64, Python 3.14.6, pytest 9.1.1. Ruff unavailable.
