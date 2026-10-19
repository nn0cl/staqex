# WP-0175: 分割後ソース全体の残存責務棚卸し

| Field | Value |
|---|---|
| Status | in_progress — LISS-0590/0592 delivered;LISS-0591 waits for repaired-baseline/guard-composition acceptance |
| Phase | LISS-0592 delivery-record commit/revalidation authorized;external outcomes then record PR gate;0591 not resumed |
| Initial / current size | L / L; no reclassification |
| Scope approval | Adjudicator approved whole-source residual-responsibility inventory / Phase 0 on2026-10-15 |
| Phase 0 acceptance | I01–I08 explicitly accepted by Adjudicator on2026-10-15 |
| Owner | Codex host / Adjudicator |
| Base | b5c96f7e4c2a846f41ac8ad5d882f0cb987cd420; PR616 merged/main CI all3 SUCCESS |
| Related branch | codex/wp-0175-responsibility-inventory-phase0 |
| Related | WP-0160 / WP-0174; accepted core decomposition specification |
| Current Next Issue | [LISS-0592](../issues/LISS-0592-parseerror-serialization-repair.md) delivered PR619/main442ce6ff;record commit/revalidation approved2026-10-19,external recordsha592 outcomes then record PR approval if all pass.0591 baseline/guard-composition acceptance separate,P08 retained |

## Goal / scope

Facadeだけでなく実装本体を含めてproduction sourceを再棚卸しし、機能・import・
診断・状態所有を保持できる次の責務分割候補を選ぶ。今回の成果物は
[詳細棚卸し](../collaboration/reviews/2026-10-15-source-responsibility-inventory.md)、
[全221-file snapshot](../collaboration/reviews/2026-10-15-source-responsibility-inventory.tsv)、
[trace / handoff](../collaboration/traces/2026-10-15-wp-0175-source-responsibility-inventory.md)。

In:現mainの全production Python集計、上位owner/consumer/state確認、legacy保持理由、
入口契約欠落の記録、候補優先順位。Out:production/test/guard変更、実体移動・削除、
Rust実装、provider選定、公開契約廃止、過去の全削除の回帰監査、commit/remote配送。
Scope/design-startに続き棚卸し結果I01–I08とPhase0を明示受入れ済み。
棚卸し承認自体は候補や修復のScope/spec/実装承認ではない。その後2026-10-15に
TypeChecker operator判定本体分離のScope/Phase0設計開始だけを別途明示承認。

## Phase 0 acceptance notes (accepted I01–I08,2026-10-15)

1. I01:固定SHAと対象集合を示す。221 productionファイル、52,695物理行。
2. I02:private/helper/legacyを含む全file snapshotと測定単位・除外を残す。
3. I03:宣言主体、判定本体、orchestration、compatibilityを区別し、facade長で
   実体移行完了を推論しない。
4. I04:上位候補の実在consumer/private hook/shared stateと静的検索の限界を示す。
5. I05:legacy ownerとfacade経路を示す。削除可能性を名前だけで認定しない。
6. I06:再現した入口欠落は独立backlogに記録し、通常経路の機能減退と混同しない。
7. I07:TypeChecker→Parserを第一・第二候補として、他familyの順序、保持理由、
   未設定routing予算と既存構造指針のfollow-upを示す。順序は実装ロードマップではない。
8. I08:実行した検証とnot_runを分け、Phase 1以降・専用設計・commitは別承認にする。

## Issue graph / candidate disposition

新しい実装Issue番号はまだ割り当てない。別scopeを受けた候補だけ専用Issue/spec、
planning record、consumer/test inventoryを作る。既存LISS0546/0547のdoneを
書き換えて再開するのではなく、残る本体移行を新しい作業単位にする。

上記の未割当は棚卸し時点の記録。operator候補の別Scope承認によりLISS-0590を
新規割当し、専用設計を作成した。他候補・修復は未選定のまま。

