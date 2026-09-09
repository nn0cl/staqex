# LISS-0521: 期限・承認・再計画のWorkflow契約

| Field | Value |
|---|---|
| Local ID | LISS-0521 |
| Status | phase-0-accepted; Phase 1 ready for Unit A |
| Phase | phase-0-accepted |
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
