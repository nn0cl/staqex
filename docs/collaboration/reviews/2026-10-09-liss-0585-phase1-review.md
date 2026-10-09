# LISS-0585 Phase 1 Red review — passed after R1/R2 correction

## Current re-review — 2026-10-09

- Current phase: Phase1 Red, agent re-review passed; human test acceptance approved
- Requested approval: next, separate Phase2 Green / implementation approval
- Approved scope: T01–T09 test-only extraction/guard contracts; human `はい。`
  authorizes the immediately preceding bounded R1/R2 correction and re-review
- Implementation allowed: no; Green remains a separate approval
- Post-review required: yes; human test acceptance, Green, Refactor and final
  verification/delivery remain distinct gates; no execution batch
- Isolation: same_context, weaker than separate_context; settings/model unchanged,
  no enabled large-change override. Dirty committed-diff metrics remain unknown.

Corrective change is limited to the new migration test file: historical shape
is reconstructed and checked before old-body mutation; the fixture additionally
copies an existing successor without altering the historical readonly manifest.
The fixture keeps pytest's `guarded` injection name; its Python function is now
`guarded_tree`. Added two pre/post-extraction fixture regression cases.
Assertions rejecting mutated bodies/missing successors and original fixture
hashes remain intact. No production or guard implementation changed in this
correction. Guard suite now202physical lines; other source sizes unchanged.

### Findings disposition

- R1: closed with evidence. Old-body mutation first restores evaluator and
  compatibility to the authorized original Tensor shape through immutable
  projections, passes the real guard, then changes the old algorithm and proves
  rejection. New pre/post-root regression invokes this exact test in both shapes.
- R2: closed with evidence. Shared dependency-copy setup includes successor bytes
  only when present in the actual root; pre/post-root regression invokes the
  real fixture and current positive, verifies successor presence matches source.
  Existing missing-successor mutation still rejects removal.
- No remaining blocking finding in the reviewed Phase1 correction. Test suite
  remains intentionally Red for four unimplemented production-ownership nodes;
  no waiver of future all-blocking verification or dynamic-consumer limitations.

Reviewer role re-read corrected test file and accepted T09 preservation clauses
from disk, then independently reran new guard plus inherited0583/0584 suites:
80passed in2.23s, exit0, failures/errors/skips/exclusions0. Full scoped12-suite
execution after corrections:168pass/4same structural Red in3.50s,172collected,
exit1, errors/skips/exclusions0. New63 cases comprise29characterization +30guard
+4structural nodes; previous109neighbors still pass with no changed failures.
Baseline/dirty HEAD a349a5b720c59f3a0e288c4751dd012c25514843, macOS27.0.1 arm64,
Python3.12.6 pytest9.0.3, cwd /Users/nn0cl/Documents/git/qpex.
git diff --check and lifecycle entries0 pass. Root/spec/all-sanity not_run.
No final-SHA or whole-repository Green claim; timestamps unavailable for these
scoped runs. No commit/push/PR; corrected tests and all records uncommitted.

The execution packet's clause/protection mapping remains valid; T09 adds
`test_t09_guard_fixture_and_old_body_mutation_work_before_and_after_extraction`
for both root shapes. Applied migration-test-shape-invariance lesson.

Human `LISS-0585 Phase 1 Red テストレビュー／acceptance承認` on2026-10-09
accepts the corrected tests/support/immutable evidence, clause/protection mapping
and R1/R2 dispositions unchanged. Approval synchronization only; no new test run.
Next: separate Phase2 Green / implementation approval. Implementation permission
remains no. Initial findings below are historical evidence.

## Historical initial review — changes requested

## Review target

- Artifact: [accepted T01–T09](../../specs/evaluator-tensor-binding-successor.md),
  new behavior/ownership/guard suites, both guard-support files and immutable
  method evidence; [execution packet](2026-10-09-liss-0585-phase1-execution.md)
- Current phase: Phase1 test review; acceptance withheld pending corrections
- Requested approval: Phase1 test-only R1/R2 correction and subsequent re-review
- Approval type: phase; no Green implementation permission
- Approved scope: Tensor responsibility extraction / exact guard migration;
  human selected `LISS-0585 Phase 1 Red テストレビュー／acceptance`
- Implementation allowed: no
- Post-review required: yes; corrected tests need review/acceptance before
  separate Phase2 implementation approval
- Execution batch: none

