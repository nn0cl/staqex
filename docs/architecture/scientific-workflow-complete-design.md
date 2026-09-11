# Staqex 完成形 Scientific Workflow 設計

| 項目 | 状態 |
|---|---|
| 文書の役割 | 完成形設計の単一提案元。Current proposal / 非Normative |
| 承認 | 2026-09-08 ADR 0217-AのArchitecture承認済み。0217-B/C、Technology / Phase 1 / Implementationは未承認 |
| Review | Solが別task/worktreeでSora案を独立点検後に修正。修正後のfresh independent contract reviewは完了（approve / findingsなし）。0217-Aは承認済み、Phase 1 / Implementationは未承認 |
| 決定案 | [ADR 0217](adr/0217-scientific-workflow-metadata-and-projection.md) |
| 受入案 | [Scientific Workflow acceptance](../specs/staqex-scientific-workflow-acceptance.md) |
| 計画 | [WP-0131](../work-plans/WP-0131-scientific-workflow-program.md) |
| 現行の優先契約 | [Project conventions](../collaboration/project-conventions.md)、[ADR 0211](adr/0211-scientific-semantic-core-and-ir-authority.md)、[ADR 0210](adr/0210-formal-limit-finite-realization-policy.md)、[ADR 0212](adr/0212-ideal-meaning-and-finite-realization-boundary.md) |

この文書は完成形の責務と検証経路を提案する。記載された型名は概念契約であり、
新しいStaqex構文、実装済みAPI、採用済みライブラリを意味しない。
承認前の実装は現行Canonical仕様に従う。承認後も実装能力は各受入証拠で別に判定する。

## 1. 対象と優先順位

創薬、災害対応、物理実験、天文観測、流体、重力、太陽/MHD、離散系、その他の科学計算を扱う。
S02は実測活性データからhit-to-leadの次回アッセイ用化合物バッチを選定する最優先の実用縦切り。
S01は観測・イベント・不確実性・安全制約・公平性・資源配分・人間承認・ローリング再計画・監査・
フォールバックを検証する縦切りとする。両者は共通モデルの上限ではない。

旧S02の合成データ選択境界サンプルはLISS-0513でBasicへ移管済み。
旧S02の8–16候補、bit-pattern、固定seedの成績は新S02の科学的有効性を示さない。
S01の既存locked storyは保持し、拡張契約が承認されるまで既存例の意味を変更しない。

完成の判定は全分野に万能Solverを作ることではない。各科学的主張について、黒板式、型付き入力、
変換、計算、観測/推定、検証結果が追跡でき、分野ごとの代表実行と不支持境界が確認できること。
未対応Solverの拒否だけをもって、その分野の完成と数えない。

## 2. 意味と依存の境界

```text
External Adapter
    -> Canonical Scientific Metadata Graph (観測・記録の意味、版、信頼状態)
    -> Domain Extension (分野固有制約、解釈、モデル構築)
    -> validated BindingContract + source mathematical declarations
    -> typed source/HIR -> Scientific Semantic IR
    -> CPU / Simulator / explicit Realize / QASM / QPU Projection
    -> typed Result -> new Observation/Model revision -> next Workflow cycle
```

これはデータの流れであり、AdapterがDomain policyを所有する依存関係ではない。
Domainは外部標準、SDK、ファイル、Graph DBに依存しない。UseCaseが検証・信頼昇格・計画・
実行・採用を決め、AdapterはPortを実装する。UIはcommand/queryと表示用状態だけを見る。
Graphは論理モデルであり、RDFストア、OWL推論エンジン、DB、JSON-LD採用を決めない。

