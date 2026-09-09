# WP-0139: S02次回assay batchの閉ループ

| Field | Value |
|---|---|
| Status | Phase 2 Green complete; Phase 3 pending |
| Phase | phase-2-green |
| Size initial/current | M / M — one bounded profile or boundary; elapsed-time estimateではない |
| Parent | [WP-0131](WP-0131-scientific-workflow-program.md) |
| Issue | [LISS-0522](../issues/LISS-0522-s02-assay-batch-cycle.md) |
| Depends on | [WP-0133](WP-0133-scientific-typed-bindings.md); [WP-0136](WP-0136-s02-classical-batch-baseline.md); [WP-0138](WP-0138-scientific-workflow-lifecycle.md); [WP-0151](WP-0151-scientific-reproducibility-evidence.md) |
| Blocks | WP-0153, WP-0158 |
| Owner / route | Sol: independent design correction and coordination; Luna: separately approved bounded phases |
| Architecture | ADR 0217-A/B/C Proposed; accepted ADRs 0210/0211/0212 remain prior constraints |
| Acceptance | [Scientific Workflow specification](../specs/staqex-scientific-workflow-acceptance.md), D04 |
| Implementation permission | no; no Phase 1 approval |
| Current Next Issue | LISS-0522 Phase 3 Refactor approval |

## Scope

測定snapshotから候補batchと理由・予測/不確実性・制約/費用を提示し、人間承認対象にする。後続実測roundは新snapshotへ取り込む。

## Out of scope

実験室送信/発注、quantum advantage、synthetic成績の実測への言換え。 共通除外: branch/commit/PR操作は今回禁止、provider SDK/認証/live QPUは独立WP。

## Acceptance scenarios and verification

D04のGiven/When/Thenを適用する。具体的検証: historical cutoff replayで後続roundを封印。選定後の評価、stale承認拒否、選定時不可視の実測値を監査。

Phase 0でfixture identity、schema/source form/API boundary、tolerance/期待diagnostic、
対象testsの配置、外部依存versionと採用判断の要否を確定する。
数式sourceを変更する場合はparser→typed HIR→Semantic IR→consumer→Resultを検証する。
Host-only契約ではport/APIの意味保存を検証し、source対応済みと主張しない。
外部service不要のfake/固定fixtureを使う。実測profileの検証は権利確認済みsnapshotを使用する。

## Phase 0 decisions

- D04はQUBOや量子実行ではなく、D01/D02/D03で固定したS02 profileから次回の
  assay batch proposalを作り、後続roundの実測を新しいsnapshotとして再取込する
  classical closed loopである。QUBOはWP-0137/LISS-0520の責務とする。
- Input fixtureは`assay:s02-round-001`のimmutable curated snapshot、
  `candidates:s02-fixture-v1`のcandidate inventory、`model:s02-v1`の
  leakage-safe prediction record、`policy:s02-batch-v1`のapproval policyを
  固定する。candidate ID、predicted IC50、uncertainty、stock status、cost、
  diversity group、source/checksum/license、cutoff、model revisionを必須fieldとする。
- Proposal DTOは`plan_id`、snapshot/model/policy identity、candidate IDs、各候補の
  selection reason、prediction/uncertainty、hard-constraint verdict、cost、
  approval status、created_at、deadline、content hashを保持する。reasonは
  D03のobjectiveとconstraint評価から生成し、自由記述を選定根拠の権威にしない。
- Historical cutoff replayではround-001以前だけを入力にしてround-002の候補・実測値を
  hidden fixtureとして封印する。proposal生成時にround-002 labelが見えた場合は
  `ASSAY_FUTURE_LABEL_VISIBLE`でfail-closedとし、後続実測は新snapshotへ取り込む
  までproposalの根拠やpredictionを変更しない。
- 承認はproposalのcontent hash、snapshot ID、policy revision、期限、approval IDに
  bindする。snapshot/model/policyの変更、期限切れ、取消、candidate stock変更、
  duplicate replayはそれぞれ`ASSAY_STALE_APPROVAL`、`ASSAY_CANDIDATE_STATE_CHANGED`
  または`ASSAY_DUPLICATE_ROUND`として採用拒否する。拒否は空の成功proposalにしない。
