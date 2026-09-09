# Scientific Workflow acceptance proposal

Status: **M0 and B01 Phase 0 accepted; Phase 1 and implementation not authorized** (2026-09-08).
Owner: [ADR 0217](../architecture/adr/0217-scientific-workflow-metadata-and-projection.md) / [complete design](../architecture/scientific-workflow-complete-design.md).
Execution ledger: [WP-0131](../work-plans/WP-0131-scientific-workflow-program.md).

この仕様は今後承認する観察可能な振る舞いを定義する。既存のscalar input、WorkflowPlan、
terminal measure、Realize契約を置換しない。新構文・実行API名は各WPのPhase 0で確定する。
M0 G01/G02/G03とB01のPhase 0設計は2026-09-08に承認済み。個別WPは以下のscenario IDとfixture/profileを固定してからPhase 1承認を求める。

## Preconditions / ownership / external dependencies

研究者がDatasetの利用権、sourceとscientific profile、目的/制約/評価protocolを所有する。
raw snapshotは変更せず、curation、Model、Planは新revisionとして作る。
AdapterはData/Chemistry/Observation/Solver portsを実装し、UseCaseが科学的policyを検証する。
受入テストはfake ports、凍結した小規模fixture、fake clockを使い、network/SDK/秘密を必要としない。
実測S02のデータ取得と利用条件はWP-0134のPhase 0で確認し、synthetic fixtureで科学的成功を代用しない。

## Minimum package M0: Metadata identity and observational truth

M0はWP-0132 / LISS-0515のみ。Graph記録・検証のHost/Domain契約であり、
parser、binding、solver、永続DB、外部reader、Workflow実行は含まない。
最小fixtureは6個のin-memory記録群: assay、道路閉鎖、天文flux、vector field、
試料付き物理実験、離散interaction。型/参照validation用で、実データや新構文ではない。
unitはこのsliceでは識別子とdimension signatureを検証するだけで換算しない。
Time/Spaceの未知情報はunknownとして保持し、勝手にUTC/経緯度を補わない。

### G01: immutable identity and metadata

Given 各fixtureにnamespaced ID/revision、source hash、profile version、value kind、
unit/dimension、time/space適用可否、missing reason、observed/estimated区分があり、
When 記録とRelationを検証してsnapshotを構築する、
Then すべての意味付きfieldとrelation endpointが検査可能で、入力順を変えてもidentityが変わらず、
既存snapshotへの変更はできず訂正は新revisionとなる。
同じID/revisionで異なるcontent、存在しないrelation endpoint、unit/dimension不一致は拒否される。
異なるnamespaceの同じlocal ID、正当なdomain graph cycleは拒否されない。

### G02: observation is not estimate or missing zero

Given 実測値0、not-measured、below-detection interval、model estimate、自然言語candidateの5記録、
When validationと観察用queryを行う、
Then 5種類を識別でき、null/unknownを0に変えず、candidateをapprovedな実測に変更しない。
欠けたInstrumentがprofileでnot-applicableなら理由を保持して受理し、
必須Procedure/source referenceが欠ければquarantine診断を返す。
型validation成功だけで人間approvalやscientific validityはtrueにならない。

### G03: scoped evidence and provenance

Given Resultがsource Evidenceと生成Activityを参照し、訂正記録が元revisionを参照する、
When snapshotを検査する、
Then supporting/refuting evidence、derivedFrom、correction lineageを辿れ、raw sourceを変更しない。
provenance derivation cycleは拒否し、source不明のAI confidenceを測定uncertaintyにしない。
PROV-Oの全serializerや推論器は不要。conceptual mappingだけを契約とする。

M0 exit: 上記3シナリオのpositive/negative対応、6分野fixtureの全必須field、
新規実行権威がないことをレビューできる。Phase 1はテストのみで、出力API形状の決定は
受入reviewに含める。Graph検証だけで後続科学実行が実装済みと判定しない。

## Shared acceptance matrix

