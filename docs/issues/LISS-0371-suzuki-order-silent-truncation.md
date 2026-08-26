# LISS-0371: `using Suzuki(order = ...)` spuriously rejects a named-constant order equal to a literal

## Metadata

- Local issue ID: LISS-0371
- Status/phase: **complete** (2026-08-08) — PR
  [#461](https://github.com/nn0cl/staqex/pull/461) merged, commit
  `24a63ad`
- Type: Kernel bug fix (`compiler/staqex/typecheck.py`,
  `compiler/staqex/backend/qasm/trotter.py`,
  `compiler/staqex/backend/qasm/lower.py`, `compiler/staqex/qpu_ir.py`);
  no example content
- Priority: P3 (spurious hard rejection for an equivalent expression —
  same category as LISS-0357/0358/0367/0368/0369, not a new
  silent-wrong-output category)
- Initial planning size: `M` (revised from `S` — the correct fix needs
  new typecheck.py infrastructure, not just a runtime-layer dedup)
- Owner / agent: Claude Code
- Program: standalone Kernel fix, found via a third architectural audit
  round (same recurring narrow-AST-shape-dispatch category)
- Parent: none
- Depends on: none
- Blocks: none
- Branch: `feature/liss-0371-suzuki-order-silent-truncation`
- GitHub Issue / PR: [#461](https://github.com/nn0cl/staqex/pull/461)
  (merged, `24a63ad`)

## Design decision

**Correction to the original finding**: the first draft of this Issue
described `using Suzuki(order = ord, steps = M)` (a named `Int`
constant carrying the same value as a literal `order = 4`) as a
*silent* wrong-output bug — `ok=True` with the wrong Suzuki product
formula silently substituted. That was verified incorrectly: the first
repro called `QASM3Emitter.emit_unit()` directly on `compiled.unit`
without first checking `compiled.ok`, which every other test and call
site in this codebase always checks first. Re-verifying by checking
`compile_source(...).ok` before emitting (the actual, only way this
path is reachable in practice) shows `compiled.ok == False`, with
`typecheck.py::_check_suzuki_policy` already emitting
`SUZUKI_ORDER_ERROR` for the named-variable case. **The bug is a
spurious hard rejection of a resolvable, equivalent expression — the
same familiar category as every other finding this session — not a
new, more severe silent-substitution category.**

`_check_suzuki_policy`'s `order_ok` check
(`isinstance(policy.order, LitInt) and policy.order.value in {2, 4}`)
only recognizes a bare literal. `typecheck.py` has **no existing
constant-folding/static-value-tracking infrastructure at all** (`grep`
for `_fold`/`_const_fold`/`_static_scalar`/`self.scalars` returns
nothing) — unlike every prior fix this session, which mirrored an
already-correct sibling pattern in the *same* file, this fix requires
building that infrastructure for the first time.

Once typecheck.py stops spuriously rejecting the program, three
runtime-layer call sites still independently duplicate the same
literal-only `order` recognition, each falling back to `order = 2` for
anything else:

1. `trotter.py::resolve_suzuki_steps` (internal step-count derivation
   for the tolerance-based auto-stepping path).
2. `backend/qasm/lower.py::_lower_evolve` — an inline duplicate right
   after calling `resolve_suzuki_steps` (which itself computed `order`
   internally but never returned it); this is the value actually
   passed to `suzuki_gates(...)`.
3. `qpu_ir.py::_lowering_policy_projection` — the exported
   `QpuProgram["lowering_policy"]["order"]` metadata field.

This mirrors LISS-0360's dedup principle (eliminate independent copies,
defer to one shared, already-general helper) — here the duplication is
within the same bug, not across an ADR update.

**Adopted fix (two layers, both required — typecheck.py alone would
still leave the runtime layer's own duplicated narrow checks producing
`order = 2` if ever reached by another path; the runtime layer alone
would leave the compiler spuriously rejecting the program before the
better runtime logic ever runs)**:

1. **typecheck.py** (`compiler/staqex/typecheck.py`): new
   `self.static_scalars: dict[str, float]` — a name→value table for
   classical scalar binds resolvable at typecheck time, seeded from
   `PRELUDE_CONSTANTS` (mirroring the runtime `scalars` dict
   `trotter.py`/`qpu_ir.py` already build the same way). Populated at
   the **two** places a plain classical `Float`/`Int` bind's value
   becomes known:
   - `check_unit`'s main-loop generic bind path (after
     `self.env[n] = ty`, the single shared hook for both
     explicitly-typed `Int ord = 4` and Type-First-inferred binds).
   - `_check_function_body` (after `self.env[name] = ty`), with its own
     save/restore swap around the existing `self.env`
     save/restore, so a function's local scalars never leak into the
     caller's or another function's scope (mirrors the existing
     `dict(base_env)` isolation for types).

   New helper `_static_scalar_value(expr) -> float | None`: resolves a
   `LitInt`/`LitFloat` directly, or a `Var` via `self.static_scalars`;
   any other shape returns `None` (not a closed value yet — fail-closed,
   matching the runtime resolver's stance). `_check_suzuki_policy`
   widened to accept `order` when `_static_scalar_value(policy.order)`
   resolves to `2` or `4`, in addition to the existing bare-literal
   check — the fail-closed `SUZUKI_ORDER_ERROR` fallback is otherwise
   unchanged.

2. **Runtime layer** (`trotter.py`/`lower.py`/`qpu_ir.py`): new
   `trotter.py::resolve_suzuki_order(order_expr, scalars) -> int`,
   built on the already-general `_eval_float` (the same helper
   `eval_time_expr` already uses, and that LISS-0360 already made fully
   general over `Var`/scalars/prelude constants/`Attr` unit
   suffixes/`BinOp` arithmetic) — falls back to `2` only when
   `_eval_float` returns `None`, which is unreachable for a program
   that passed the widened typecheck (typecheck already rejects any
   order that doesn't resolve to 2 or 4). `resolve_suzuki_steps` gains a
   `scalars` parameter (both callers already have a `scalars` dict in
   scope) and uses the new helper internally. `lower.py`'s inline
   duplicate is deleted, replaced by a direct call to
   `resolve_suzuki_order`. `qpu_ir.py`'s inline duplicate is replaced
   the same way.

## Explicitly out of scope

- The QASM-backend `apply(rx(...), ...)` angle silent-gate-drop bug —
  a related but separate finding from the same audit round, tracked
  separately as LISS-0372 (severity not yet re-verified against the
  `compiled.ok`-first lesson learned here).
- `qpu_ir.py::_lowering_policy_projection`'s own separate, narrower
  `scalars`-population gap (only literal `Float`/`Int` top-level binds
  populate its local `scalars` dict) — unaffected by this fix (a
  non-literal-sourced named scalar used as `order` still correctly
  falls back to `2` there, unchanged).
- `steps`/`tolerance`'s own literal-only recognition in the same three
  runtime functions — `None` is a legitimate "not specified,
  auto-compute" sentinel already handled correctly by the callee,
  unlike `order`'s previously-spurious rejection.
- General expression arithmetic (`order = a + b`) in
  `_static_scalar_value` — the approved acceptance scenario only
  requires a named-constant lookup; literal and named-scalar resolution
  is the minimal fix for the confirmed finding.

## Acceptance reference

```gherkin
Feature: Suzuki order resolves a named classical constant, not just a literal

  Scenario: a named integer constant order is honored, not spuriously rejected
    Given `Int ord = 4; ... using Suzuki(order = ord, steps = 3)`
    When compiled and QASM-emitted
    Then compilation succeeds (no SUZUKI_ORDER_ERROR)
    And it produces the identical gate sequence as the literal
      `using Suzuki(order = 4, steps = 3)` form

  Scenario: the QPU IR lowering-policy projection reports the correct order
    Given the same named-constant-order source
    When `build_qpu_ir` runs
    Then `lowering_policy["order"]` equals 4, not the previous fallback of 2

  Scenario: a genuinely unresolvable order is still rejected unchanged
    Given an `order` expression referencing an unbound name
    When compiled
    Then it is still rejected (SUZUKI_ORDER_ERROR), or falls back to
      order 2 if some other path makes it ok=True (regression guard —
      fallback *behavior* is unchanged, only recognition is widened)
```

## Verification plan for this design intake (not shipped as a test)

Both the original (incorrect) "silent" framing and the corrected
"spurious rejection" framing verified live before/after the correction
via direct `compile_source(...).ok` inspection. Full `pytest tests/ -q`
sweep after the fix, diffed against the current baseline (0 failed,
1321 passed — `main` is fully green), confirming no regression.
`spec_verification` expected unchanged (161/161).

## AI planning record (size M)

- Status: Green, pre-Refactor
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-08
- Size: `M` — one new typecheck.py tracking mechanism (dict +
  helper + two population hook points + one save/restore pair) plus
  one new runtime helper and three call-site updates.
- Route: direct implementation by this session.
- Confidence: high; the severity framing was corrected via re-verification
  before implementation began, and both the spurious-rejection Red state
  and the resolved Green state were directly confirmed via `git stash`
  isolation.

## Exit criteria

- [x] Phase 1 Red: confirmed via `git stash` isolation of the four
      modified source files — `test_named_variable_order_emits_the_same_gate_count_as_the_literal`
      and `test_qpu_ir_lowering_policy_reports_the_correct_order` fail
      with `compiled.ok == False` / `SUZUKI_ORDER_ERROR` (the corrected,
      documented reason — a spurious rejection, not a silent
      wrong-gate-count); `test_unresolvable_order_still_falls_back_to_2`
      already passed (its `if compiled.ok: ... else: ...` shape covers
      the pre-fix rejection path).
- [x] Phase 2 Green: typecheck.py + trotter.py + lower.py + qpu_ir.py
      changes restored; all 3 tests pass.
- [x] Phase 3 Refactor: this design decision section revised in place to
      record the severity correction (silent → spurious rejection) and
      the expanded main+function scope; `docs/architecture/open-work-register.md`
      updated; reviewer empathy summary below.
- [x] Full regression: `pytest tests/ -q` → 1324 passed, 0 failed
      (+3 this Issue's own new tests); `python3 tests/spec_verification/run_all.py`
      → 161/161 (100%, Gate: PASS, unchanged); `git diff --check` → clean.

### 変更の要約 (PR Summary)

**何を目的として何を変更したか**: 第3回アーキテクチャ監査で発見した
`using Suzuki(order = ord, ...)`(リテラルと同じ値を持つ名前付き
`Int`定数)が`SUZUKI_ORDER_ERROR`で拒否される問題を修正した。当初
「サイレントに間違った出力を出す」バグとして報告したが、
`compiled.ok`を先にチェックしない誤った検証方法によるものだった。
このコードベースの他の全ての呼び出し箇所と同じ方法(`compiled.ok`
を先にチェック)で再検証した結果、実際には型検査時点で正しく
拒否されている(ただし本来は等価な式として受理されるべき)ことが
判明し、セッション内の他の発見と同じ「不要な拒否」カテゴリだと
訂正した。修正には`typecheck.py`に定数解決の仕組みを新規実装する
必要があった(既存の兄弟パターンを模倣するだけで済んだ
LISS-0368/0369とは異なる)。`self.static_scalars`という新しい
name→value追跡辞書を`check_unit`のmainループと
`_check_function_body`の両方に追加し、`_check_suzuki_policy`が
名前付き定数を解決できるようにした。ランタイム層の3箇所の重複した
狭いチェックも、新しい共有ヘルパー`resolve_suzuki_order`に統合した。

### 残存リスク・検証の溝 (Verification Gap)

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- 当初の「サイレントに間違った出力」という重大度判定が誤りだった
  ことを`git stash`によるRed状態の直接確認で訂正した。この自己訂正
  自体が本Issueの設計判断セクションと`open-work-register.md`の両方
  に記録されている。
- `_static_scalar_value`はリテラルと名前付き定数の解決のみをサポート
  し、算術式(`order = a + b`)は意図的にサポート外とした——承認された
  受け入れシナリオが名前付き定数のみを要求しているため、スコープを
  最小限に保った。
- `_check_function_body`用に`self.static_scalars`のsave/restoreを
  `self.env`と同じパターンで実装したが、関数のローカルスカラーが
  呼び出し元や他の関数に漏れないことは、`_check_function_body`が
  main()の文処理ループより前に呼ばれる(その時点でmain()のローカル
  スカラーはまだ何も登録されていない)という実行順序に依存した設計
  である。

**人間がコードレビューで重点的に見るべきポイント**:
- `self.static_scalars`の2箇所のポピュレーション地点
  (`check_unit`メインループの`self.env[n] = ty`直後、
  `_check_function_body`の`self.env[name] = ty`直後)が、分類上
  「単純な古典スカラーバインド」以外のケース(State/Operator/
  Object/Enum等)を誤って追跡していないか。

## Non-goals

- LISS-0372 (separate `rx` angle finding).
- `qpu_ir.py`'s own narrower `scalars`-population gap.
- `steps`/`tolerance`'s literal-only recognition (fallback is a
  legitimate sentinel, not a silent-wrong-default).
- General arithmetic in `_static_scalar_value` (literal + named-scalar
  lookup is the minimal fix for the confirmed finding).
