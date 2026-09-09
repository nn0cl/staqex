# WP-0151: 分野共通の再現・反証・費用証拠

| Field | Value |
|---|---|
| Status | Phase 2 Green complete; Phase 3 pending |
| Phase | phase-2-green |
| Size initial/current | M / M — one bounded profile or boundary; elapsed-time estimateではない |
| Parent | [WP-0131](WP-0131-scientific-workflow-program.md) |
| Issue | [LISS-0534](../issues/LISS-0534-scientific-reproducibility-evidence.md) |
| Depends on | [WP-0133](WP-0133-scientific-typed-bindings.md); [WP-0138](WP-0138-scientific-workflow-lifecycle.md) |
| Blocks | WP-0139, WP-0141, WP-0153, WP-0157, WP-0158 |
| Owner / route | Sol: independent design correction and coordination; Luna: separately approved bounded phases |
| Architecture | ADR 0217-A/B/C Proposed; accepted ADRs 0210/0211/0212 remain prior constraints |
| Acceptance | [Scientific Workflow specification](../specs/staqex-scientific-workflow-acceptance.md), E01 |
| Implementation permission | no; no Phase 1 approval; Unit A only after typed approval |
| Current Next Issue | LISS-0534 Unit A Phase 3 Refactor approval |

## Scope

RunManifest/claim/evaluation protocolを固定し、再現水準、metric、baseline、全overheadと失敗/棄却を報告する。

## Out of scope

実機実行、全性能benchmarkを一括実装、成功metricへのretune。 共通除外: branch/commit/PR操作は今回禁止、provider SDK/認証/live QPUは独立WP。

## Acceptance scenarios and verification

E01のGiven/When/Thenを適用する。具体的検証: same manifest replay、numeric/statistical水準差、hash変更、heldout再利用検出、queue/encode/失敗費用欠落。

Phase 0でfixture identity、schema/source form/API boundary、tolerance/期待diagnostic、
対象testsの配置、外部依存versionと採用判断の要否を確定する。
数式sourceを変更する場合はparser→typed HIR→Semantic IR→consumer→Resultを検証する。
Host-only契約ではport/APIの意味保存を検証し、source対応済みと主張しない。
外部service不要のfake/固定fixtureを使う。実測profileの検証は権利確認済みsnapshotを使用する。

## Phase 0 decisions

- E01は再現可能性・反証可能性・費用証拠を報告するprovider-neutral契約であり、
  成功metricを良く見せるためのretuneや実機benchmarkではない。失敗・棄却・未検証も
  claimの一部として保存する。
- 固定fixtureは`manifest:s02-d03-v1`、`snapshot:s02-round-001`、
  `model:s02-v1`、`baseline:greedy-feasible-v1`、`environment:local-python-v1`
  とする。RunManifestはsource/fixture hash、input snapshot、model/baseline revision、
  seed、numeric precision、software/runtime versions、command identity、created_atを
  必須とする。
- EvidenceRecordはrun ID、manifest hash、status、selected output、metric、uncertainty、
  comparison population、cost breakdown、failure/diagnostic、source/license、
  replay referenceを保持する。queue/encode/execute/decode/verificationの費用は
  欠落時にゼロ補完せず、`EVIDENCE_COST_MISSING`で未完了とする。
- Unit Aはmanifest identity、同一manifest replay、source/fixture hash変更、seed/環境
  差分、numeric/statistical reproduction levelを扱う。完全一致を要求するのは
  manifest/identity/構造であり、数値はprofileが宣言したabsolute/relative tolerance内、
  統計結果は事前固定したsample count/confidence intervalで判定する。
- Unit Bはclaim/evaluation protocol、heldout再利用、都合のよいrunだけの分母化、
  失敗・棄却の隠蔽、費用欠落、prospective evidence欠落を扱う。claimは
  `reproduced`、`falsified`、`inconclusive`、`not-evaluated`のいずれかとし、
  `inconclusive`を成功扱いしない。
