# LISS-0593 Phase1 Red test review — changes requested

Date:2026-10-22 JST. This is an agent review,not human test acceptance.
Historical initial review. Authorized R1/N1 correction and its current
[re-review](2026-10-22-liss-0593-phase1-r1-review.md) supersede the pending
correction request below;retain original findings/evidence unchanged.

## Review target / authority

- Canonical:[F01–F10](../../specs/scientific-semantic-pure-family-batch.md),
  [Issue](../../issues/LISS-0593-scientific-semantic-pure-family-batch.md),
  [WP-0175](../../work-plans/WP-0175-source-responsibility-inventory.md).
- Representative [trace/handoff](../traces/2026-10-22-liss-0593-pure-semantic-batch.md).
- Approved scope/current phase:Phase1 Red test review execution for the ten
  authored artifacts and bounded three-carrier proposal. Implementation:no.
  No test correction,live-carrier application,commit or remote delivery allowed.
- Re-read from disk:accepted spec,all three new Python files and manifest,
  original function bodies,raw Git snapshots,Issue/trace,review/readiness,
  verification,source-quality,routing and process-lesson contracts.
- Effective isolation:same_context,implementation host,empty model identifiers.
  This is weaker than separate_context and does not replace the Adjudicator.
  No enabled large-change override. `routing.json` records dirty-tree metrics
  as unknown;committed diff0 is not a size measurement of this authored cohort.

## Findings / dispositions

### R1 — blocking: F02 omits independent relation-field mutations

At `tests/test_liss_0593_pure_families_red.py:128–162`,node,operation and
realization-record fields are individually mutated,but relations only have
their two-element sequence reversed. Neither `SemanticRelation.kind` nor
`SemanticRelation.node_ids` has an independent persistent mutation case.
F02 explicitly requires independent mutations of every serialized field;
the original payload serializes both at legacy.py:323. A populated oracle
comparison and raw body equality are valuable,but do not satisfy that explicit
minimum evidence inventory.

Independent Git-body execution confirms each single-field change changes the
baseline digest and agrees through all three actual entrypoints. Therefore
these cases are reachable,not an approved unreachable/out-of-scope exception.
Disposition:apply after human authorization;not fixed during review. Add two
named/parametrized persistent field cases,check original digest change and
baseline equivalence through all entrypoints,then reconcile the F02 matrix.
No production defect or current output regression is asserted by this finding.

### N1 — nonblocking improvement: make inspection ordering inputs distinguishable

At `tests/test_liss_0593_pure_families_red.py:196`,all three collected inputs
have at most one distinct role lane and one exactness value. The test checks
the correct formula,but its data cannot distinguish sorted lanes from stable
first-seen deduplication or all-exact from any-exact on populated inputs.
The author recorded a supplemental mixed probe;fresh review also observes
`quantum,classical,quantum` => `quantum,classical` and mixed exactness =>
`unresolved` through the baseline and actual paths. Neither is a persistent
collected case. Exact raw-body protection independently constrains this move,
so this is not a second blocking defect.
Disposition:propose adding that mixed input with distinct node dimensions
within the same test-only correction;no accepted behavior/requirement changes.

## Clause reconciliation / named failure scenarios

- F01/F05:three sole-owner Reds are genuine;complete raw original bodies are
  compared and legacy duplicate definitions forbidden. Runtime import audit
  of installed successor ownership remains future Green evidence.
- F02:R1 blocks complete acceptance;other core/node/operation/record,ordering,
  JSON/hash and malformed controls exist. No claim of full serialized-field
  coverage until R1 closes.
- F03:oracle/result identity,empty/duplicate/unresolved,first/default diagnostic
  and malformed cases pass;N1 strengthens persistent data diversity.
- F04:actual wildcard manifests/signatures,model identity,scoped legacy pickle
  and four cold import orders through consumers pass for current code. This
  is not proof of future imports or all dynamic consumers.
