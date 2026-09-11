# LISS-0522: S02次回assay batchの閉ループ

| Field | Value |
|---|---|
| Local ID | LISS-0522 |
| Status | done |
| Phase | complete |

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
制約・費用・承認対象、未来label、stale approval、stock変更、後続roundの新snapshot化に加え、
approval identity/deadline、missing provenance、duplicate roundを固定する9つの契約を追加した。
production codeは変更していない。Phase 2ではproposal DTOとfail-closed診断をこのRed契約に対応させる。
次の承認対象は`LISS-0522 Phase 2 Green / Implementation`である。

Phase 1 Red correction record: 正常系candidate fixtureへ固定source hash/licenseを追加し、
approval期限を将来値へ固定した。期限切れケースは`as_of`を明示し、missing provenanceは
provenanceを除いた専用fixtureへ分離した。これにより正常系と拒否系のfixture境界を分離した。

Phase 2 Green record: `compiler/staqex/s02_assay_batch_cycle.py` にimmutable snapshot、
approval-bound proposal、deterministic content hash、follow-up snapshot ingestionを追加した。
future label、stale approval、stock変更をfail-closedにし、prospective evidence未取得は明示的に
`unavailable`とする。Red suiteは変更していない。

Phase 3 Refactor record: proposal入力検証、候補選定、選定理由生成、content hash組み立てを
名前付きhelperへ分離し、DTO・診断コード・受入挙動を維持した。AST、D04スモーク、差分、
文書ライフサイクル検査は通過した。ローカル環境では`pytest`が利用できない。これは
2026-09-11の最終レビューで未充足と判定された第一回実装の履歴記録であり、完了を意味しない。

Final review disposition (2026-09-11): approval identity/deadline/hash、uncertainty/provenance、
approval expiry、duplicate roundの受入境界が不足していたため未承認。既存実装を変更せず、
Phase 1 Redの追補テストを追加した。次の承認対象は`LISS-0522 Phase 2 Green / Implementation`である。

Phase 2 Green follow-up record: `BatchProposal`へpolicy revision、approval hash、deadline、
uncertainty、provenanceを追加した。approval期限、candidate provenance、candidate model revisionを
検証し、duplicate follow-up roundを`ASSAY_DUPLICATE_ROUND`で拒否する。修正済みRedテストは変更していない。
`py_compile`、直接D04スモーク、`git diff --check`は通過した。pytestはローカル未導入のため未実行である。
次の承認対象は`LISS-0522 Phase 3 Refactor 承認`である。

Phase 3 Refactor follow-up record: candidate選択判定、provenance抽出、model revision判定、
proposal観測値組み立てを名前付きhelperへ分離した。DTO、診断コード、受入挙動、Redテストは
変更していない。`py_compile`、直接D04スモーク、`git diff --check`は通過した。pytestは
ローカル未導入のため未実行である。次の承認対象は`LISS-0522 Phase 3 最終レビュー 承認`である。

Final review follow-up (2026-09-11): `PYTHONPATH=. .venv/bin/pytest -q
tests/test_s02_assay_batch_cycle_red.py`は8 passed / 1 failed。失敗は既存のfollow-up
fixtureが`revision=1`のままで、正常系が期待するrevision 2へ進んでいないテスト不整合である。
実装はrevisionを厳密に検証している。pytest利用不可の記載はこの検証結果で訂正する。
Phase 1 Red テストfixture修正承認後、`round:002`を`revision=2`で生成するよう修正した。
focused pytestは9 passed、`py_compile`、`git diff --check`も通過した。次の承認対象は
`LISS-0522 Phase 3 最終レビュー 承認`である。

Phase 3 final review (2026-09-11): fixture correction後のD04 focused suiteは9 passed。
関連S02 suiteは23 passed / 3 failedだったが、失敗は今回変更していないLISS-0517の既存
DTO表現に限定されるため、本Issueの完了を阻害しない別Issue境界として記録した。
`py_compile`と`git diff --check`も通過した。D04の受入境界、diagnostic、実装分離、文書同期を
確認し、最終レビューを承認する。

Process review: no operating-contract deviation or operational problem found.
