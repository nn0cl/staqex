# LISS-0541: S02量子projectionと古典baseline比較

| Field | Value |
|---|---|
| Local ID | LISS-0541 |
| Status | done |
| Phase | done |
| Type / priority | feature / P1 |
| Initial/current size | M / M |
| Owner | Sol independent design correction; Luna only after phase-specific approval |
| GitHub issue | none |
| Parent | LISS-0514 |
| Depends on | LISS-0520, LISS-0522, LISS-0534 |
| Blocks | LISS-0536 |
| Related branch | none — branch operations forbidden in this design task |
| Work plan / canonical planning record | [WP-0158](../work-plans/WP-0158-s02-quantum-baseline-comparison.md), AIP-WP-0158-2026-09-08-001 |
| Acceptance notes | D05/Q01/E01; [acceptance proposal](../specs/staqex-scientific-workflow-acceptance.md) |
| Adjudicator decisions | ADR 0217/acceptance review; profile/technology if needed; distinct Phase 1, Phase 2/Implementation, Phase 3 approvals |

Scope、Out of scope、検証、risk、完了条件、Luna phaseは上記WPを単一計画元とする。
このIssueは新規提案で、既存完了Issueを再開しない。承認済みscope/phaseの継承はない。

Phase 0 profile review record: WP-0158でD04固定snapshot、D03の5候補oracle/baseline、
Q01 `.sqxa` artifact、E01 manifestを同一problem lineageへ固定した。1候補1 binary carrier、
明示variable order、cardinality/diversity penalty、terminal budget verifier、decode/feasibility
独立検算、全overheadのlane別証拠、量子lane拒否時の`inconclusive`扱いを決定した。
Phase 1 testsは`tests/test_s02_quantum_baseline_comparison_red.py`に置き、fake portsと固定fixture
だけを使用する。新規dependency、provider SDK、AWS Braket、live QPUは選択しない。

Numeric policyはfloat64、energy/objective absolute tolerance `1e-12`、identity/decoded IDs/constraint
verdictは完全一致とする。期待diagnosticはWP-0158記載の量子lane fail-closed群を使用する。
一般budget quadratization、alternative encoding、sampled finite-target統計、provider mappingは
別Phase 0 decision boundaryであり、本Issueへ無言吸収しない。

Historical Phase 0 outcome before approval: acceptance/profile review complete;
Adjudicator acceptance was pending.

Adjudicator accepted the Phase 0 profile. Phase 1 Red is now ready, but no
implementation permission is granted. Next request:
`LISS-0541 Phase 1 Red 承認`.

Phase 1 Red record: `tests/test_s02_quantum_baseline_comparison_red.py`に5件のD05契約を追加した。
正常一致、候補集合不一致、decode/constraint違反、quantum runtime拒否、cost欠落を対象とし、
fake/in-memory laneだけを使用する。focused pytestは実装モジュール未存在による5件の意図した
failure、`py_compile`と`git diff --check`はpass。次の承認対象は
`LISS-0541 Phase 2 Green / Implementation 承認`である。

Phase 2 Green record: `compiler/staqex/s02_quantum_baseline_comparison.py`にprovider-neutralな
lane比較を実装した。candidate identity、decode/feasibility、objective tolerance、cost完全性を
検証し、quantum runtime拒否はclassical fallback付き`inconclusive`として保持する。Red suiteは
変更していない。focused pytestは5 passed、`py_compile`と`git diff --check`もpass。次の承認対象は
`LISS-0541 Phase 3 Refactor 承認`である。

Phase 3 Refactor record: selection equality、missing-cost result、matched result生成をhelperへ
分離した。public DTO、診断コード、lane precedence、tolerance、fallback挙動、Red suiteは維持。
focused pytestは5 passed、`py_compile`と`git diff --check`もpass。次の承認対象は
`LISS-0541 Phase 3 最終レビュー 承認`である。

Final review disposition (2026-09-11): D05/D03/Q01 focused verificationは14 passed。
一方、snapshot/cutoff、profile、baseline/artifact、encoding、manifestのlane identityが
machine-checkされず、outer `ComparisonInput`に一度だけ保持されているため、異なる入力を
比較できる余地がある。Phase 3最終レビューは未承認とし、次にlineage contractのPhase 1 Red
追補が必要である。次の承認対象は`LISS-0541 Phase 1 Red lineage-contract correction 承認`。

Phase 1 Red lineage-contract correction record: lane fixtureへsnapshot、candidate set、profile、
baseline、artifact、encoding、manifestのidentityを追加し、snapshot/artifact不一致のquarantineと
matched resultでのlineage保持を検証する2件を追加した。既存5件のD05契約は意味を変更していない。
実装は変更せず、focused pytestは7件の意図したfailure（`LaneResult`/`ComparisonResult`未対応）を
全件収集し、`py_compile`と`git diff --check`はpass。次の承認対象は
`LISS-0541 Phase 2 Green / Implementation 再承認`。

Phase 2 Green lineage-contract correction record: `LaneResult`へ7つのlineage identityを追加し、
lane間および`ComparisonInput`の期待値との照合を実装した。不一致は比較成立前にfail-closedで
quarantineし、matched `ComparisonResult`へlineage証跡を保持する。既存の候補、制約、objective、
cost、runtime rejection/fallback挙動は維持。focused pytestは7 passed、`py_compile`と
`git diff --check`もpass。次の承認対象は`LISS-0541 Phase 3 Refactor 承認`。

Phase 3 Refactor record: lineage field listとdiagnostic mappingをprivate helper/constantへ集約し、
重複した照合ロジックを整理した。public DTO、assertion、diagnostic code、precedence、fallback挙動は
変更していない。D05および関連S02 focused pytestは16 passed、`py_compile`と`git diff --check`もpass。
次の承認対象は`LISS-0541 Phase 3 最終レビュー 承認`。

Final review record (2026-09-11): D05のlineage、candidate identity、decode/feasibility、objective
tolerance、cost、runtime rejection境界を確認し、blockerなし。D05および関連S02 focused pytestは
16 passed、`py_compile`と`git diff --check`もpass。provider SDK、network、credential、live QPUは
引き続き対象外。Process review: no operating-contract deviation or operational problem found.
LISS-0541はbounded provider-neutral comparison kernelとしてdone。広い科学profileとprovider deliveryは
別タスクで扱う。
