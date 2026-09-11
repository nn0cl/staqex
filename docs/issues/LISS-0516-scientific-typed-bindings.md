# LISS-0516: 意味を保持する型付き古典入力とdecode

| Field | Value |
|---|---|
| Local ID | LISS-0516 |
| Status | complete — Phase 3 Refactor reviewed 2026-09-08 |
| Phase | phase-0-design |
| Type / priority | feature / P0 |
| Initial/current size | M / M |
| Owner | Sol independent design correction; Luna only after phase-specific approval |
| GitHub issue | none |
| Parent | LISS-0514 |
| Depends on | LISS-0515 |
| Blocks | LISS-0520, LISS-0522, LISS-0525, LISS-0526, LISS-0531, LISS-0533, LISS-0534 |
| Related branch | none — branch operations forbidden in this design task |
| Work plan / canonical planning record | [WP-0133](../work-plans/WP-0133-scientific-typed-bindings.md), AIP-WP-0133-2026-09-08-001 |
| Acceptance notes | B01; [acceptance proposal](../specs/staqex-scientific-workflow-acceptance.md) |
| Adjudicator decisions | ADR 0217-A Architecture承認済み、B01 Phase 0 acceptance承認済み；Technology、Phase 1、Phase 2/Implementation、Phase 3は別承認 |
| Phase 1 Red approval | User approved `WP-0133 / LISS-0516 Phase 1 Red` on 2026-09-08; B01 tests added, no implementation |
| Phase 2 Green / Implementation approval | User approved `Phase 2 Green／Implementation承認` on 2026-09-08; B01 binding implementation added |
| Phase 3 review | User approved `WP-0133 / LISS-0516 Phase 3 Refactor` on 2026-09-08; behavior and assertions preserved |

Scope、Out of scope、検証、risk、完了条件、Luna phaseは上記WPを単一計画元とする。
このIssueは新規提案で、既存完了Issueを再開しない。承認済みscope/phaseの継承はない。

Phase 0 decision record: `BindingContract`／`DecodedBinding` の責務、明示
mappingのみ許可する規則、stale/unknown/axis/shape/source identityの診断、
6 fixtureと `tests/test_scientific_typed_bindings_red.py` の配置を確定した。

Process review: no operating-contract deviation or operational problem found.
