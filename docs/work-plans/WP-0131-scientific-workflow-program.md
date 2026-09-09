# WP-0131: 完成形 Scientific Workflow program

| Field | Value |
|---|---|
| Status / Phase | review / phase-0-design |
| Size initial/current | XL / XL — program coordination only; Luna実装単位ではない |
| Parent Issue | [LISS-0514](../issues/LISS-0514-scientific-workflow-program.md) |
| Authority | [完成形設計案](../architecture/scientific-workflow-complete-design.md)、[ADR 0217 Proposed](../architecture/adr/0217-scientific-workflow-metadata-and-projection.md)、[受入仕様案](../specs/staqex-scientific-workflow-acceptance.md) |
| Scope approval | 2026-09-08 全科学分野の設計修正を依頼済み |
| Implementation permission | none; tests/production/provider/branch/commit/PR/mergeは今回実行しない |
| Depends on | none for design; child implementation uses explicit dependency DAG below |
| Inventory count | 28 total records: this parent WP/LISS pair plus 27 child WP/LISS pairs |
| Current Next Issue | WP-0151/LISS-0534 Unit B Phase 1 Red; then WP-0139/LISS-0522 Phase 1 Red; QUBO is WP-0137/LISS-0520 |
| Review | [independent correction review record](../collaboration/reviews/2026-09-08-scientific-workflow-design-review.md) |

## [DESIGN CHECK]

- Scope and expected behavior: Architecture Path / Phase 0。S02最優先だが全科学分野の共通意味と完成条件を設計する。
- Specifications and files inspected: AGENTS、Quickstart、AT-TDD、conventions、readiness、current decision/open-work register、科学input/scopes/hybrid workflow/semantic core、S01 locked、旧S02、ADR 0210/0211/0212、既存WP台帳。
- Component boundaries: External Adapter / Metadata Graph / Domain Extension / binding / source-derived Semantic IR / Projection / Workflow。VO候補は観測・時空間・出典・不確実性・版・変換証跡。
- Applicable constraints: 現行source/state/Realize、clean dependencies、履歴非Normative、未承認技術非採用。
- Decisions/ambiguities: 設計Scopeのみ承認済み。dataset/assay/solver版、公平性policy、数値thresholdは各profileのPhase 0で決定。
- AI context: 関連Canonical/ADRと台帳を含め、実測data本体、秘密、無関係source、過去branchを除外。
- Task routing: Sol役で別task/worktreeのSora案を独立検証して設計修正。通常routing設定はsame_contextだが、本依頼の明示的な独立訂正loopを記録する。Lunaは承認された1WP/1phaseのみ。具体model overrideなし。
- Evidence contract: 指摘に根拠/修正先/未検証を添え、実装claimと設計proposalを区別。
- Verification: links/IDs/DAG/文書lifecycle/diff。コードとテスト実装・実機検証は行わない。

## Scope / Out of scope / completion

Scopeは創薬、災害、物理実験、天文、連続場/流体/重力/太陽MHD、離散系とその他profileの接続。
Modelの完成範囲はS01/S02に従属しない。通常WPはM。一部のsource/IR/状態境界を跨ぐWP（0137/0138/0143/0154/0156/0157）はreviewでMからLへ再分類し、各WP内にMのA/B unitsを定義した。Lunaへ渡すのは1 unit/1 phaseだけ。
未知技術、SDK、実機操作、DB、Rust migration、実験/災害指示はこのprogramの実装範囲外。

Program completionには下表全required縦切りの正常実行・失敗境界・source fidelity・再現証拠が必要。
S02の古典batchやlinear MHDだけで完了しない。特定研究用途の無限なSolver一覧を約束せず、
各分野のrequired profileをPhase 0で固定し、新分野は同じ拡張契約で追加できることを検証する。
科学的成功/優位は別の仮説判定であり、反証された結果も正しく報告できればsoftware受入と両立する。

Completion claimは二層に分ける。個別のclassical-only Scientific Workflowは対応profileの
観測・Model・Plan・Result・再現証拠だけで成立でき、量子laneを必須にしない。
完成形program全体のhybrid/quantum接続claimには追加でWP-0137/0158のQ01/D05証拠を要求するが、
それは個別classical workflowの有効性やS02次回batch提案を待たせない。

## Ordered roadmap