| ID | Given | When | Then / failure neighbor |
|---|---|---|---|
| B01 | typed Param/tensorとmetadata snapshot、unit/frame/index map | BindingContractを検証しround-trip decode | source symbol、snapshot版、shape/axis/index、欠損、観測/推定を追跡。identityまたは証跡付き明示unit/axis mappingのみ受理。stale snapshot、unknown unit、axis/shape不一致、Host keyだけの入力は診断付きで拒否 |
| D01 | version-pinned assay recordsにcompound/target/assay ID、endpoint、unit、relation、replicate、source、checksum/license | S02 Domainがcuration | measuredとpredictionを別記録化。IC50・nM・互換assay-familyだけ集約し、censoredを等号にせず、単位/assay混在・identity collision・license欠落は明示quarantine |
| D02 | WP-0134 curated IC50 profile、固定availability cutoffとcompound/replicate group split | fit/selection/evaluation | holdoutや未来roundをfitへ使わず、同一groupの漏れを検出。FitRecordはtrain/transform/feature-selection IDsとcutoffを示す。未知holdout label、prediction uncertainty、applicabilityを保持し、漏洩は`MODEL_SPLIT_GROUP_OVERLAP`等でfail-closed |
| D03 | 固定candidate inventory、batch size 2、budget 8、stock/diversity hard constraints、predicted IC50 objective、predefined baseline | 小規模全subset oracleと`greedy-feasible-v1`を同一入力で実行 | feasibilityとscoreを独立に検算。candidate set不一致・constraint/score不一致は診断し、infeasibleは`no-feasible-plan`であり空集合の成功ではない |
| Q01 | 小さいbinary problemと明示encoding、scale、offset、index map | QUBO/Ising/Quantum Projectionへ変換 | 全割当energyとdecodeが合う。penalty-only低energyの違反を検出。非unitary projectorの無条件gate化は拒否 |
| W01 | immutable snapshot、deadline、approval hash、fake Jobs/events | late event、duplicate、timeout、cancel raceを注入 | 新Plan revisionを作り、stale result/expired approvalは採用不可。明示fallbackは別lane/Job。安全制約の緩和は自動実行されない |

### E01 Phase 0 profile (reproducibility, falsification, and cost evidence)

E01は成功だけを集計するbenchmarkではなく、RunManifest、claim、evaluation、failure、
costの証拠契約である。`manifest:s02-d03-v1`、`snapshot:s02-round-001`、
`model:s02-v1`、`baseline:greedy-feasible-v1`、`environment:local-python-v1`を固定し、
source/fixture hash、input/model/baseline identity、seed、precision、runtime、command、
metric、uncertainty、comparison population、cost breakdown、failure/diagnostic、replay
referenceを保持する。manifest identityは完全一致、数値は宣言済みtolerance、統計値は
事前固定sample count/confidence intervalで判定する。heldout再利用、分母bias、費用欠落、
失敗隠蔽は拒否し、実測・実機が無い場合は未検証と表示する。

### W01 Phase 0 profile (provider-neutral lifecycle)

W01はJob実行基盤ではなく、WorkflowPlan/Jobのidentity・承認・期限・採用状態を管理する
契約である。`plan:s02-round-001`、`snapshot:s02-round-001`、`approval:s02-policy-v1`、
`job:s02-fake-001`とfake UTC clockを固定し、Plan採用とJob完了を別状態として記録する。
Unit Aはpure state transition、期限切れ/取消承認、stale result、identity不一致を扱う。
Unit Bはfake event/clockでduplicate・late event・timeout/cancel race・別lane fallbackを
扱う。期限、snapshot/plan hash、approval policy、event sequenceの不一致はdiagnostic付き
で拒否し、fallbackは新しいPlan/Jobとしてのみ許可する。scheduler、provider retry、
実運用actuationは受入範囲外である。
| D04 | train/validation/holdoutを隔離した実測snapshotと候補在庫、承認policy | 次回assay batchを提案し、凍結した後続round結果を後から取込 | candidate IDs、selection理由、予測/不確実性、constraint verdict、費用、approval対象を報告。実測なしのhit改善は未検証と表示 |

