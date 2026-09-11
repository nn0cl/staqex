# WP-0154: 重力metric・gauge・初期拘束profile

| Field | Value |
|---|---|
| Status | proposed |
| Phase | phase-0-design |
| Size initial/current | M / L — source/IR/consumerまたは複数状態境界のため設計reviewで再分類 |
| Parent | [WP-0131](WP-0131-scientific-workflow-program.md) |
| Issue | [LISS-0537](../issues/LISS-0537-relativistic-gravity-profile.md) |
| Depends on | [WP-0143](WP-0143-continuous-field-semantic-contract.md); [WP-0148](WP-0148-physical-experiment-gravity-profile.md) |
| Blocks | WP-0153 |
| Owner / route | Sora/Sol: design coordination; Luna: separately approved bounded phases |
| Architecture | ADR 0217-A/B Proposed; accepted ADRs 0210/0211/0212 remain prior constraints |
| Acceptance | [Scientific Workflow specification](../specs/staqex-scientific-workflow-acceptance.md), P03/F01 |
| Implementation permission | no; no Phase 1 approval |
| Current Next Issue | LISS-0537 Phase 0 acceptance/profile review only |

## Scope

一つの既知の相対論的時空/摂動問題を選び、metric、接続/微分、gauge、初期拘束と既存Solver projectionを検証する。

## Out of scope

一般GR solver自作、Newton profileからの暗黙変換、全数値相対論。 共通除外: branch/commit/PR操作は今回禁止、provider SDK/認証/live QPUは独立WP。

## Acceptance scenarios and verification

P03/F01のGiven/When/Thenを適用する。具体的検証: 既知metricの不変量とconstraint residual、coordinate変換の意味、不適合gauge/IC拒否。

Phase 0でfixture identity、schema/source form/API boundary、tolerance/期待diagnostic、
対象testsの配置、外部依存versionと採用判断の要否を確定する。
数式sourceを変更する場合はparser→typed HIR→Semantic IR→consumer→Resultを検証する。
Host-only契約ではport/APIの意味保存を検証し、source対応済みと主張しない。
外部service不要のfake/固定fixtureを使う。実測profileの検証は権利確認済みsnapshotを使用する。

## Risk / stop conditions

chart依存成分と物理量の混同。Phase 0で対象方程式と既存ecosystemを選定する必要。
承認済みspecと衝突する場合はArchitecture Pathへ戻す。
下記のM以下のunitに分け、Lunaには一つのunit・一つのphaseだけを渡す。さらに複数境界へ広がるなら追加Issueへ再分割する。
依存はdoneまたは明示waiverが必要。計画の作成/レビューは実装依存の完了を意味しない。

## Completion conditions

受入positive/negativeの対、sourceまたはportからの意味保存、実行/拒否の証拠、
profile限界、費用/誤差/出典の適用fieldを示す。Phase 3 review、Adjudicator final review、
LISS/WP/register同期とprocess reviewを経てdoneにする。
profile一つの完了を分野全体の完成と扱わない。追加profileはWP-0131のcoverage gateへ戻す。

## Luna implementation phases

0. このWPのscopeとP03/F01の具体fixture/期待値をreview。ADR承認とreadinessを確認。
1. 個別Phase 1承認後、受入に対応するRed testsだけを作り、意図した失敗を提示。
2. testsの人間reviewとPhase 2/Implementation承認後、当該境界だけ最小Green。
3. Phase 3承認後、意味を変えずRefactor、再検証、review evidenceと台帳同期。
一回の依頼で複数phaseを実行しない。既存実装と一致する受入は先に証拠を確認し重複実装しない。

## AI planning record

- ID: AIP-WP-0154-2026-09-08-001; status: proposed.
- Author/environment: Sora role, Codex desktop, local shared worktree.
- Model/reasoning: N/A — role指定のみ、実行構成の表示値は取得していない。
- Created: 2026-09-08; size: L (initial M); execution scope: 上記一契約/一profile、Lunaへ各phase別に渡す。
- Estimated tokens range/midpoint/metric: N/A — fixture/API/technology review前で信頼できる見積根拠なし。
- Basis/assumptions/confidence: 依存と拒否境界に基づく分割、既存port再利用を仮定、medium。再分類理由: 関連するsource/IR/consumerまたは複数状態境界を含むため。
- Revises: none; WP-0131親計画から新規分割。以前の承認済み見積は変更しない。

## Bounded Luna units (one unit per approved phase)

- **Unit A / P01-gr-a / M**: 一つの時空profileでmetric/frame/gauge/initial constraintのsource/metadata対応を固定し構造と単位を検証。数値Solverは除外。
- **Unit B / P01-gr-b / M**: Aの固定profileを既存計算ecosystemへ接続し、既知不変量とconstraint residualを比較。一般GR solverは除外。

親scenarioの既存期待を狭めずこの二つへ配分する。各unitは別のPhase 1 test review、Phase 2/Implementation、Phase 3承認を要する。WP全体の一括実装依頼は禁止。両unitの証拠がそろうまでWPはdoneにしない。