1. **共通core最小承認**: WP-0132。6分野のmetadata記録でS01/S02への過度な限定を防ぐ。
2. **S02実用古典縦切りを最優先**: 0133/0134 -> 0135 -> 0136、0138 -> 0139。
   0151の証拠契約を0139の最終評価前に統合する。実測dataとcutoffを早期に固定する。
   0137は独立に進められるが、未対応QPUをS02古典利用の待ち条件にしない。
3. **S02量子比較**: 0137/0151 + 完了した0139の固定problemを使い、同条件baseline、
   encoding/decode/棄却費用込みで検証する。これはWP-0158として別reviewし、
   0139の完了だけで量子比較済みにしない。実機はWP-0126へ別途依頼。
4. **S01検証縦切り**: 0140 -> 0141、共通0138と0151を利用。公平性/安全閾値は人間決定。
5. **天文・物理**: 0142は独立した天文profile。0132/0133と0143 -> 0145から
   0148 -> 0154、0157へ進み、物理実験を天文adapterの完了に依存させない。
6. **連続計算**: 0143 -> 0144/0145/0146、0144 -> 0147。
   0146 -> 0149 -> 0155 -> 0156でlinearから非線形流体・太陽MHDへ進む。
7. **離散系/自然言語/他分野**: 0150、0152、全profile証拠を0153で統合。

同時並行は依存関係上の可能性を示すだけで、この依頼はsubagentや実装の起動を指示しない。

## WP / LISS dependency inventory

各リンク先がScope / Out of scope / ADR / 受入 / 検証 / risk / 完了条件 / Luna phasesの詳細を持つ。
すべて新規提案であり、下表のstatusは実装着手状態を意味しない。

