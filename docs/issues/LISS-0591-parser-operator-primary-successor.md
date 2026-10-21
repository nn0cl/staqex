# LISS-0591: Parser operator-primary本体分離

## Metadata

- Local issue ID:LISS-0591
- GitHub issue:none;local planning only
- Status:review — R2 local checkpoint;actual-SHA evidence required for Phase3 gate
- Phase:r2-phase-2-local-checkpoint-phase-3-gated
- Type:refactor / behavior-preserving body migration
- Priority:high,next selected WP0175 candidate
- Initial planning size:L
- Current planning size:L
- Reclassification reason:none
- Owner/agent:Codex host / Adjudicator
- Related branch:codex/liss-0591-repaired-baseline
- Accepted repaired base:dca93187f50594b0417ae88067154baaf3c0ea7c
- Original immutable base:22335a5768c17a41eb94682e7dd14d3e6df004bd

## Summary / historical initial acceptance notes

Scope/Architecture Path Phase0 design-start explicitly approved2026-10-16.
Dedicated Issue/spec P01–P10,limited3-carrier policy and Phase0 explicitly
accepted by Adjudicator2026-10-16. Canonical agreement:
[dedicated P01–P10 spec](../specs/parser-operator-primary-successor.md).
Move only117-line operator-primary algorithm to existing family;retain single
Parser state,public/private hooks,AST/ParseError identity,token/error timing.
No actual code/test/fixture/guard edits;no implementation permission.
Three named test carriers may be migrated only after dedicated policy acceptance
and separate Phase1 execution approval. That execution approval was received
2026-10-16,but readiness check exposed the P08 mismatch below;no tests authored.

## Dependencies

- Parent:WP-0175 (I01–I08 inventory accepted2026-10-15).
- Depends on:accepted core decomposition;LISS0590/record delivery resolved.
  LISS0592 repair/records delivery and B01–B10 repaired-baseline/guard-composition
  handoff resolved by explicit acceptance2026-10-19,no waiver.
  Previous original source base historical.
- Blocks:none selected;future Parser work has separate gates.
- Related:LISS0547 existing families;BUG-WP0175-002 is separate and not touched.

## Adjudicator decision points

- Received2026-10-16:dedicated Issue/spec P01–P10,exact3-carrier policy,Phase0 acceptance.
- Approval type:phase/design acceptance;approved scope:operator-primary design.
- Implementation allowed:no;post-review required:yes;execution batch:N/A.
- Phase1 execution separately approved2026-10-16;paused before authoring tests.
- Received2026-10-19:B01–B10,exact6-carrier policy and supplemental Phase0 acceptance.
- Resumed Phase1 execution separately authorized/executed2026-10-19.
- Received2026-10-19:human corrected Phase1 test acceptance of22-artifact cohort.
- Received2026-10-19:Phase2 implementation approval/execution;verification blocked.
- Received2026-10-19:R2 export/EOF Scope/Phase0 design-start approval.
- Received2026-10-19:R2 E01–E08/limited3-new-test correction policy acceptance.
- Received2026-10-19:R2 Phase1 test-only execution approval/completion.
- Received2026-10-21:R2 Phase1 test review execution approval/completion,review pass.
- Received2026-10-21:R2 human exact-cohort test acceptance467971d6…0bb9.
- Received2026-10-21:R2 Phase2 implementation approval;E02/E03 correction applied.
- Received2026-10-21:local commit/actual-SHA all-blocking verification approval.
- Next:Phase3 review approval only after successful actual-SHA evidence;R1 closed.
- No commit,push,PR,merge,bug repair or further candidate authority inferred.

## Context / design

- Included:accepted core boundary,WP0175,actual parser/entry/context/consumers,
  four manifest provenances,actual copy utilities,selected neighboring tests.
- Omitted:unrelated grammar,Rust,provider/service choice,secrets,history-wide audit.
- Assumptions:mechanical algorithm move,callbacks remain on live Parser.
- Open decisions:Phase3 review permission after actual-SHA verification,then final review
  approvals;return to design if another protected path must change.
  Historical P08 discrepancy resolved by0592 and
  accepted B01–B10;successful P08 retained.
- Trace/handoff:[representative trace](../collaboration/traces/2026-10-16-liss-0591-parser-operator-primary.md).

## AI planning record — AIP-0591-001

