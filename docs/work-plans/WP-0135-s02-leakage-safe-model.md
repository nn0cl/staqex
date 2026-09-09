# WP-0135: S02 splitと予測Model検証

| Field | Value |
|---|---|
| Status | done |
| Phase | complete |
| Size initial/current | M / M — one bounded profile or boundary; elapsed-time estimateではない |
| Parent | [WP-0131](WP-0131-scientific-workflow-program.md) |
| Issue | [LISS-0518](../issues/LISS-0518-s02-leakage-safe-model.md) |
| Depends on | [WP-0134](WP-0134-s02-measured-assay-profile.md) |
| Blocks | WP-0136 |
| Owner / route | Sol: independent design correction and coordination; Luna: separately approved bounded phases |
| Architecture | ADR 0217-A accepted; accepted ADRs 0210/0211/0212 remain prior constraints |
| Acceptance | [Scientific Workflow specification](../specs/staqex-scientific-workflow-acceptance.md), D02 |
| Implementation permission | approved for bounded D02 implementation only; completed |
| Current Next Issue | WP-0136 / LISS-0519 classical batch baseline |

## Scope

一つのcuration profileに対しcutoff/group splitとfit/transform履歴、予測/uncertainty/適用域を保持する。

## Out of scope

モデル探索の無制限自動化、clinical/ADMET妥当性保証。 共通除外: branch/commit/PR操作は今回禁止、provider SDK/認証/live QPUは独立WP。

## Acceptance scenarios and verification

D02のGiven/When/Thenを適用する。具体的検証: train-only fit、compound/replicate重複、future round/holdout流入を検出。calibrationと予測誤差は固定評価集合で確認。

Phase 0でfixture identity、schema/source form/API boundary、tolerance/期待diagnostic、
対象testsの配置、外部依存versionと採用判断の要否を確定する。
数式sourceを変更する場合はparser→typed HIR→Semantic IR→consumer→Resultを検証する。
Host-only契約ではport/APIの意味保存を検証し、source対応済みと主張しない。
外部service不要のfake/固定fixtureを使う。実測profileの検証は権利確認済みsnapshotを使用する。

## Phase 0 decisions

- The input is one WP-0134 curated IC50/nM profile. Each fixture record has
  `record_id`, `compound_id`, `replicate_group_id`, `activity_id`,
  `available_at`, `round_id`, and a separate label/measurement field. The
  fixture is synthetic and deterministic; it does not claim a real model or
  scientific result.
- The fixed availability cutoff is
  `2025-01-01T00:00:00Z`. The split is fixed by opaque compound groups into
  `train`, `validation`, and `holdout`; a compound and all of its replicate
  records must stay in one partition. The implementation must not randomly
  reshuffle or infer a split from arrival order.
- Records available after the cutoff, including future-round records, are
  retained as unavailable evidence but cannot enter fit, transform fitting,
  feature selection, or tuning. A holdout label remains hidden to fit and
  selection and is revealed only to the fixed evaluation operation.
- Fit provenance is a separate immutable `FitRecord` containing model
  revision, split profile ID, train record IDs, transform-fit record IDs,
  feature-selection record IDs, cutoff, and source/curated snapshot revision.
  Prediction output contains prediction, uncertainty, applicability status,
  and the fit-record ID; it never becomes a measured activity record.
- The provider-neutral `ModelPort` is limited to fit, transform, predict, and
  fixed evaluation calls. Split policy, leakage detection, label visibility,
  and scientific acceptance remain in the domain/use case. No sklearn,
  database, model registry, cloud service, or provider is selected.
- Stable diagnostics are:
  `MODEL_SPLIT_GROUP_OVERLAP`, `MODEL_CUTOFF_LEAKAGE`,
  `MODEL_HOLDOUT_LABEL_LEAKAGE`, `MODEL_FIT_HISTORY_INCOMPLETE`, and
  `MODEL_FEATURE_FIT_LEAKAGE`. Leakage is fail-closed; it is not silently
  repaired by moving records between partitions.
