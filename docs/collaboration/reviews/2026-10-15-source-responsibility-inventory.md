# 分割後ソースの残存責務棚卸し — Phase 0

Status: Evidence / inventory I01–I08 and Phase0 accepted by Adjudicator2026-10-15.
Owner: [WP-0175](../../work-plans/WP-0175-source-responsibility-inventory.md).
Date: 2026-10-15 Asia/Tokyo.
Source baseline: `b5c96f7e4c2a846f41ac8ad5d882f0cb987cd420` (PR616 merged main).
This is an inventory, not a product-review pass or implementation permission.

## 結論

最大の残件は **TypeCheckerとParserの処理本体移行**。既存のfamily入口は
あるが、多くは大きな元ファイルの `_legacy_*` を呼ぶだけである。
入口の存在、旧メソッド名の不在、facadeの短さは、本体分割の完了証拠に
ならない。一方、ASTのような宣言中心の集合を、巨大な分岐ロジックと同じ
理由で細分化する必要もない。

機能を保った整理を優先する。`legacy`は不要・未使用・削除可能の意味では
なく、現状では実装所有者や必要な互換経路である。今回の削除候補は **なし**。
「削除しても機能減退しない」「過去の削除に減退がない」「全テストが網羅的」
とは主張しない。これらには別の履歴比較・到達性・振る舞い証拠が必要。

## 測定対象・単位・再現性

- `git ls-files '*.py'` の818ファイルをAST解析。構文解析エラーなし。
- production集計は tracked `compiler/**/*.py` の **221ファイル、52,695物理行**。
  private、helper、`legacy`、`__init__.py`をすべて含む。
- tracked compiler配下の非PythonファイルはREADMEのみ。他言語の実装を
  Python集計に混ぜていない。tests568／scripts12／examples17 Pythonは
  production行数から除外するが、attribute利用の静的検索には含めた。
- 物理行は空行・コメント・docstring込み。関数spanは`def`からend行まで、
  decoratorは除外、入れ子を含む。ファイル内unionは入れ子の二重加算を除く。
  **実行コード行数や責務数ではない**。class/function数はAST定義数。
- [全221ファイルの固定スナップショット](2026-10-15-source-responsibility-inventory.tsv)
  に物理行、関数span union、class/function数、最大関数span、各SHA256を保存。
- 詳細AST/import/attribute索引、集計scriptと実行記録:
  `/private/tmp/wp-0175-inventory.u2JUrt/`。一時領域のため永続保証なし。
  永続の集計値・consumer根拠・問題記録は本書／TSV／WPに残す。
- import観測は相対importを名前解決し、実在するtracked production moduleに
  合わせた静的候補。nested/conditional/TYPE_CHECKING importを含む。
  runtimeの依存解決、循環の有無、全動的consumer、文字列参照、serialization、
  semantic owner数を証明するものではない。attribute名一致もreceiver未解決。

## 大きさと集中の違い

以下は物理行降順。unionは「関数定義範囲のunion」であって業務ロジック量ではない。

| ファイル (`compiler/staqex/`以下) | 物理行 | 関数span union | class / function定義 | 実体と判断 |
|---|---:|---:|---:|---|
| `typecheck.py` | 4,690 | 4,428 | 3 / 92 | TypeChecker4,472行・86直接メソッド。Ty36行、TypedExpr3行よりも判定本体の集中が支配的 |
| `parser.py` | 3,679 | 3,385 | 2 / 129 | Parser3,504行・125直接メソッド。文法、cursor状態、回復、profile別処理が同居 |
| `scientific_semantic/legacy.py` | 1,803 | 1,669 | 0 / 40 | canonical構築、runtime plan、QPU projection、realization、fingerprint等の実体 |
| `backend/qasm/lowering/legacy.py` | 1,520 | 1,353 | 1 / 36 | capability拒否、AST互換、semantic lowering、evolution、resource予算 |
| `quantum_semantic_ir_legacy.py` | 1,372 | 868 | 33 / 48 | immutable型群に加えてinvariant・verifier・lowering。単なるDTO集でもない |
| `hir_legacy.py` | 1,135 | 917 | 5 / 40 | HIR構築、linear-use状態、scope/Uncompute検証 |
| `pipeline_legacy.py` | 1,096 | 784 | 1 / 28 | compile orchestration、diagnostic分類、IR/plan組立、入力処理 |
| `ast_nodes_legacy.py` | 1,064 | 22 | 103 / 7 | 主にAST宣言。大きな処理関数とは別扱い。grammar-family依存の理由があるときに型群を分離 |
| `finite_binder_legacy.py` | 1,027 | 895 | 1 / 40 | domain境界、index置換、展開、metadata、Host係数統合 |
| `unitarity_check.py` | 933 | 803 | 0 / 23 | lineage追跡、expression walk、apply/isometry/Hermitian等の判定 |
| `runtime/evaluator.py` | 929 | 500 | 7 / 73 | live状態所有者・DTO・orchestration・hook。短くなったが全面完了とはしない |
| `backend/qasm/emitter.py` | 917 | 830 | 2 / 16 | AST出力、QPU出力、canonical確認。lowering側と別の本体 |
| `qpu_ir.py` | 737 | 603 | 3 / 34 | QPU projection/IR/verifier側の追加棚卸し対象 |
| `cli.py` | 669 | 589 | 0 / 25 | delivery/command orchestration。domain移動の前に入出力境界を確認 |
| `runtime/evaluation/operators.py` | 619 | 577 | 0 / 17 | 実体移行済みだがresolution/factory/finite/second-quantizedを含む |
| `runtime/evaluation/observation.py` | 606 | 569 | 0 / 19 | 観測・measurement等の残存実装。facade行数には現れない |
| `modules.py` | 590 | 515 | 1 / 14 | SourcePort経由のload/mergeとmodule意味処理 |
| `h1_authoring.py` | 562 | 428 | 3 / 20 | authoringモデル・validation境界 |
| `target_routing.py` | 548 | 397 | 9 / 23 | routing evidenceとtarget capability |
| `runtime/evaluation/calls.py` | 532 | 501 | 0 / 5 | `bind_call`だけで480行。実体が移った後にも集中が残る例 |

