# LISS-0522: S02次回assay batchの閉ループ

| Field | Value |
|---|---|
| Local ID | LISS-0522 |
| Status | Phase 2 Green complete; Phase 3 pending |
| Phase | phase-2-green |
| Type / priority | feature / P0 |
| Initial/current size | M / M |
| Owner | Sol independent design correction; Luna only after phase-specific approval |
| GitHub issue | none |
| Parent | LISS-0514 |
| Depends on | LISS-0516, LISS-0519, LISS-0521, LISS-0534 |
| Blocks | LISS-0536, LISS-0541 |
| Related branch | none — branch operations forbidden in this design task |
| Work plan / canonical planning record | [WP-0139](../work-plans/WP-0139-s02-assay-batch-cycle.md), AIP-WP-0139-2026-09-08-001 |
| Acceptance notes | D04; [acceptance proposal](../specs/staqex-scientific-workflow-acceptance.md) |
| Adjudicator decisions | ADR 0217/acceptance review; D04 Phase 0 acceptance approved 2026-09-09; profile/technology if needed; distinct Phase 1, Phase 2/Implementation, Phase 3 approvals |

Scope、Out of scope、検証、risk、完了条件、Luna phaseは上記WPを単一計画元とする。
このIssueは新規提案で、既存完了Issueを再開しない。承認済みscope/phaseの継承はない。

Phase 0 decision record: D04はS02のclassical closed loopであり、QUBOではない。
`assay:s02-round-001`、`candidates:s02-fixture-v1`、`model:s02-v1`、
`policy:s02-batch-v1`を固定し、candidate IDs、selection reason、prediction/uncertainty、
constraint verdict、cost、provenance、approval hash、deadlineをproposalに保持する。
round-002の未来labelはproposal生成時に不可視とし、後続実測は新snapshotへ取り込む。
未来label混入、stale approval、candidate状態変更、重複round、provenance欠落を
diagnostic付きでfail-closedにする。QUBOはWP-0137/LISS-0520の責務である。

Phase 0 acceptance outcome: profile/schema/API boundary、positive/negative fixture、
port ownership、diagnostic、toleranceを確定した。WP-0138/LISS-0521とWP-0151/LISS-0534が
完了したため、依存は解消されPhase 1 Redがreadyになった。明示waiverは不要である。

Phase 1 Red record: `tests/test_s02_assay_batch_cycle_red.py` にproposalの選定理由・予測・
制約・費用・承認対象、未来label、stale approval、stock変更、後続roundの新snapshot化を
固定する5つの失敗契約を追加した。production codeは変更していない。次の承認対象は
LISS-0522 Phase 2 Green / Implementationである。

Phase 2 Green record: `compiler/staqex/s02_assay_batch_cycle.py` にimmutable snapshot、
approval-bound proposal、deterministic content hash、follow-up snapshot ingestionを追加した。
future label、stale approval、stock変更をfail-closedにし、prospective evidence未取得は明示的に
`unavailable`とする。Red suiteは変更していない。次の承認対象はPhase 3 Refactorである。
