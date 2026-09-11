# WP-0158: S02量子projectionと古典baseline比較

| Field | Value |
|---|---|
| Status | complete |
| Phase | done |
| Size initial/current | M / M — one bounded profile or boundary; elapsed-time estimateではない |
| Parent | [WP-0131](WP-0131-scientific-workflow-program.md) |
| Issue | [LISS-0541](../issues/LISS-0541-s02-quantum-baseline-comparison.md) |
| Depends on | [WP-0137](WP-0137-scientific-quantum-projection.md); [WP-0139](WP-0139-s02-assay-batch-cycle.md); [WP-0151](WP-0151-scientific-reproducibility-evidence.md) |
| Blocks | WP-0153 |
| Owner / route | Sol: independent design correction and coordination; Luna: separately approved bounded phases |
| Architecture | ADR 0217-A/B/C Proposed; accepted ADRs 0210/0211/0212 remain prior constraints |
| Acceptance | [Scientific Workflow specification](../specs/staqex-scientific-workflow-acceptance.md), D05/Q01/E01 |
| Implementation permission | complete for this bounded provider-neutral comparison kernel |
| Current Next Issue | none for WP-0158; broader conformance remains WP-0153 |

## Scope

固定した実測S02 problemを同じ候補/制約で量子Simulator/有限targetと古典baselineへ渡し、終端decode/feasibilityと総費用を比較する。

## Out of scope

live QPU、provider導入、候補集合やmetricの結果後変更、量子優位の保証。 共通除外: branch/commit/PR操作は今回禁止、provider SDK/認証/live QPUは独立WP。

## Acceptance scenarios and verification

D05/Q01/E01のGiven/When/Thenを適用する。具体的検証: small-instance oracle、同一cutoff/候補集合/constraint、全encoding/queue/shots/棄却費用を比較。QPU拒否時は理想意味と古典結果を保持してlaneを区別。

Phase 0でfixture identity、schema/source form/API boundary、tolerance/期待diagnostic、
対象testsの配置、外部依存versionと採用判断の要否を確定する。
数式sourceを変更する場合はparser→typed HIR→Semantic IR→consumer→Resultを検証する。
Host-only契約ではport/APIの意味保存を検証し、source対応済みと主張しない。
外部service不要のfake/固定fixtureを使う。実測profileの検証は権利確認済みsnapshotを使用する。

## Phase 0 acceptance/profile review

### Fixed inputs and lineage

- D04 input snapshot: `assay:s02-round-001` from the immutable curated
  snapshot; no raw assay mutation and no later-round labels.
- Candidate inventory: `candidates:s02-fixture-v1`, five candidates from the
  D03 fixture, with `candidate:001` and `candidate:002` as the expected
  optimum under the fixed profile.
- Profile: `batch:s02-v1`, batch size 2, budget 8, maximum one candidate per
  diversity group, objective `minimize_predicted_ic50_nM`.
- Classical lanes: `baseline:greedy-feasible-v1` and
  `oracle:enumeration-v1`; both consume the identical candidate tuple and
  profile. The enumeration oracle is the correctness reference, not a claim
  of production-scale optimization.
- Quantum artifact: `artifact:s02-d05-q01-v1`, problem
  `problem:s02-batch-v1`, schema `sqxa/1`, source hash and content hash
  retained. Runtime capability is `finite-binary-projection`.
- Evidence manifest: `manifest:s02-d05-v1`, environment
  `environment:local-python-v1`, fixed seed `s02-d05-seed-001`, float64,
  command identity, all lane identities, and cost fields.

### Encoding and comparison boundary

- Use one explicit binary carrier `x_candidate` per candidate. `x=1` means
  selected and `x=0` means not selected; variable order is the candidate
  inventory order and is stored in the encoding map.
- The fixed cardinality and diversity constraints are encoded explicitly in
  the QUBO penalty terms. The budget is checked by the independent terminal
  feasibility verifier and is part of the fixed profile; this bounded fixture
  has no budget-infeasible feasible-size subset. A future profile that needs
  budget slack variables requires a new Phase 0 decision and is not silently
  folded into this unit.
- The quantum lane owns only projection, artifact loading, finite execution
  handoff, and terminal decode. The classical baseline owns selection policy;
  adapters do not decide feasibility, objective, or scientific success.
- Comparison requires identical candidate IDs, profile revision, cutoff,
  selected-cardinality, hard constraints, and objective inputs. It reports
  exact selected-ID match, feasibility match, objective value/gap to the
  enumeration oracle, decode validity, and a separated cost breakdown.
- A QPU/finite-target rejection, missing artifact, invalid decode, or missing
  cost is retained as a quantum-lane failure or `inconclusive` comparison.
  It never becomes a classical success or a quantum-advantage claim.

### Numeric, statistical, and diagnostic policy

- Deterministic local comparison uses float64 with absolute energy/objective
  tolerance `1e-12`; identity, variable order, constraint verdict, and
  decoded candidate IDs require exact equality.
