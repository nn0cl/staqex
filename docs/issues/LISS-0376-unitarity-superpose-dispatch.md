# LISS-0376: unitarity guard's quantum-lineage tracker misses `superpose`

## Metadata

- Local issue ID: LISS-0376
- Status/phase: **complete** (2026-08-08) — PR
  [#470](https://github.com/nn0cl/staqex/pull/470) merged, commit
  `2cd8950`
- Type: Kernel bug fix (`compiler/staqex/unitarity_check.py`); no
  example content
- Priority: P4 (a static-analysis coverage gap that is currently
  dormant — not reachable at runtime today because `superpose(...)`
  coherent execution is itself unconditionally fail-closed-rejected by
  a separate, deliberate LISS-0320 gate — but confirmed real at the
  static-analysis layer and will become live once superpose execution
  ships)
- Initial planning size: `S`
- Owner / agent: Claude Code
- Program: standalone Kernel fix, second and final candidate from the
  fifth architectural audit round (LISS-0375 covered the first)
- Parent: none
- Depends on: none
- Blocks: none
- Branch: `feature/liss-0376-unitarity-superpose-dispatch`
- GitHub Issue / PR: [#470](https://github.com/nn0cl/staqex/pull/470)
  (merged, `2cd8950`)

## Design decision

Live-verified: `state psi = |0>; state bad = map(psi, x -> 0)` (a
bit-collapsing, non-injective classical remap on a ket-bound quantum
lineage) correctly raises `NON_UNITARY_TRANSFORM_ERROR`
(`unitarity_check.py`, ADR 0045/0052). The identical construct, with
the quantum lineage instead bound via `superpose(control) { 0 -> psi,
1 -> psi }` before the same `map(...)` call, compiles without
`NON_UNITARY_TRANSFORM_ERROR` at all — the diagnostic set is otherwise
identical between the two cases except for this one missing code.

Root cause: `unitarity_check.py::_expr_is_quantum` — the function that
decides whether a bound name feeds the `quantum`/`strict` tracking
dicts `check_unitarity` uses to police non-unitary transforms — has
cases for `KetLit`, `Coin`, `Var`, `Dirac`, `Inspect`, `UnaryNot`,
`Call`, `WhenExpr`, `BinOp`, `TensorExpr`, `EvolveExpr`, `TupleExpr`,
`Pipe`, `Attr`, `Lambda`, but no case for `SuperposeExpr`
(`superpose(control) { ... }`, LISS-0320's coherent-lane surface,
"structurally parallel to `WhenExpr`" per its own AST-node docstring)
— so a `superpose`-bound state is silently tracked as non-quantum and
every subsequent non-unitary-transform check on it is skipped, the
same narrow-AST-shape-dispatch category as every finding this session.

**Downstream reachability**: live-verified that any program binding a
state via `superpose(...)` currently fails at *runtime* regardless,
with `COHERENT_EXECUTION_UNSUPPORTED` (`runtime/evaluator.py`, a
deliberate LISS-0320 fail-closed gate) — so this gap cannot yet produce
a silently-wrong *measured* result in practice. It is a confirmed,
real coverage gap in a static analysis pass whose job is to be
unconditional, not a currently-exploitable runtime bug; fixed now as a
regression-prevention measure so the gap does not surface later, once
superpose coherent execution ships, as a much harder-to-trace silent
bug.

**Adopted fix**: add a `SuperposeExpr` case to `_expr_is_quantum`,
mirroring the existing `WhenExpr` case immediately above it exactly
(same `ctrl`/`arms[].body` structure, per `SuperposeArm`'s own
docstring stating it is "structurally parallel to `WhenArm`") — quantum
if either the control or any arm body is itself quantum.

## Explicitly out of scope

- Actually shipping `superpose(...)` coherent execution (LISS-0320's
  own scope; this fix only closes a latent static-analysis gap that
  would otherwise resurface once that ships).
- LISS-0375 (the round's first candidate,
  `nested_when.py::_walk` missing a `TensorExpr` case) — fixed and
  merged separately.

## Acceptance reference

```gherkin
Feature: the unitarity guard's quantum-lineage tracker recognizes a superpose-bound state

  Scenario: a non-unitary transform on a superpose-bound state is rejected the same way a ket-bound one already is
    Given `state sp = superpose(control) { 0 -> psi, 1 -> psi }`
      followed by a bit-collapsing `map(sp, x -> 0)`
    When compiled
    Then it raises NON_UNITARY_TRANSFORM_ERROR (regression guard: the
      equivalent ket-bound form already raises this)
```

## Verification plan for this design intake (not shipped as a test)

The gap confirmed live before drafting this Issue by comparing
diagnostic code sets between the baseline ket-bound case (correctly
rejected) and the equivalent superpose-bound case (silently missing
just the one diagnostic) via `compile_source(...)` alone — no
execution needed, since this is a purely static-analysis gap. Full
`pytest tests/ -q` sweep after the fix, diffed against the current
baseline (0 failed, 1332 passed — `main` is fully green), confirming no
regression. `spec_verification` expected unchanged (161/161).

## AI planning record (size S)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-08
- Size: `S` — one new case in one dispatch function, mirroring an
  already-correct, structurally-identical sibling case (`WhenExpr`)
  immediately above it.
- Route: direct implementation by this session.
- Confidence: high — the gap, its non-exploitability today (blocked by
  a separate deliberate fail-closed gate), and the fix's target pattern
  were all directly confirmed by reading the surrounding code and
  live-reproducing before planning.

## Exit criteria

- [x] Phase 1 Red: `tests/test_liss_0376_unitarity_superpose_dispatch_red.py`
      added (2 cases). Confirmed via `git stash` isolation: the
      baseline ket-bound case already passed unchanged (correctly
      rejected before this fix); the superpose-bound case failed with
      `NON_UNITARY_TRANSFORM_ERROR` absent from the diagnostics,
      matching the finding exactly.
- [x] Phase 2 Green: `_expr_is_quantum` gained a `SuperposeExpr` case,
      mirroring the existing `WhenExpr` case immediately above it
      exactly (same `ctrl`/`arms[].body` structure). Both tests pass.
- [x] Phase 3 Refactor: design decision section already recorded the
      full rationale, including the current non-exploitability caveat,
      at Plan time (no new findings surfaced during Green); reviewer
      empathy summary below.
- [x] Full regression: `pytest tests/ -q` → **1332 passed, 0 failed**
      (+2 this Issue's own new tests, on top of the pre-LISS-0375
      baseline this branch was cut from) — `main` stays fully green;
      `python3 tests/spec_verification/run_all.py` → **161/161** (100%,
      Gate: PASS, unchanged); `git diff --check` → clean.

### 変更の要約 (PR Summary)

**何を目的として何を変更したか**: 第5回アーキテクチャ監査の第2候補、
`unitarity_check.py::_expr_is_quantum`(状態が量子系統かどうかを
追跡する関数、ADR 0045/0052の非ユニタリ変換ガードの基盤)が
`SuperposeExpr`(LISS-0320のコヒーレント合成レーン)を認識せず、
`superpose(...)`でバインドされた状態が非量子として誤追跡され、
後続の非ユニタリ変換チェックが完全にスキップされていた問題を
修正した。`SuperposeArm`のdocstringが明記する通り`WhenArm`と
構造的に並行なので、既存の`WhenExpr`ケースをそのまま模倣した
1ケース追加のみの最小修正。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- この不具合は現時点では実際には到達不可能であることを実装前に
  確認した——`superpose(...)`でバインドされた状態は、別の意図的な
  LISS-0320のfail-closedゲート(`COHERENT_EXECUTION_UNSUPPORTED`)
  により実行時に必ず拒否されるため、今回の静的解析ギャップだけでは
  サイレントに誤った測定結果を生成することはできない。それでも、
  静的解析パスは本来無条件であるべきという原則と、将来
  `superpose`のコヒーレント実行が実装された際に発見しづらい
  サイレントバグとして再浮上することを防ぐため、回帰防止措置として
  今のうちに修正することが承認された。
- テストは`compile_source`のみで検証しており、実行(`run_source`)は
  不要——これは純粋に静的解析層のギャップであるため。

**人間がコードレビューで重点的に見るべきポイント**:
- Priority P4という優先度付けと「現在到達不可能」という説明が、
  実装内容(1ケース追加のみ)の小ささと釣り合っているか。

## Non-goals

- Shipping `superpose(...)` coherent execution.
- LISS-0375 (separate finding, tracked independently).
