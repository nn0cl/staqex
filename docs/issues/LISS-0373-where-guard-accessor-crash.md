# LISS-0373: `where` binder guard crashes on `next(...)`/`wrap(...)` index accessors

## Metadata

- Local issue ID: LISS-0373
- Status/phase: **complete** (2026-08-08) — PR
  [#465](https://github.com/nn0cl/staqex/pull/465) merged, commit
  `2951c4e`
- Type: Kernel bug fix (`compiler/staqex/finite_binder.py`); no example
  content
- Priority: P1 (uncaught Python exception propagating out of the public
  `compile_source()` API for a physically plausible program — more
  severe than any narrow-AST-shape-dispatch finding earlier this
  session, which at worst produced a diagnostic or a silently wrong
  result, never a raw crash)
- Initial planning size: `S`
- Owner / agent: Claude Code
- Program: standalone Kernel fix, first candidate from a fourth
  architectural audit round (same recurring narrow-AST-shape-dispatch
  category; LISS-0374 tracks the round's second candidate)
- Parent: none
- Depends on: none
- Blocks: none
- Branch: `feature/liss-0373-where-guard-accessor-crash`
- GitHub Issue / PR: [#465](https://github.com/nn0cl/staqex/pull/465)
  (merged, `2951c4e`)

## Design decision

Live-verified: `sum (i in Index<0..2>, j in Index<0..2>) where i == j
{ Z[i] * Z[j] }` compiles cleanly. The equivalent-shaped guard using
the `next(...)` index accessor — the same accessor that already works
correctly in an indexed operator body (`Z[next(i)]`) — crashes
`compile_source()` itself with an **uncaught `ValueError`**:

```
ValueError: where guard must use static binder indices
  finite_binder.py:426 _static_value → :444 _guard_matches → :559 _binder_values
  → :618/616 _retained_leaf_count → :746 _operator_metadata → :768 lower_finite_binders
  → qpu_ir.py:576 qpu_ir_diagnostics → pipeline.py:555 _analyze_unit → pipeline.py:633 compile_source
```

Root cause: the same narrow-AST-shape-dispatch category as every
finding this session, but here the fail-closed narrow check's failure
mode is a raw exception, not a diagnostic — `_resolve_bound_index`
(used only for `where`-guard evaluation, via `_static_value` →
`_guard_matches` → `_binder_values`) recognizes only `OpVar`/`OpLit`:

```python
def _resolve_bound_index(expr: OpExpr, bindings: Mapping[str, int]) -> int | None:
    if isinstance(expr, OpVar) and expr.name in bindings:
        return bindings[expr.name]
    if isinstance(expr, OpLit):
        return int(expr.value)
    return None
```

Its sibling `_resolve_index` (used for indexed-term expansion, e.g.
`Z[next(i)]`) already has the general case, including an `OpCall`
branch for the `next`/`wrap` accessors via `_resolve_accessor`.
`_static_value` calling the narrower function and then raising
unconditionally when it returns `None` is what turns "index accessor
not recognized" into "crash the compiler."

**Adopted fix**: eliminate the narrow duplicate — `_static_value`/
`_guard_matches`/`_binder_values` (the only caller chain that reaches
`_resolve_bound_index` for guard evaluation) now thread a `_Context`
through instead of a bare `bindings` dict, and `_static_value` calls
the already-general `_resolve_index` directly. `_binder_values`
(finite_binder.py, inside the `for value in values:` loop) already
computes everything a `_Context` needs (`bindings`, `register_size`,
this binder's own `start`/`end` as `domain_start`/`domain_end`,
`context.arrays`, `context.register_sizes`) to build the `_Context` it
yields on a guard match — that same `_Context` construction is now
built once per iteration and reused for both the guard check and the
yield, instead of being built only after the (previously bare-dict)
guard check passed. `_resolve_bound_index` itself is left unchanged
and still used by its other, unrelated caller (`_substitute_indices`,
line 397) — that usage was not part of this finding and is out of
scope.

## Explicitly out of scope

- `_resolve_bound_index`'s use in `_substitute_indices` (binder-index
  substitution before Jordan-Wigner mapping) — a different call chain,
  not part of this finding, not live-verified as buggy.
- LISS-0374 (the fourth audit round's second candidate,
  `typecheck.py::_check_matrix_element_middle` silently accepting a
  `<0|obj.method|1>`-shaped type error) — tracked separately.
- Any further fourth-round candidates beyond the two confirmed real
  findings (two false positives were ruled out during the audit and
  are not pursued).

## Acceptance reference

```gherkin
Feature: a `where` binder guard accepts the same index-accessor shapes an indexed operator body already does

  Scenario: next(...) in a where guard no longer crashes the compiler
    Given `sum (i in Index<0..2>, j in Index<0..2>) where i == next(j) { Z[i] * Z[j] }`
    When compiled
    Then compile_source() returns normally (no uncaught exception)
    And `compiled.ok` is `True`

  Scenario: the guard's semantics match the equivalent explicit-arithmetic form
    Given the next(j) guard above and an equivalent guard using only
      accepted-today shapes (e.g. explicit adjacent-index pairing)
    When both are compiled and evolved
    Then they produce the same accepted Hamiltonian structure (same
      number of retained terms)
```

## Verification plan for this design intake (not shipped as a test)

The crash confirmed live before drafting this Issue: `compile_source()`
raised an uncaught `ValueError` for the `next(...)`-guard source, with
the exact traceback recorded above. Full `pytest tests/ -q` sweep after
the fix, diffed against the current baseline (0 failed, 1326 passed —
`main` is fully green), confirming no regression. `spec_verification`
expected unchanged (161/161).

## AI planning record (size S)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-08
- Size: `S` — thread an already-available `_Context` through three
  functions in the same call chain and switch one function call to an
  already-general sibling; no new logic.
- Route: direct implementation by this session.
- Confidence: high — the crash, its root cause, and the fix's target
  pattern (`_resolve_index`, already correct and already used for the
  identical accessor shapes elsewhere) were all directly confirmed by
  reading the surrounding code and live-reproducing before planning.

## Exit criteria

- [x] Phase 1 Red: `tests/test_liss_0373_where_guard_accessor_crash_red.py`
      added (2 cases). Confirmed via `git stash` isolation of the fix:
      both fail with the exact documented uncaught `ValueError: where
      guard must use static binder indices`, traced through
      `_static_value` → `_guard_matches` → `_binder_values` →
      `_retained_leaf_count` → `_operator_metadata` →
      `lower_finite_binders` → `qpu_ir_diagnostics` → `_analyze_unit` →
      `compile_source`, matching the finding exactly.
- [x] Phase 2 Green: `_static_value`/`_guard_matches`/`_binder_values`
      now thread a `_Context` (built once per binder-value iteration,
      reused for both the guard check and the yielded context) instead
      of a bare `bindings` dict; `_static_value` calls the already-
      general `_resolve_index` instead of the narrower
      `_resolve_bound_index`. Both tests pass; live-verified the
      `next(j)`-guard source now produces the same 3-`rz`-gate QASM
      output as the hand-written equivalent Hamiltonian
      (`Z[1]*Z[0] + Z[2]*Z[1]`), confirming correct semantics, not just
      absence-of-crash.
- [x] Phase 3 Refactor: design decision section already recorded the
      full rationale at Plan time (no new findings surfaced during
      Green); reviewer empathy summary below.
- [x] Full regression: `pytest tests/ -q` → **1328 passed, 0 failed**
      (+2 this Issue's own new tests) — `main` stays fully green;
      `python3 tests/spec_verification/run_all.py` → **161/161** (100%,
      Gate: PASS, unchanged); `git diff --check` → clean.

### 変更の要約 (PR Summary)

**何を目的として何を変更したか**: 第4回アーキテクチャ監査の第1候補、
`where`バインダーガード内で`next(...)`/`wrap(...)`インデックス
アクセサを使うとコンパイラ本体が未処理例外(`ValueError`)を送出する
問題を修正した。これはこのセッションで発見された中で最も重大な
不具合(診断メッセージすら出さずコンパイラAPI自体がクラッシュする)
だった。原因は`_static_value`(`where`ガード評価専用)が
`_resolve_bound_index`という狭い認識(`OpVar`/`OpLit`のみ)の関数を
呼んでおり、`None`が返ると無条件に例外を送出していたこと。
インデックス付きオペレータ本体(`Z[next(i)]`)は既に正しく
`_resolve_index`(`next`/`wrap`アクセサ対応)を使っていたため、
この既存の正しい兄弟関数に処理を委譲するよう変更した。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- `_resolve_index`は`_Context`オブジェクトを引数に取るが、
  `_static_value`/`_guard_matches`は従来`bindings`という素の辞書
  しか受け取っていなかった。`_binder_values`のループ内で既に
  この`binder`自身の`start`/`end`(domain境界、`wrap()`アクセサに
  必要)を含む`_Context`を構築していた(ガード判定通過後に
  yield用として)ことを確認し、その構築をガード判定より前に
  移動して再利用する形にした——新しい情報を作り出したのではなく、
  既に計算済みだが後で使われていた値を早めに使っただけである。
- 修正が「クラッシュしない」だけでなく「正しい物理的意味を持つ」
  ことを検証するため、`next(j)`ガードの結果を手書きの等価な
  ハミルトニアン(`Z[1]*Z[0] + Z[2]*Z[1]`)とQASMゲート数レベルで
  比較し、両方とも3個の`rz`ゲートで一致することを確認した。

**人間がコードレビューで重点的に見るべきポイント**:
- `_resolve_bound_index`自体は変更せず、`_substitute_indices`
  (別の呼び出し元、binder index substitution用)でそのまま
  使い続けている——このスコープ限定判断が妥当か。
- `_Context`を早期構築する変更が、ガード非適用(`apply_guard=False`)
  の経路や`descending`フラグの扱いに影響しないか。

## Non-goals

- `_substitute_indices`'s own use of `_resolve_bound_index`.
- LISS-0374 (separate finding, tracked independently).