| 層 | 所有する意味 | 禁止する意味の追加 |
|---|---|---|
| External Adapter | 外部ID・版・元フィールド・schema validation・値の読み出し | 妥当性の科学的判断、単位/CRSの推定、目的関数、暗黙の欠損補完 |
| Metadata Graph | 記述の同一性、関係、時空間、根拠、信頼状態 | 生の式文字列から実行を許可すること |
| Domain Extension | assay互換性、道路可達性、天文calibration、保存則等の宣言と検証 | SDK依存、S01/S02固有ルールのcoreへの固定 |
| Binding UseCase | 型/次元/軸/意味/版の適合、変換記録、検証済み入力封筒 | hostキーの存在だけで信頼すること |
| Scientific Semantic IR | source由来の構造化された実行意味と型、位相、正確性 | Graph、AST形、外部DTOを独立した実行意味源にすること |
| Projection | 能力判定済み変換、誤差・資源契約 | 許可のない有限化、古典/量子の入替え |
| Workflow | snapshot、Job、期限、承認、再計画、結果採用 | Theoryの変更、実行中Stateから古典値を抜くこと |

数式を最初に定義し、その後にBindingsと実行方針を記述する。Unicode黒板表示は表示層であり、
現行ASCII source契約を変更しない。物理法則を配列shapeやhost callback名から逆定義しない。
Modelのformula参照だけでは実行できない。source nodeとの結合が必要で、式編集は新Model版になる。
Graphから生成されたsourceも通常のparser/typecheck/IR検証を通し、生成器のDTOを直注入しない。

## 3. 共通メタモデル

全記録はnamespaced ID、revision、schema/profile version、source reference、quality/review stateを持つ。
IDの同値性は外部名の文字列一致から推測しない。同一性の統合にはmapping evidenceが必要。
値はimmutable snapshotで扱い、訂正はsupersedes関係として追加する。

| 概念 | 必須の意味と関係 |
|---|---|
| Entity / Relation | 型付き対象と方向/役割を持つ関係。node/edge、parallel edge、hyperedgeは役割付きrelationとして表現可能。関係にも有効期間と出典 |
| Observation | FeatureOfInterest、ObservableProperty、Procedure、Instrumentまたは観測者の役割、Result、phenomenon/result/ingest time、evidence。観測行為と値を分離 |
| ObservableProperty | quantity kind、dimension、許容unit、値域/分類語彙。測定可能性を定義し、quantum Observableとの同一視をしない |
| Instrument | sensor、装置、観測系。校正版、能力、配置、有効期間。計算モデルを測定器と偽らない |
| Procedure | 測定/試料化/推定/シミュレーションの方法、版、入出力型、条件 |
| FeatureOfInterest | 観測が何について述べるか。建物、分子、天体、場の領域、物理系などEntityの役割 |
| Sample | 対象から採取/生成した試料。isSampleOf、採取手順・時刻・母集団/位置。chemical sample、simulation sample、quantum shotを区別 |
| Event | source event ID、発生/受信時刻、有効区間、影響対象、優先度根拠、dedup key。観測からのイベント推定は別evidence |
| Time | instant/interval、time scale/calendar/epoch、precision、unknown。phenomenon timeとresult timeとingest timeを混ぜない |
| Space | geometry/topology/domain、CRS/frame、orientation、epoch、coverage/resolution。天球、物理座標、meshを経緯度へ強制しない |
| Uncertainty | distribution/interval/covariance/ensemble/censoring/unknown、unit、coverage、相関group、方法。AI confidenceと測定誤差を混同しない |
| Evidence | 原記録/文献/検証への参照、content hash、span、取得時刻、権利、支持/反証するclaim。重複出典は独立証拠に数えない |
| Provenance | 入出力entity、activity、agent/role、used/derivedFrom/generatedBy、policyとsoftware版。来歴DAGとdomain graphのcycle許容を区別 |
| Dataset | immutable manifest、partition、schema、license/access policy、checksum、欠損規則、coverage、raw/curated/derived区分 |
| Model | 方程式/仮定、source参照、fit対象Dataset版、パラメータ、妥当領域、校正/検証、discrepancy。学習器と物理モデルの双方 |
| Objective | 対象decision変数、方向、尺度、単位、集約/優先順位、評価Procedure、科学的仮説との関係 |
| Constraint | hard/soft、定義域、適用時間、predicate、根拠、閾値、承認者。ペナルティとhard feasibilityを分離 |
| Plan | input snapshot、Model/Objectives/Constraints版、actions、資源、期限、approval、fallback。案/実行承認/実行済みを分離 |
| Result | value/carrier、status、observed/estimated/simulated/symbolic区分、uncertainty、quality、method、input/Job/Plan/evidence参照 |