## Review procedure and routing

Role switched to reviewer; files and spec re-read from disk, inherited helper
diff inspected, current suites rerun, future-shape tests exercised through
temporary copies. No test or production correction while reviewing.
Configured/effective isolation same_context, model empty: weaker independence
than separate_context, not human approval. Large-change override/numeric
structure settings absent. `review-change.py --root . --base HEAD --head HEAD`
returns normal same_context and dirty-tree unknown: committed diff counts0
are not measurements of this uncommitted change. Current new support/suites
120/188/172/52physical lines; semantic graph/cycle metrics remain unassessed.

## Findings / dispositions

### R1 [P1] Historical-body mutation test depends on an unextracted checkout

`tests/test_liss_0585_tensor_guard_migration_red.py:138–144` reads the current
Evaluator source and requires `left = _amps_indep(expr.left)` before applying
its mutation. Correct T07 implementation removes that method from Evaluator,
so this test fails at its setup assertion rather than testing protection.

Deterministic reproduction: construct the already-approved extracted shape
using `extracted_shape` in a pytest temporary tree, then call
`test_t09_changed_original_method_is_not_an_allowed_projection`. It fails
before mutation because the old-method substring is absent.

Disposition: apply after explicit test-only correction authorization. Recover
the historical method shape with the immutable projection/evidence first,
then mutate and call the real guard; keep both old-body and successor-algorithm
negative assertions. Do not retain a dead production body or relax the test.
Blocks test acceptance and Green readiness.

### R2 [P1] Real-guard fixture omits the successor in a migrated checkout

`tests/test_liss_0585_tensor_guard_migration_red.py:22–28` copies only the eight
historical readonly paths. The new successor is absent from that historical
manifest, intentionally immutable. After correct extraction, the copied
Evaluator has installed Tensor wiring but its temporary tree lacks the actual
successor. `check` rejects the authorized current shape with
`missing tensor implementation`.

Deterministic reproduction: create an extracted temporary tree, use it as the
fixture's ROOT, invoke the existing `guarded` fixture in another temporary tree,
then execute the `current` positive. It rejects the missing copied successor.

Disposition: apply after explicit test-only correction authorization. Copy the
actual successor when present as an additional test dependency without changing
the old readonly manifest/hash; verify the current and extracted roots both
prepare complete guarded trees. Keep deliberate missing-successor rejection.
Blocks test acceptance and Green readiness.

### Other assessed failure scenarios

Existing tests reject wrong/duplicate installer, setup, altered algorithm,
reintroduced body, unrelated state/body/exports, old foreach mapping/setup and
five immutable byte changes. Current-shape positives and mutations pass
together, so these checks are not vacuous reject-all. Old fixtures/API names/
assertions are retained. Scope and behavior T01–T08 are mapped in the execution
packet; T09's future-lifecycle validity is incomplete due to R1/R2.
No new semantic correction, provider, state owner or exclusion proposed.

## Verification

HEAD/baseline a349a5b720c59f3a0e288c4751dd012c25514843, dirty test/docs tree;
cwd /Users/nn0cl/Documents/git/qpex, macOS27.0.1 arm64, Python3.12.6 pytest9.0.3.
Same12-suite command as execution packet:166passed/4expected structural Red
in3.27s, exit1,170collected, errors/skips/exclusions0. Current scoped suite
matches prior baseline; no new/resolved failures in those selectors.
Separate future-shape diagnostic reproduces both R1/R2, exit0 (diagnostic asserts
both defects were observed). These are additional test-lifecycle blockers, not
the four intended production-ownership Red failures.
Root/spec/all-sanity not_run; no all-blocking or final-SHA Green claim.
Precise timestamps not captured for this review run; raw output in task tools.

## What changed and next decision

Review/status/trace/lesson documentation only. Tests, production, fixtures and
exclusions not modified by this review. Uncommitted; no push/PR/merge.
Request authorization to correct R1/R2 in Phase1 test scaffolding and re-review.
No acceptance/pass or implementation approval may be inferred from this packet.

## Adjudicator checklist

- [ ] Approve bounded test-only R1/R2 corrections, preserving assertions/fixtures.
- [ ] Require pre-/post-extraction positive fixture checks and real negatives.
- [ ] Review corrected diff and rerun before accepting Phase1.
- [ ] Keep Phase2 and delivery approvals separate.

Decision: changes requested; human correction authorization pending.