- Status:accepted2026-10-16 with dedicated Issue/spec/Phase0 acceptance;
  size/estimate/scope unchanged,no implementation approval inferred.
- Created by:Codex host,desktop macOS27.0.1 arm64 repository.
- Model/reasoning setting as displayed:N/A;stable identifiers not exposed.
- Created at:2026-10-16 Asia/Tokyo.
- Planning size:L/L;multi-phase split with nested immutable guard/copy closure,
  callback/error boundary and broad regression. Not an ETA.
- Intended route:host scoped design/deterministic checks;review.same_context
  (weaker);implementation.host only after explicit future approval;modelIDs empty.
- Intended scope:sole primary algorithm plus narrow declarations/factory/wiring,
  exact3 test-carrier plumbing under approved guard policy.
- Estimated token range/midpoint/metric:N/A;no calibrated estimator exposed.
- Basis:Parser3679/class3504,body117;3 exception-construction sites,11 callbacks,
  3 actual production imports and4 readonly manifest provenances.
- Assumptions:preserve actual constructor/types and private binding;static
  consumers are not a full dynamic/serialization graph.
- Confidence:high source measurements;medium planned guard closure;unknown
  full dynamic graph/custom serialization/coverage completeness.
- Revises/revision reason/superseded by:none.

## Verification / work notes

Source baseline22335a57;initial tree clean. Inventory14 actual-context probes,
adjacent46PASS,inherited45PASS,spec161/161PASS at clean source SHA. Environment,
commands,timestamps/exits in `/private/tmp/liss-0591-phase0.8hzegU/`.
Root/all-sanity not freshly run;no all-blocking Green or new acceptance test.
Final doc/no-source-change checks are recorded in trace after execution.
Current documents uncommitted;no tested design-commit SHA is claimed.

## P08 readiness conflict (historical discovery;live repair owner LISS-0592)

- Observed2026-10-16 at unchanged source22335a57,macOS27.0.1 arm64,
  CPython3.12.6. Command/dirty-doc state/timing/exit/output captured externally:
  `/private/tmp/liss-0591-phase0.8hzegU/phase1-p08-baseline.json` and .out/.err;
  diagnostic script `/private/tmp/liss-0591-red.DtUMQj/p08-baseline.py`.
- Existing `ParseError.__init__` calls `super().__init__(message)` so args
  contain only message. Standard pickle reconstruction invokes the class with
  that one argument;required line/col are absent. Dumps succeeds,loads fails
  with TypeError. Ordinary OpLit with Span round-trips successfully.
- Accepted P08 expects representative AST/error round-trip,while the accepted
  boundary forbids changing the ParseError class/constructor. Both cannot be
  claimed satisfied by a pure body migration under current default behavior.
- This was a Phase0 design evidence omission by the authoring agent. Not a
  new product regression,not a structural extraction Red,not proof that
  normal parsing or compilation is broken. No coverage/behavior waiver.
- Proposed disposition (not yet approved):change only P08's error serialization
  expectation to characterize/preserve the existing default-load TypeError,
  retain successful AST round-trip and public class/error field identity.
  Tests must explicitly distinguish dump success from load failure,not skip
  the path or install a custom reducer. A serialization fix requires a
  separate behavior-change scope/spec/Red/implementation gate.
- Current P01–P10 bytes and guard policy unchanged. No production/test/fixture/
  guard edits performed;remaining Phase1 work paused at readiness.
- Approval requested:bounded P08 correction proposal authoring only;then human
  corrected-spec acceptance before resuming Phase1. Previous Phase1 approval
  is retained,not inferred as acceptance of a changed contract. No Phase2,
  constructor fix,commit or remote action allowed. AIP0591-001 L/L unchanged.

Update2026-10-17:human rejected the failure-preservation direction and requested
proper repair/completion. Above limited-correction proposal is superseded.
Live repair contract/planning now belong to
[LISS-0592](LISS-0592-parseerror-serialization-repair.md),not a duplicated bug
ledger here. P08 success requirement retained. Repair needs its own reviewed
specification/Red/implementation;0591 retains prior Phase1 authorization but
waits for repair and accepted fresh-baseline/guard-composition handoff.

## Supplemental Phase0 —2026-10-19

