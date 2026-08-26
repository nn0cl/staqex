# LISS-0320: `superpose` formal grammar, AST, and type boundary

## Metadata

- Local issue ID: LISS-0320
- Status/phase: **complete** / `phase-3-refactor` (2026-08-04) — Adjudicator
  Completion approval granted; PR #345
- Type: Feature Path (language surface — grammar/AST/typecheck)
- Priority: P1
- Initial planning size: `M`
- Current planning size: `M`
- Owner / agent: Claude Code
- Program: [WP-0092](../work-plans/WP-0092-quantum-mental-model-follow-up.md)
- Parent: [ADR 0189](../architecture/adr/0189-quantum-mental-model-and-observation-contract.md),
  [ADR 0190](../architecture/adr/0190-s02-selection-boundary-and-mix-control.md)
- Depends on: none (grammar addition only; does not require `controlled`)
- Blocks: coherent amplitude/phase execution semantics; `superpose`
  target/QASM lowering and capability rejection (both separately scoped,
  not this Issue)
- Related: LISS/PR for `controlled` formal grammar (not yet filed — deferred
  to its own Issue so this Issue's scope stays single-lane per Adjudicator
  instruction not to mix `superpose` and `controlled` grammar work)
- Branch: `feature/liss-0320-superpose-formal-grammar`
- GitHub Issue / PR: PR #345 (https://github.com/nn0cl/staqex/pull/345)

## Intent

Give `superpose` a real, first-class place in the primary Staqex grammar/AST/
type-check path, distinct from:

- `mix` / `WhenExpr` (probabilistic mixture — must never be conflated).
- `H1Superposition` (the shallow, line-based lexeme-scan classifier added in
  PR #344's `Parser._parse_h1_experiment_body`, which only tags a source
  line for the H1 authoring/state-transform-plan diagnostic and performs no
  real parsing, typing, or evaluation).

Concretely: `superpose(control) { pat -> expr, ... }` parses to a new
`SuperposeExpr`/`SuperposeArm` AST node (structurally parallel to
`WhenExpr`/`WhenArm`), typechecks to `State<T>` from its arm bodies, and is
never silently accepted as `Mixture`/`mix`. Because a typed node must not
crash the evaluator, attempting to actually evaluate a program containing
`superpose` fails closed with one explicit, documented diagnostic (proposed
code: `COHERENT_EXECUTION_UNSUPPORTED`) rather than an unhandled-node
exception or a silent fallback to mixture semantics.

## Explicitly out of scope

- `controlled` grammar/type boundary (separate future Issue).
- Real coefficient/phase-preserving coherent execution math.
- QASM/QPU target-profile lowering and capability-rejection framework (the
  evaluator guard added here is a baseline safety minimum, not that system).
- Any change to the existing H1 authoring heuristic (`H1Superposition`,
  `_parse_h1_experiment_body`) — it is left as-is.
- Scientific lexicon work (separate WP-0092 work unit).

## Acceptance reference

[`staqex-v1-quantum-mental-model-follow-up.md` §4.5](../specs/staqex-v1-quantum-mental-model-follow-up.md)
("`superpose` formal-grammar acceptance scenarios (Phase 1 target,
LISS-0320)").

## AI planning record (size M)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-04
- Size: `M` — touches `tokens.py`, `ast_nodes.py`, `parser.py`,
  `typecheck.py`, and `runtime/evaluator.py`, but the added surface is one
  new expression form structurally mirroring the existing, well-understood
  `WhenExpr`/`WhenArm` pattern; no new port, adapter, or persistence
  boundary. May reclassify to `L` if arm-pattern exhaustiveness or the
  evaluator guard placement surfaces unexpected interaction with existing
  `WhenExpr` code paths during Phase 1 Red.
- Route: direct implementation by this session (no external AI/model call
  planned beyond normal code generation).
- Estimate: N/A — no token/time budget tracked for this environment.
- Assumptions: `superpose` needs its own `TokenKind` (not reusing
  `TokenKind.WHEN`, unlike how `mix` reuses `WHEN` today) so `SuperposeExpr`
  and `WhenExpr` remain structurally distinguishable at parse time, not just
  by AST class.
