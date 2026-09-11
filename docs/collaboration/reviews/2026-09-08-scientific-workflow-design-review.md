# Scientific Workflow design correction review

| Field | Value |
|---|---|
| Phase / scope | Architecture Path / phase-0-design。依頼された全科学分野の設計修正だけ |
| Review isolation | same_context。作者がdiskの成果物を読み直すreviewで、separate_contextより弱い。独立レビュー済みではない |
| Result | 設計修正packetを提出可能。Architecture承認/Phase 1 readinessは未成立 |
| Implementation permission | no。code/tests/branch/commit/PR/merge操作なし |
| Review target | [完成形設計案](../../architecture/scientific-workflow-complete-design.md)、[ADR 0217](../../architecture/adr/0217-scientific-workflow-metadata-and-projection.md)、[受入案](../../specs/staqex-scientific-workflow-acceptance.md)、[WP-0131](../../work-plans/WP-0131-scientific-workflow-program.md) |
| Next approval | Architecture 0217-AとM0 acceptanceの審査。Phase 1/Implementationは別の後続判断 |
| Post-review requirement | AdjudicatorのArchitecture判断、L/XL設計の独立した契約review。その後に個別phase承認 |

## Review basis actually inspected

- 現行: Project conventions、current decision register、open-work register、DEC-0006、
  Scientific Semantic Core、scalar scientific input、scientific scopes、hybrid/workflow surface、
  continuous discretization、classical/quantum realization boundaries、ADR 0210/0211/0212。
- 既存縦切りの境界: S01 locked scenario、旧S02 acceptance、WP-0093/0106/0130、LISS-0513 closeout。
- 既存未完了/完了owner: WP-0092/0107/0108/0118/0119/0120–0126/0128/0129、
  LISS-0035/0443–0445/0480/0504。台帳は進捗の証拠であり仕様の代用ではない。
- 新成果物: architecture/ADR/spec、全WP/LISSのfieldとdependency inventory、
  M0とS02量子比較packetを再読。新規file全体のlink/ID/DAG/phase-policyを機械検査。
- 外部標準: OGC CityGML/SensorThings、W3C SOSA/SSN/PROV-O、IVOA ObsCore/VOTable、
  ChEMBL/RDKit一次資料を公開文書で確認。mappingは設計者の提案、準拠/採用版は未認定。

## Findings and dispositions

| ID / severity | 根拠・不足/衝突 | 修正とdisposition |
|---|---|---|
| R01 / high | 旧S02 specのsynthetic manifest/8–16候補/selection boundaryとWP-0130完了は、実測hit-to-leadの受入ではない | apply: 新D01–D04と0134–0139/0158。旧specにlineage notice、WP-0093に後継案内。旧成績の意味は変更しない |
| R02 / high | scalar input specはgeometry/tensor/uncertainty/qualityをdefer。host配列やcallbackで意味保存を証明できない | apply: core metamodelとB01、WP-0132/0133。units/axes/time/frame/missing/sourceとobserved/estimatedを保持 |
| R03 / high | Metadata Graphを新IRにするとADR 0211のsource-derived authorityと衝突 | apply: Graphは記述のみ、Binding+sourceを経てIRへ。caller DTO注入禁止、0217-Aとして分離 |
| R04 / high | continuous bridge specは数値離散化をdefer。LISS-0504のprovenance回復だけではSolver対応にならない | apply: F01/N01–N04と0143–0147。source構造、IC/BC、FDM/FEM/spectral、AMR/保存性の成功と拒否を分離 |
| R05 / high | hybrid workflowはimmutable iterationとterminal resultに限定。deadline、late event、approval expiry、Plan採用が不足 | apply: W01/WP-0138。Job完了とPlan採用を分け、stale結果とcancel raceを検証 |
| R06 / high | 旧S02のno-classical-substitutionと実用fallbackが無区分だと衝突 | apply: target拒否を保持したまま明示別Job/lane。QPU成功に偽装しない。hard制約緩和は人間の別判断 |
| R07 / high | 既存fixed-seed benchmarkは実測データのリーク防止・科学的再現性を保証しない | apply: D02/E01、cutoff/group split、train-only fit、反証/失敗を含む費用、0151を0139/0141の明示依存に修正 |
| R08 / medium | S01 storyだけでは天文、重力、fluid/MHD、離散系を十分検証できない | apply: 0142–0157の分野profileとcoverage表。linear/Poissonだけの完了にしない |
| R09 / high | QUBO/Ising/Hamiltonianの意味とProjectorの実機可能性が混同されやすい | apply: Q01、offset/scale/index/energy全小割当検証、非unitary/QPU拒否、postselection overhead |
| R10 / medium | 自然言語confidenceを実測uncertaintyへ転用すると証拠の種類を壊す | apply: L01/0152、candidate/source span/否定/伝聞/reviewと型付き実測を別に扱う |
| R11 / medium | 完了したWP-0093/0106/0130を大規模後継scopeで再開すると履歴が漂流する | already closed with evidence: 既存closeoutを維持。新28 WP/LISS（親1+子27）を提案し、open-workに追加 |
| R12 / high | 全完成形ADRを最初の実装許可と誤認し得る | apply: 0217-A/B/Cと承認種類を分割。M0はmetadata受入だけ、B/CとPhase 1/2は未承認 |
| R13 / medium | S02量子比較が0139後の名前のない将来作業では実施漏れになる | apply: WP-0158/LISS-0541を追加、0153完成gateの依存に含めた |
| R14 / medium | 旧S02に`when`撤去記述、現行conventionsにstate-preserving `when`記述があり、履歴を現行として読むと衝突 | out of scope: 本設計でsyntax/既存受入を変更しない。新語彙を使うchild Phase 0は現行language specとownerの照合が必要。M0はsyntaxに依存しない |
| R15 / medium | 既存WP-0117のfilename重複でIDが一意でない | out of scope: 新規番号は0131以降を使用し重複なしを検査。既存再採番/移動は別ledger整理scope |

