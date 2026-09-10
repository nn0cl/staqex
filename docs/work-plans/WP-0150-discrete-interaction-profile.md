# WP-0150: 一般離散graph・相互作用・Hamiltonian

| Field | Value |
|---|---|
| Status | Phase 2 Green complete; Phase 3 pending |
| Phase | phase-2-green |
| Size initial/current | M / M — one bounded profile or boundary; elapsed-time estimateではない |
| Parent | [WP-0131](WP-0131-scientific-workflow-program.md) |
| Issue | [LISS-0533](../issues/LISS-0533-discrete-interaction-profile.md) |
| Depends on | [WP-0133](WP-0133-scientific-typed-bindings.md); [WP-0137](WP-0137-scientific-quantum-projection.md) |
| Blocks | WP-0153 |
| Owner / route | Sol: independent design correction and coordination; Luna: separately approved bounded phases |
| Architecture | ADR 0217-A/B Proposed; accepted ADRs 0210/0211/0212 remain prior constraints |
| Acceptance | [Scientific Workflow specification](../specs/staqex-scientific-workflow-acceptance.md), R01 |
| Implementation permission | no; no Phase 1 approval |
| Current Next Issue | LISS-0533 Phase 3 Refactor approval |

## Scope

S02以外のspin/interaction小系でgraphから明示Modelを構築し古典/量子energyとdecodeを比較する。

## Out of scope

全graphを自動Hamiltonian化、一般量子優位、live QPU。 共通除外: branch/commit/PR操作は今回禁止、provider SDK/認証/live QPUは独立WP。

## Acceptance scenarios and verification

R01のGiven/When/Thenを適用する。具体的検証: node/edge/index、interaction対称性、全小規模energy、unsupported targetとvalid近傍。

Phase 0でfixture identity、schema/source form/API boundary、tolerance/期待diagnostic、
対象testsの配置、外部依存versionと採用判断の要否を確定する。
数式sourceを変更する場合はparser→typed HIR→Semantic IR→consumer→Resultを検証する。
Host-only契約ではport/APIの意味保存を検証し、source対応済みと主張しない。
外部service不要のfake/固定fixtureを使う。実測profileの検証は権利確認済みsnapshotを使用する。

## Risk / stop conditions

graph edgeとinteraction lawの同一視、offset/scale不一致。
承認済みspecと衝突する場合はArchitecture Pathへ戻す。
一つの契約/代表profileを越える場合はMのままLunaへ渡さず子Issueへ再分割する。
依存はdoneまたは明示waiverが必要。計画の作成/レビューは実装依存の完了を意味しない。

## Completion conditions

受入positive/negativeの対、sourceまたはportからの意味保存、実行/拒否の証拠、
profile限界、費用/誤差/出典の適用fieldを示す。Phase 3 review、Adjudicator final review、
LISS/WP/register同期とprocess reviewを経てdoneにする。
profile一つの完了を分野全体の完成と扱わない。追加profileはWP-0131のcoverage gateへ戻す。

## Luna implementation phases

0. このWPのscopeとR01の具体fixture/期待値をreview。ADR承認とreadinessを確認。
1. 個別Phase 1承認後、受入に対応するRed testsだけを作り、意図した失敗を提示。
2. testsの人間reviewとPhase 2/Implementation承認後、当該境界だけ最小Green。
3. Phase 3承認後、意味を変えずRefactor、再検証、review evidenceと台帳同期。
一回の依頼で複数phaseを実行しない。既存実装と一致する受入は先に証拠を確認し重複実装しない。

## AI planning record

- ID: AIP-WP-0150-2026-09-08-001; status: proposed.
- Author/environment: Sol role, Codex desktop, local shared worktree.
- Model/reasoning: N/A — role指定のみ、実行構成の表示値は取得していない。
- Created: 2026-09-08; size: M; execution scope: 上記一契約/一profile、Lunaへ各phase別に渡す。
- Estimated tokens range/midpoint/metric: N/A — fixture/API/technology review前で信頼できる見積根拠なし。
- Basis/assumptions/confidence: 依存と拒否境界に基づく分割、既存port再利用を仮定、medium。
- Revises: none; WP-0131親計画から新規分割。以前の承認済み見積は変更しない。

