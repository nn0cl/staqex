# LISS-0375: `NESTED_WHEN_ERROR` guard misses a `mix` wrapped in a tensor product

## Metadata

- Local issue ID: LISS-0375
- Status/phase: **complete** (2026-08-08) — PR
  [#469](https://github.com/nn0cl/staqex/pull/469) merged, commit
  `fe29104`
- Type: Kernel bug fix (`compiler/staqex/nested_when.py`); no example
  content
- Priority: P3 (a static coherence guard is bypassable for one AST
  shape; in the live repro the same program still fails downstream for
  an unrelated reason, so not yet a confirmed silently-wrong-output
  path, but the guard itself — meant to be unconditional — is confirmed
  bypassed)
- Initial planning size: `S`
- Owner / agent: Claude Code
- Program: standalone Kernel fix, first candidate from a fifth
  architectural audit round (same recurring narrow-AST-shape-dispatch
  category; LISS-0376 tracks the round's second candidate)
- Parent: none
- Depends on: none
- Blocks: none
- Branch: `feature/liss-0375-nested-when-tensor-dispatch`
- GitHub Issue / PR: [#469](https://github.com/nn0cl/staqex/pull/469)
  (merged, `fe29104`)

## Design decision

Live-verified: `state bad = mix (c) { 0 -> mix (d) {...}, else -> |0> }`
(a `mix` nested directly inside another `mix`'s arm) correctly raises
`NESTED_WHEN_ERROR` (ADR 0045's static coherence guard —
`nested_when.py::check_nested_when`). The identical coherence
violation, embedded directly in a single `*|*` tensor-product statement
(`state ab = a *|* (mix (c) { 0 -> mix (d) {...}, else -> |0> })`),
compiles without `NESTED_WHEN_ERROR` at all. (An earlier repro attempt
first bound the nested `mix` to its own name in a separate statement,
then tensor-combined it with a second statement — that version still
correctly raised `NESTED_WHEN_ERROR`, because `check_nested_when`
checks each statement's own top-level expression independently and the
nested-`mix` bind statement is itself directly a `WhenExpr`. The gap
only reproduces when the nested `mix` is embedded *inside* the tensor
expression at the same statement, which is what the fix targets.)

Root cause: `nested_when.py::_walk` — the recursive expression walker
that finds every `WhenExpr` reachable from a statement — has cases for
`BinOp`, `Call`, `Attr`, `Dirac`, `Inspect`, `Pipe`, `Lambda`,
`TupleExpr`, `EvolveExpr`, `WhenExpr`, but no case for `TensorExpr`
(`a *|* b`), so a nested `mix` reachable only through a tensor operand
is never visited — the same narrow-AST-shape-dispatch category as
every finding this session.

**Adopted fix**: add a `TensorExpr` case to `_walk`, recursing into
`expr.left`/`expr.right` — mirroring the existing two-operand
`BinOp`/`Pipe` cases immediately above it in the same function.

## Explicitly out of scope

- LISS-0376 (the round's second candidate,
  `unitarity_check.py::_expr_is_quantum` missing a `SuperposeExpr`
  case) — tracked separately.
- Any further fifth-round candidates beyond the two confirmed real
  findings (both approved for this batch).

## Acceptance reference

```gherkin
Feature: the nested-mix coherence guard covers a mix reachable through a tensor product

  Scenario: a nested mix wrapped in a *|* tensor product is rejected the same way the direct form already is
    Given a nested `mix` inside another `mix`'s arm, reached only
      through `a *|* (...)`
    When compiled
    Then it raises NESTED_WHEN_ERROR (regression guard: the direct,
      unwrapped form already raises this)
```

## Verification plan for this design intake (not shipped as a test)

The gap confirmed live before drafting this Issue: the direct nested
`mix` raises `NESTED_WHEN_ERROR`; the tensor-wrapped identical
construct does not. Full `pytest tests/ -q` sweep after the fix, diffed
against the current baseline (0 failed, 1330 passed — `main` is fully
green), confirming no regression. `spec_verification` expected
unchanged (161/161).

## AI planning record (size S)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-08
- Size: `S` — one new case in one recursive walker function, mirroring
  an already-correct sibling case (`BinOp`/`Pipe`) three lines away.
- Route: direct implementation by this session.
- Confidence: high — the gap and its minimal fix pattern were directly
  confirmed by reading the surrounding code and live-reproducing before
  planning.

## Exit criteria

- [x] Phase 1 Red: `tests/test_liss_0375_nested_when_tensor_dispatch_red.py`
      added (2 cases). First repro attempt (nested `mix` bound to its
      own name, tensor-combined in a separate statement) incorrectly
      still passed pre-fix — corrected to embed the nested `mix`
      directly inside the tensor expression at the same statement,
      confirmed via `git stash` isolation: the direct form passes
      unchanged; the corrected tensor-wrapped form fails with
      `NESTED_WHEN_ERROR` absent from the diagnostics, matching the
      finding exactly.
- [x] Phase 2 Green: `_walk` gained a `TensorExpr` case recursing into
      `expr.left`/`expr.right`, mirroring the existing `BinOp`/`Pipe`
      two-operand cases immediately above it. Both tests pass.
- [x] Phase 3 Refactor: design decision section revised in place to
      record the corrected repro shape (the first attempt's false
      negative and why); reviewer empathy summary below.
- [x] Full regression: `pytest tests/ -q` → **1332 passed, 0 failed**
      (+2 this Issue's own new tests) — `main` stays fully green;
      `python3 tests/spec_verification/run_all.py` → **161/161** (100%,
      Gate: PASS, unchanged); `git diff --check` → clean.

### 変更の要約 (PR Summary)

**何を目的として何を変更したか**: 第5回アーキテクチャ監査の第1候補、
`NESTED_WHEN_ERROR`静的コヒーレンス・ガード(ADR 0045)が`*|*`
テンソル積内に埋め込まれた入れ子`mix`を検出できない問題を修正した。
`_walk`という再帰的な式ウォーカーが`TensorExpr`のケースを持たず、
テンソル演算子の被演算子を辿らなかったことが原因。直近の
`BinOp`/`Pipe`ケースと全く同じ2項再帰パターンを1件追加するだけの
最小修正。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- 最初のRedテスト再現コードが誤っていた: 入れ子`mix`を先に別の変数
  `b`にバインドしてから、別の文で`a *|* b`とテンソル結合する形では、
  `check_nested_when`が各文のトップレベル式を独立にチェックする
  仕組み上、`b`のバインド文自体が直接`WhenExpr`であるため、
  修正前でも正しく検出されてしまっていた(偽陰性)。`git stash`で
  Redを確認した際にこの誤りが判明し、入れ子`mix`をテンソル式の
  内部に直接埋め込む形(`a *|* (mix (c) { ... mix(d) ... })`)に
  再現コードを修正して初めて、修正前の実際のギャップを正しく
  再現できた。この訂正過程をDesign decisionセクションに明記した。

**人間がコードレビューで重点的に見るべきポイント**:
- 具体的な再現コードで`compiled.ok`ではなく診断コード集合
  (`NESTED_WHEN_ERROR`の有無)のみをアサートしている理由——このケースは
  他の無関係な診断(`SEMANTIC_CARRIER_MISMATCH_ERROR`等)により
  `compiled.ok`自体は元々`False`になるため、狙った診断コードの
  有無だけを見る必要があった。

## Non-goals

- LISS-0376 (separate finding, tracked independently).