| Issue | Status | Initial / current size | Planning record | Depends on | Branch |
|---|---|---|---|---|---|
| [LISS-0590](../issues/LISS-0590-typechecker-operator-body-successor.md) | done / delivered;feature PR617 and records PR618/main22335a57,PR/main CI successful | L / L | AIP-0590-001 accepted2026-10-16 | WP0175 I01–I08 accepted;delivered mainb5c96f7e | codex/liss-0590-delivery-records (merged) |
| [LISS-0591](../issues/LISS-0591-parser-operator-primary-successor.md) | blocked / phase-1-red readiness only;waits for0592 | L / L | AIP-0591-001 accepted2026-10-16 | existing resolved prerequisites plus0592 repair/repaired-baseline handoff | codex/liss-0591-parser-operator-phase0 |
| [LISS-0592](../issues/LISS-0592-parseerror-serialization-repair.md) | done / delivered PR619/main442ce6ff,PR/main CI all3 SUCCESS;record commit/revalidation authorized | L / L | AIP-0592-001 accepted2026-10-17 | existing ParseError/guard baseline,no dependency on0591 extraction | codex/liss-0592-delivery-records |

Human2026-10-17 requests actual repair,not preserving the serialization failure.
0592 now owns repair contract;0591 remains blocked on0592 and later agreed
repaired-baseline handoff. Its original P08 success clause stays unchanged.
No repair implementation/commit authority inferred;all normal gates apply.
Dedicated repair R01–R07,limited2-carrier guard policy,0591 dependency policy
and Phase0 subsequently explicitly accepted2026-10-17. No clause changes.
Phase1 execution separately approved2026-10-17. Authored R01–R07 tests and exact
two-carrier plumbing,production unchanged. Dedicated72 expected failures/36
passes;inherited293/adjacent39 pass at dirty22335a57. Root/spec/all-sanity
not_run;no exclusion/all-blocking Green/commit. Details owned by0592 Issue/spec/
trace. Next gate:0592 Phase1 test review execution,then human test acceptance
and separate Green approval;0591 remains blocked,not implicitly resumed.

Review execution approved2026-10-18. [0592 review](../collaboration/reviews/2026-10-18-liss-0592-phase1-review.md)
requires R1 raw-byte guard correction before test acceptance;no tests/source
changed in review. Next:R1 test-only correction/re-review approval,not Green.

Subsequent2026-10-18 R1 correction/re-review explicitly approved and executed:
new guard raw read+6 newline negatives only;R1 closed in agent re-review.
Current114:72 expected Red/42 pass,inherited293/adjacent39 pass,no source or
fixture/hash/old-carrier change. Next:human corrected-test acceptance,then
separate Green approval.0592 Issue/spec/review/trace own detailed evidence.

Human corrected-test acceptance explicitly received2026-10-18 for exact0592
cohort3d77b215…65029e/R1 re-review. Metadata only,source/tests/agreements
unchanged,no runtime rerun. Next:separate0592 Phase2 implementation approval;
0591 still waits for actual repair and accepted repaired-baseline handoff.

LISS0590 delivery-record PR618 merged22335a5768c17a41eb94682e7dd14d3e6df004bd;
PR/main CI all3SUCCESS,each root2938/spec161. This closes the previous record
delivery gate;older pending statements below are historical. Source tree for
new scoped Parser design is fixed at that merge. Inventory snapshot unchanged.
LISS0591 Scope/Phase0 design-start explicitly approved2026-10-16. Accepted
[dedicated specification](../specs/parser-operator-primary-successor.md) owns
P01–P10 and exact3-carrier policy;no Phase1/test/guard/implementation permission.
Dedicated Issue/spec/Phase0 acceptance separately received2026-10-16;
current next gate is Phase1 execution,not another Phase0 acceptance.
Both plan-owned bug dispositions remain unchanged;other candidates unselected.

Phase1 test/limited-guard execution subsequently approved2026-10-16. Baseline
readiness probe found P08 error-pickle expectation conflicts with actual source;
canonical discrepancy/proposed disposition is in LISS0591. Paused before test/
guard authoring;accepted clauses unchanged,no serialization repair or waiver.
Next gate:bounded P08 correction proposal approval,then corrected-spec acceptance.