| WP / LISS | Scope title | Acceptance | Depends on | Status |
|---|---|---|---|---|
| [WP-0132](WP-0132-scientific-metadata-graph.md) / [LISS-0515](../issues/LISS-0515-scientific-metadata-graph.md) | 科学Metadata Graphの同一性と観測信頼 | G01/G02/G03 | none | proposed |
| [WP-0133](WP-0133-scientific-typed-bindings.md) / [LISS-0516](../issues/LISS-0516-scientific-typed-bindings.md) | 意味を保持する型付き古典入力とdecode | B01 | WP-0132 | proposed |
| [WP-0134](WP-0134-s02-measured-assay-profile.md) / [LISS-0517](../issues/LISS-0517-s02-measured-assay-profile.md) | S02実測assay取込とcuration | D01 | WP-0132 | proposed |
| [WP-0135](WP-0135-s02-leakage-safe-model.md) / [LISS-0518](../issues/LISS-0518-s02-leakage-safe-model.md) | S02 splitと予測Model検証 | D02 | WP-0134 | proposed |
| [WP-0136](WP-0136-s02-classical-batch-baseline.md) / [LISS-0519](../issues/LISS-0519-s02-classical-batch-baseline.md) | S02古典batch目的とfeasibility oracle | D03 | WP-0135 | proposed |
| [WP-0137](WP-0137-scientific-quantum-projection.md) / [LISS-0520](../issues/LISS-0520-scientific-quantum-projection.md) | 離散問題からQuantum Projectionの変換契約 | Q01 | WP-0133 | proposed |
| [WP-0138](WP-0138-scientific-workflow-lifecycle.md) / [LISS-0521](../issues/LISS-0521-scientific-workflow-lifecycle.md) | 期限・承認・再計画のWorkflow契約 | W01 | WP-0132 | proposed |
| [WP-0139](WP-0139-s02-assay-batch-cycle.md) / [LISS-0522](../issues/LISS-0522-s02-assay-batch-cycle.md) | S02次回assay batchの閉ループ | D04 | WP-0133, WP-0136, WP-0138, WP-0151 | proposed |
| [WP-0140](WP-0140-geographic-sensor-adapter-profile.md) / [LISS-0523](../issues/LISS-0523-geographic-sensor-adapter-profile.md) | CityGML・graph・SOSA/SensorThings接続 | X01 | WP-0132 | proposed |
| [WP-0141](WP-0141-s01-rolling-plan-validation.md) / [LISS-0524](../issues/LISS-0524-s01-rolling-plan-validation.md) | S01安全・公平・資源のrolling検証 | S01 | WP-0138, WP-0140, WP-0151 | proposed |
| [WP-0142](WP-0142-astronomy-observation-profile.md) / [LISS-0525](../issues/LISS-0525-astronomy-observation-profile.md) | ObsCore/VOTable天文観測縦切り | A01 | WP-0132, WP-0133 | proposed |
| [WP-0143](WP-0143-continuous-field-semantic-contract.md) / [LISS-0526](../issues/LISS-0526-continuous-field-semantic-contract.md) | 連続場・tensor・偏微分・IC/BCのsource契約 | F01 | WP-0133 | proposed |
| [WP-0144](WP-0144-finite-difference-solver-profile.md) / [LISS-0527](../issues/LISS-0527-finite-difference-solver-profile.md) | 有限差分RealizeとSolverPort | N01 | WP-0143 | proposed |
| [WP-0145](WP-0145-finite-element-solver-profile.md) / [LISS-0528](../issues/LISS-0528-finite-element-solver-profile.md) | 有限要素weak formとRealize | N02 | WP-0143 | proposed |
| [WP-0146](WP-0146-spectral-solver-profile.md) / [LISS-0529](../issues/LISS-0529-spectral-solver-profile.md) | スペクトルbasisと有限mode実行 | N03 | WP-0143 | proposed |
| [WP-0147](WP-0147-adaptive-mesh-conservation.md) / [LISS-0530](../issues/LISS-0530-adaptive-mesh-conservation.md) | 適応メッシュと保存的transfer | N04 | WP-0144 | proposed |
| [WP-0148](WP-0148-physical-experiment-gravity-profile.md) / [LISS-0531](../issues/LISS-0531-physical-experiment-gravity-profile.md) | 校正付き物理実験とNewton重力 | P01 | WP-0132, WP-0133, WP-0145 | proposed |
| [WP-0149](WP-0149-linear-fluid-mhd-profile.md) / [LISS-0532](../issues/LISS-0532-linear-fluid-mhd-profile.md) | 流体・MHD線形検証縦切り | P02 | WP-0146 | proposed |
| [WP-0150](WP-0150-discrete-interaction-profile.md) / [LISS-0533](../issues/LISS-0533-discrete-interaction-profile.md) | 一般離散graph・相互作用・Hamiltonian | R01 | WP-0133, WP-0137 | proposed |
| [WP-0151](WP-0151-scientific-reproducibility-evidence.md) / [LISS-0534](../issues/LISS-0534-scientific-reproducibility-evidence.md) | 分野共通の再現・反証・費用証拠 | E01 | WP-0133, WP-0138 | proposed |
| [WP-0152](WP-0152-natural-language-observation-candidates.md) / [LISS-0535](../issues/LISS-0535-natural-language-observation-candidates.md) | 自然言語由来観測候補の信頼境界 | L01 | WP-0132 | proposed |
| [WP-0153](WP-0153-cross-domain-conformance-completion.md) / [LISS-0536](../issues/LISS-0536-cross-domain-conformance-completion.md) | 分野拡張と完成判定のconformance | C01 | WP-0139, WP-0141, WP-0142, WP-0147, WP-0148, WP-0149, WP-0150, WP-0151, WP-0152, WP-0154, WP-0155, WP-0156, WP-0157, WP-0158 | proposed |
| [WP-0154](WP-0154-relativistic-gravity-profile.md) / [LISS-0537](../issues/LISS-0537-relativistic-gravity-profile.md) | 重力metric・gauge・初期拘束profile | P03/F01 | WP-0143, WP-0148 | proposed |
| [WP-0155](WP-0155-nonlinear-fluid-profile.md) / [LISS-0538](../issues/LISS-0538-nonlinear-fluid-profile.md) | 非線形流体とclosureの明示境界 | P04 | WP-0144, WP-0147, WP-0149 | proposed |
| [WP-0156](WP-0156-solar-mhd-profile.md) / [LISS-0539](../issues/LISS-0539-solar-mhd-profile.md) | 太陽/MHD観測結合と磁場拘束 | P05/A01 | WP-0142, WP-0147, WP-0149, WP-0155 | proposed |
| [WP-0157](WP-0157-inverse-ensemble-scientific-workflow.md) / [LISS-0540](../issues/LISS-0540-inverse-ensemble-scientific-workflow.md) | 逆問題・ensemble・実験再計画 | P06/E01/W01 | WP-0138, WP-0148, WP-0151 | proposed |
| [WP-0158](WP-0158-s02-quantum-baseline-comparison.md) / [LISS-0541](../issues/LISS-0541-s02-quantum-baseline-comparison.md) | S02量子projectionと古典baseline比較 | D05/Q01/E01 | WP-0137, WP-0139, WP-0151 | proposed |