値carrierはscalar、category、vector、tensor、field、graph、distribution、symbolic relation、artifact referenceを
区別する。shapeだけでなくaxis name、index domain/order、basis、variance/covariance、unitとmissing maskを保持する。
欠損はunknown/not-measured/not-applicable/below-detection/invalid/redactedを区別し、0やNaNへの無言変換を禁止。
必須情報が無いraw記録はquarantineできるが、実行可能なbindingにはしない。
すべての記録に科学的に不要なCRS等を要求せず、profileごとにrequired/optional/not-applicableを定義する。

信頼状態はcandidate -> validated -> reviewed/approved、またはrejected/superseded。
validatedは型とschemaが合うことだけを示し、科学的妥当性や意思決定承認を含まない。
外部の実測と、自然言語から抽出された「観測したという主張」と、モデル予測を別種に保持する。

## 4. 外部標準・既存エコシステムの接続

下表のmappingはStaqex側の**設計提案**で、標準全体への準拠宣言ではない。
外部クラスをStaqex class/keywordとして全コピーしない。Adapter profileごとに版、対応範囲、
必須mapping、変換理由、保持する未解釈拡張、拒否項目を契約化する。

ここでは二段階のgateを分ける。mapping proposal は外部概念を内部のどの意味へ接続し、
何を推定・昇格してはならないかだけを示す。profile decision は特定version/encoding/subset、
必須field、round-trip/loss policy、license、採用Adapter/libraryを別のTechnology/Phase 0判断で固定する。
下表はすべて前者であり、後者は未決定である。

