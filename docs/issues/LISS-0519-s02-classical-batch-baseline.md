# LISS-0519: S02古典batch目的とfeasibility oracle

| Field | Value |
|---|---|
| Local ID | LISS-0519 |
| Status | done |
| Phase | complete |
| Type / priority | feature / P0 |
| Initial/current size | M / M |
| Owner | Sol independent design correction; Luna only after phase-specific approval |
| GitHub issue | none |
| Parent | LISS-0514 |
| Depends on | LISS-0518 |
| Blocks | LISS-0522 |
| Related branch | none — branch operations forbidden in this design task |
| Work plan / canonical planning record | [WP-0136](../work-plans/WP-0136-s02-classical-batch-baseline.md), AIP-WP-0136-2026-09-08-001 |
| Acceptance notes | D03; [acceptance proposal](../specs/staqex-scientific-workflow-acceptance.md) |
| Adjudicator decisions | ADR 0217-A承認済み、D03 Phase 0 acceptance承認済み、Phase 1 Red承認済み、Phase 2 Green / Implementation承認済み、Phase 3 Refactor承認済み、Phase 3最終レビュー承認済み |

Scope、Out of scope、検証、risk、完了条件、Luna phaseは上記WPを単一計画元とする。
このIssueは新規提案で、既存完了Issueを再開しない。承認済みscope/phaseの継承はない。

Phase 0 decision record: candidate 5件、batch size 2、budget 8、stock／diversity
groupのhard constraint、predicted IC50合計最小のobjective、全subset enumeration
oracle、`greedy-feasible-v1` baseline、feasibilityとscoreの独立検算、
`no-feasible-plan`、4つのdiagnostic、root Red suiteの配置を確定した。実験発注、
量子回路、optimizer library、実データは対象外とする。

Phase 2 Green record: `compiler/staqex/s02_classical_batch_baseline.py` を追加し、
全subset oracle、`greedy-feasible-v1`、hard constraint検証、candidate set／
constraint／score mismatch診断、`no-feasible-plan`を実装した。

Phase 3 Refactor record: comparison quarantine result constructionをhelperへ
集約し、受入契約・診断コード・選択結果を変更せず可読性を改善した。

Phase 1 Red record: `tests/test_s02_classical_batch_baseline_red.py` に、
oracle／baseline一致、no-feasible-plan、candidate set不一致、constraint／score
不一致の失敗契約を追加した。実装はまだ追加していない。

Final review record: 2026-09-09に承認。D03 bounded sliceを完了とし、larger-scale
optimization、experiment ordering、quantum comparisonは別作業として残す。
詳細は[Review Summary](../collaboration/reviews/2026-09-09-liss-0519-phase3-final-review.md)。

Process review: no operating-contract deviation or operational problem found.
