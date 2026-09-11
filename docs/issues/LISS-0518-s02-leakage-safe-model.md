# LISS-0518: S02 splitと予測Model検証

| Field | Value |
|---|---|
| Local ID | LISS-0518 |
| Status | done |
| Phase | complete |
| Type / priority | feature / P0 |
| Initial/current size | M / M |
| Owner | Sol independent design correction; Luna only after phase-specific approval |
| GitHub issue | none |
| Parent | LISS-0514 |
| Depends on | LISS-0517 |
| Blocks | LISS-0519 |
| Related branch | none — branch operations forbidden in this design task |
| Work plan / canonical planning record | [WP-0135](../work-plans/WP-0135-s02-leakage-safe-model.md), AIP-WP-0135-2026-09-08-001 |
| Acceptance notes | D02; [acceptance proposal](../specs/staqex-scientific-workflow-acceptance.md) |
| Adjudicator decisions | ADR 0217-A承認済み、D02 Phase 0 acceptance承認済み、Phase 1 Red承認済み、Phase 2 Green / Implementation承認済み、Phase 3 Refactor承認済み、Phase 3最終レビュー承認済み |

Scope、Out of scope、検証、risk、完了条件、Luna phaseは上記WPを単一計画元とする。
このIssueは新規提案で、既存完了Issueを再開しない。承認済みscope/phaseの継承はない。

Phase 0 decision record: WP-0134のcurated IC50/nM profileを入力とし、固定cutoff
`2025-01-01T00:00:00Z`、compound／replicate group単位のtrain／validation／holdout
split、未来roundとcutoff後データのfit流入拒否、hidden holdout label、FitRecordの
train／transform／feature-selection履歴、predictionのuncertainty／applicability、
5つの漏洩診断、固定評価metric、root Red suiteの配置を確定した。fixtureはsynthetic
であり、モデル・実データ・ライブラリは選定しない。

Phase 1 Red record: `tests/test_s02_leakage_safe_model_red.py` に、固定group
split、group overlap、cutoff leakage、holdout label exclusion、feature-fit
leakage、prediction uncertainty/applicabilityの失敗契約を追加した。実装は
まだ追加していない。

Phase 2 Green record: `compiler/staqex/s02_leakage_safe_model.py` を追加し、
固定group split、cutoff leakageのfail-closed判定、FitRecordによるfit証跡、
holdout label exclusion、prediction uncertainty/applicabilityを実装した。

Phase 3 Refactor record: fit結果生成とquarantine処理をhelperへ集約し、
受入契約・診断コード・証跡フィールドを変更せず可読性を改善した。

Final review record: 2026-09-09に承認。D02 bounded sliceを完了とし、model
selection、prospective validation、provider integrationは別作業として残す。
詳細は[Review Summary](../collaboration/reviews/2026-09-09-liss-0518-phase3-final-review.md)。

Process review: no operating-contract deviation or operational problem found.