- 期待diagnosticは`EVIDENCE_MANIFEST_MISMATCH`、`EVIDENCE_HASH_CHANGED`、
  `EVIDENCE_HELDOUT_REUSE`、`EVIDENCE_DENOMINATOR_BIAS`、
  `EVIDENCE_COST_MISSING`、`EVIDENCE_RUN_FAILURE_HIDDEN`、
  `EVIDENCE_PROSPECTIVE_UNAVAILABLE`とする。seedだけで実機bit一致を主張せず、
  provider差・確率性・未実行を別fieldで報告する。
- Port境界は`RunManifestPort`、`EvidenceStorePort`、`CostObservationPort`とする。
  manifest identity、claim判定、分母・heldout policy、失敗の可視化はUseCase/Domainが
  所有し、adapterはrun情報と証拠の取得・保存だけを担う。外部provider SDKは選択しない。
- Phase 1 testsはUnit Aを`tests/test_reproducibility_manifest_red.py`、Unit Bを
  `tests/test_reproducibility_claims_red.py`へ分離する。まずUnit Aだけを実装し、Unit Bは
  Unit Aの受入後に別承認する。
- Process lessons applied: 完了した小profileを分野全体のcoverageと混同せず、成功だけでなく
  rejection/failureと観測可能なreport metadataを同じ証拠境界で扱う。

## Phase 1 Red record — Unit A

- Added only `tests/test_reproducibility_manifest_red.py`.
- The suite fixes same-manifest replay, hash/identity change rejection, and
  numeric tolerance mismatch behavior.
- Unit B claim/evaluation/cost tests and all production implementation remain
  out of this phase.

## Risk / stop conditions

seedで実機bit一致を要求。都合のよいrunsだけを分母にすること。
承認済みspecと衝突する場合はArchitecture Pathへ戻す。
一つの契約/代表profileを越える場合はMのままLunaへ渡さず子Issueへ再分割する。
依存はdoneまたは明示waiverが必要。計画の作成/レビューは実装依存の完了を意味しない。

## Completion conditions

受入positive/negativeの対、sourceまたはportからの意味保存、実行/拒否の証拠、
profile限界、費用/誤差/出典の適用fieldを示す。Phase 3 review、Adjudicator final review、
LISS/WP/register同期とprocess reviewを経てdoneにする。
profile一つの完了を分野全体の完成と扱わない。追加profileはWP-0131のcoverage gateへ戻す。

## Luna implementation phases

0. このWPのscopeとE01の具体fixture/期待値をreview。ADR承認とreadinessを確認。
1. 個別Phase 1承認後、受入に対応するRed testsだけを作り、意図した失敗を提示。
2. testsの人間reviewとPhase 2/Implementation承認後、当該境界だけ最小Green。
3. Phase 3承認後、意味を変えずRefactor、再検証、review evidenceと台帳同期。
一回の依頼で複数phaseを実行しない。既存実装と一致する受入は先に証拠を確認し重複実装しない。

## AI planning record

- ID: AIP-WP-0151-2026-09-08-001; status: proposed.
- Author/environment: Sol role, Codex desktop, local shared worktree.
- Model/reasoning: N/A — role指定のみ、実行構成の表示値は取得していない。
- Created: 2026-09-08; size: M; execution scope: 上記一契約/一profile、Lunaへ各phase別に渡す。
- Estimated tokens range/midpoint/metric: N/A — fixture/API/technology review前で信頼できる見積根拠なし。
- Basis/assumptions/confidence: 依存と拒否境界に基づく分割、既存port再利用を仮定、medium。
- Revises: none; WP-0131親計画から新規分割。以前の承認済み見積は変更しない。

## Phase 2 Green record — Unit A

- Added `compiler/staqex/reproducibility_evidence.py` with immutable
  `RunManifest`, `EvidenceRecord`, diagnostics, and replay comparison.
- Implemented exact manifest/hash identity checks and explicit numeric
  tolerance handling; changed evidence is rejected or marked inconclusive.
- The reviewed Red suite was not changed. Unit B claim/evaluation/cost
  evidence remains out of scope.
- Direct Green smoke checks, syntax, diff, and document lifecycle checks passed.
