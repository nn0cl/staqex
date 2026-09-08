# WP-0132: 科学Metadata Graphの同一性と観測信頼

| Field | Value |
|---|---|
| Status | complete — Phase 3 Refactor reviewed 2026-09-08 |
| Phase | phase-0-design |
| Size initial/current | M / M — one bounded profile or boundary; elapsed-time estimateではない |
| Parent | [WP-0131](WP-0131-scientific-workflow-program.md) |
| Issue | [LISS-0515](../issues/LISS-0515-scientific-metadata-graph.md) |
| Depends on | none |
| Blocks | WP-0133, WP-0134, WP-0138, WP-0140, WP-0142, WP-0148, WP-0152 |
| Owner / route | Sol: independent design correction and coordination; Luna: separately approved bounded phases |
| Architecture | ADR 0217-A accepted — Architecture approval 2026-09-08; accepted ADRs 0210/0211/0212 remain prior constraints |
| Acceptance | [Scientific Workflow specification](../specs/staqex-scientific-workflow-acceptance.md), G01/G02/G03 |
| M0 acceptance approval | User approved `WP-0132 / LISS-0515 M0 G01/G02/G03 acceptance` on 2026-09-08 |
| Implementation permission | no; no Phase 1 approval |
| Current Next Issue | None for this bounded M0 slice; broader profiles require new WP/approval |

## Scope

6分野の小さなin-memory fixtureでEntity/Relation、Observation、Evidence、Provenance、Time/Space/Uncertaintyとrevisionを検証する。

## Out of scope

reader、parser、DB、単位換算、Solver、Workflow実行。 共通除外: branch/commit/PR操作は今回禁止、provider SDK/認証/live QPUは独立WP。

## Acceptance scenarios and verification

G01/G02/G03のGiven/When/Thenを適用する。具体的検証: 同ID異内容、dangling reference、provenance cycle、欠損と0、実測と推定の区別。domain graph cycleは成功する。

Phase 0でfixture identity、schema/source form/API boundary、tolerance/期待diagnostic、
対象testsの配置、外部依存versionと採用判断の要否を確定する。
数式sourceを変更する場合はparser→typed HIR→Semantic IR→consumer→Resultを検証する。
Host-only契約ではport/APIの意味保存を検証し、source対応済みと主張しない。
外部service不要のfake/固定fixtureを使う。実測profileの検証は権利確認済みsnapshotを使用する。

## Risk / stop conditions

Graphが第二の実行意味源になること。profile必須fieldの過剰強制。
承認済みspecと衝突する場合はArchitecture Pathへ戻す。
一つの契約/代表profileを越える場合はMのままLunaへ渡さず子Issueへ再分割する。
依存はdoneまたは明示waiverが必要。計画の作成/レビューは実装依存の完了を意味しない。

## Completion conditions

受入positive/negativeの対、sourceまたはportからの意味保存、実行/拒否の証拠、
profile限界、費用/誤差/出典の適用fieldを示す。Phase 3 review、Adjudicator final review、
LISS/WP/register同期とprocess reviewを経てdoneにする。
profile一つの完了を分野全体の完成と扱わない。追加profileはWP-0131のcoverage gateへ戻す。

## Luna implementation phases

0. このWPのscopeとG01/G02/G03の具体fixture/期待値をreview。ADR承認とreadinessを確認。
1. 個別Phase 1承認後、受入に対応するRed testsだけを作り、意図した失敗を提示。
2. testsの人間reviewとPhase 2/Implementation承認後、当該境界だけ最小Green。
3. Phase 3承認後、意味を変えずRefactor、再検証、review evidenceと台帳同期。
一回の依頼で複数phaseを実行しない。既存実装と一致する受入は先に証拠を確認し重複実装しない。

## AI planning record

- ID: AIP-WP-0132-2026-09-08-001; status: proposed.
- Author/environment: Sol role, Codex desktop, local shared worktree.
- Model/reasoning: N/A — role指定のみ、実行構成の表示値は取得していない。
- Created: 2026-09-08; size: M; execution scope: 上記一契約/一profile、Lunaへ各phase別に渡す。
- Estimated tokens range/midpoint/metric: N/A — fixture/API/technology review前で信頼できる見積根拠なし。
- Basis/assumptions/confidence: 依存と拒否境界に基づく分割、既存port再利用を仮定、medium。
- Revises: none; WP-0131親計画から新規分割。以前の承認済み見積は変更しない。

Process review: no operating-contract deviation or operational problem found.