- The fixed evaluation reports MAE as the primary error metric, RMSE as a
  secondary metric, and 90% interval coverage when uncertainty is available.
  Metric computation is descriptive for this slice; no clinical, ADMET, or
  prospective efficacy claim is made. Identity/cutoff checks use exact
  timestamp and group equality, not numeric approximation.
- Phase 1 tests live in `tests/test_s02_leakage_safe_model_red.py` and cover:
  valid group split, replicate/group overlap rejection, future-round/cutoff
  leakage rejection, hidden holdout labels, incomplete fit history, and
  prediction uncertainty/applicability evidence.

## Phase 1 Red record

- Added only `tests/test_s02_leakage_safe_model_red.py`.
- The suite fixes the observable D02 contract for accepted fixed splits,
  group-overlap quarantine, cutoff leakage quarantine, holdout-label exclusion,
  feature-fit leakage quarantine, and prediction uncertainty/applicability
  provenance.
- The expected implementation module is
  `compiler.staqex.s02_leakage_safe_model`; it is intentionally absent until
  Phase 2/Implementation approval.

## Phase 2 Green record

- Implemented `compiler/staqex/s02_leakage_safe_model.py` for the bounded D02
  contract only.
- `SplitProfile` and `build_split` preserve a predeclared group split and
  quarantine group overlap or cutoff leakage without reshuffling records.
- `FitRecord` records train/transform/feature-selection provenance and keeps
  holdout labels out of fit history. `Prediction` retains uncertainty,
  applicability, and fit provenance without becoming a measured activity.
- No model library, provider, database, real dataset, or QPU behavior was
  added.

## Phase 3 Refactor record

- Centralized accepted and quarantined fit-result construction in small helper
  functions and a single model revision constant.
- Preserved split, leakage diagnostics, FitRecord fields, and Prediction
  evidence without changing assertions or behavior.
- Direct refactor checks, syntax, diff, and document lifecycle checks passed.

## Final review record

Phase 3 final review approved on 2026-09-09. The bounded D02 slice is complete;
model selection, prospective validation, and provider integration remain
explicitly out of scope. See [Review Summary](../collaboration/reviews/2026-09-09-liss-0518-phase3-final-review.md).

Process review: no operating-contract deviation or operational problem found.

## Risk / stop conditions

scaffold/time splitの科学的選択が未固定。tuningによるholdout再利用。
承認済みspecと衝突する場合はArchitecture Pathへ戻す。
一つの契約/代表profileを越える場合はMのままLunaへ渡さず子Issueへ再分割する。
依存はdoneまたは明示waiverが必要。計画の作成/レビューは実装依存の完了を意味しない。

## Completion conditions

受入positive/negativeの対、sourceまたはportからの意味保存、実行/拒否の証拠、
profile限界、費用/誤差/出典の適用fieldを示す。Phase 3 review、Adjudicator final review、
LISS/WP/register同期とprocess reviewを経てdoneにする。
profile一つの完了を分野全体の完成と扱わない。追加profileはWP-0131のcoverage gateへ戻す。

## Luna implementation phases

0. このWPのscopeとD02の具体fixture/期待値をreview。ADR承認とreadinessを確認。
1. 個別Phase 1承認後、受入に対応するRed testsだけを作り、意図した失敗を提示。
2. testsの人間reviewとPhase 2/Implementation承認後、当該境界だけ最小Green。
3. Phase 3承認後、意味を変えずRefactor、再検証、review evidenceと台帳同期。
一回の依頼で複数phaseを実行しない。既存実装と一致する受入は先に証拠を確認し重複実装しない。

## AI planning record

- ID: AIP-WP-0135-2026-09-08-001; status: proposed.
- Author/environment: Sol role, Codex desktop, local shared worktree.
- Model/reasoning: N/A — role指定のみ、実行構成の表示値は取得していない。
- Created: 2026-09-08; size: M; execution scope: 上記一契約/一profile、Lunaへ各phase別に渡す。
- Estimated tokens range/midpoint/metric: N/A — fixture/API/technology review前で信頼できる見積根拠なし。
- Basis/assumptions/confidence: 依存と拒否境界に基づく分割、既存port再利用を仮定、medium。
- Revises: none; WP-0131親計画から新規分割。以前の承認済み見積は変更しない。