- Positive/negativeの代表ケースは、(a)固定snapshotからD03選定結果と理由を含む
  proposalを作る、(b)凍結後にround-002実測を取り込んで新revisionを作る、(c)未来label
  混入、stale approval、stock変更、重複round、missing uncertainty/licenseを拒否する、
  の組み合わせとする。実測がまだない場合は`prospective_evidence: unavailable`
  と明示し、hit改善を主張しない。
- Port境界は`AssaySnapshotPort`、`CandidateInventoryPort`、`PredictionProfilePort`、
  `ApprovalPolicyPort`とする。proposal policy、cutoff、stale判定、証拠表示は
  UseCase/Domainが所有し、adapterは取得と形式変換だけを担う。
- 期待diagnosticは`ASSAY_FUTURE_LABEL_VISIBLE`、`ASSAY_STALE_APPROVAL`、
  `ASSAY_CANDIDATE_STATE_CHANGED`、`ASSAY_DUPLICATE_ROUND`、
  `ASSAY_MISSING_PROVENANCE`、`ASSAY_NO_PROSPECTIVE_EVIDENCE`とする。
  snapshot/hash/identityは完全一致、prediction値は入力profileの記録値を保持し、
  再計算による丸め差を受入条件にしない。
- Phase 1 testsは`tests/test_s02_assay_batch_cycle_red.py`に置き、fake/fixed fixtureだけを
  使用する。WP-0138のPlan/approval lifecycleとWP-0151のRunManifest/evidence契約が
  完了するまで、Phase 1のRed作成も開始しない。依存waiverを新たに決定するADRは未作成である。

## Risk / stop conditions

prospective証拠の不足。実測候補在庫と公共data間の分布差。
承認済みspecと衝突する場合はArchitecture Pathへ戻す。
一つの契約/代表profileを越える場合はMのままLunaへ渡さず子Issueへ再分割する。
依存はdoneまたは明示waiverが必要。計画の作成/レビューは実装依存の完了を意味しない。

## Completion conditions

受入positive/negativeの対、sourceまたはportからの意味保存、実行/拒否の証拠、
profile限界、費用/誤差/出典の適用fieldを示す。Phase 3 review、Adjudicator final review、
LISS/WP/register同期とprocess reviewを経てdoneにする。
profile一つの完了を分野全体の完成と扱わない。追加profileはWP-0131のcoverage gateへ戻す。

## Luna implementation phases

0. このWPのscopeとD04の具体fixture/期待値をreview。ADR承認とreadinessを確認。
1. 個別Phase 1承認後、受入に対応するRed testsだけを作り、意図した失敗を提示。
2. testsの人間reviewとPhase 2/Implementation承認後、当該境界だけ最小Green。
3. Phase 3承認後、意味を変えずRefactor、再検証、review evidenceと台帳同期。
一回の依頼で複数phaseを実行しない。既存実装と一致する受入は先に証拠を確認し重複実装しない。

## AI planning record

- ID: AIP-WP-0139-2026-09-08-001; status: proposed.
- Author/environment: Sol role, Codex desktop, local shared worktree.
- Model/reasoning: N/A — role指定のみ、実行構成の表示値は取得していない。
- Created: 2026-09-08; size: M; execution scope: 上記一契約/一profile、Lunaへ各phase別に渡す。
- Estimated tokens range/midpoint/metric: N/A — fixture/API/technology review前で信頼できる見積根拠なし。
- Basis/assumptions/confidence: 依存と拒否境界に基づく分割、既存port再利用を仮定、medium。
- Revises: none; WP-0131親計画から新規分割。以前の承認済み見積は変更しない。

## Phase 2 Green record

- Added `compiler/staqex/s02_assay_batch_cycle.py` with immutable assay
  snapshots, approval-bound batch proposals, deterministic proposal hashes,
  and follow-up snapshot ingestion.
- Implemented future-label rejection, stale-approval rejection, candidate
  stock-change rejection, explicit prospective-evidence status, and exact
  follow-up revision advancement.
- The reviewed D04 Red suite was not changed. No laboratory dispatch, provider,
  QPU, or scheduler integration was added.
- Direct Green smoke checks, syntax, diff, and document lifecycle checks passed.