- F06:six raw snapshots match immutable Git directly. Independently assembled
  three-file post bytes match the proposed inverse;original algorithms and
  non-target bytes are not normalized away. Production inventory remains224
  tracked files,including223 Python files.
- F07/F09:real staged readers on distinct independently Git-built pre/post
  roots accept12 intact reads and reject48 missing/comment/whole-CRLF/mixed-LF
  mutations. Persistent tests additionally cover body/order/wiring/duplicate/
  import/sibling mutations and actual frozen loops/unrelated source/test edits.
  Six live-reader integration Reds remain until separately authorized carrier
  application. Rejection-only results are not called live protection.
- F08:explicitly bounded pure-helper closure preserves stdlib-only imports and
  rejects project/relative imports and dynamic execution. TEST plumbing alone
  executes in temporary roots;proposed production remains raw/AST data.
- F10:no test acceptance or Green inferred,no assertion/hash/exclusion edits.

## Deterministic evidence

Review receipts:`/private/tmp/liss-0593-red-review-20261022.H7p1b2/`.
`audit.py`/`audit.json`:independent Git/raw-body/field and reader controls;
per-suite JSON/stdout/stderr/JUnit:exact commands,times,exit and failure IDs.
Baseline/tested HEAD:`103fba434ab01db5534981bd5784d833a457b222`,dirty new
tests/docs on `codex/liss-0593-pure-semantic-batch-design`,not a committed result.
cwd:`/Users/nn0cl/Documents/git/qpex`;explicit repository PYTHONPATH.
Environment:macOS27.0.1 arm64,CPython3.12.6,pytest9.0.3,numpy2.4.6,PyYAML6.0.3.

| Fresh suite | Pass | Fail | State |
|---|---:|---:|---|
| focused249 |240|9|Red:3 ownership+6 live-carrier integration |
| inherited433 |431|2|0591 P10/0592 R06 new-test-path guards |
| adjacent28 |28|0|passed |
| root3503 |3492|11|Red:exact focused9/inherited2 union |
| spec161 |161|0|passed |

Fresh root completed in445.25s. Error/skip/excluded0 in all pytest runs.
Failure IDs exactly match author receipts:focused9 plus inherited2,no resolved
or additional failure. The inherited failures are0591 P10 and0592 R06 rejecting
new test paths;they remain blockers for Green,not waived regressions. All3254
old root nodes are retained,plus249 new;baseline853b4537 has identical compiler/
tests to103fba43. Comparison receipts are in finish-checks.json. No waivers.
The inspected author nested-copy harness was also freshly rerun:all four
Parser/TypeChecker pre/post combinations pass on semantic-post raw roots,
exercising unchanged0592/0585/0590/0587/0588/0589 copy/mutation consumers.
nested-copy-review.json retains the command and temporary-tree path.
Original author result/cohort is preserved,not substituted for fresh review.
Full sanity/compileall and installed post-move dependency/serialization checks
are not_run in this review;Phase2/3/final-SHA all-blocking gates remain open.

Reviewed ten-artifact cohort:
`8ebc79765ab51be5fa9a4032d6958f07ef85913c3a33b7382b27cc509b4fe52d`.
Accepted F-table:
`9fd536ecc2de89371708899ad8b44eeed22de552ba3984bde4c0f285869f62f5`.
Both stay unchanged during review. Helper/tests179/299/231 physical lines,
max function35/29/38;qualitative single-responsibility disposition retained.
Original1803-line legacy remains a known body-migration target,not a shorter
facade completion claim. No configured numeric structure budget is invented.

## Requested decision / post-review requirement

Request **LISS-0593 Phase1 Red R1テスト限定修正／再レビュー承認**.
Approval type:phase/test-only correction and re-review. Scope:R1 plus proposed
N1 input improvement in the new pure-family test and corresponding metadata.
Preserve all frozen evidence/new guard/composition tests and all old carriers,
production,assertions and exclusions. Post-review:yes,then human corrected-test
acceptance;Green/implementation remains a separate later approval.
Decision:pending. This packet neither accepts tests nor executes that repair.
