# WP-0134: S02実測assay取込とcuration

| Field | Value |
|---|---|
| Status | done |
| Phase | complete |
| Size initial/current | M / M — one bounded profile or boundary; elapsed-time estimateではない |
| Parent | [WP-0131](WP-0131-scientific-workflow-program.md) |
| Issue | [LISS-0517](../issues/LISS-0517-s02-measured-assay-profile.md) |
| Depends on | [WP-0132](WP-0132-scientific-metadata-graph.md) |
| Blocks | WP-0135 |
| Owner / route | Sol: independent design correction and coordination; Luna: separately approved bounded phases |
| Architecture | ADR 0217-A accepted; 0217-B Proposed; accepted ADRs 0210/0211/0212 remain prior constraints |
| Acceptance | [Scientific Workflow specification](../specs/staqex-scientific-workflow-acceptance.md), D01 |
| Implementation permission | approved for bounded D01 implementation only |
| Current Next Issue | WP-0135 / LISS-0518 leakage-safe model validation |

## Scope

一つのtarget/assay-family/endpointと凍結した実測snapshotを選定し、ChEMBL形式の記録をDataPortから取り込み、化学処理はChemistryPortへ接続する。

## Out of scope

SDKの無承認採用、全assay統合、model fit、候補選定、実験発注。 共通除外: branch/commit/PR操作は今回禁止、provider SDK/認証/live QPUは独立WP。

## Acceptance scenarios and verification

D01のGiven/When/Thenを適用する。具体的検証: compound/assay/target ID、unit、relation、replicate、license/hashを検証。互換データ成功とcensor/不一致quarantine。

Phase 0でfixture identity、schema/source form/API boundary、tolerance/期待diagnostic、
対象testsの配置、外部依存versionと採用判断の要否を確定する。
数式sourceを変更する場合はparser→typed HIR→Semantic IR→consumer→Resultを検証する。
Host-only契約ではport/APIの意味保存を検証し、source対応済みと主張しない。
外部service不要のfake/固定fixtureを使う。実測profileの検証は権利確認済みsnapshotを使用する。

## Phase 0 decisions

- Profile scope is one target, one biochemical assay family, and one endpoint:
  inhibition `IC50`, expressed in `nM`, with relation values `=`, `<`, or `>`.
  `Ki`, `Kd`, EC50, cellular assays, and incompatible assay formats are not
  silently combined. Fixture identifiers are opaque and do not claim a real
  dataset or target measurement.
- A frozen snapshot must carry source identifier, source checksum, license/use
  status, acquisition timestamp, schema/profile version, and raw-record count.
  Missing license or checksum quarantines the snapshot; no live download is
  needed for Phase 1.
- Raw records retain separate compound, target, assay, activity, replicate, and
  source identifiers. Curation creates a new revision and never edits raw
  records. Canonicalization may validate identity through `ChemistryPort`, but
  may not silently rewrite structures or merge unrelated compounds.
- `DataPort` supplies raw records and snapshot metadata; `ChemistryPort` supplies
  identity validation only. Neither port owns endpoint compatibility, censoring,
  replicate grouping, or scientific acceptance policy; those remain in the
  use-case/domain contract.
- Curation accepts only compatible endpoint/unit/assay-family records and keeps
  the relation and censoring marker. Incompatible or incomplete records enter
  explicit `quarantine` with one of `ASSAY_ENDPOINT_MISMATCH`,
  `ASSAY_UNIT_MISMATCH`, `ASSAY_RELATION_LOSS`, `ASSAY_REPLICATE_MISMATCH`,
  `ASSAY_SOURCE_LICENSE_MISSING`, or `ASSAY_IDENTITY_COLLISION`.
- Phase 1 test location is the root suite
  `tests/test_s02_assay_profile_red.py`. Its fixed cases are: one accepted
  measured activity, one censored activity, mixed endpoint rejection, unit
  mismatch quarantine, replicate identity collision, and missing license.
- No ChEMBL release, external schema version, chemistry library, reader,
  database, model, or provider is selected by this Phase 0 decision.

## Risk / stop conditions

endpoint混合、構造標準化による誤った同一性、再配布権不明。
承認済みspecと衝突する場合はArchitecture Pathへ戻す。
一つの契約/代表profileを越える場合はMのままLunaへ渡さず子Issueへ再分割する。
依存はdoneまたは明示waiverが必要。計画の作成/レビューは実装依存の完了を意味しない。

## Completion conditions

受入positive/negativeの対、sourceまたはportからの意味保存、実行/拒否の証拠、
profile限界、費用/誤差/出典の適用fieldを示す。Phase 3 review、Adjudicator final review、
LISS/WP/register同期とprocess reviewを経てdoneにする。
profile一つの完了を分野全体の完成と扱わない。追加profileはWP-0131のcoverage gateへ戻す。

## Luna implementation phases

0. このWPのscopeとD01の具体fixture/期待値をreview。ADR承認とreadinessを確認。
1. 個別Phase 1承認後、受入に対応するRed testsだけを作り、意図した失敗を提示。
2. testsの人間reviewとPhase 2/Implementation承認後、当該境界だけ最小Green。
3. Phase 3承認後、意味を変えずRefactor、再検証、review evidenceと台帳同期。
一回の依頼で複数phaseを実行しない。既存実装と一致する受入は先に証拠を確認し重複実装しない。

## Phase 2 Green record

- Implemented `compiler/staqex/s02_assay_profile.py` for the bounded D01
  contract only.
- `FrozenAssaySnapshot` preserves immutable raw metadata and records;
  `curate_snapshot` returns a new revision without editing the raw snapshot.
- Accepted records preserve `=`, `<`, and `>` relations and are restricted to
  the selected biochemical IC50/nM profile.
- Endpoint, unit, relation, target, provenance, activity identity, and
  replicate identity violations return explicit quarantine diagnostics.
- No provider, chemistry library, live dataset, database, model fitting, or
  QPU behavior was added.

## Phase 3 Refactor record

- Centralized record-level compatibility checks in `_record_diagnostic` without
  changing diagnostic codes or acceptance behavior.
- Kept the raw snapshot and curated records immutable at the public boundary.
- Added explicit rejection of boolean snapshot revisions, preserving the
  positive-integer revision contract.
- Re-ran the accepted, censored, endpoint, unit, replicate, identity, and
  provenance checks after refactoring.

Process review: no operating-contract deviation or operational problem found.

## Final review record

Phase 3 final review approved on 2026-09-09. The bounded D01 slice is complete;
provider/real-dataset integration and chemistry normalization remain explicitly
out of scope. See [Review Summary](../collaboration/reviews/2026-09-09-liss-0517-phase3-final-review.md).

## AI planning record

- ID: AIP-WP-0134-2026-09-08-001; status: proposed.
- Author/environment: Sol role, Codex desktop, local shared worktree.
- Model/reasoning: N/A — role指定のみ、実行構成の表示値は取得していない。
- Created: 2026-09-08; size: M; execution scope: 上記一契約/一profile、Lunaへ各phase別に渡す。
- Estimated tokens range/midpoint/metric: N/A — fixture/API/technology review前で信頼できる見積根拠なし。
- Basis/assumptions/confidence: 依存と拒否境界に基づく分割、既存port再利用を仮定、medium。
- Revises: none; WP-0131親計画から新規分割。以前の承認済み見積は変更しない。
