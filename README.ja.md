# Staqex

**Staqex**（スタケックス / *Quantum-Probabilistic Executable*）は、理論物理の計算式を書くように、
量子コンピュータ向けのプログラムを書けることをめざしたプログラミング言語です。

[English README](README.md) · [Quickstart](QUICKSTART.ja.md) ·
[アーキテクチャ](docs/architecture/README.md) ·
[言語仕様](docs/specs/staqex-language-specification.md)

> **旧称は QPex。** 2026-07-29 に商標上の競合を理由として Staqex に改称しました。
> 言語仕様・ADR の内容に変更はありません。改称の詳細は
> [`docs/architecture/README.md`](docs/architecture/README.md#project-rename-history)
> を参照してください。
>
> **Kernel タグ:** QPex 時代のツリーは **`v0.1.1`**（最後の `compiler/qpex/`
> コミット）をピン留めしてください。現行／次の Staqex Kernel ラインは
> **`v0.2.0`** です。

## ライセンス

**MIT OR Apache-2.0** のデュアルライセンス。
[LICENSE](LICENSE) / [LICENSE-MIT](LICENSE-MIT) / [LICENSE-APACHE](LICENSE-APACHE)。

## 現状（正直な棚卸し）

| 層 | 実態 |
|----|------|
| 協働 / AT-TDD | `llm-project-template` を導入済み（`AGENTS.md`、ADR 0001–0012 など） |
| 規範的な言語面 | `docs/specs/staqex-language-specification.md` と ADR 0013 以降 |
| **今動く Kernel** | **Python** の `compiler/staqex/`（字句〜型検査〜 Joint 評価） |
| ローカル実行 | provider-neutral Host APIの`run`／`submit`とローカルJointシミュレータ |
| OpenQASMターゲット | OpenQASM 3へのlowering、routing、ファイル出力（オフライン） |
| 実行artifact | portable／target-resolved `.sqxa` writer・reader・Runtime preflight |
| AWS Braket | Host adapterとlive job CLIを実装済み。ただし実機実行は明示的opt-inでCI未実施 |
| 科学workflow | S02 assay cycleと量子・古典baseline比較のbounded APIを実装。広い分野対応は継続中 |
| GPU | 予約済み。現在はCPU Jointへfallback |
| 仕様検証 | `python3 tests/spec_verification/run_all.py`（現在161/161 pass） |

受け入れ済み仕様と明示された AT-TDD フェーズなしに、言語挙動を実装しないこと
（`AGENTS.md`）。

言語の意味、semantic validation、有限化方針、artifact identity、測定解釈は
Staqexが所有し、SDK/API変換、認証情報、provider job状態、transportはHost adapterが
所有します。adapterがソースの意味を変更したり、拒否された有限化を成功に見せたりする
ことはありません。

## 物理学者向け DX

プログラマ道具は「物理の単位」として見せる（Java 式の儀式は置かない）:

| 構文 | 物理的な読み |
|------|----------------|
| `enum` | 排他的な幾何・基底 |
| `struct` | 不変パラメータの束 |
| `class` + `fun init` | **物理系** / 実験セットアップ（`new` は禁止） |
| `namespace` | 理論のセクター |
| 修飾なし / `pub` / `_` | モジュール内 / 公開 API / クラス私有（`protected` なし） |

詳細: [`docs/architecture/physicist-dx-harmony.md`](docs/architecture/physicist-dx-harmony.md)、
ADR **0054–0056**、**0058**。

## 実行

```bash
python3 -m compiler.staqex run examples/basics/B01_never_leave_the_state/never_leave_the_state.sqx --seed 0
python3 -m compiler.staqex run examples/applied/A06_topological_edge_memory/main_topological_edge_memory.sqx --seed 0
```

例一覧: [`examples/README.md`](examples/README.md)。

## OpenQASMとQPU境界

OpenQASM 3の出力はローカルで生成できます。providerへ接続せず、未対応のsemantic
projectionは暗黙変換せず拒否します。`qpu:<profile>`は現状ローカルcompile／出力経路で、
GPU targetはCPUシミュレーションへfallbackします。

実AWS Braketへの送信CLIもありますが、AWS Braket SDK、Hostの認証情報、device ARN、shots、
費用上限、送信直前の対話確認が必要で、実費が発生し得ます。今回のローカルテストやCIでは
実機を実行しません。job lifecycleは`qpu-job-status`、`qpu-job-wait`、`qpu-job-result`、
`qpu-job-cancel`です。

`.sqxa`は実行artifactの境界であり、provider SDK、認証情報、人間の承認記録はartifactへ
入りません。詳細は[ADR 0219](docs/architecture/adr/0219-sqxa-target-build-boundary.md)と
[LISS-0542](docs/issues/LISS-0542-sqxa-target-build.md)を参照してください。

## 科学workflowの現状

S02では、実測assay入力、leakage-safe model、古典batch cycle、再現性証拠、量子・古典
baseline比較をboundedなPython APIとして扱います。候補、decode／feasibility、objective、
cost、lineageを検証し、runtime拒否や不完全cost、制約違反、lineage不一致はfail-closedで
扱います。これは量子優位や実科学的妥当性を主張するものではなく、広い科学分野の完成は
別途ロードマップで進行中です。

言語仕様ベンチマーク用ショーケース（examples カタログの**最下行**）:
[`examples/showcase/S01_quantum_disaster_response/`](examples/showcase/S01_quantum_disaster_response/)
— **言語仕様のベンチマークのために書かれた**災害司令室 OS
（[README](examples/showcase/S01_quantum_disaster_response/README.md)）。
余震・都市火災・火災旋風リスクを二次災害として含む。

## 検証

```bash
python3 tests/spec_verification/run_all.py
python3 tests/test_modern_oop_and_visibility.py
python3 -m pytest -q tests/test_s02_assay_batch_cycle_red.py \
  tests/test_s02_quantum_baseline_comparison_red.py
```

## エージェント入口

1. `AGENTS.md`  
2. `docs/architecture/agent-quickstart.md`  
3. `docs/collaboration/session-start-and-resume.md`  

テンプレート同期は `.collaboration-template-version` を基準に、
`update-ai-collaboration-files.sh` で行う。
**製品 README と言語 ADR はターゲット所有**であり、テンプレの README では
上書きしない。