### D04 Phase 0 profile (S02 closed loop)

D04はQUBO/量子実行ではなく、`assay:s02-round-001`のimmutable curated snapshot、
`candidates:s02-fixture-v1`、`model:s02-v1`、`policy:s02-batch-v1`から次回assay
proposalを作り、後続roundを新snapshotとして取り込むclassical closed loopである。
Proposalはcandidate IDs、selection reason、prediction/uncertainty、hard-constraint
verdict、cost、snapshot/model/policy identity、approval hash、deadlineを保持する。
proposal生成時に後続roundのlabelが見えた場合、またはapproval期限・snapshot・candidate
状態が変わった場合はdiagnostic付きで採用拒否する。実測がない場合は未検証と表示し、
hit改善を主張しない。QUBO/encodingはQ01のWP-0137/LISS-0520で扱う。
| X01 | CityGML objectとnode/edge graph、SensorThings/SOSA profile fixture | external portからGraphにmapping | topology/geometry/LoD、time/FOI/property/procedure/sourceを保持。道路のgeometryだけではpassableと断定しない |
| S01 | 既存K-ku storyとfake観測/不足資源、公平性・安全policy | 道路閉鎖/欠測/期限超過に対してrolling replan | 各Planの到達可能性・capacity・minimum service違反と未充足需要を表示。人間承認前の指示なし。前Planが危険なら無条件再利用なし |
| A01 | ObsCore dataset metadataとVOTableのflux/uncertainty/null/units/time-frame fixture | Adapterとcalibration modelを経由 | tableを意味付きObservationへ接続。time scale/CRS不一致を検出、上限値を検出値へ変えない。既知signalの推定とcoverage不足を区別 |
| F01 | unit/basis付きscalar/vector/tensor field、PDE、IC/BC、domain | sourceをparse/typecheckしSemantic IRへ | partial derivative/conditions/axisが構造化され、式とbindingの単位不一致拒否。field DTOの注入だけでは合格しない |
| N01 | 熱方程式のmanufactured solutionとexplicit FDM Realize | grid/stepを変えてsolver実行 | 事前指定の収束次数区間、BC、error budgetを満たす。安定性違反は計算前または契約上の診断で拒否 |
| N02 | Poissonのweak form、function/test space、mesh/element/quadrature | explicit FEM Realize | analytic/manufactured解との誤差・patch検証、次元整合。BC欠落や特異系を成功にしない |
| N03 | periodic場とbasis/mode cutoff/normalization/dealias policy | explicit spectral Realize | 既知mode/収束を確認。非周期境界の不適合やaliasing未処置を黙認しない |
| N04 | coarse/fine meshと保存量、estimator/transfer/budget | refine/coarsenまたは予算上限到達 | lineageとglobal balanceを保持。max cells超過はpartial成功でない。正常なcoarsenもpositive caseに含む |
| P01 | 校正付き物理実験、Newtonian gravity profileの密度・領域/BC | 観測とPoisson Modelを結合 | unit/frame/calibration版、potential/accelerationの検証を示す。GR/gauge関連の非対応をNewtonian結果で代用しない |
| P02 | fluid mass/momentum/energyとMHD field/BC/source profile | 正当なadvection/MHD wave benchmarkを実行 | 保存残差・収束・divergenceを別測定し、適合/不適合を報告。未選定closureや境界を推定しない |
| R01 | discrete graph、interaction law、Hamiltonian、finite domain | classical/quantum pathを比較 | graph symmetry/edge weight/energy/decoded結果が一致。graphそのものをHamiltonianと扱う入力を拒否 |
| E01 | manifest/seed/environment/metric/stop-ruleを固定 | replayとbaseline比較 | identity、numeric tolerance、statistical protocolの指定水準で再現。encoding/queue/失敗/棄却費用を含め優位不明を許す |
| L01 | 否定・伝聞・曖昧時刻を含む文章とsource span | candidate抽出後にreview | source/uncertainty/review状態を保持。承認前に観測/Planへ採用しない。既に型付き実測の再取込はcandidate化を強要しない |
| C01 | 新分野のversioned extension profileとsource/fixture/oracle | conformance登録と実行 | coreをS01/S02専用変更せず接続できる。未知profileは保管できても実行拒否。claimedな分野は成功する実行証拠が必須 |