| 外部語彙/形式 | 提案mappingと守る境界 | 一次資料 |
|---|---|---|
| CityGML | city object -> Entity/FeatureOfInterest、geometry/LoD -> Space、relations -> typed Relation。道路の通行可否は別Observation/Domain判定 | [OGC CityGML](https://www.ogc.org/standards/citygml/) |
| node/edge graph | 外部node/edge IDと方向・多重辺・重み単位を保持。建物隣接、交通到達、分子結合、interaction edgeを同一predicateにしない | 本設計のEntity/Relation契約 |
| SOSA/SSN | 観測、property、procedure、sensor、sample、FOIを役割付きで接続。量子測定の新syntaxを導入しない | [W3C SOSA/SSN](https://www.w3.org/TR/vocab-ssn/) |
| OGC SensorThings | Thing/Location/Sensor/Datastream/ObservedProperty/Observation/FOIの参照を残す。Sensing取込とTaskingによる実操作を分離 | [OGC SensorThings](https://www.ogc.org/standards/sensorthings/) |
| IVOA ObsCore / VOTable | Dataset発見用metadataとtable交換を区別。obs identity、spatial/time/spectral coverage、units、UCD、null、array metadataを保持 | [ObsCore](https://www.ivoa.net/documents/ObsCore/)、[VOTable](https://www.ivoa.net/documents/VOTable/) |
| PROV-O | entity/activity/agentとused/generated/derivedの来歴交換。StaqexのEntityとPROV Entityのmapping範囲をprofileで宣言 | [W3C PROV-O](https://www.w3.org/TR/prov-o/) |
| ChEMBL | compound/target/assay/activity/sourceを別IDで保持。endpoint、relation、unit、assay contextを落とさない | [ChEMBL data questions](https://chembl.gitbook.io/chembl-interface-documentation/frequently-asked-questions/chembl-data-questions) |
| RDKit | 化学構造読取・記述子・類似度等をChemistryPort越しに利用。standardization/descriptor設定と版を記録し再実装しない | [RDKit documentation](https://www.rdkit.org/docs/GettingStartedInPython.html) |
| 自然言語 | source span付きObservationCandidate。日時/単位/対象/否定/伝聞/不確実性を保持。人間の確認前にvalidatedな実測へ昇格しない | [AI I/O contract](io-reasoning-contracts.md) |

標準・SDKの採用版は未選定。技術選定時にversion-specific資料、license、脆弱性、最小実ファイル、
欠損/unknown extension、round-trip/意味保存の契約テストを確認する。GIS、天文table/coordinate、
化学構造、数値SolverをKernel内に複製しない。完全なbyte round-tripを意味保存の必須条件にはせず、
非対応の実行意味はquarantine/reject、未解釈raw拡張はhash付き参照に残す。

## 5. 黒板・連続場・Solver

典型的な黒板契約は以下。これは数式であり、未承認のStaqex構文例ではない。

- 場: u : Ω × I -> V。Vはscalar/vector/tensor fiberで、座標frameとunitを持つ。
- PDE: F(u, ∂t u, ∇u, ∇²u; θ) = 0。
- 初期条件: u(x,t0)=u0(x)。境界条件: B(u,∂n u,x,t)=g(x,t) on ∂Ω。
- 保存則: d/dt ∫Ω ρ dV + ∫∂Ω J·n dS = ∫Ω s dV。
- 離散化: u_h = Σ_i c_i φ_i とrestriction/prolongation/measurement functional。

partial derivativeは変数・次数・作用対象を持つ構造node。tensorはrank/axis/basisと反変/共変の
必要なprofileを持ち、転置、内積、縮約、frame変換をshape一致だけで許さない。
PDEの同定、境界条件、初期条件、適用領域、定数/単位が欠けたModelから計算結果を作らない。
exact/symbolic inspectionは式の観察であって、解が存在する・求まったことの証拠ではない。

| 手法 | 明示的Realize契約に必要な選択 | 最低検証 |
|---|---|---|
| 有限差分 FDM | grid/domain、stencil、order、time integrator、step、安定性条件、境界処理 | manufactured solutionの収束、境界値、step不適合拒否 |
| 有限要素 FEM | weak form、function/test space、mesh、element family/order、quadrature、BC、assembly policy | weak/strong form対応、patch/convergence、unit、特異系診断 |
| スペクトル法 | basis、domain、mode cutoff、normalization、boundary compatibility、alias/dealias policy | mode収束、既知mode、aliasing監査 |
| 適応メッシュ AMR | estimator、tolerance、refine/coarsen、max cells/levels、transfer法、stop budget | conservative transfer、mesh版/lineage、budget exhaustion |

SolverはDomainのSolverProblem/SolverPolicy/SolverResult契約とUseCaseの実行選択、
NumericalSolverPortの具体Adapterに分ける。残差、収束理由、iteration/mesh履歴、error boundか
empirical estimateか、数値精度、費用、deadlineを返す。residualが小さいだけでmodel妥当性を認定しない。
Solver不収束や発散は部分値をsuccessful resultへ変えない。診断用partial値は用途制限付きResult。
明示された有限化を伴うCPU近似にはADRs 0210/0212のRealize境界と、
ADR 0211のsource-derived Semantic IR権威をともに適用する。

物理実験は校正/測定モデル、天文はtime/frame/coverage、重力はmetric/geometry/gauge/unitsと
初期拘束、流体はmass/momentum/energy、MHDは磁場divergenceと境界・source項を追加する。
Einstein方程式全系、乱流closure、太陽corona等の各物理profileは専用受入で段階追加し、
Poissonや線形波の実行成功を分野全体のSolver完了へ拡大しない。

## 6. 離散系・最適化・Quantum Projection

離散構造のdomain/index、graph、interaction、Hamiltonianは別の意味を持つ。
化学結合graphや道路graphから物理Hamiltonianを暗黙に生成しない。
ObjectiveとConstraintは意味付きdecision variables上で先に定義する。

QUBOは明示されたbinary変数について E(x)=xᵀQx+c。係数表の上下三角/対称二重計上規約、
変数順序、定数offset、単位/無次元化scaleを記録する。
Isingへの x_i=(1-s_i)/2、s_i∈{-1,+1} と対応するZ固有値規約を固定し、全小規模割当で
energyとdecodeが一致することを確認する。Hamiltonianの物理エネルギーと最適化costは別kind。
penalty weights、auxiliary variables、slack、constraint relaxationは変換証跡を要し、
低energyだけでhard feasibilityを認めない。Projectorはfeasible subspaceという理想意味で、
一般の非unitary projectorを無償の決定的QPU gateと扱わない。

QuantumProjectionContractはsource node、problem/snapshot hash、encoding、basis/index map、
preparation、objective/constraint対応、ancilla/precision、observable、terminal decode、
Realize policy、error/resource budget、capability判定を持つ。
入力のID辞書や元観測はHostで保持し、Kernelへは許された型付きcarrierと必要な係数を渡す。
省略されたmetadataはbinding/artifactの参照で必ず往復追跡可能とする。
大規模古典データを安価に量子状態へロードできるとは仮定しない。

Quantum Projectionを使わないclassical-only科学Workflowも同じModel/Result契約を通る。
量子ルートはclassical baselineとの比較候補であり、科学Workflowの成立条件ではない。
したがって個別Workflowの科学的有効性判定は量子laneの有無で失敗させない。一方、
本programが「classical/quantum接続まで設計・検証済み」と主張する最終gateでは、
別途Q01/D05の変換・比較証拠を要求する。この二つのcompletion claimを混同しない。

## 7. 型付き境界と変換証跡

BindingContractはinput snapshot、source symbol/node、scientific type、dimension/unit、
axis/index map、frame/time、missing/quality policy、observation-vs-estimate、evidenceを結びつける。
既存Param/ScientificInput/CoefficientTensor/HostInputPortは再利用候補であり、
`host("...")`やFloat配列を使う互換経路でもこの外側契約を省略できない。
逆に全metadataをqubitへencodeする必要はない。

| 変換/操作 | 意味と許可条件 | 禁止/失敗 |
|---|---|---|
| 外部record -> typed input | profile、raw evidence、unit/frame/ID検証 | unknownを0へ置換、sourceなし昇格 |
| exact/symbolic inspect | canonical構造、式・仮定・未評価状態を返す | 数値解/有限実行済みとの虚偽表示 |
| classical numerical solve | source-visible finite policy、solver contract、誤差/収束 | 隠れたmesh/step選択 |
| Simulator | backend種別。exact inspectionとfinite numerical/state simulationを区別 | Simulatorという名前だけでexact保証 |
| Realize | sourceと異なる有限実行物を明示的に作る | 理想式の置換、予算超過後のpartial artifact |
| QASM | finite artifactの交換/compile target | QASM生成を実機実行/科学的妥当性と表示 |
| QPU | capability-approved artifactをJob portへ渡し実機結果を受ける | SDK objectのKernel流入、未実行結果の生成 |
| quantum result -> classical | terminal measure + validated JobResult + decode map | mid-program implicit collapse |
| fallback | 同じsnapshot/目的/制約の別lane、新Job identity、理由、承認条件 | QPU成功への偽装、無言のoptimizer置換 |

変換記録はinput/output identities、source nodes、policy/version、loss/assumptions、unit/frame/index変換、
error/resource evidenceを持つ。拒否diagnosticは変換成功のprovenanceではない。
ADR 0210のresource overflowではtarget-plan provenanceも保持せず、必要なauditは拒否事実を参照する。
既存dynamic laneはその専用契約に従い、static laneを拡張しない。

## 8. Hybrid Workflow / Job / 人間承認

Workflow revisionはimmutableなinput snapshot、Model/Objectives/Constraints版、
DAG/反復body、input/output scientific types、budget、deadline、最大反復、termination policy、
fallback policy、approval policyを参照する。Data/Clock/Artifact/Evidence/Approval/Event ports、
Solver/Chemistry/Observation adapter portsを候補とする。既存Job/submit/cancel/result portを複製しない。

```text
candidate -> validated -> planned -> awaiting_approval -> authorized
    -> submitted -> running -> completed/failed/cancelled/expired
completed -> verified -> accepted_for_plan または rejected/stale
new observation/event -> new snapshot -> new plan revision
```

Jobは計算完了、Planは現実に採用する意思決定で、承認targetを分ける。
計算の承認と現実の化合物発注・アッセイ実行・災害指示は同一ではない。
approvalはactor、purpose、snapshot/plan hash、policy版、期限、取消状態を持つ。
入力や安全制約が変われば旧承認を新Planへ移さない。

期限にはdata cutoff、計画締切、Job締切、approval expiry、actuation windowを区別する。
到着順ではなくevent time/ingest timeとwatermark方針でsnapshotを作る。
重複イベントはdedupし、遅延結果はstaleとして保存しても現行Planを上書きしない。
cancel応答前のtimeoutでもside effectの有無を推測して再submitせず、Job identity/idempotency能力を確認する。
resource contention、queue/transfer/encoding時間もend-to-end期限に含める。

fallbackは事前承認されたclassical solver、最後に検証されたPlanの再検証、human-only decision等。
hard safety/fairness制約を満たせなければno-action/needs-humanで停止する。制約緩和は新しい明示承認。
S01では公平性の対象集団、欠測集団、待ち時間/配分指標、minimum serviceを人間が決める。
S02では予測の上位候補だけでなくdiversity、uncertainty、available stock、assay budgetを計画に反映する。

## 9. 科学的検証・再現性・費用

RunManifestはraw/curated Dataset hash、license、split、feature transforms、Model版、source hash、
compiler/solver/adapter版、environment、seed/精度、Realize、target/capability、Job/Plan/approval IDs、
結果/検証証拠を保持する。実測データの外部更新は別snapshotとする。
bit-identical replay、numerically equivalent replay、statistical replicationを区別する。
同じseedの実機結果一致を要求しない。QPU校正・noise/shot情報の欠落はunknownと明記する。

リーク防止はsplitをfit/descriptor selection/tuningより前に固定し、同一compound/replicate/assay系列や
時間・空間相関をprofileに従って分離する。holdoutは最終評価専用。active learningの次round結果は
選定時点で不可視とし、data availability cutoffを監査する。評価に使ったtestへ再調整したら新実験と記録。

各仮説はprimary metric、baseline、evaluation partition、tolerance/statistical protocol、失敗条件、
stop ruleを事前登録する。性能差が無い/悪い/不確定という結果も正式なResult。
古典baselineは同じinput候補集合、制約、cutoff、資源条件を使う。小規模enumerationは正解oracle、
実用規模は適切な既存optimizer/heuristicを使い分ける。

qualityは測定品質、model calibration、constraint violation、solver error、missingness、drift、
科学的discrepancyを別々に示す。時間/費用はデータ取込、curation、fit、encoding、compile、queue、
transfer、shots、decode、rerank、human reviewを分解し、estimate/observedを区別する。
postselectionの棄却率、shots再試行、失敗Jobも分母から除かない。
量子優位、臨床効果、災害安全性の主張はこの設計だけでは成立しない。

## 10. 拡張規約と残る決定

新分野はcoreのenumへS01/S02名を足す方式ではなく、versioned Domain Extension profileを登録する。
profileは概念mapping、必要metadata、式の型・次元、binding、solver/projection capability、
受入sourceとnegative case、検証oracle、migrationを揃える。未知profileはmetadata保管可能、実行は拒否。

Architecture approval対象はMetadata/IR権威分離、profile/Binding/Workflow/Projection契約。
Technology approval対象は具体adapter/library/version/format/provider選択で、現在未選定。
S02のtarget/assay/endpoint、採用Dataset snapshot、品質閾値、baseline手法、費用単位、
S01の公平性/安全policy、各Solverの数値toleranceはprofileのPhase 0で固定する。
空欄を実装時の推測で埋めず、その決定に依存しないcore WPから進める。

完全ロードマップと最小承認対象は[WP-0131](../work-plans/WP-0131-scientific-workflow-program.md)を参照。