- The local simulator lane is deterministic, so statistical confidence is not
  claimed. A finite target or sampled provider result must supply its own
  predeclared shots/confidence interval in E01; it is out of scope here.
- Expected fail-closed diagnostics are `QUANTUM_CANDIDATE_SET_MISMATCH`,
  `QUANTUM_DECODE_INVALID`, `QUANTUM_CONSTRAINT_VIOLATION`,
  `QUANTUM_ARTIFACT_UNAVAILABLE`, `QUANTUM_RUNTIME_REJECTED`,
  `QUANTUM_COST_MISSING`, `QUANTUM_COMPARISON_INCONCLUSIVE`,
  `QUANTUM_PROJECTION_UNSUPPORTED`, and `QUANTUM_BASELINE_MISMATCH`.

### Ports, files, and dependency decision

- Planned ports are `ClassicalBaselinePort`, `QuantumProjectionPort`,
  `FiniteExecutionPort`, `CostObservationPort`, and `EvidenceStorePort`.
  Domain/use-case code owns comparison policy and diagnostics; adapters only
  translate the existing D03/Q01/E01 records.
- Phase 1 Red tests go in
  `tests/test_s02_quantum_baseline_comparison_red.py`. They use fixed in-memory
  fixtures and fake ports; no network, credentials, SDK, or live QPU is
  required.
- No new dependency or technology is selected. The implementation reuses the
  existing D03 baseline/oracle, Q01 `.sqxa` artifact boundary, and E01
  provider-neutral evidence types. AWS Braket/provider selection remains a
  separate future task.

### Open decision boundaries

- This Phase 0 profile intentionally fixes the small one-bit-per-candidate
  encoding and penalty semantics only for `problem:s02-batch-v1`.
- General budget quadratization, alternative encodings, sampled finite-target
  statistics, provider mapping, and live QPU execution require separate
  profile/technology approval. No implementation permission is implied by
  this design record.

Phase 0 outcome: profile, fixture lineage, comparison contract, ports,
diagnostics, tolerances, test placement, and dependency policy are specified.
The profile was accepted by the Adjudicator. No implementation permission is
implied; next request is `LISS-0541 Phase 1 Red 承認`.

## Phase 1 Red record

- Added only `tests/test_s02_quantum_baseline_comparison_red.py`.
- The five tests fix matching-lane comparison, candidate-set mismatch,
  invalid quantum decode/constraint verdict, retained quantum runtime
  rejection, and missing-cost handling.
- Tests use the fixed D03/D04 lineage and fake/in-memory lane records. No
  provider, network, credential, or live QPU is used.
- `PYTHONPATH=. .venv/bin/pytest -q tests/test_s02_quantum_baseline_comparison_red.py`
  reports 5 intentional failures because the production comparison module is
  not present. `py_compile` and `git diff --check` pass.
- Next request: `LISS-0541 Phase 2 Green / Implementation 承認`.

## Phase 2 Green record

- Added `compiler/staqex/s02_quantum_baseline_comparison.py` with immutable
  lane/result DTOs, cost completeness, terminal decode/feasibility checks,
  candidate identity comparison, objective tolerance, and explicit quantum
  `inconclusive` fallback handling.
- The reviewed Red suite was unchanged. No provider SDK, network, credential,
  live QPU, or general QUBO automation was added.
- Focused pytest: 5 passed. `py_compile` and `git diff --check` pass.
- Next request: `LISS-0541 Phase 3 Refactor 承認`.

## Phase 1 Red lineage-contract correction record

- Added only lineage fields to the lane fixtures and two Red contracts in
  `tests/test_s02_quantum_baseline_comparison_red.py`. The new contracts cover
  snapshot/artifact mismatch quarantine and preservation of comparison
  lineage identity in a matched result.
- The existing five D05 contracts remain unchanged in meaning. The suite now
  reports 7 intentional failures because `LaneResult` and `ComparisonResult`
  do not yet expose or validate the approved lineage contract.
- No production code, provider SDK, network, credential, or live QPU was
  changed or used. `py_compile` and `git diff --check` pass.
- Next request: `LISS-0541 Phase 2 Green / Implementation 再承認`.

## Phase 2 Green lineage-contract correction record

- Extended `LaneResult` with snapshot, candidate-set, profile, baseline,
  artifact, encoding, and manifest identities. Extended `ComparisonInput` with
  the encoding and manifest expectations while retaining compatibility defaults
  for the fixed D05 profile.
- Added fail-closed comparison of lane-to-lane and quantum-to-input lineage.
  Candidate/profile mismatches use `QUANTUM_CANDIDATE_SET_MISMATCH`; other
  lineage mismatches use `QUANTUM_BASELINE_MISMATCH`.
- Extended matched `ComparisonResult` with the comparison lineage evidence.
  Existing candidate, feasibility, objective, cost, rejection, and fallback
  behavior remains unchanged. No provider SDK, network, credential, or live
  QPU was used.
- Focused pytest: 7 passed. `py_compile` and `git diff --check` pass.
- Next request: `LISS-0541 Phase 3 Refactor 承認`.

## Phase 3 Refactor record

