# LISS-0534: 分野共通の再現・反証・費用証拠

| Field | Value |
|---|---|
| Local ID | LISS-0534 |
| Status | phase-0-accepted; Phase 1 ready for Unit A |
| Phase | phase-0-accepted |
| Type / priority | feature / P0 |
| Initial/current size | M / M |
| Owner | Sol independent design correction; Luna only after phase-specific approval |
| GitHub issue | none |
| Parent | LISS-0514 |
| Depends on | LISS-0516, LISS-0521 |
| Blocks | LISS-0522, LISS-0524, LISS-0536, LISS-0540, LISS-0541 |
| Related branch | none — branch operations forbidden in this design task |
| Work plan / canonical planning record | [WP-0151](../work-plans/WP-0151-scientific-reproducibility-evidence.md), AIP-WP-0151-2026-09-08-001 |
| Acceptance notes | E01; [acceptance proposal](../specs/staqex-scientific-workflow-acceptance.md) |
| Adjudicator decisions | ADR 0217/acceptance review; E01 Phase 0 acceptance approved 2026-09-09; profile/technology if needed; distinct Unit A/Unit B phase approvals |

Scope、Out of scope、検証、risk、完了条件、Luna phaseは上記WPを単一計画元とする。
このIssueは新規提案で、既存完了Issueを再開しない。承認済みscope/phaseの継承はない。

Phase 0 decision record: E01はprovider-neutralな再現・反証・費用証拠契約である。
`manifest:s02-d03-v1`、`snapshot:s02-round-001`、`model:s02-v1`、
`baseline:greedy-feasible-v1`、`environment:local-python-v1`を固定し、manifest hash、
input/model/baseline identity、seed、precision、runtime、command、cost breakdown、
failure/diagnostic、replay referenceを証拠へ保持する。Unit Aはmanifest/replay identityと
hash/tolerance、Unit Bはclaim、heldout再利用、分母bias、失敗/費用欠落を扱う。
Unit A/Bのtestsとphase approvalは分離する。

Phase 0 acceptance outcome: schema、port ownership、diagnostic、tolerance、Unit分割を
確定した。Unit AはPhase 1 Red ready、Unit BはUnit A受入後の別承認待ちである。