- Confidence: medium-high on grammar/AST/typecheck; medium on the exact
  evaluator guard placement without first reading the full `WhenExpr`
  evaluation dispatch in `runtime/evaluator.py`.
- Revision links: none yet.

## Exit criteria

- [x] Phase 1 Red: acceptance test(s) implementing spec §4.5's four
      scenarios exist and fail for the documented reason (no `SuperposeExpr`
      today; `superpose` lexes as a plain identifier). Commit `06e4d6a`: 3/4
      failed on `PARSE_ERROR`, 1/4 (mix/when regression) passed unchanged.
- [x] Phase 2 Green: minimal implementation makes those tests pass without
      editing the tests, without touching `controlled`, and without changing
      existing `mix`/`when` behavior (regression scenario passes unchanged).
      Commit `d375fd9`: 4/4 passed. One test-file correction was needed
      (import `run_source` from `compiler.staqex.host`, not
      `compiler.staqex.run` — the latter does not catch
      `KernelDiagnosticError`); no assertion was weakened.
- [x] Phase 3 Refactor: no behavior change; reviewer empathy summary
      produced (see below). One micro-refactor (merged two identical
      `isinstance` branches in `hir.py::_expr_children` into one tuple
      check) — re-verified green after.
- [x] Full regression: `pytest tests/ -q` → 1209 passed; `python3
      tests/spec_verification/run_all.py` → 161/161; `git diff --check` →
      clean.
- [x] WP-0092 synchronized with the outcome (this same reviewable unit).
      `open-work-register.md` intentionally not yet updated — see note below;
      will be updated at Completion approval alongside PR/merge evidence, to
      avoid recording "shipped" before Adjudicator sign-off.

## Reviewer empathy summary

**何を目的として何を変更したか**: `superpose`を、PR #344が追加した浅いH1行走査
ヒューリスティックとは別に、通常のパーサ/AST/型検査経路の一級市民にした。
`SuperposeExpr`は`WhenExpr`(`mix`)と構造的に並行だが型としては別物であり、
`mix`へのフォールバックは一切ない。コヒーレント振幅/位相の実行は別スライスの
ため、実際にプログラムを評価しようとすると`COHERENT_EXECUTION_UNSUPPORTED`で
明示的にfail closedする(クラッシュや`mix`への暗黙フォールバックはしない)。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- 診断コード名`COHERENT_EXECUTION_UNSUPPORTED`は本Issueの提案であり、
  Adjudicatorの命名選好が未確認(LISS-0320本文の「open decision」参照)。
- `SuperposeExpr`の型検査は`WhenExpr`の網羅性検査
  (`_check_when_enum_exhaustive`)と係数位置チェック
  (`COEFFICIENT_IN_QUANTUM_POSITION`)を意図的に複製していない —
  これらは`mix`の真空サンプリング実行ポリシーに紐づく規則であり、
  `superpose`はまだ実行できないため適用対象外と判断した。将来の実行実装
  スライスで再検討が必要。
- `hir.py`のリニアリソース消費解析(`_expr_children`/
  `_consume_when_linear_uses`)への追加は、`compiled.ok`を通すために
  実行時に発見した必須修正であり、事前のDESIGN CHECKでは予見していなかった
  (`unitarity_check.py`/`physical_axioms.py`/`pipeline.py`等、他の
  `WhenExpr`参照箇所は今回のテストでは到達せず、変更不要だった — ただし
  将来`superpose`が他の文脈で使われた場合、追加の`WhenExpr`参照箇所に
  同様のギャップが見つかる可能性がある)。

**人間がコードレビューで重点的に見るべきポイント**:
- 診断コード名の最終承認。
- `hir.py`の線形消費解析修正が正しいかどうか(`control`が両方の腕で
  正しく「消費済み」として扱われるか)。
- `SuperposeExpr`型検査で網羅性/係数チェックを省略した判断への同意。
- `open-work-register.md`をこのタイミングで更新するか、PR/マージ時まで
  待つかの手順確認。

## Non-goals

- Making `superpose` executable with real physics.
- Deciding `controlled`'s grammar.
- Any QASM/backend lowering work.
