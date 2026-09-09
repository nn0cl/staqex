# LISS-0521: 期限・承認・再計画のWorkflow契約

| Field | Value |
|---|---|
| Local ID | LISS-0521 |
| Status | done |
| Phase | complete |
| Type / priority | feature / P0 |
| Initial/current size | M / L — WP記載の境界複雑性により再分類 |
| Owner | Sol independent design correction; Luna only after phase-specific approval |
| GitHub issue | none |
| Parent | LISS-0514 |
| Depends on | LISS-0515 |
| Blocks | LISS-0522, LISS-0524, LISS-0534, LISS-0540 |
| Related branch | none — branch operations forbidden in this design task |
| Work plan / canonical planning record | [WP-0138](../work-plans/WP-0138-scientific-workflow-lifecycle.md), AIP-WP-0138-2026-09-08-001 |
| Acceptance notes | W01; [acceptance proposal](../specs/staqex-scientific-workflow-acceptance.md) |
| Adjudicator decisions | ADR 0217/acceptance review; W01 Phase 0 acceptance approved 2026-09-09; profile/technology if needed; distinct Unit A/Unit B phase approvals |

Scope、Out of scope、検証、risk、完了条件、Luna phaseは上記WPを単一計画元とする。
このIssueは新規提案で、既存完了Issueを再開しない。承認済みscope/phaseの継承はない。

Phase 0 decision record: W01はprovider-neutralなWorkflowPlan/Job採用契約であり、
実行schedulerやprovider retryではない。Unit Aはsnapshot/plan hash、approval expiry/
cancel、stale result、pure state transitionを扱い、Unit Bはfake clock/eventによる
duplicate、late event、timeout/cancel race、別lane fallbackを扱う。Plan採用とJob完了を
別状態にし、identity/hash/sequenceの不一致はdiagnostic付きでfail-closedにする。
Unit AとUnit Bのtestsとphase approvalは分離する。

Phase 0 acceptance outcome: fixture identity、state/API boundary、ports、diagnostic、
UTC timestamp rule、positive/negative cases、Unit A/B分割を確定した。Unit AはPhase 1
Red ready、Unit BはUnit A受入後の別承認待ちである。

Phase 1 Red record: `tests/test_workflow_lifecycle_unit_a_red.py` にUnit Aの5つの
失敗契約を追加した。production code、Unit B、scheduler、provider接続は変更していない。
次の承認対象はUnit AのPhase 2 Green / Implementationである。

Phase 2 Green record: `compiler/staqex/workflow_lifecycle.py` にUnit Aのimmutable
identity/approval/Plan/Job result DTOとpure adoption transitionを追加した。期限・取消・
stale/identity不一致・未承認Planをfail-closedにし、Red suiteは変更していない。Unit B、
scheduler、provider retry、actuationは未実装である。
次の承認対象はUnit AのPhase 3 Refactorである。

Phase 3 Refactor record: current-plan identityとapproval-current判定をpure helperへ
抽出し、Unit Aのassertion、diagnostic code、adoption behaviorを変更していない。
次の承認対象はUnit Aの最終レビューである。

Unit A final review record: 2026-09-09にidentity binding、approval expiry/cancellation、
stale result rejection、Job完了とPlan採用の分離を確認し、Unit Aを完了とした。Unit Bの
event dedup、late event、timeout/cancel race、fallbackは未完了であり、WP全体はdoneではない。
詳細は[Review Summary](../collaboration/reviews/2026-09-09-liss-0521-unit-a-final-review.md)。
次の承認対象は`LISS-0521 Unit B Phase 1 Red 承認`である。

Unit B Phase 1 Red record: `tests/test_workflow_lifecycle_unit_b_red.py` にduplicate/
late event、timeout/cancel race、fallback requires new Planの4つの失敗契約を追加した。
production codeは変更していない。次の承認対象はUnit BのPhase 2 Green / Implementationである。

Unit B Phase 2 Green record: `compiler/staqex/workflow_lifecycle.py` にimmutableな
processed event key、`apply_event`、`request_fallback`を追加した。duplicate/late event、
timeout/cancel race、暗黙fallbackをdiagnostic付きで拒否し、Red suiteは変更していない。
次の承認対象はUnit BのPhase 3 Refactorである。

Unit B Phase 3 Refactor record: event revision判定とcompleted Plan構築をpure helperへ
抽出し、duplicate/stale/race/fallbackの診断と既存assertionを維持した。次の承認対象は
Unit Bの最終レビューである。

Final review record: 2026-09-09にUnit A/Bを確認し、W01 bounded contractを完了とした。
provider scheduler/retry、real actuation、external event transportは対象外のままである。
詳細は[Review Summary](../collaboration/reviews/2026-09-09-liss-0521-final-review.md)。

Process review: no operating-contract deviation or operational problem found.
