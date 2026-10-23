# LISS-0593 Phase1 Red R1 correction / re-review

Date:2026-10-22 JST. Agent re-review:R1/N1 closed;human corrected-test
review/acceptance explicitly approved2026-10-22 JST.
Declared root rerun finished:3495PASS/11FAIL,unchanged failure IDs plus three
new passing cases. This is not Green or production implementation permission.

## Review target / authority

- Canonical:[accepted F01–F10](../../specs/scientific-semantic-pure-family-batch.md),
  [Issue](../../issues/LISS-0593-scientific-semantic-pure-family-batch.md),
  [WP-0175](../../work-plans/WP-0175-source-responsibility-inventory.md).
- Original [changes-requested review](2026-10-22-liss-0593-phase1-red-review.md)
  remains historical evidence;representative [trace](../traces/2026-10-22-liss-0593-pure-semantic-batch.md)
  owns current handoff and phase permissions.
- Human explicitly authorized **LISS-0593 Phase1 Red R1テスト限定修正／再レビュー**.
  Approved scope:R1 plus N1 input improvement in the new pure-family test and
  corresponding metadata. Current phase:Phase1 Red correction/re-review.
  Production implementation:no. Old/live guard application:no. Commit/push/
  PR/merge:no. Post-review/human corrected-test acceptance:required,separate.
- Role switch:after the bounded correction,re-read the actual modified test,
  spec,original review,readiness,original Git algorithms and deterministic
  receipts. No further test correction while acting as reviewer.
- Routing:same_context review,host implementation,empty model identifiers;
  weaker isolation than separate_context. No enabled large-change override.
  routing.json explicitly reports unknown uncommitted size,not zero-sized work.

## Changes / clause mapping / findings

- **R1,closed with evidence,F02**:
  `test_f02_each_serialized_relation_field_is_preserved[kind/node_ids]` adds
  two collected cases. Each asserts exactly one relation field changes,then
  checks changed digest versus original plus original-equivalent behavior
  and no input mutation through all three current entrypoints.
  Independent AST inventory from raw Git matches exactly those two fields.
- **N1,applied and closed,F03**:
  `test_f03_inspection_order_exactness_and_original_object_identity[mixed-lanes-exactness-dimensions]`
  adds one collected input. Three distinguishable nodes retain first-seen
  quantum/classical/quantum lane order,exact/unresolved/exact and distinct
  type/dimension pairs. Existing result/identity/order assertions are unchanged.
- Named failure controls:independent Git-baseline functions wrapped with six
  counterexamples (ignore kind,ignore node_ids,sort lanes,use populated any-exact,
  reverse dimensions,reverse source-node IDs). The actual new cases reject all
  six after reaching each injected call. Three intact cases pass before and
  after temporary monkeypatching (six positive invocations),so rejection is
  not setup failure. Only test entrypoints are patched;repository production
  and raw proposed successor shape are never modified/executed.
- Preservation:all old function/test body AST and assertions are identical;
  all original inspection parameter inputs/IDs retained. Only the new helper,
  new two-case test and extra input/decorator formatting differ. Full raw diff
  retained as correction.diff. The other nine cohort artifacts are byte-identical,
  including new inverse/composition tests and all seven evidence fixtures.
  Six raw source/carrier snapshots independently match original Git.
- F01/F04–F10 protections remain unchanged:original consumers,scope/exclusions,
  sole-owner checks and exact inverse/real-copy controls retained. Current code's
  cold-import/wildcard/pickle evidence does not prove installed future ownership
  or every dynamic consumer. Installed eager/lazy audit remains a Green gate.
- No new blocking finding in the bounded correction. Nine expected focused
  Reds and two inherited path-guard failures remain implementation blockers,
  not review findings waived by this packet.

## Verification / evidence contract

Evidence:`/private/tmp/liss-0593-r1-20261022.7b3vun/`.
before.json captures the exact pre-correction test and ten artifact hashes;
rereview.py/rereview.json independently check preservation and counterexamples;
per-suite JSON/stdout/stderr/JUnit retain commands,cwd,times,exit and IDs.
Tested HEAD/base:`103fba434ab01db5534981bd5784d833a457b222`,dirty new
tests/docs on `codex/liss-0593-pure-semantic-batch-design`;not a final-SHA claim.
cwd:`/Users/nn0cl/Documents/git/qpex`,explicit PYTHONPATH;macOS27.0.1arm64,
CPython3.12.6,pytest9.0.3,numpy2.4.6,PyYAML6.0.3,full Git history.
Same commands as the accepted spec;JUnit arguments only add external evidence.

| Fresh suite | Pass | Fail | State |
|---|---:|---:|---|
| focused252 |243|9|Red:3 ownership+6 live-reader integration |
| inherited433 |431|2|0591 P10/0592 R06 test-path guards |
| adjacent28 |28|0|passed |
| root3506 |3495|11|Red:exact focused9/inherited2 union |
| spec161 |161|0|passed |

Root completed in442.12s;all3503 prior node IDs retained plus the three named
new PASS cases. All failure IDs exactly match the prior review across focused,
inherited,adjacent and root;no new or resolved failure. Reviewer-side direct
reexecution of the three added cases:3PASS. All pytest runs have error/skipped/
excluded0. No old failure or exclusion waived. finish-checks.json records this
comparison,seven-document whitespace/34relative-link validation,document/
active-Red(entries0)/coverage lifecycle and tracked whitespace checks:all PASS.
The two inherited failures must pass after separately authorized carrier
application. Full repository-sanity,compileall and installed successor graph
are not_run here;all declared blockers must pass at later Green/final gates.
No CI or remote delivery was attempted.

Corrected ten-artifact cohort:
`496c5d8a11a57a6ce2c42262812d684dcb8f99a2c2e015cd0eb027486a116c1c`.
Original cohort8ebc7976…fe52d remains recoverable in historical receipts;
new evidence identifies the authorized test correction,not a historical hash
regeneration. Manifest97738cc8…e6a and accepted F-table9fd536ec…62f5 unchanged.
Helper/composition179/231 lines unchanged;pure-family test299→326 lines,max
function29 unchanged. Retain one cohesive behavioral test file to keep the
correction bounded and adjacent to the existing field/inspection tests. No
numeric budget configured;qualitative readability disposition,no new owner.

## Human acceptance decision / next gate

Human explicitly approved **LISS-0593 Phase1 Red 修正済みテストレビュー／acceptance**
on2026-10-22 JST. Approval type:phase/test acceptance of the exact corrected
ten-artifact cohort496c5d8a…116c1c and this re-review,including R1/N1 closure.
Decision:approved by the Adjudicator,not inferred from agent checks or CI.
Acceptance recording changes metadata only;no runtime suite rerun or new Green
claim. Exact cohort/spec and documentation checks are recorded separately as
acceptance-checks.json in the same external evidence directory.

Next requested approval:**LISS-0593 Phase2 Green／implementation承認**.
Scope:only the accepted three-function/three-production-file move and exact
three-carrier test plumbing;preserve accepted tests and frozen evidence.
Implementation allowed:no until that explicit phase/implementation approval.
Post-review required:yes,Green verification then separate Phase3/final gates.
No commit,push,PR,merge or named execution-batch approval is inferred.
