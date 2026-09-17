# LISS-0514: 完成形 Scientific Workflow設計修正

| Field | Value |
|---|---|
| Local ID | LISS-0514 |
| Status / phase | review / phase-0-design |
| Type / priority | architecture / P0 |
| Initial/current size | XL / XL |
| Owner | Sol independent design correction; Adjudicator architecture decision |
| GitHub issue / parent / depends on | none / none / none for design |
| Blocks | LISS-0515–0541 architecture/acceptance gates |
| Related branch | none — branch operations forbidden |
| Work plan / AI planning record | [WP-0131](../work-plans/WP-0131-scientific-workflow-program.md), AIP-WP-0131-2026-09-08-001 |
| Inventory count | 28 total records: this parent WP/LISS pair plus 27 child WP/LISS pairs |
| Acceptance | [Scientific Workflow proposal](../specs/staqex-scientific-workflow-acceptance.md) |
| Adjudicator decisions | Scope分割、Architecture、profileごとのTechnology、Phase、Implementationを分離。ADR 0217-A Architecture承認済み（2026-09-08）；B/C、Technology、Phase、Implementationは未承認 |

設計Scopeは依頼済み。設計/仕様/ADR案/計画の修正だけを行い、親Issue自体の実装とGit mutationは行わない。
詳細計画・統合判断・承認packetはWP-0131を単一元とする。独立設計reviewは承認済みで、ADR 0217-AはArchitecture承認済み。
M0のbounded child（WP-0132〜0133）とS02の承認済みchildは完了している。親programは全分野の完成判定を保持するためdoneではなく、次のchildはWP-0141/LISS-0524 Phase 0である。
