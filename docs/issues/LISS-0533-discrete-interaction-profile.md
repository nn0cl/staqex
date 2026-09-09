# LISS-0533: 一般離散graph・相互作用・Hamiltonian

| Field | Value |
|---|---|
| Local ID | LISS-0533 |
| Status | Phase 0 accepted; Phase 1 pending |
| Phase | phase-0-accepted |
| Type / priority | feature / P1 |
| Initial/current size | M / M |
| Owner | Sol independent design correction; Luna only after phase-specific approval |
| GitHub issue | none |
| Parent | LISS-0514 |
| Depends on | LISS-0516, LISS-0520 |
| Blocks | LISS-0536 |
| Related branch | none — branch operations forbidden in this design task |
| Work plan / canonical planning record | [WP-0150](../work-plans/WP-0150-discrete-interaction-profile.md), AIP-WP-0150-2026-09-08-001 |
| Acceptance notes | R01; [acceptance proposal](../specs/staqex-scientific-workflow-acceptance.md) |
| Adjudicator decisions | ADR 0217/acceptance review; profile/technology if needed; distinct Phase 1, Phase 2/Implementation, Phase 3 approvals |

Scope、Out of scope、検証、risk、完了条件、Luna phaseは上記WPを単一計画元とする。
このIssueは新規提案で、既存完了Issueを再開しない。承認済みscope/phaseの継承はない。

Phase 0 acceptance record: R01は`graph:r01-spin-chain-3-v1`の3-node spin interaction
chainを代表fixtureとし、Graph、InteractionLaw、明示Hamiltonian Projectionを別境界にする。
全2^3 assignmentのenergy/decode、edge symmetry、Q01有限projection接続を検証し、graphの
Hamiltonian暗黙化、duplicate edge、index/symmetry不一致、unsupported targetは診断付きで
fail-closedにする。次は`LISS-0533 Phase 1 Red`である。