1,000行超は9ファイル。参考として300行超は45ファイルだが、live routingに
300行閾値は設定されていない。数値だけで違反や新たな分割義務と判定しない。

## 実体・consumer・状態の根拠

### TypeChecker — 第一候補

- `typechecking/operators.py:10`は`context._legacy_check_operator(...)`へ委譲。
  `typecheck.py:4629`が`_check_operator_expr`を同じクラスのlegacy本体へalias。
  production経路はfamily入口へ全面移行していない。
- 最大関数は`check_unit:233`の582行。前宣言収集、class/enum/interface/
  function/effect登録、function body確認、mainのチェックが同居する。
  `_legacy_infer_call:3959`436行、`_infer_binop:3609`305行も別の集中。
- 実consumer: `pipeline_legacy.py:61,854`がTypeCheckerを生成し、
  `hir_legacy.py:44,167`がTy/TypeCheckerと検査済み状態を読む。
  `_check_operator_expr`は同一クラス内430/1387/1660/1671–1679/1766/2349行等で利用。
  alias/private hookと再帰経路は残存契約として調査する。
- AST上の`self`への代入先名は19種類。`env`,`typed`,`diagnostics`,
  `_binder_depth`,`_active_register_set`,`_current_effects`等を含む。
  これは19の独立ownerという意味ではない。**live ownerは維持**し、保存・復元・
  診断順・再帰タイミングを専用specで固定する必要がある。
- 最初のbounded候補: `_legacy_check_operator`281行の実体を既存operator familyへ
  移す設計。単にhelperを挟むのではなく唯一の実装ownerを確認する。
  Ty参照を理由にfacade逆importや循環を導入しない型配置が設計課題。
  これ自体のScope/spec/Phase承認は今回の棚卸しacceptanceと別。

### Parser — 第二候補

- `parsing/expressions.py:10`が`_legacy_parse_expression`へ委譲し、
  `parser.py:3675`が`_primary`を元クラスの同本体へaliasする。
  その他statement/operator/scientific/recoveryも同様の橋が残る。
- 実consumer: `pipeline_legacy.py:1018`、`modules.py:66`、`access.py`の
  Parser import。cursorの`tokens/i/_prev`、diagnostics、norm/commutator文脈、
  scientific binding正規化とprofile状態を共有する。
- AST上の`self`代入先名は10種類。token消費順、lookahead、precedence、
  recovery、Span、alias名の正規化を保つ必要がある。
- keywordの文字列だけで機械分割せず、top-level/scientific/statement/
  expression/operator/recoveryという文法と依存に基づくfamily単位を候補とする。
  operator-primary117行等のbounded単位から実体を移す設計が考えられるが未選定。

### 他の主要ownerと、legacyを消せない根拠