優先候補と根拠の唯一の詳細表は棚卸し文書。TypeCheckerの281行operator walkは
bounded設計の第一提案。582行check_unit全体移動、Ty再設計、unitarity pass統合は
同時承認にしない。Parser/Scientific/QASM/runtimeの順序は調査優先度のみ。

## Plan-owned bug records (canonical, no fix authorized)

### BUG-WP0175-001 — TypeChecker dimension-family callback missing

- Status: proposed; observed boundary defect,not a declared active Red exclusion.
- Initial/current size:M/M; reclassification:none.
- Phase:phase-0-design; owner:WP-0175 planning / Adjudicator.
- Evidence:`typechecking/dimensions.py:14` calls `_legacy_check_dimensions`;
  actual TypeChecker has no callback. Direct real-context probe reproduces
  AttributeError before argument processing.
- Existing tests:0546 callable/context-text checks pass without invoking this
  entry. Normal pipeline impact/consumer reachability and intended assignment
  contract remain unassessed;do not claim all normal typechecking broken.
- Acceptance evidence needed:approved intended argument/result/diagnostic
  contract and real-context positive/negative tests,then separate implementation.
- Dependencies:contract disposition before touching this entry/context;
  not an automatic blocker for unrelated operator-family design.
- Planning record:AIP-BUG-WP0175-001-001,proposed2026-10-15,Codex host,M,
  intended route host with same_context review;scope limited to diagnosing and
  later specifying this missing bridge. Estimates/model/reasoning identifiers
  N/A(unavailable);confidence medium;no revision/supersession. No fix permission.

### BUG-WP0175-002 — Parser top-level-family callback missing

- Status:proposed;observed boundary defect,not a declared active Red exclusion.
- Initial/current size:M/M; reclassification:none.
- Phase:phase-0-design;owner:WP-0175 planning / Adjudicator.
- Evidence:`parsing/top_level.py:14` calls `_legacy_parse_declaration`;
  actual Parser lacks it. Real-context direct probe reproduces AttributeError.
- Empty-token Parser only isolates callback lookup;not evidence of valid
  source rejection. Normal Parser.parse uses other methods. Reachable dynamic
  external consumers and intended declaration contract remain unassessed.
- Acceptance evidence needed:approved declaration entry/return/token-consumption/
  error/recovery contract plus real-context tests. No guessed alias/repair.
- Dependencies:disposition before changing this entry/context;not a blanket
  prerequisite for every candidate.
- Planning record:AIP-BUG-WP0175-002-001,proposed2026-10-15,Codex host,M,
  intended host/same_context route;scope later specification of this bridge.
  Estimates/model/reasoning identifiers N/A(unavailable);confidence medium;
  no revision/supersession. No fix permission.

Do not remove or change frozen tests to hide either defect. Plan-owned records
do not waive future blocking failures. If promoted to dedicated Issues,transfer
canonical ownership explicitly instead of copying mutable bug ledgers.

## AI planning record — AIP-WP-0175-001

- Status:accepted2026-10-15 with I01–I08/Phase0 acceptance;estimates/scope unchanged.
- Created by:Codex host in desktop macOS repository,2026-10-15.
- Model/reasoning display identifiers:N/A,not exposed as stable recorded labels.
- Initial/current planning size:L/L;whole source metrics,multiple responsibility
  families and unknown dynamic consumer boundaries. This is not an ETA.
- Intended route:host static inventory/design;review.same_context,weaker;
  implementation.host setting recorded but implementation not authorized.
- Intended scope:Phase0 artifacts only;no new technology/architecture decision.
- Estimated token range/midpoint/metric:N/A,no calibrated estimator exposed.
  Actual token usage/source:N/A,not available for attribution.
- Basis:221 production/818 total Python files,9 files over1,000 physical lines,
  named facades delegating to large active owners;state/call/private compatibility.
