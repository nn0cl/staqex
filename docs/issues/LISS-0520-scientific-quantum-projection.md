# LISS-0520: 離散問題からQuantum Projectionの変換契約

| Field | Value |
|---|---|
| Local ID | LISS-0520 |
| Status | Phase 3 Refactor complete; final review pending |
| Phase | phase-3-refactor |
| Type / priority | feature / P1 |
| Initial/current size | M / L — WP記載の境界複雑性により再分類 |
| Owner | Sol independent design correction; Luna only after phase-specific approval |
| GitHub issue | none |
| Parent | LISS-0514 |
| Depends on | LISS-0516 |
| Blocks | LISS-0533, LISS-0541 |
| Related branch | none — branch operations forbidden in this design task |
| Work plan / canonical planning record | [WP-0137](../work-plans/WP-0137-scientific-quantum-projection.md), AIP-WP-0137-2026-09-08-001 |
| Acceptance notes | Q01; [acceptance proposal](../specs/staqex-scientific-workflow-acceptance.md) |
| Adjudicator decisions | ADR 0217/acceptance review; profile/technology if needed; distinct Phase 1, Phase 2/Implementation, Phase 3 approvals |

Scope、Out of scope、検証、risk、完了条件、Luna phaseは上記WPを単一計画元とする。
このIssueは新規提案で、既存完了Issueを再開しない。承認済みscope/phaseの継承はない。

Phase 1 Red record: `tests/test_liss_0520_sqxa_runtime_loader_red.py` に、`.sqxa`のround-trip、
content hash改ざん、未知schema、provider-neutral Runtime loader、unsupported runtimeの
fail-closedを検証する5契約を追加した。production codeは変更していない。次は、Red確認後の
Phase 2 Green / Implementationである。

Phase 2 Green record: `compiler/staqex/quantum_artifact.py` に最小の`.sqxa` writer/readerと
provider-neutral Runtime loaderを追加した。readerはschemaとcontent hashを検証し、loaderは
`local-simulator`のみを受理してunsupported runtimeをfallbackなしで拒否する。Red suiteは
変更していない。AST、直接スモーク、差分、文書ライフサイクル検査は通過した。次は
`LISS-0520 Phase 3 Refactor 承認`である。

Phase 3 Refactor record: schema検証、document読込、encoding復元、runtime capability選択を
名前付きhelperへ分離した。公開API、serialized payload、診断、accepted runtime behaviorは
変更していない。AST、挙動維持スモーク、差分、文書ライフサイクル検査は通過した。次は
`LISS-0520 Phase 3 最終レビュー 承認`である。
