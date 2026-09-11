# LISS-0517: S02実測assay取込とcuration

| Field | Value |
|---|---|
| Local ID | LISS-0517 |
| Status | done |
| Phase | complete |
| Type / priority | feature / P0 |
| Initial/current size | M / M |
| Owner | Sol independent design correction; Luna only after phase-specific approval |
| GitHub issue | none |
| Parent | LISS-0514 |
| Depends on | LISS-0515 |
| Blocks | LISS-0518 |
| Related branch | none — branch operations forbidden in this design task |
| Work plan / canonical planning record | [WP-0134](../work-plans/WP-0134-s02-measured-assay-profile.md), AIP-WP-0134-2026-09-08-001 |
| Acceptance notes | D01; [acceptance proposal](../specs/staqex-scientific-workflow-acceptance.md) |
| Adjudicator decisions | ADR 0217-A Architecture承認済み、D01 Phase 0 acceptance承認済み、Phase 1 Red承認済み、Phase 2 Green / Implementation承認済み、Phase 3 Refactor承認済み、Phase 3最終レビュー承認済み |

Scope、Out of scope、検証、risk、完了条件、Luna phaseは上記WPを単一計画元とする。
このIssueは新規提案で、既存完了Issueを再開しない。承認済みscope/phaseの継承はない。

Phase 0 decision record: 単一target／biochemical assay-family／IC50・nM
profile、raw snapshotのchecksum/license、compound/target/assay/activityの
分離、censoring・replicate保持、DataPort/ChemistryPort境界、quarantine診断、
6 fixtureと `tests/test_s02_assay_profile_red.py` の配置を確定した。

Phase 1 Red record: `tests/test_s02_assay_profile_red.py` に、互換IC50の受入、
censoring保持、endpoint/unit不一致、replicate identity衝突、activity identity
衝突、checksum/license欠落の失敗契約を追加した。実装モジュールは未作成で、
Phase 2/Implementation承認まではコードを追加しない。

Phase 2 Green record: `compiler/staqex/s02_assay_profile.py` を追加し、
凍結raw snapshotを変更せずにcurated revisionを生成する最小実装を行った。
互換IC50/nMのrelation保持と、endpoint/unit/relation/target/provenance、
activity identity、replicate identityのquarantine診断を実装した。

Phase 3 Refactor record: record-level検証を`_record_diagnostic`へ集約し、
診断コードと受入意味を変えずに重複分岐を整理した。snapshot revisionの
型境界も明示し、受入・censoring・quarantineの再検証を完了した。

Process review: no operating-contract deviation or operational problem found.

Final review record: 2026-09-09に承認。D01 bounded sliceを完了とし、provider／
実データ取得／chemistry normalizationは別作業として残す。詳細は
[Review Summary](../collaboration/reviews/2026-09-09-liss-0517-phase3-final-review.md)。
