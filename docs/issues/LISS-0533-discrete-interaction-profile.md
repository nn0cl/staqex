# LISS-0533: 一般離散graph・相互作用・Hamiltonian

| Field | Value |
|---|---|
| Local ID | LISS-0533 |
| Status | done |
| Phase | complete |
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

Phase 1 Red record: `tests/test_liss_0533_discrete_interaction_red.py` に、明示graph/law
projection、energy/decode、graph-as-Hamiltonian、duplicate edge、index mismatch、unsupported
targetの5契約を追加した。production codeは変更していない。次は
`LISS-0533 Phase 2 Green / Implementation`である。

Phase 2 Green record: `compiler/staqex/discrete_interaction_profile.py` にGraph、
InteractionLaw、明示IsingProjectionの境界と、node/index・duplicate edge・symmetry・target
検証、energy/decodeを実装した。Red suiteは変更していない。対象pytestは5件通過し、ASTと
文書ライフサイクル検査も通過した。次は`LISS-0533 Phase 3 Refactor 承認`である。

Phase 3 Refactor record: target判定、explicit law解決、node index生成、edge検証、projection
term構築を名前付きhelperへ分離した。公開型、diagnostic、energy/decode挙動、Red suiteは
変更していない。対象pytestは5件通過し、AST・差分・文書ライフサイクル検査も通過した。
次は`LISS-0533 Phase 3 最終レビュー 承認`である。

Final review correction record: diagnostic codeを`DiscreteProfileError.code`として構造化し、
5つのnegative testで5種のexact codeを検証した。修正後pytestは6件通過し、再レビューで指摘解消を
確認した。`LISS-0533 Phase 3 最終レビュー 承認`によりR01 bounded unitを完了した。

Final review record: 6件のpytest、AST、差分、文書ライフサイクル検査を確認し、R01のbounded
discrete interaction projectionをdoneとした。graph、Hamiltonian、unsupported targetの
境界は別profileの拡張余地として維持する。

Process review: no operating-contract deviation or operational problem found.