| 実体 | 実在する経路・責務 | 保存すべきもの |
|---|---|---|
| Scientific Semantic legacy | `builder`→canonical構築、`runtime_plan`→plan、`qpu_projection`→QPU、`realization`→realization、`fingerprint`→hash。各familyがlegacyへ委譲 | source-derived canonical authority、一貫したnode/provenance、投影は派生のみ |
| QASM lowering legacy | `lower.py`がwildcard exportし、`lowering/semantic.py`→`_from_dag`、`ast_compat.py`→`_from_ast_patterns`、preflight/evolution/resourcesも実体を呼ぶ | accepted QASM byte一致、拒否順序、no partial artifact、profile/resource境界 |
| Quantum Semantic IR legacy | 公開`quantum_semantic_ir.py`が再exportし、h1_authoring・pipeline・measurement readinessが公開側を利用 | `__all__`、immutable型/invariant、schema、verification/identity |
| HIR legacy | 公開`hir.py`経由でpipeline/scientific lexicon contractが利用 | completed TypeCheckerのviewとlinear-generation/Uncompute規則 |
| pipeline legacy | `pipeline.py`経由でCLI/run/host等がcompile entrypointを利用 | orchestration順、入力SourcePort、diagnostic/result契約 |
| finite binder legacy | `finite_binder.py`再exportに加え4 private helperを明示再export。runtime operators/observation/execution/Host係数等が使用 | public/private import、有限展開、Host metadata・エラー・budget |
| AST legacy | `ast_nodes.py`が103型等を再export。静的production import候補は公開側73ファイル | class identity/import、constructor/field順、Span/serialization |
| runtime legacy_control_binding | compatibility installerのprivate bridgeから残る`when`経路 | legacyという名をunused証拠にせず、受入済み制御意味を維持 |

静的直接importはlegacy実体側1件でも、公開facadeを経由した多数の利用がある。
7つの大きなlegacy ownerとruntimeの1つを確認した。**どれも名前だけで削除しない**。
公開名の完全列挙とidentity/serialization比較は各実体移行のPhase 0/1で行う。

`unitarity_check.py`はParserではなくpipelineの静的検証passで、
`pipeline_legacy.py:851`が呼ぶ。lineage、式walk、apply行列、isometry、evolveの
Hermitian規則は別責務として分けられる候補。検証基準や許容誤差を変更しない。

`calls.bind_call:53`480行はclass/struct/Partial、receiver、user function、
組込み操作を扱う。productionの静的import候補はbinding/compatibility/
dynamic_lane/execution/static_foreach/Evaluatorの6ファイル。
既に専用ownerに移った実装にも次段の責務分割余地がある。

## 調査で再現した入口契約の欠落

修復のcanonical recordはWP-0175の`BUG-WP0175-001/002`。

1. `typechecking.dimensions.check_assignment(TypeChecker())` →
   `AttributeError: 'TypeChecker' object has no attribute '_legacy_check_dimensions'`。
2. `parsing.top_level.parse_declaration(Parser([]))` →
   `AttributeError: 'Parser' object has no attribute '_legacy_parse_declaration'`。

両入口は`*args, **kwargs`を受けるが、引数を処理する前にcallback取得で失敗。
他の有効な引数を渡しても、現在の実contextにcallbackがないという境界は残る。
空Parserはこの入口欠落のprobeであって、有効sourceのparse失敗の証拠ではない。
通常pipeline全体の故障・未使用・削除可能性はここから推論しない。
どの契約を入口に与えるか未決定のため、aliasesを勝手に追加しない。

既存LISS0546–0550の5スイート **20 PASS**。TypeChecker/Parserのテストは
callable存在、元名の`def`不在、Protocol内の文字列等を確認するが、この2入口を
実contextで呼ばず、本体がlegacy名で同居していることも拒否しない。
これは **構造受入の証拠範囲が狭い** という結果であり、全テストが無意味とか
通常機能が失われたという結論ではない。将来のRedには実入口の結果、実体の
唯一性・配置、private binding、状態、意味のpositive/negativeが必要。

## 推奨順序（実装承認・確定ロードマップではない）

| 優先 | 次の設計候補 | 最小の入り口／注意 |
|---:|---|---|
| 1 | TypeCheckerのfamily実体移行 | operator check281行を第一候補に、private再帰・型参照・状態/診断順を固定。`check_unit`582行の丸ごと移動とは別 |
| 2 | Parserの文法本体移行 | family単位のtoken/cursor契約を固定。keyword別の無条件分割はしない |
| 3 | Scientific Semanticの構築とprojection実体 | 既存modelを再利用し、canonical builderと派生projectionを混同しない |
| 4 | Unitarity判定family | walk、lineage、行列/isometry、evolve検証を識別。Parserへ混ぜない |
| 5 | QASM lowering / emitter | preflight/resource/semantic/AST fallbackと出力を別々の契約で扱う |
| 6 | runtime calls / executionの内部再分割 | 大きなbind_call/statement dispatcherの順序・live state・private consumerを固定 |
| 7 | HIR / finite binder / pipeline / Quantum Semantic IR | モデル・verifier・lowering・orchestrationを分ける理由を確認。各々別Issue/specが必要 |
| 保持理由あり | AST宣言群、Evaluator state facade | 大きさだけで削らない。型family整理や残存orchestrationの具体的な変更理由が必要 |