- Assumptions:tracked compiler tree is production Python,source fixed at base;
  static import/attribute analysis is not full runtime reachability.
- Confidence:high for sizes/hashes and two callback absences;medium for proposed
  responsibility order;unknown for full graph/serialization/test completeness.
- Revises/revision reason/superseded by:none.

## Verification / next gate

Fresh:818-file AST/inventory,2 read-only reproductions,20 existing structural
tests,spec161/161 PASS. Final document checks/snapshot audit recorded in trace. Production/tests
unchanged;root/all-sanity fresh local not_run. Prior main CI is baseline
evidence only. No full Green/new Red suite/coverage-completeness claim.

Human approval received: **WP-0175 棚卸し結果 I01–I08 と Phase 0 acceptance**
on2026-10-15. Approval type:phase/design acceptance. Approved scope:inventory only.
Implementation allowed:no. Post-review required:yes,selected candidate needs
separate Scope/Phase0/spec then normal Red/acceptance/implementation/review gates.
Batch:N/A. No commit/push/PR/merge permission inferred.

TypeChecker operator判定本体分離のScope／Phase0設計開始は別途承認済み。
LISS-0590専用Issue/spec O01–O10・限定guard方針・Phase0は2026-10-16に別途明示受入れ。
Phase1 execution subsequently approved2026-10-16 and authored;source unchanged.
R1 bounded test-only correction/re-review explicitly approved and executed
2026-10-16;agent_pass/R1 closed. Child Issue/review/trace own exact bytes/evidence.
Corrected Phase1 exact tests/re-review accepted2026-10-16.
Phase2 implementation separately approved/performed2026-10-16;accepted tests
unchanged,focused passes;copy-smoke/source-clean/final-SHA gap remains.
Local commit/actual-SHA rerun separately approved2026-10-16. Results outside
the tree at the child Issue's verification.json path;no predeclared PASS.
That clean-SHA gate passed at6b6741f04ae135da1d88ea4dc6a008508a38609e;
Phase3 explicitly approved and agent review passed2026-10-16 without code/test edits.
Fresh root2938/spec161/sanity10 and focused117/inherited162/adjacent90PASS.
Current [Phase3 packet](../collaboration/reviews/2026-10-16-liss-0590-phase3-review.md)
owns evidence/limitations;current records uncommitted,final record SHA pending.
Final verification/review-record commit explicitly approved2026-10-16 for the
existing9Markdown cohort. Actual new SHA/results live externally at
`/private/tmp/liss-0590-final.rZOcJU/verification.json`,not predeclared PASS.
Actual record commitc1b915331f7a0cdb0466c3ec88940dc57acf9c3e passes root2938/
spec161/sanity10 and all declared focused/consumer checks. Human final-result
acceptance explicitly received2026-10-16;no code/test or inventory-scope changes.
Acceptance-record save/revalidation separately approved2026-10-16 for7Markdown
records only;actual SHA/results external at
`/private/tmp/liss-0590-accepted-sha.iLTcre/verification.json`,not predeclared PASS.
That delivery gate was explicitly approved/executed2026-10-16. PR617 merged
main2ca7d4f43d226142ea7f3121c69997b515f0be53;actual PR/main CI all3SUCCESS,
each root2938/spec161. Child done;merge tree equals approved2a728d24 HEAD.
Local7Markdown delivery-closeout save/reverification separately approved2026-10-16;
record branchcodex/liss-0590-delivery-records from delivered main2ca7d4f4.
Actual clean SHA/results external at
`/private/tmp/liss-0590-delivery-record-sha.PdUqXX/verification.json`,not predeclared PASS.
After required PASS,next record-only delivery approval;no push/PR/merge here.
No next implementation or bug repair started. Both plan-owned bug records
remain proposed;their repair contracts/implementations were not accepted here.

Process review:not yet;plan is in_progress with scoped follow-up,not done. No new process rule or lesson
written;existing body-ownership/private-consumer/state/compatibility lessons applied.