## Phase 0 decisions

- R01の代表fixtureは`graph:r01-spin-chain-3-v1`とする。nodeは`spin:0`、
  `spin:1`、`spin:2`、edgeは`spin:0--spin:1`（J=1.0）と
  `spin:1--spin:2`（J=-0.5）、local fieldはh=(0.25, 0.0, -0.25)の
  小規模Ising interactionとする。S02のassay/QUBO fixtureとは別identityにする。
- Graph DTOはnode ID、edge ID、端点順、方向性、重み、重み単位、symmetry policy、
  source/checksum/licenseを保持する。InteractionLawはedge weightとlocal fieldの
  意味を所有し、Graph DTO自体はHamiltonianやoptimization costを意味しない。
- Projection DTOは明示的に`kind: ising-hamiltonian`、variable/index map、
  `H(s)=sum(J_ij s_i s_j)+sum(h_i s_i)+offset`、scale、offset、decode policy、
  source graph identity、projection revisionを保持する。Hamiltonianの物理energyと
  optimization costは別kindとして扱い、暗黙変換しない。
- 正常系は全2^3 spin assignmentでedge対称性、energy、decodeを照合し、Q01の
  `SQXA`/runtime loaderへ渡せる有限projectionとして表現する。数値toleranceは
  fixtureのdecimal係数に対する`1e-12`、index/identity/hashは完全一致とする。
- 拒否診断は`DISCRETE_GRAPH_AS_HAMILTONIAN`（projection指定なし）、
  `DISCRETE_DUPLICATE_EDGE`、`DISCRETE_INDEX_MISMATCH`、
  `DISCRETE_SYMMETRY_MISMATCH`、`DISCRETE_UNSUPPORTED_TARGET`を固定する。
  拒否時はpartial Hamiltonian、SQXA、runtime inputを生成しない。
- Phase 1のテストは`tests/test_liss_0533_discrete_interaction_red.py`に置く。
  fixed in-memory fixtureのみを使用し、network、provider SDK、実機QPU、外部graph
  libraryは使用しない。新規dependency採用判断は不要である。
- Source/API boundaryはGraph -> validated InteractionLaw -> explicit Hamiltonian
  Projection -> Q01 artifact/runtime inputとし、graph adapterは形式変換のみを担当する。
  graphのsemantic authorityとHamiltonian projectionのauthorityを同一DTOへ統合しない。

## Phase 0 acceptance record

- Approval: `WP-0150 / LISS-0533 Phase 0 acceptance 承認`.
- R01 fixture identity、schema/API boundary、energy/decode tolerance、diagnostics、
  test placement、依存判断を確定した。次はPhase 1 Redである。

## Phase 1 Red record

- Added `tests/test_liss_0533_discrete_interaction_red.py` with five contracts
  for explicit graph/law projection, energy/decode behavior, graph-as-
  Hamiltonian rejection, duplicate-edge rejection, index mismatch, and
  unsupported-target rejection.
- Production code remains unchanged. The suite is intentionally Red until the
  separately approved Phase 2 minimum implementation.

## Phase 2 Green record

- Added `compiler/staqex/discrete_interaction_profile.py` with explicit
  `InteractionGraph`, `InteractionLaw`, and `IsingProjection` boundaries.
- Implemented graph/law validation, undirected duplicate-edge detection,
  complete node/index coverage, finite target gating, Ising energy evaluation,
  and spin decode without partial projection on rejection.
- The Red suite was not changed. Targeted pytest passed **5 tests**; AST and
  document lifecycle checks also passed.
- Provider SDK, live QPU, and automatic graph-to-Hamiltonian inference remain
  out of scope.