Human authorized repaired-baseline/guard-composition Scope and Phase0 design
start. Repair PR619 and records PR620 delivered;PR620 merge/main `dca93187`,
PR CI39187823442/main CI39188895779 all3 success,root3052/spec161.
Delivery [outcome](https://github.com/nn0cl/staqex/pull/620#issuecomment-6258339854).
These are previous delivery results,not fresh all-blocking for this design.

New agreement proposal:B01–B10 in the [canonical spec](../specs/parser-operator-primary-successor.md).
Existing3-carrier proposal misses0592 whole-parser/carrier/test fingerprints,
operators/path freezes and new-context copy closure. Propose exactly3 additional
plumbing paths:0592 guard support,boundary test and migration dependency copier.
Original fixtures/hashes and repair behavior stay unchanged;exact inverse views
preserve historical checks instead of resetting their baselines. Proposal only.

AIP-0591-001 supplement:L/L unchanged,extra integration complexity is now
explicit;original planning retained as historical. Approved scope this attempt:
design/investigation only. B01–B10 acceptance,then explicit resumed Phase1
execution,then test review/acceptance and implementation remain separate gates.
No production/test/fixture edit,commit or remote delivery authority inferred.
Current P01–P10 and all successful P08 requirements retained.

Fresh probe and existing regression evidence at actual clean source base are
recorded as `baseline591-*-20261019.{json,out,err}` outside Git. New0591 tests,
post-extraction shape execution,root/all-sanity and full dynamic graph are not
run/proven by this Phase0. Representative trace records exact outcomes and handoff.

### Human acceptance —2026-10-19

Received **LISS-0591 修復済みベースライン・B01–B10／限定6-carrier方針とPhase 0 acceptance**.
The complete B01–B10 and6-path dispositions are accepted without edits to their
requirements. Earlier proposal wording above is design history. AIP-0591-001
supplement accepted,L/L unchanged. Resumed Phase1 execution remains separately
gated,followed by test review/acceptance,implementation,review/final verification
and delivery. No source/test/fixture change or fresh runtime verification for
this metadata-only receipt;prior baseline evidence retains its SHA/environment.

## Phase1 execution result —2026-10-19

Human explicitly authorized resumed P01–P10/B01–B10 tests and exact6-carrier
plumbing. Added16 closed new test/support/fixture files and changed only those
6 existing test carriers,plus these4 related records. Production/old fixtures/
other existing tests remain byte-identical to repaired base dca93187.

171 new nodes:4 expected structural Red,167 PASS;no errors/skips. Existing
repair114,inherited293,adjacent39 and spec161/161 pass. Clean-base comparisons
for those existing suites remain passing;no failure waiver/exclusion. Current
tree is dirty/test-only;root/all-sanity/final-commit not_run. Exact commands,
initial authoring corrections and immutable cohort in representative trace;
clause mapping/new-path inventory in canonical spec.22-artifact cohort:
`82458c74523978e6ea16cf7dcd32c3bdc4c2e2b15926a470aa1c171c72ed414d`.
No review pass claimed;next explicit Phase1 test review execution,then human
test acceptance. Phase2/commit/remote actions remain separately gated.

## Phase1 review —2026-10-19

Explicit review execution approval received. Same-context review (weaker)
requires changes:R1 [P2],new0591 readonly operators reader returns immutable
fixture bytes when the requested original operators.py is deleted on pre
shape. Independent Git-built repaired/unrepaired roots:4 intact positives,
2 wrong new-reader acceptances,2 inherited-reader rejections. This is a test
guard blind spot,not an observed production regression;not a claim that all
guards or CI miss deletion. Current tests unchanged:171 nodes remain4 expected
Red/167 PASS;repair114/inherited293/adjacent39/spec161 pass.
[Review packet](../collaboration/reviews/2026-10-19-liss-0591-phase1-review.md).
Next:bounded correction of2 new0591 test files/re-review authorization;no
implementation,old fixture/hash/assertion relaxation or seventh carrier.

## R1 correction / re-review result —2026-10-19

Human R1 test-only correction/re-review approval received. Only2 new0591 files
changed:requested operators existence check plus8 paired positive/deletion
controls across both readers,repair states and extraction states. New179 nodes:
4 same expected Red/175 PASS;old171 nodes/outcomes unchanged. Repair114,
inherited293,adjacent39,spec161/161 PASS. Same reviewer probe inputs now yield
4 normal positives/4 deletion rejections. R1 closed in same-context agent
re-review,no other blocking correction finding. Full review record above.

Corrected22-artifact cohort
`68d6eef02b5e18a01ed4e3f4fef22c95ae740c71a57881b56b65708f3f1b5547`;
other20 test artifacts/old fixtures/6 carriers/all223 production bytes unchanged.
Current tree dirty at dca93187,no commit/source edit/full-blocking claim. Next:
human corrected-test acceptance,then separate Phase2 implementation approval.

## Human corrected-test acceptance —2026-10-19

Explicit **LISS-0591 Phase 1 Red 修正済みテストレビュー／acceptance承認** received.
Accepted22-artifact cohort:
`68d6eef02b5e18a01ed4e3f4fef22c95ae740c71a57881b56b65708f3f1b5547`.
R1 correction/re-review and179-node inventory accepted;original P/B clauses,
6-carrier boundary and immutable fixtures remain unchanged. Prior runtime
results are not rerun or reattributed for this receipt. Implementation,commit
and remote delivery not authorized. Next:Phase2 Green/implementation approval.

## Phase2 verification blocker —2026-10-19

Explicit Phase2 Green/implementation approval received. Changed only the3
approved production paths;accepted22 test artifacts remain unchanged. Focused
179 PASS,repair113 PASS/1 FAIL,inherited293 PASS,adjacent39 PASS,spec161 PASS.
Full root3230 PASS/1 FAIL;only failure is0592 R04 below,0 errors/skips.
Existing0592 R04 exact public-export test fails:successor imports add9 public
names. Accepted0591 raw guard requires exactly that module text and rejects an
export-preserving declaration. Its required trailing blank also fails
`git diff --check`. This is an integration agreement gap,not permission to
weaken0592 or alter accepted tests. Implementation stopped;no Phase3/commit.

Proposed R2 design scope:explicit `__all__` preserving all4 original exports
(`Any`, `ParserContext`, `annotations`, `parse_operator_expression`),bounded
new0591 expected-wiring/negative-control corrections,and successor-only EOF
normalization without changing immutable fixtures or facade inverse bytes.
Proposal not accepted or implemented. Next:human Scope/Phase0 design-start
approval for R2 export/EOF consistency. Full evidence/current handoff in
[trace](../collaboration/traces/2026-10-16-liss-0591-parser-operator-primary.md).

## R2 Phase0 design —2026-10-19

Explicit R2 Scope/Phase0 design-start approval received. Design-only work,
Architecture Path;no source/test changes. Canonical proposal is
[R2 E01–E08](../specs/parser-operator-primary-successor.md).
Preserve exact4 original exports via explicit `__all__`,remove exactly one
new-successor terminal LF,and correct only3 new0591 test paths (support,
guard_migration,consumers) after separate future approval. Existing6 carriers,
fixtures/hashes,0592 assertions and original P/B clauses unchanged. No parallel
Issue/ADR or new semantic/state boundary;AIP0591-001 L/L unchanged,R2 bounded
design supplement,not a third implementation attempt in this phase.

Read-only probe confirms9 added live globals and both raw serialization conflicts;
in-memory proposal AST-valid but not executed. Runtime results remain historical
Phase2 evidence. Next:**LISS-0591 R2補足仕様E01–E08・限定3新規テスト修正方針とPhase 0 acceptance**.
Type:phase/design acceptance;implementation allowed:no;post-review:yes;batch:N/A.
No test execution,implementation,commit or delivery authority inferred.

## Human R2 Phase0 acceptance —2026-10-19

Received the unique R2 E01–E08/limited3-new-test policy Phase0 acceptance target;
human `ISS-0591` denotes LISS-0591. Accepted E-row fingerprint
`8a32ec5ed774117f4c8c9903b2ef2cec8528b857f33b2606541b8d680ba1897a`.
No clause/source/test/fixture change or execution approval inferred. Phase2
export/EOF failures remain unresolved. Next:**LISS-0591 R2 Phase1 Red（限定3新規テスト修正）の実行承認**.
Type:phase execution,test-only;implementation allowed:no;post-review:yes;batch:N/A.
After execution:review/human corrected-cohort acceptance,then separate Phase2.

## R2 Phase1 execution result —2026-10-19

Explicit limited3-test Phase1 execution approval received/executed. Changed
only support/guard_migration/consumers plus4 status records. New22 guard nodes
and1 live wildcard node;all179 prior identities retained. Candidate cohort
`467971d66fb895fc6364d40b8f5580b9c62f715c247fe2832c892885f5030bb9`,
not reviewed or human-accepted. Production,existing6 carriers,other19 cohort
artifacts and fixtures unchanged. P/B/E clauses unchanged.

Focused202:157 PASS/45 Red (43 strict successor-wiring,2 actual export mismatch).
Separate paired controls30 PASS;repair90 PASS/24 FAIL,inherited287 PASS/6 FAIL,
adjacent39 PASS,spec161/161 PASS. No errors/skips or exclusions. Original live
copy cases stop on the intentionally invalid owner;external data-only corrected
input replay retains8 actual copy shapes and1 distinct-shape PASS without
executing/importing the projected source. Full commands/node comparison and
limitations in spec/trace;no full-Green or independent review claim.

Next:**LISS-0591 R2 Phase1 Red テストレビュー実施承認**. Type:phase/review
execution,implementation allowed:no;post-review:yes;batch:N/A. Human corrected
cohort acceptance and renewed implementation require separate later gates.

## R2 Phase1 review —2026-10-21

Review execution explicitly approved/completed,same_context/weaker. No actionable
test finding;candidate467971d6…0bb9 remains unchanged. Focused202:157 PASS/45 Red,
repair114:90 PASS/24 FAIL;extended inherited428:422 PASS/6 wiring failures.
Independent20 reader positives/120 rejections and8 copy+1 distinct shape PASS;
actual runtime failures remain blocking. No source/test edits during review.
[Review packet](../collaboration/reviews/2026-10-21-liss-0591-r2-phase1-review.md).
Next:**LISS-0591 R2 Phase1 Red テストレビュー／acceptance承認**.
Type:phase/test acceptance;implementation allowed:no;post-review:yes;batch:N/A.

## Human R2 test acceptance —2026-10-21

Explicit R2 Phase1 review/acceptance received for cohort
`467971d66fb895fc6364d40b8f5580b9c62f715c247fe2832c892885f5030bb9`.
No source/test changes or runtime rerun for this receipt;existing export/EOF
failures unresolved. Next:**LISS-0591 R2 Phase2 Green／implementation承認**.
Type:phase+implementation,only operators.py E02/E03 correction;implementation
allowed:not yet;post-review:yes;batch:N/A. No commit/remote authority inferred.

## R2 Phase2 verification —2026-10-21

Implementation explicitly approved/executed,only operators.py literal export
declaration/one-LF correction. Tests/source outside that path unchanged this
phase. Focused202,repair114,inherited428,adjacent42,root3254,spec161 PASS;
root0 failures/errors/skips/exclusions. Same-node failures45/24/6 resolved.
Raw/AST/cohort/export/compile/whitespace audits PASS. Local sanity9 PASS/1 FAIL:
template copy refuses uncommitted distributed spec. PR-only traceability not
applicable locally. Phase2 all-blocking/clean actual-SHA gate remains unresolved.

Evidence/limitations in final spec section and trace. Next:
**LISS-0591 R2 ローカルコミット／実SHAで全blocking再検証承認**.
Type:local commit+verification;implementation allowed:no further edits;
post-review:yes;batch:N/A. No Phase3/push/PR/merge authority inferred.

## Approved local checkpoint —2026-10-21

Local commit/all-blocking actual-SHA verification explicitly approved. Related
tests,implementation and records committed separately;no source/test edit or
remote action. Results are produced after this checkpoint commit at
`/private/tmp/liss-0591-r2-sha-20261021.2BHEPI/result.json` with full commands,
SHA/clean state,environment,times and failures. This pre-run receipt asserts no
success;missing evidence requires revalidation. No later tracked edit without
another final-SHA all-blocking run. Next,only if all pass:
**LISS-0591 R2 Phase3 Refactor／review承認**. Type:phase/review execution,
implementation allowed:no new scope;post-review:yes;batch:N/A. Issue not done.

## References

- [Accepted core decomposition](../specs/staqex-core-module-decomposition.md).
- [WP-0175](../work-plans/WP-0175-source-responsibility-inventory.md).
- Original source evidence is repository Git22335a57;no external technology chosen.

## Process review

- Outcome:not yet;issue blocked during Phase2 verification,not done.
- Lesson written:no new rule;existing ownership/private consumer/guard/typed
  approval/real-site/quantitative lessons applied in design.
- Template-feedback path:none requested.