## Required end-state coverage

| 分野 | 最低必要な実行証拠 | Owner |
|---|---|---|
| 創薬S02 | 実測assay由来の次batch、leakage-free retrospective cycle、別lane量子比較の可否/費用、prospective結果が無ければその限界 | 0134–0139、0151、0158、0153 |
| 災害S01 | 道路/需要イベント、時間内replan、safety/fairness/resource verdict、人間承認とfallback | 0140–0141 |
| 物理実験/逆問題 | sample/instrument/calibration、観測と推定、相関uncertainty、next-measurement cycle | 0148、0157 |
| 天文 | ObsCore/VOTable、time/frame/calibration、signalと非検出・coverage | 0142 |
| 連続場 | source PDE/IC/BC、vector/tensorとFDM/FEM/spectral各正常計算、AMR保存性 | 0143–0147 |
| 重力 | Newtonian Poissonと別profileのmetric/gauge/initial-constraint検証 | 0148、0154 |
| 流体 | linearとcompressible nonlinear/shock、closure明示、保存量 | 0149、0155 |
| 太陽/MHD | linear waveとsolar領域のvector磁場・観測/境界・divergence | 0149、0156 |
| 離散系 | 非S02 interaction/graph、Hamiltonian、QUBO/Isingの変換とdecode | 0137、0150 |
| その他科学計算 | 新profile一つのsource/binding/実行/Resultを追加し未知profile拒否を確認 | 0153 |
| 自然言語 | 候補の出典/否定/伝聞/信頼review。実測への自動昇格なし | 0152 |

## Existing-work reconciliation

現行の振る舞いはspec/ADRから、進捗はWP/LISSの最新closeoutから確認した。
古い途中経過や先頭のstaleなstatus文を新しい承認とはみなさない。

| Existing owner / observed ledger | 判定 | 新計画への引継ぎ |
|---|---|---|
| LISS-0513 / WP-0130 done | 維持、再開なし | Basic移管の事実を前提に新S02を0134–0139で新規定義 |
| WP-0093 A–E complete | 後継、新scope | 合成選択境界の旧証拠。新S02の実測科学根拠として流用しない |
| LISS-0443 / WP-0106 complete、WP-0115 complete | 維持 | numerical identity/blackboard境界を再利用。実測hit改善の証拠ではない |
| LISS-0035 local Workflow complete、scientific input scalar slice accepted | 拡張後継 | 0133/0138でtyped metadata/deadline/replanを追加。Job engine複製なし |
| WP-0107 consumer-wide pending、WP-0108 bounded complete | 統合、現行未完了owner維持 | 0133/0143等のPhase 0で該当consumer inventoryを確認。未完了consumer移行を子WP内へ無言吸収しない |
| WP-0092 public observation execution open、LISS-0480/0481 bounded metadata shipped | 別scope維持 | 科学Observationは量子Observation algebraではない。新lexiconや観測algebraを本計画で実装しない |
| WP-0120 bounded readiness complete / broader families deferred | family-specific新規 | 0143–0156を新profile ownerとし、QASM readiness成功をSolver実装と扱わない |
| WP-0121 finite artifact、WP-0122 QASM、WP-0123 bounded Host、WP-0124 offline evidence complete | 再利用 | 0137/0138/0151は既存artifact/Job/security/evidenceへ接続。承認済み範囲を拡大しない |
| WP-0125 ready conditional、WP-0126 proposed human-run | 独立維持 | 実機/SDK/credentials/運用は既存ownerへ。科学coreの実装待ち条件にしない |
| WP-0128 bounded Phase 3 complete / broad follow-ups open、WP-0129 done | 維持 | tensor/policyの既存正常形を守る。0143のfield/tensorを別scopeで設計 |
| LISS-0504 done、既存continuous discretization bridge accepted | 維持、後継 | source/contract provenance修復は完了。現行specは数値離散化を明示defer。0143–0147はその新scopeで、bridge記録を数値実行証拠にしない |
| WP-0118/0119 approved planning baseline | 補完 | WP-0131/open-work側から実機readiness計画を参照し、既存本文や以前のscope承認は変更・継承しない |

