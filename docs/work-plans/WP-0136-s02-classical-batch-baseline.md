# WP-0136: S02古典batch目的とfeasibility oracle

| Field | Value |
|---|---|
| Status | done |
| Phase | complete |
| Size initial/current | M / M — one bounded profile or boundary; elapsed-time estimateではない |
| Parent | [WP-0131](WP-0131-scientific-workflow-program.md) |
| Issue | [LISS-0519](../issues/LISS-0519-s02-classical-batch-baseline.md) |
| Depends on | [WP-0135](WP-0135-s02-leakage-safe-model.md) |
| Blocks | WP-0139 |
| Owner / route | Sol: independent design correction and coordination; Luna: separately approved bounded phases |
| Architecture | ADR 0217-A accepted; accepted ADRs 0210/0211/0212 remain prior constraints |
| Acceptance | [Scientific Workflow specification](../specs/staqex-scientific-workflow-acceptance.md), D03 |
| Implementation permission | approved for bounded D03 implementation only; completed |
| Current Next Issue | WP-0139 / LISS-0522 QUBO feasibility and encoding |

## Scope

同一候補集合でbudget/stock/diversity等のhard constraintsと目的を定義し、小規模enumeration oracleと一つの古典baselineを比較する。

## Out of scope

量子回路、prospective assay、baseline手法の無承認採用。 共通除外: branch/commit/PR操作は今回禁止、provider SDK/認証/live QPUは独立WP。

## Acceptance scenarios and verification

D03のGiven/When/Thenを適用する。具体的検証: 列挙可能な小問題でscoreとconstraint verdict一致。実測profileで実用規模baselineの費用を計測。infeasible近傍も確認。

Phase 0でfixture identity、schema/source form/API boundary、tolerance/期待diagnostic、
対象testsの配置、外部依存versionと採用判断の要否を確定する。
数式sourceを変更する場合はparser→typed HIR→Semantic IR→consumer→Resultを検証する。
Host-only契約ではport/APIの意味保存を検証し、source対応済みと主張しない。
外部service不要のfake/固定fixtureを使う。実測profileの検証は権利確認済みsnapshotを使用する。

## Phase 0 decisions

- Input is the single WP-0134/WP-0135 S02 profile plus a frozen candidate
  inventory. Candidate records retain candidate ID, predicted IC50 in nM,
  uncertainty, stock status, cost units, and diversity group. The fixture is
  deterministic and synthetic; it is not a prospective assay recommendation.
- The candidate set is fixed to five opaque IDs (`candidate:001` through
  `candidate:005`) and batch size is exactly two. The budget is 8 cost units;
  stock must be available; at most one candidate from a diversity group may be
  selected. These are hard constraints, not penalties.
- The objective is to minimize the sum of predicted IC50 values over the
  selected batch. Uncertainty is reported beside the score but is not silently
  substituted into the objective. Every candidate and constraint input is
  identical for enumeration and the baseline.
- The enumeration oracle evaluates every two-candidate subset and independently
  returns feasibility, objective score, and selected IDs. If no subset is
  feasible, the result is `no-feasible-plan`, never an empty successful plan.
- The predefined classical baseline is `greedy-feasible-v1`: sort by predicted
  IC50 ascending, then candidate ID for ties; append a candidate only when all
  hard constraints remain satisfied. This is a deterministic reference, not a
  technology selection or claim of optimality beyond the oracle-sized fixture.
- The use case owns objective, hard-constraint, infeasibility, and comparison
  policy. `CandidateSourcePort` supplies the frozen inventory and
  `ClassicalSelectionPort` supplies the baseline lane; neither adapter owns
  scientific policy. No optimizer library, database, provider, or QPU is
  selected.
- Stable diagnostics are `BATCH_CANDIDATE_SET_MISMATCH`,
  `BATCH_CONSTRAINT_MISMATCH`, `BATCH_SCORE_MISMATCH`, and
  `BATCH_NO_FEASIBLE_PLAN`. Constraint verdict and score are returned as
  separate fields so penalty-only low scores cannot be accepted as feasible.