- Consolidated the lineage field list and mismatch diagnostic mapping into
  private helpers/constants, removing duplicated comparison logic without
  changing public DTOs, assertions, diagnostic codes, or precedence.
- Focused D05 plus related S02 verification: 16 passed. `py_compile` and
  `git diff --check` pass.
- No provider SDK, network, credential, or live QPU was used.
- Next request: `LISS-0541 Phase 3 最終レビュー 承認`.

## Final review record

- Final review approved the D05 lineage, candidate identity, decode/feasibility,
  objective tolerance, cost, and runtime rejection boundaries. No blocker was
  found; provider SDK, network, credentials, and live QPU remain out of scope.
- Focused D05 plus related S02 verification: 16 passed. `py_compile` and
  `git diff --check` pass.
- Process review: no operating-contract deviation or operational problem found.
- WP-0158 is complete for the bounded comparison kernel. Broader scientific
  profile coverage and live-provider delivery remain separate work.

## Phase 3 Refactor record

- Extracted selection equality, missing-cost result construction, and matched
  result construction into named helpers.
- Preserved the public DTOs, diagnostic codes, lane precedence, comparison
  tolerance, fallback behavior, and reviewed Red suite.
- Focused pytest: 5 passed. `py_compile` and `git diff --check` pass.
- Next request: `LISS-0541 Phase 3 最終レビュー 承認`.

## Phase 3 final-review disposition (2026-09-11)

- Focused D05, D03, and Q01 verification passed 14 tests.
- Final review found that snapshot/cutoff, profile, baseline/artifact,
  encoding, and manifest lineage are stored only at the outer input and are
  not machine-checked per lane. This is a blocker against the accepted Phase
  0 identity contract.
- The prior Phase 2/3 implementation remains bounded comparison behavior, not
  completion. Next request:
  `LISS-0541 Phase 1 Red lineage-contract correction 承認`.

## Risk / stop conditions

postselectionやencoding費用の除外、拒否を量子実行成功と表示。
承認済みspecと衝突する場合はArchitecture Pathへ戻す。
一つの契約/代表profileを越える場合はMのままLunaへ渡さず子Issueへ再分割する。
依存はdoneまたは明示waiverが必要。計画の作成/レビューは実装依存の完了を意味しない。

## Completion conditions

受入positive/negativeの対、sourceまたはportからの意味保存、実行/拒否の証拠、
profile限界、費用/誤差/出典の適用fieldを示す。Phase 3 review、Adjudicator final review、
LISS/WP/register同期とprocess reviewを経てdoneにする。
profile一つの完了を分野全体の完成と扱わない。追加profileはWP-0131のcoverage gateへ戻す。

## Luna implementation phases

0. このWPのscopeとD05/Q01/E01の具体fixture/期待値をreview。ADR承認とreadinessを確認。
1. 個別Phase 1承認後、受入に対応するRed testsだけを作り、意図した失敗を提示。
2. testsの人間reviewとPhase 2/Implementation承認後、当該境界だけ最小Green。
3. Phase 3承認後、意味を変えずRefactor、再検証、review evidenceと台帳同期。
一回の依頼で複数phaseを実行しない。既存実装と一致する受入は先に証拠を確認し重複実装しない。

## AI planning record

- ID: AIP-WP-0158-2026-09-08-001; status: proposed.
- Author/environment: Sol role, Codex desktop, local shared worktree.
- Model/reasoning: N/A — role指定のみ、実行構成の表示値は取得していない。
- Created: 2026-09-08; size: M; execution scope: 上記一契約/一profile、Lunaへ各phase別に渡す。
- Estimated tokens range/midpoint/metric: N/A — fixture/API/technology review前で信頼できる見積根拠なし。
- Basis/assumptions/confidence: 依存と拒否境界に基づく分割、既存port再利用を仮定、medium。
- Revises: none; WP-0131親計画から新規分割。以前の承認済み見積は変更しない。

## Phase 1 Red record

- Added only `tests/test_s02_quantum_baseline_comparison_red.py`.
- The five tests fix matching-lane comparison, candidate-set mismatch,
  invalid quantum decode/constraint verdict, retained quantum runtime
  rejection, and missing-cost handling.
- Tests use the fixed D03/D04 lineage and fake/in-memory lane records. No
  provider, network, credential, or live QPU is used.
- Focused pytest reports 5 intentional failures because the production
  comparison module is not present. `py_compile` and `git diff --check` pass.
- Next request: `LISS-0541 Phase 2 Green / Implementation 承認`.

## Phase 2 Green record

- Added `compiler/staqex/s02_quantum_baseline_comparison.py` with immutable
  lane/result DTOs, cost completeness, terminal decode/feasibility checks,
  candidate identity comparison, objective tolerance, and explicit quantum
  `inconclusive` fallback handling.
- The reviewed Red suite was unchanged. No provider SDK, network, credential,
  live QPU, or general QUBO automation was added.
- Focused pytest: 5 passed. `py_compile` and `git diff --check` pass.
- Next request: `LISS-0541 Phase 3 Refactor 承認`.
