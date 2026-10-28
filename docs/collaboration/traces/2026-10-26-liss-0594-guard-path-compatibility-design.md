# 2026-10-26 — LISS-0594 guard path compatibility supplement design

## Request

- Date: 2026-10-26 Asia/Tokyo
- User request: approved Scope / Phase 0 design-start for the compatibility
  supplement blocking the LISS-0594 Red cohort.
- Current state: GU compatibility supplement Phase 3 review and dirty-tree
  final verification passed locally on 2026-10-28; immutable commit-SHA
  verification remains pending. The main decomposition is still Phase 1 Red.
- Canonical issue: [LISS-0594](../../issues/LISS-0594-unitarity-check-family-separation.md)
- Canonical specification: [GU01–GU09 acceptance](../../specs/unitarity-check-family-separation.md#guard-compatibility-supplement--phase-0-accepted-gu01gu09)
- Parent: [WP-0175](../../work-plans/WP-0175-source-responsibility-inventory.md)
- Planning record: AIP-0594-002, proposed in the issue.

## Context ledger

- Included: prior LISS-0594 Phase 1 results; exact failure nodes P10/R06/F09/G07;
  LISS-0591 historical path reader; LISS-0593 `new_test_paths`, carrier
  projection, copied-root setup, semantic set assertions and fixed 26-path
  check; lifecycle and verification requirements.
- Omitted: production code; unrelated historical guard behavior; all
  implementation and test execution; regeneration or weakening of frozen
  hashes, path sets, evidence, or assertions.
- Assumptions: the only current follow-on artifact is
  `tests/test_liss_0594_unitarity_family_red.py` (SHA-256
  `d85d28f37a30317a959eced12d16f348e45c4093ddd92033fca4edd282db408f`).
  This is an exact path dependency and must not be conflated with the original
  26-path LISS-0591/0593 cohort.
- Open decisions: Adjudicator review/acceptance of the exact Phase 1 Red cohort
  and later separate implementation approval. Any newly discovered path
  consumer or required baseline/evidence change invalidates this bounded
  proposal.
- Route: Codex host; local deterministic source/test-graph inspection.
  Runtime review routing is `same_context`; implementation isolation is
  irrelevant now and no implementation approval exists.
- Process lessons applied: preserve exact raw/Git history evidence;
  construct independently evidenced copied pre/post roots; require the
  follow-on file to exist and include a missing-file negative; keep exact
  active-Red phase metadata synchronized. Recursive AST-walker lesson is out
  of scope for this path-only issue.

## Attempt 1

- Environment: local repository, branch
  `codex/liss-0594-unitarity-family-design`, HEAD
  `93a2548ae168a70a3c3340bf79533de95828dc39`; current LISS-0594 changes remain
  uncommitted and were preserved.
- Model/reasoning as displayed: N/A; not exposed in task context.
- Scope: trace exact path rejection and copied guard composition, then propose
  a bounded supplement with explicit negatives and phase gates.
- Result: proposed GU01–GU09; no tests or guards changed and no tests run.
- Approval: user approved the compatibility supplement's Scope / Phase 0
  design-start on 2026-10-26. This is not acceptance of GU01–GU09, Phase 1,
  or Phase 2 authorization.
- Decision: Adjudicator accepted GU01–GU09 on 2026-10-26. This is Phase 0
  acceptance only; Phase 1 execution remains separately gated.
- Token use: N/A; unavailable to the agent.

## Verification and next safe action

- Checks: exact source for the six failing consumer paths and
  `carrier_after()`/copied-root construction reviewed; `git diff --check`,
  active-Red lifecycle and document lifecycle checks passed.
- Result: Phase 0 acceptance recorded. No test/guard changes or runtime tests.
- Changed files: LISS-0594 Issue/spec/WP status and this trace only.
- Next: Adjudicator reviews/accepts the supplementary Red tests. No
  guard/support edits before that review and separate implementation approval.

## Attempt 2 — supplementary Phase 1 Red

- Approval: explicit Phase 1 Red execution approval received 2026-10-26 for
  accepted GU01–GU09; implementation permission remains no.
- Environment: branch `codex/liss-0594-unitarity-family-design`, base HEAD
  `93a2548ae168a70a3c3340bf79533de95828dc39`, dirty tree; Darwin arm64,
  CPython 3.12.6, pytest 9.0.3.
- Test artifact SHA-256: `tests/test_liss_0594_unitarity_family_red.py`
  `1d49a7155e269e7e13e24299e1c5c249aa036d677b85f17c12486928bd1ae8f8`;
  composition test SHA-256
  `0feed57bf3d59c1770c4b8c8e97738463afa20def12b1ab4b02bd370a1c14d9f`.
- Scope: add exact singleton membership, missing-artifact and historic-return
  contracts; add the path separately to copied-root setup and preserve the
  26-path semantic cohort. No support/guard, baseline, production, fixture
  evidence, or exclusion changed.
- Results: focused LISS-0594 plus adjacent 0411/0436/0376: 22 passed / 4 Red
  (one pre-existing structural Red and three compatibility Reds). Focused
  supplement selection: 9 intended failures. Full LISS-0593 composition module:
  208 passed / 32 failures, each at the undeclared follow-on inventory boundary.
  The six inherited P10/R06/F09/G07 nodes were rerun and remain the same six
  path-boundary failures; no pre-addition root baseline was captured.
- Review: same-context (weaker than separate-context) re-read found a
  synthetic-vs-real copied-root Git listing risk. The test helper now retains
  the original subprocess function before monkeypatching and asserts physical
  artifact presence and source shape separately. The fixed LISS-0593 prefix
  hash test passes; original node IDs/assertions remain, with only exact
  follow-on setup/expectations added.
- Deterministic checks: `git diff --check`, active-Red lifecycle and document
  lifecycle passed. Full blocking suite not run in Phase 1.
- Next: Adjudicator Phase 1 Red review/acceptance. Phase 2 requires separate
  implementation approval.

## Attempt 3 — test-setup correction and Phase 1 Red re-review

- Approval: the user explicitly authorized correcting and re-reviewing the
  Phase 1 Red cohort after the first all-blocking run found four setup failures.
- Route: `same_context` per `runtime-routing.toml`; this review is weaker than
  separate-context review. The reviewer re-read the accepted specification,
  changed tests and deterministic output from disk.
- Corrections: keep GU02/GU05 coverage in the already declared
  `tests/test_liss_0594_unitarity_family_red.py`; keep LISS-0593 test changes to
  exact follow-on inventory setup and copied-root consumer wiring. Preserve the
  B08 synthetic inventory test through one exact follow-on path addition and
  an explicit raw-byte projection from its prior Git version. Scope the GU07
  synthetic inventory monkeypatch so P10/R06 then invoke real copied-root Git
  inventory. Preserve GU08 positive/negative fault sequencing while including
  the singleton in the injected exact inventory.
- Findings/dispositions: B08 omitted the authorized singleton from its mock;
  applied the exact singleton expectation. GU08's fault setup omitted that
  singleton and failed before the intended negative assertion; applied the
  corrected exact inventory. GU07 leaked a shared `subprocess.check_output`
  mock into production inventory; bounded the mock and restored the actual
  runner before consumer calls. Supplement tests were placed in the LISS-0594
  module as GU08 requires. No semantic test assertion, frozen evidence, or
  historical path set was weakened or regenerated.
- Verification on dirty HEAD `93a2548ae168a70a3c3340bf79533de95828dc39`,
  Darwin arm64, CPython 3.12.6, pytest 9.0.3:
  - Focused LISS-0594 plus LISS-0411/0436/0376: 25 passed / 1 expected Red at
    `test_phase1_structure_moves_recursive_walker_out_of_public_module`.
  - LISS-0591 guard migration plus LISS-0593 guard composition: 319 passed.
  - CI root pytest with active-Red ignores: 3,589 passed / 0 failed.
  - Spec verification: 161/161 PASS; test lifecycle, document lifecycle and
    `git diff --check` PASS.
- Review result: Phase 1 Red re-review passed. Adjudicator re-acceptance of the
  corrected cohort remains required. Prior implementation authorization was
  exercised for only the exact support-path singleton; no further Green work,
  commit or remote delivery was authorized here.

## Attempt 4 — Phase 1 re-acceptance recorded

- Approval: Adjudicator explicitly re-accepted the corrected LISS-0594 Phase 1
  Red cohort on 2026-10-27.
- The exact singleton support-path Phase 2 implementation was already
  authorized and locally verified. No additional source or test changes were
  made after the recorded CI root suite (3,589 passed), 319 inherited guard
  tests, 161/161 spec verification, and 25 passed / 1 expected structural Red
  focused result.
- Scope boundary: GU compatibility supplement only. The main
  `unitarity_check.py` decomposition remains unimplemented and its structural
  Red remains active.
- Current next gate: Adjudicator Phase 3 Refactor/review approval for the GU
  compatibility supplement. All evidence remains provisional on dirty HEAD
  `93a2548ae168a70a3c3340bf79533de95828dc39`; final-SHA verification is still
  required after commit.

## Attempt 5 — Phase 3 review under non-CI venv

- Approval: Adjudicator explicitly approved GU compatibility supplement
  Phase 3 Refactor/review on 2026-10-28.
- Route: same-context per `runtime-routing.toml`, weaker than separate-context.
  Canonical spec, Issue, source/tests and deterministic evidence were reread
  from disk.
- Refactor: corrected `new_test_paths()` diagnostic wording so the exact
  follow-on artifact is not mislabeled as only a LISS-0593 artifact. No
  assertion, path set or historic evidence changed.
- Environment: macOS arm64, venv CPython 3.14.8 / pytest 9.1.1. Focused run:
  29 passed / 1 intended main-source structural Red. Inherited LISS-0591/0593
  run: 49 failures in AST-baseline comparisons, 270 passed. The active
  interpreter differed from the repository CI Python 3.12 configuration.
- Disposition: do not treat these failures as product regressions before
  comparing under the declared CI-compatible interpreter. One representative
  failure was selected for that comparison.

## Attempt 6 — CI-compatible review and verification

- Environment: macOS arm64, CPython 3.12.6 / pytest 9.0.3. The representative
  AST-baseline node passed alone; the inherited LISS-0591/0593 suites passed
  319/319. Focused LISS-0594 with LISS-0411/0436/0376 passed 29 cases with one
  intended main-source structural Red. Root blocking pytest, using the exact
  lifecycle-declared LISS-0594 exclusion, passed 3,589/3,589. Spec verification
  passed 161/161.
- Additional checks: active-Red and document lifecycle, coverage ledger,
  execution-batch record validation (20 records), behavior-preservation
  baseline (3 cases), changed Python compilation, and `git diff --check` passed.
- Repository template-copy smoke refused the dirty task checkout because the
  new spec is untracked under a distributed source path. Re-ran that smoke in
  a temporary clean clone at the same committed HEAD; it passed. This does not
  include the task's uncommitted LISS-0594 records.
- Review disposition: GU compatibility supplement Phase 3 review passed
  locally. The initial 3.14 failures are environment-incompatible and do not
  reproduce under Python 3.12.6. Main `unitarity_check.py` remains unmodified;
  its expected structural Red is not part of this supplement.
- Structure: production source bodies changed: zero. The 344-line single
  LISS-0594 test module is retained to satisfy GU08's exact single-path
  contract. No `[source_structure]` budget is configured; `review-change.py`
  reports dirty-tree metrics as unknown. Conditional large-change routing is
  not enabled; same-context review remains the effective route. Manual
  worktree accounting found 1,363 inserted/deleted lines overall and 392
  added Python lines, all test/support code; production-source additions are
  zero. The clean committed revision is still required for the tool's
  implementation-size metrics.
- Evidence state: all runs used dirty HEAD
  `93a2548ae168a70a3c3340bf79533de95828dc39`; final-SHA verification remains
  pending. Review summary:
  [2026-10-28 Phase 3 review](../reviews/2026-10-28-liss-0594-phase3-review.md).
- At the Phase 3 review checkpoint, next was separate Adjudicator
  final-verification approval. It was received on 2026-10-28; Phase 3 review
  approval alone authorized no commit, push, PR, or merge.

## Attempt 7 — dirty-tree final verification

- Approval: Adjudicator explicitly approved final verification on 2026-10-28.
- State: HEAD `93a2548ae168a70a3c3340bf79533de95828dc39`, dirty worktree;
  macOS arm64, CPython 3.12.6, pytest 9.0.3. Production and test source files
  were unchanged since Phase 3 verification; only review/status records changed.
- Results: focused LISS-0594 plus LISS-0411/0436/0376: 29 passed / 1 expected
  structural Red; inherited LISS-0591/0593: 319 passed; root blocking pytest
  with the declared active-Red exclusion: 3,589 passed / 0 failed; spec
  verification: 161/161. Lifecycle, document, coverage, execution-batch (20),
  refactor baseline (3), Python compilation and diff checks passed.
- Disposition: GU compatibility supplement passed dirty-tree local final
  verification. No new comparable-environment failures. The main unitarity
  split remains unimplemented and its structural Red remains active.
- Limitation/next: no commit was authorized or made, so final immutable-SHA
  verification remains pending. Next requires separate local-commit/actual-SHA
  approval and then a fresh all-blocking rerun. No remote delivery approval.