- Phase 1 tests live in `tests/test_s02_classical_batch_baseline_red.py` and
  cover oracle/baseline agreement on the feasible fixture, independent
  constraint verification, candidate-set mismatch, score mismatch, and the
  no-feasible-plan result.

## Phase 1 Red record

- Added only `tests/test_s02_classical_batch_baseline_red.py`.
- The suite fixes the observable D03 contract for oracle/baseline agreement,
  explicit no-feasible-plan semantics, candidate-set mismatch quarantine, and
  non-comparable constraint/score results.
- The expected implementation module is
  `compiler.staqex.s02_classical_batch_baseline`; it is intentionally absent
  until Phase 2/Implementation approval.

## Phase 2 Green record

- Implemented `compiler/staqex/s02_classical_batch_baseline.py` for the bounded
  D03 contract only.
- Exhaustive enumeration and `greedy-feasible-v1` share the same candidate
  records and hard feasibility checks; score and feasibility remain separate.
- Candidate-set, constraint, and score mismatches are quarantined, and an
  infeasible fixture returns `no-feasible-plan` rather than empty success.
- No optimizer library, quantum circuit, provider, database, or experiment
  ordering was added.

## Phase 3 Refactor record

- Centralized comparison quarantine result construction in a small helper.
- Preserved oracle／baseline selection, feasibility, score, and diagnostic
  behavior without changing assertions.
- Direct refactor checks, syntax, diff, and document lifecycle checks passed.

## Final review record

Phase 3 final review approved on 2026-09-09. The bounded D03 slice is complete;
larger-scale optimization, experiment ordering, and quantum comparison remain
explicitly out of scope. See [Review Summary](../collaboration/reviews/2026-09-09-liss-0519-phase3-final-review.md).

Process review: no operating-contract deviation or operational problem found.

## Phase 1 Red record

- Added only `tests/test_s02_classical_batch_baseline_red.py`.
- The suite fixes the observable D03 contract for oracle/baseline agreement,
  explicit no-feasible-plan semantics, candidate-set mismatch quarantine, and
  non-comparable constraint/score results.
- The expected implementation module is
  `compiler.staqex.s02_classical_batch_baseline`; it is intentionally absent
  until Phase 2/Implementation approval.

## Risk / stop conditions

penaltyをhard制約と誤認、候補集合/費用の比較条件不一致。
承認済みspecと衝突する場合はArchitecture Pathへ戻す。
一つの契約/代表profileを越える場合はMのままLunaへ渡さず子Issueへ再分割する。
依存はdoneまたは明示waiverが必要。計画の作成/レビューは実装依存の完了を意味しない。

## Completion conditions

受入positive/negativeの対、sourceまたはportからの意味保存、実行/拒否の証拠、
profile限界、費用/誤差/出典の適用fieldを示す。Phase 3 review、Adjudicator final review、
LISS/WP/register同期とprocess reviewを経てdoneにする。
profile一つの完了を分野全体の完成と扱わない。追加profileはWP-0131のcoverage gateへ戻す。

## Luna implementation phases

0. このWPのscopeとD03の具体fixture/期待値をreview。ADR承認とreadinessを確認。
1. 個別Phase 1承認後、受入に対応するRed testsだけを作り、意図した失敗を提示。
2. testsの人間reviewとPhase 2/Implementation承認後、当該境界だけ最小Green。
3. Phase 3承認後、意味を変えずRefactor、再検証、review evidenceと台帳同期。
一回の依頼で複数phaseを実行しない。既存実装と一致する受入は先に証拠を確認し重複実装しない。

## AI planning record

- ID: AIP-WP-0136-2026-09-08-001; status: proposed.
- Author/environment: Sol role, Codex desktop, local shared worktree.
- Model/reasoning: N/A — role指定のみ、実行構成の表示値は取得していない。
- Created: 2026-09-08; size: M; execution scope: 上記一契約/一profile、Lunaへ各phase別に渡す。
- Estimated tokens range/midpoint/metric: N/A — fixture/API/technology review前で信頼できる見積根拠なし。
- Basis/assumptions/confidence: 依存と拒否境界に基づく分割、既存port再利用を仮定、medium。
- Revises: none; WP-0131親計画から新規分割。以前の承認済み見積は変更しない。