再開が必要と判断した既存done WPはない。未完了consumer/observationのownerも変更しない。
新規分割・統合方針そのものはAdjudicator review待ち。旧記録の本文や承認履歴は書き換えない。
既存WP-0117の重複番号は観察された台帳上の既知問題として保持し、この設計で再採番しない。

## Approval separation and next smallest package

| Approval type | 今回の状態 | 次に審査する具体的対象 |
|---|---|---|
| Scope | 全科学Workflow設計修正は依頼済み | WP-0131の新規分割・依存・後継判断。着手は一つのchild WPごと |
| Architecture | 0217-Aのみ承認済み | Metadata/IR権威、adapter mapping、非実行境界。binding/profile/projection/Workflow/approvalは0217-B/Cまたは各WPで別途審査 |
| Technology selection | 未承認 | adapter/library/version/dataset profileごと。DB/RDF engine/SDKを暗黙採用しない |
| Phase | Phase 0設計修正のみ | M0仕様をreview後、LISS-0515 Phase 1 Redを別承認 |
| Implementation | 明示的に禁止 | Phase 1 testsのreview後、LISS-0515 Phase 2と実装範囲を別承認 |

**次の最小パッケージ M0:** WP-0132/LISS-0515のG01/G02/G03受入仕様審査。
Graph記録validationだけ、6小fixture、
外部reader/SDK/DB/source syntax/実行は含まない。
ADR 0217-B/C、全roadmapのArchitectureや実装をまとめて承認する依頼ではない。Architectureとacceptanceを審査し、
その後Phase 1 Redを独立して許可する。Technology選定はM0に不要。

実測assay選定をM0の待ち条件にしない。S02で次に必要なdecisionはWP-0134の
Dataset/target/endpoint/curation profileで、これを未決のままLunaへ実装依頼しない。

## 後続phase受付・Luna委譲の指示案

以下は次回指示文の提案であり、AGENTS/runtime routingを変更せず、他taskへ送信もしない。

> 完成形Scientific Workflowの受付・設計調整を担当してください。最初にcurrent decision/open-work
> registerとADR 0217案、完成形設計、WP-0131、選択したchild WPの受入だけを確認してください。
> 旧S02はBasic移管済みで、新S02は実測活性データから次回assay batchを選ぶ科学Workflowです。
> S01/S02を共通モデルの上限にしないでください。
> まずM0（WP-0132/LISS-0515、G01/G02/G03）のArchitecture/acceptance審査をまとめ、
> 承認後にPhase 1を別途求めてください。Lunaには承認された1 WPまたは1 unit/1 phaseとfixture/期待結果/許可path、
> dependency状態、外部port、negativeと隣接positive例、停止条件だけを渡してください。
> Scope、Architecture、Technology、Phase、Implementationを分けて記録してください。
> Parser/IR/consumer能力をDTOの存在で代用せず、metadata-only実装を言語機能と呼ばないでください。
> 別lane fallback、出典/欠損/観測と推定、期限/承認、leakage、費用/反証をreview対象にしてください。
> 完了した旧WPを再開せず、既存consumer/observationの未完了ownerと衝突したら別の受入scopeを提示してください。
> 実機/SDK/認証はWP-0123/0126の独立タスクに残してください。今回の文書だけを根拠に実装しないでください。

## AI planning record

- ID: AIP-WP-0131-2026-09-08-001; status: proposed; author: Sol role / Codex desktop.
- Model/reasoning: N/A — role指定であり構成表示値は取得していない。date: 2026-09-08.
- Size: XL; route: 別task/worktreeでSora案をSolが独立点検し設計修正。
  修正後のfresh independent contract reviewはapprove（findingsなし）で完了。
  Lunaへはchild WPの各phaseを別指定。
- Estimated tokens range/midpoint/metric: N/A — 全分野profileのtech/acceptance未固定で信頼できる見積なし。
- Basis/assumptions/confidence: 既存port/IRを再利用し、1境界/1代表profileに分割。medium。
- Revises: Sora draft proposal。WP-0093/0118/0119の履歴本文は変更せず、
  新program側で後継・接続関係だけを記録。
- Execution trace: [2026-09-08](../collaboration/traces/2026-09-08-scientific-workflow-design.md).
