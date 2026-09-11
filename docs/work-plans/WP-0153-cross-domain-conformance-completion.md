# WP-0153: 分野拡張と完成判定のconformance

| Field | Value |
|---|---|
| Status | proposed |
| Phase | phase-0-design |
| Size initial/current | M / M — one bounded profile or boundary; elapsed-time estimateではない |
| Parent | [WP-0131](WP-0131-scientific-workflow-program.md) |
| Issue | [LISS-0536](../issues/LISS-0536-cross-domain-conformance-completion.md) |
| Depends on | [WP-0139](WP-0139-s02-assay-batch-cycle.md); [WP-0141](WP-0141-s01-rolling-plan-validation.md); [WP-0142](WP-0142-astronomy-observation-profile.md); [WP-0147](WP-0147-adaptive-mesh-conservation.md); [WP-0148](WP-0148-physical-experiment-gravity-profile.md); [WP-0149](WP-0149-linear-fluid-mhd-profile.md); [WP-0150](WP-0150-discrete-interaction-profile.md); [WP-0151](WP-0151-scientific-reproducibility-evidence.md); [WP-0152](WP-0152-natural-language-observation-candidates.md); [WP-0154](WP-0154-relativistic-gravity-profile.md); [WP-0155](WP-0155-nonlinear-fluid-profile.md); [WP-0156](WP-0156-solar-mhd-profile.md); [WP-0157](WP-0157-inverse-ensemble-scientific-workflow.md); [WP-0158](WP-0158-s02-quantum-baseline-comparison.md) |
| Blocks | none |
| Owner / route | Sol: independent design correction and coordination; Luna: separately approved bounded phases |
| Architecture | ADR 0217-A/B/C Proposed; accepted ADRs 0210/0211/0212 remain prior constraints |
| Acceptance | [Scientific Workflow specification](../specs/staqex-scientific-workflow-acceptance.md), C01 |
| Implementation permission | no; no Phase 1 approval |
| Current Next Issue | LISS-0536 Phase 0 acceptance/profile review only |

## Scope

各profileのsource/binding/実行/結果/拒否/再現証拠を登録し、その他の科学分野の一つの追加profileでcore拡張不要を確認する。

## Out of scope

万能Solver実装、拒否だけによる分野完成、未検証の性能主張。 共通除外: branch/commit/PR操作は今回禁止、provider SDK/認証/live QPUは独立WP。

## Acceptance scenarios and verification

C01のGiven/When/Thenを適用する。具体的検証: coverage matrixと独立review。追加profileの正常実行と未知profile拒否、全required claimの証拠リンク。

Phase 0でfixture identity、schema/source form/API boundary、tolerance/期待diagnostic、
対象testsの配置、外部依存versionと採用判断の要否を確定する。
数式sourceを変更する場合はparser→typed HIR→Semantic IR→consumer→Resultを検証する。
Host-only契約ではport/APIの意味保存を検証し、source対応済みと主張しない。
外部service不要のfake/固定fixtureを使う。実測profileの検証は権利確認済みsnapshotを使用する。

## Risk / stop conditions

MVPだけで完了、profile listの無限拡大。追加profileはPhase 0で一つに固定。
承認済みspecと衝突する場合はArchitecture Pathへ戻す。
一つの契約/代表profileを越える場合はMのままLunaへ渡さず子Issueへ再分割する。
依存はdoneまたは明示waiverが必要。計画の作成/レビューは実装依存の完了を意味しない。

## Completion conditions

受入positive/negativeの対、sourceまたはportからの意味保存、実行/拒否の証拠、
profile限界、費用/誤差/出典の適用fieldを示す。Phase 3 review、Adjudicator final review、
LISS/WP/register同期とprocess reviewを経てdoneにする。
profile一つの完了を分野全体の完成と扱わない。追加profileはWP-0131のcoverage gateへ戻す。

## Luna implementation phases

0. このWPのscopeとC01の具体fixture/期待値をreview。ADR承認とreadinessを確認。
1. 個別Phase 1承認後、受入に対応するRed testsだけを作り、意図した失敗を提示。
2. testsの人間reviewとPhase 2/Implementation承認後、当該境界だけ最小Green。
3. Phase 3承認後、意味を変えずRefactor、再検証、review evidenceと台帳同期。
一回の依頼で複数phaseを実行しない。既存実装と一致する受入は先に証拠を確認し重複実装しない。

## AI planning record

- ID: AIP-WP-0153-2026-09-08-001; status: proposed.
- Author/environment: Sol role, Codex desktop, local shared worktree.
- Model/reasoning: N/A — role指定のみ、実行構成の表示値は取得していない。
- Created: 2026-09-08; size: M; execution scope: 上記一契約/一profile、Lunaへ各phase別に渡す。
- Estimated tokens range/midpoint/metric: N/A — fixture/API/technology review前で信頼できる見積根拠なし。
- Basis/assumptions/confidence: 依存と拒否境界に基づく分割、既存port再利用を仮定、medium。
- Revises: none; WP-0131親計画から新規分割。以前の承認済み見積は変更しない。
