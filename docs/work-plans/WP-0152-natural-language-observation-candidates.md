# WP-0152: 自然言語由来観測候補の信頼境界

| Field | Value |
|---|---|
| Status | proposed |
| Phase | phase-0-design |
| Size initial/current | M / M — one bounded profile or boundary; elapsed-time estimateではない |
| Parent | [WP-0131](WP-0131-scientific-workflow-program.md) |
| Issue | [LISS-0535](../issues/LISS-0535-natural-language-observation-candidates.md) |
| Depends on | [WP-0132](WP-0132-scientific-metadata-graph.md) |
| Blocks | WP-0153 |
| Owner / route | Sora/Sol: design coordination; Luna: separately approved bounded phases |
| Architecture | ADR 0217-A Proposed; accepted ADRs 0210/0211/0212 remain prior constraints |
| Acceptance | [Scientific Workflow specification](../specs/staqex-scientific-workflow-acceptance.md), L01 |
| Implementation permission | no; no Phase 1 approval |
| Current Next Issue | LISS-0535 Phase 0 acceptance/profile review only |

## Scope

source span付きcandidateの否定/伝聞/曖昧時刻/単位/対象とreview dispositionを受け渡す。

## Out of scope

LLM provider選定/導入、自動trusted昇格、runtime内LLM。 共通除外: branch/commit/PR操作は今回禁止、provider SDK/認証/live QPUは独立WP。

## Acceptance scenarios and verification

L01のGiven/When/Thenを適用する。具体的検証: fake extractorで出典なし/否定/曖昧候補拒否またはreview保持。正当なhuman昇格はactor/対象hashを保持。

Phase 0でfixture identity、schema/source form/API boundary、tolerance/期待diagnostic、
対象testsの配置、外部依存versionと採用判断の要否を確定する。
数式sourceを変更する場合はparser→typed HIR→Semantic IR→consumer→Resultを検証する。
Host-only契約ではport/APIの意味保存を検証し、source対応済みと主張しない。
外部service不要のfake/固定fixtureを使う。実測profileの検証は権利確認済みsnapshotを使用する。

## Risk / stop conditions

confidenceを測定誤差と誤認。本文命令をpolicyとして実行。
承認済みspecと衝突する場合はArchitecture Pathへ戻す。
一つの契約/代表profileを越える場合はMのままLunaへ渡さず子Issueへ再分割する。
依存はdoneまたは明示waiverが必要。計画の作成/レビューは実装依存の完了を意味しない。

## Completion conditions

受入positive/negativeの対、sourceまたはportからの意味保存、実行/拒否の証拠、
profile限界、費用/誤差/出典の適用fieldを示す。Phase 3 review、Adjudicator final review、
LISS/WP/register同期とprocess reviewを経てdoneにする。
profile一つの完了を分野全体の完成と扱わない。追加profileはWP-0131のcoverage gateへ戻す。

## Luna implementation phases

0. このWPのscopeとL01の具体fixture/期待値をreview。ADR承認とreadinessを確認。
1. 個別Phase 1承認後、受入に対応するRed testsだけを作り、意図した失敗を提示。
2. testsの人間reviewとPhase 2/Implementation承認後、当該境界だけ最小Green。
3. Phase 3承認後、意味を変えずRefactor、再検証、review evidenceと台帳同期。
一回の依頼で複数phaseを実行しない。既存実装と一致する受入は先に証拠を確認し重複実装しない。

## AI planning record

- ID: AIP-WP-0152-2026-09-08-001; status: proposed.
- Author/environment: Sora role, Codex desktop, local shared worktree.
- Model/reasoning: N/A — role指定のみ、実行構成の表示値は取得していない。
- Created: 2026-09-08; size: M; execution scope: 上記一契約/一profile、Lunaへ各phase別に渡す。
- Estimated tokens range/midpoint/metric: N/A — fixture/API/technology review前で信頼できる見積根拠なし。
- Basis/assumptions/confidence: 依存と拒否境界に基づく分割、既存port再利用を仮定、medium。
- Revises: none; WP-0131親計画から新規分割。以前の承認済み見積は変更しない。