| P03 | 一つの既知時空/摂動profileのmetric、chart、gauge、初期拘束とsource | 型検証後に既存Solver/analytic consumerへ射影 | 事前固定した不変量/constraint residualが参照値の許容内。chart変更で不変量が一致。不適合gauge/欠けたICは拒否しNewton結果へ置換しない |
| P04 | 固定したcompressible shock benchmark、状態方程式/closure、flux、IC/BC | 明示Realizeと既存流体Solverで計算 | 参照解との誤差、mass/momentum/energy balanceを別々に検証。不正density/BCや不収束を成功にしない |
| P05 | 固定したsolar領域のvector磁場Observation/estimate、time/frame/coverageとModel | 校正/BC binding後にMHD Solverへ射影 | 実測と推定BC、divergence/保存残差、source項、参照benchmarkを追跡。coverage不足やframe/cadence不一致は無言補完せず拒否またはreview-required |
| P06 | 既知parameterを持つ独立した校正検証dataとcorrelated ensemble、cutoff、承認policy | 逆問題を解き次測定候補を計画 | parameter recovery/coverageと識別不能性を報告しModel revisionを更新。相関欠落、同化dataの評価再利用、旧承認の新Plan転用を拒否 |
| D05 | D04の固定した実測problemとQ01のencoding、同一古典baseline、E01 protocol | 量子Simulator/finite targetと古典laneを比較 | terminal decodeとfeasibilityを独立検算し全overhead込みの結果を報告。QPU拒否は拒否として保持し古典結果で量子成功を偽装しない。quantum advantage不明を有効な判定とする |

## S02 practical protocol acceptance

第一実用縦切りは一つのtarget/assay-family/endpointに限定して開始し、
共通モデルの対応範囲とは分離する。Phase 0でDataset release/checksum、利用条件、
curation policy、assay互換条件、cutoff、compound identity/replicate grouping、
候補在庫、batch size、費用、評価metric/threshold、baselineとoracleを固定する。
これらはまだ選定されていないためD01以降は現時点ではPhase 1-readyではない。

活動量の値・単位・不等号・測定条件を失わない。IC50/Ki等異なるendpointを無条件混合しない。
学習値、予測値、batch採用、実験後の測定値を別Dataset版にする。
S02の最初の比較は古典のみでも成立する。QPU capability拒否時は結果を失敗laneとして残し、
承認された古典fallbackのbatchを別報告する。実験室への送信や化合物購入は本仕様外。

retrospective replayはhistorical cutoffで後続実測を封印し、batch選択後に評価する。
prospective validationは別途承認された実アッセイによる次round値を用いる。
retrospective好成績をprospective改善やhit-to-lead成功へ言い換えない。

## Completion evidence required per implementation WP

各WPは受入scenario、input profile、source/port boundary、positive/negative隣接例、
実装claim、検証command、artifact/diagnostic、known gapsを1対1で対応付ける。
source機能をclaimするWPはparser -> typed HIR -> Semantic IR -> consumer -> Resultまで示す。
Host-only metadata WPはparser到達をclaimせずport/APIを検証する。

Phase 1前にnumeric tolerance・fixture license・対応method・test locationを固定する。
Phase 2はreviewed testsを変更して通さない。Phase 3でassertionの意味を維持し再検証する。
本設計ではテストもproductionも作らず、完了済みテストの実行成績を再取得していない。

## Out of scope

Provider SDK/credentials/live device submission、実災害への指示、assay発注、特定DB、
Rust migration、量子優位の保証。未承認のsyntax/APIの実装。
既存WP-0123/0126の実機・security境界は独立して維持する。