2つの入口修復は別backlog。全候補の一律prerequisiteにはしないが、該当入口や
contextを触る設計では先に契約をdispositionする。追跡記録は失敗のwaiverではない。

### 型オブジェクトについて

Tyは既にfrozen dataclassで、TypedExprも存在する。主な集中は型定義の個数より
`kind/payload`やAST形による判定、スコープ/effect/単位/診断の同居にある。
次の設計ではTy/診断内部表現/家族別contextの型境界を検討してよいが、すべての
dictをobjectに置換することや全`isinstance`を型メソッドへ移すことは提案しない。
envのmappingやRustでのenum matchには正当な役割がある。公開診断dictやimportを
保ったまま、意味のあるvariant/invariantだけを型に寄せる候補は別途承認が必要。

## 構造budgetのdisposition

live TOMLに数値budget/large_change overrideはない。一方、受入済み
`staqex-core-module-decomposition.md`の指針は新実装module通常1,200行未満、
150行超関数／1,200行超classにcohesion理由を要求する。今回は既存実装を測った
だけで、新たな超過や例外承認は作らない。超過は消えたことにしない。

- 1,200行超file5件: TypeChecker、Parser、Scientific legacy、QASM legacy、
  Quantum Semantic legacy。上記優先1/2/3/5/7のfollow-up候補。
- 1,200行超class2件: TypeChecker4,472、Parser3,504。優先1/2。
- 150行超関数は下記20件。ownerはWP-0175計画担当／Adjudicator。各ownerを
  次に変更する前の専用Scope/spec gateで、分離・保持理由・明示例外を決める。
  今回のbacklog記載で構造受入やblocking失敗を免除しない。

| owner | 150行超関数とspan | disposition |
|---|---|---|
| TypeChecker | check_unit582、operator281、declaration170、expression217、binop305、call436 | 優先1。familyごとの設計。stateful dispatcher保持には理由が必要 |
| Parser | parse246、expression212 | 優先2。文法／recoveryの消費順を固定 |
| Scientific Semantic | canonical builder360、QPU projection310 | 優先3。semantic authorityを保持 |
| QASM | AST fallback446、emit_unit336、emit_qpu_program172 | 優先5。goldensと原子的拒否 |
| runtime | bind_call480、legacy execution341、bind_method170 | 優先6。frame/live-state契約 |
| pipeline | _analyze_unit165 | 優先7。orchestration順を保持 |
| Lexer | tokenize170 | 後続候補。最長token処理の結束性を次回触る前に確認 |
| Unitarity | expression check225 | 優先4。walkとpolicyを識別 |
| host | _submit_compiled162 | 後続候補。port/lifecycle orchestrationを触る前に設計 |

## 検証と未確認範囲

Fresh local at source SHA b5c96f7e; tracked変更は設計文書のみ。
macOS27.0.1 arm64、CPython3.12.6、pytest9.0.3、cwd repository root、
external probeには明示PYTHONPATH。command/timing/exitは外部capture JSON。

- 818 tracked Python AST解析: PASS。
- 221-file物理行／AST／hash inventory: PASS。TSVとの最終照合はtraceに記録。
- 既存構造5 suites: 20 passed、fail/error/skipなし（報告出力）。
- spec verification: **161/161 PASS**。aggregate skip数はharness未報告。
- 2入口probe: **欠落を再現**。harnessのexit0はproduct Greenではない。
- 文書lifecycle、active-Red lifecycle、coverage ledger、diff whitespace、
  compiler/tests無変更の最終結果はtrace参照。
- root/sanity全体の新規local実行、cold全順序、全serialization、解決済み
  dependency graph/cycles、全consumer runtime smoke: **not_run / unassessed**。
  b5c96f7eのmain CIはroot2821/spec161/sanity成功の既存証跡を利用するが、
  このdirty設計文書に対する新しいall-blocking Greenとは主張しない。

独立照合で初期集計の条件分岐内function定義の取りこぼしを検出した。
pipeline/Unitary/Evaluatorの定義数を28/23/73へ訂正し、全221行をGitのsource
から独立再計算して一致を確認。総行数・上位順位・大関数20件は不変。
初回失敗ログを保持し、修正した集計だけを最終snapshotとしている。

棚卸し結果／WP-0175 Phase0は明示受入れ済み。次は選んだ最小候補の
Scope／Phase0設計開始を別途承認し、専用Issue/specを設計する。テスト・実装・削除・commit/
push/PRは今回実行しない。