| R16 / medium | source/IR/consumerと複数状態境界のWPを一律Mとする見積は過小 | apply: 0137/0138/0143/0154/0156/0157をM→Lに再分類。各WPを独立承認するMのA/B unitsへ分け、一括Luna実装を禁止 |

## Failure-oriented re-review

再読では「6分野でも同じscalar recordだけになる」「unknown CRSを勝手に補完」
「理想式inspectが数値解扱い」「unsupported targetが古典成功に書換えられる」
「deadline内計算だがapproval期限切れ」「future assay結果がfitに入る」
「AMRの局所error改善で大域保存が壊れる」「QUBO定数offsetがdecodeで失われる」を確認した。
各項目は受入のnegative caseと、正当な0/unknown保管/明示換算/隣接Hamiltonian/正常Job等の
positive caseに対応する。実装で通過したことはまだ検証していない。

## Remaining blockers and limits

- ADR 0217は未承認。M0受入に対する人間review/独立契約reviewは未実施。
- 実測S02 target/assay/data release/license、model/baseline、数値profile/solver版、
  fairness/safety閾値は各Phase 0 decision。後続WPはPhase 1-readyと主張しない。
- 現行コード全体の再監査・全テスト実行は今回の設計依頼の対象外。
  既存完了claimはcloseoutの記録に基づき、本作業で再実証していない。
- 通常のdomain実行をunsupported診断だけで済ませることは完成gateを満たさない。

## Review target for Adjudicator

- Approved scope: 全科学Workflowの設計修正だけ（2026-09-08依頼）。
- Current phase: Architecture Path / Phase 0。
- Requested next review: **Architecture 0217-A**、WP-0132/LISS-0515の**M0 acceptance**。
- Implementation allowed: **no**。Technology selection: M0には不要。
- Post-review: 人間決定をartifactへ記録し、Phase 1 Redは別承認。Greenはreviewed Redの後に別承認。
- Decision: pending。Approved/approved with comments/rejectedのいずれも代理記入しない。

これはレビューすべき具体的な設計packetで、承認済み状態を作るものではない。
[Same-context review skill](../../../.agents/skills/same-context-review/SKILL.md)の
“When to escalate”はADR変更および作者とreviewerが同じL以上の作業をAdjudicator判断へ送る。
本packetはその条件に該当するため、自己reviewを独立承認として閉じない。

## Verification

決定的検査の最終結果と全変更file一覧は
[execution trace](../traces/2026-09-08-scientific-workflow-design.md)に記録する。
source code/production testsの追加・編集なし。外部SDK/data download/live submissionなし。
