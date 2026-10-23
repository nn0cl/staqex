# LISS-0593 guard-consumer supplement Phase1 Red review

## Review packet

- Scope: review G01–G09 supplement Red tests and readonly adoption of the two
  inherited failures. This agent review does not grant human test acceptance or
  implementation permission.
- Canonical documents re-read: [accepted supplement specification](../../specs/scientific-semantic-pure-family-batch.md),
  [LISS-0593](../../issues/LISS-0593-scientific-semantic-pure-family-batch.md),
  [WP-0175](../../work-plans/WP-0175-source-responsibility-inventory.md),
  [trace](../traces/2026-10-22-liss-0593-pure-semantic-batch.md), and
  `docs/collaboration/verification-policy.md`.
- Tests re-read: `tests/test_liss_0593_guard_composition_red.py`,
  `tests/test_liss_0593_pure_families_red.py`, and unchanged
  `tests/test_liss_0591_guard_migration_red.py`.
- Findings: none requiring correction before human acceptance. G01/G06 pin the
  existing production, prior assertions and append-only test boundary. G02/G03/G05
  expose the five specified live gaps. Staged cases establish intact positives
  before mutation rejection, reconstruct stale carrier bytes from immutable
  source and verify the stale SHA, and test each of ten semantic paths as a
  missing listing entry and a real missing file. G07 exercises frozen consumers
  on pre/corrected copied roots; G08 proves injected counterexamples reach both
  intact and mutated cases. The original231-line prefix is retained. The two
  inherited failures run as their original test nodes without edits/exclusions.
- Dispositions: G01–G09 map to named collected cases; no accepted assertion,
  fixture or exclusion was weakened. No test changes were made during review.
- Remaining blockers: five new expected Red failures and two inherited failures
  remain. Source-clean copy smoke, final-SHA checks, human test acceptance, and
  separate Green/implementation approval remain later gates. This review does
  not claim Green.
- Reviewer verification: focused335 = 330 passed / 5 specified Red;
  inherited433 = 431 passed / same two failures; adjacent28 passed. Errors,
  skips and exclusions:0. The all-blocking root receipt was re-read, not rerun
  by reviewer:3589 total,3582 passed/7 failed, exactly the five new and two
  inherited IDs; all3506 prior node IDs retained plus83 new nodes. Spec and
  compileall author receipts re-read and passed.
- Tested SHA/environment: `103fba434ab01db5534981bd5784d833a457b222`, dirty
  working tree; macOS27.0.1 arm64, CPython3.12.6, pytest9.0.3, numpy2.4.6,
  PyYAML6.0.3. JUnit and suite receipts:
  `/private/tmp/liss-0593-guard-red-20261023.7un5D4/`.
- Failure comparison: prior root3506 had3504 passes and the same two inherited
  failures. Supplement adds83 nodes:78 pass and five named expected Red. Root
  failures are exactly the five new plus two retained; no unexplained failure,
  error, skip or exclusion appeared.
- Spec-to-change: only test-code change is the83-case append to the existing
  composition test, mapped in the G01–G09 scenario matrix. The other nine cohort
  artifacts and all fixtures match their accepted pre-supplement hashes. New
  cohort:`cb85f98ae0752650b6dac5ff494ee6967586c74c58395ca3b3a24a0a78b8851c`.
  No production or live helper/caller change occurred during Red or review.
- Consumer/structure: actual0590/0591/0592 frozen consumers are exercised on
  pre/corrected copied roots with negative controls. Test file633 lines, maximum
  function span38; no numeric structure budget is configured. Single-file
  append follows G06.
- Effective route: `same_context`, weaker than `separate_context`; host review,
  empty model identifier, no enabled large-change override. Review-change
  reports dirty diff metrics as unknown, not zero. Artifacts were re-read and
  focused/inherited/adjacent suites rerun; author/root evidence is not an
  independent-context review.
- Lessons applied: `red-contract-scope` and
  `readonly-inverse-artifact-existence`; named controls, exact path existence,
  stale raw reconstruction, and preservation of previous node IDs were checked.
  No new reusable lesson was needed.
- Next approval: human **LISS-0593 guard-consumer補足 Phase1 Red
  テストレビュー／acceptance**. If accepted, a separate **Phase2 Green／
  implementation approval** is required before helper repair.

## Review decision

Agent review result: **PASS for human acceptance review**. This is not human
test acceptance, Phase2 approval or a Green result. Same-context review is
weaker than separate-context review.
