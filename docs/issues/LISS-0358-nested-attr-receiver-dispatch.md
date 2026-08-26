# LISS-0358: method calls on a nested struct/class-field receiver (`outer.inner.method()`)

## Metadata

- Local issue ID: LISS-0358
- Status/phase: **complete** (2026-08-08) — PR
  [#434](https://github.com/nn0cl/staqex/pull/434) merged, commit
  `693d395`
- Type: Kernel bug fix (`compiler/staqex/runtime/evaluator.py`,
  `compiler/staqex/parser.py`); no example content
- Priority: P2
- Initial planning size: `S`
- Owner / agent: Claude Code
- Program: standalone Kernel fix, found via a general-purpose
  architectural audit of narrow AST-shape dispatch patterns (same bug
  category as LISS-0357), requested directly by the Adjudicator after
  LISS-0357 in response to the standing concern that a physicist
  rearranging/composing expressions must not hit spurious Kernel
  failures
- Parent: none
- Depends on: none
- Blocks: none
- Branch: `feature/liss-0358-nested-attr-receiver-dispatch`
- GitHub Issue / PR: [#434](https://github.com/nn0cl/staqex/pull/434)
  (merged, `693d395`)

## Design decision

A general-purpose audit (requested after LISS-0357) searched
`typecheck.py` and `evaluator.py` for other instances of the same bug
shape LISS-0357 fixed: a function dispatching on the exact AST *shape*
of an expression rather than its general evaluated *value*, with a
worse/erroring fallback for any other shape. It found three call sites
sharing byte-for-byte the same narrow gate:

```python
if isinstance(recv_expr, Var) and recv_expr.name in self.objects:
    inst = self.objects[recv_expr.name]
    ...
```

(or the equivalent `if not isinstance(recv_expr, Var) or recv_expr.name
not in self.objects: raise KernelError(...)` phrasing) in:

1. `evaluator.py::_bind_call` (ADR 0056 `instance.method(args)` as a
   StateBind RHS).
2. `evaluator.py::_eval_classical_method_call` (ADR 0179 `recv.method(…)`
   as a classical-value operand).
3. `evaluator.py::_resolve_operator_method_call` (LISS-0139
   `Operator H = recv.method(…)`).

All three reject a receiver that is a nested field access
(`outer.inner.method()`, where `inner` is itself a class/struct field
of `outer`), even though `typecheck.py` already type-checks this
expression correctly via its own general `self._infer(expr.callee.obj)`
— the type checker has no problem with a nested-`Attr` receiver; only
the evaluator's dispatch is narrow.

**Live-verified** (both fail with the fix reverted):

- `Float nested = o.inner.get()` (StateBind path, site 1) →
  `RUNTIME_ERROR: unsupported method get`.
- `Float nested = o.inner.get() + 0.0` (embedded classical-value path,
  site 2) → `RUNTIME_ERROR: classical method call requires a bound
  receiver (got \`Attr\`)`.

**A second, separate bug in a different layer was found investigating
site 3** (`Operator`-returning nested-receiver methods):
`Operator H = o.inner.h()` fails to even *parse*
(`PARSE_ERROR: expected identifier, got ')'`), before reaching the
evaluator at all. Root-caused to `parser.py::_type_first_bind`'s
LISS-0139 heuristic for `Operator H = recv.method(…)`, which used a
fixed 4-token lookahead (`IDENT DOT IDENT LPAREN`) that only recognizes
*exactly one* dotted hop before the call; anything else (including two
hops, `o.inner.h(`) falls through to the Operator-DSL mini-language
parser (`_op_expression`), which does not understand a general nested
method call and fails with the observed `PARSE_ERROR`. Confirmed by
direct code reading of the failing token sequence
(`IDENT DOT IDENT DOT IDENT LPAREN` does not match the 4-token check).

**Adopted fix** (both layers, since the Operator-return path needs both
to be end-to-end usable):

1. `evaluator.py`: introduce one shared helper `_resolve_receiver_instance
   (recv_expr, assign=None)` — the existing bare-`Var`-in-`self.objects`
   fast path is preserved exactly; any other expression shape resolves
   through the already-general `self._eval_value(recv_expr, assign or {})`,
   returning the result only if it is a `ClassInstance`/`StructValue`
   (wrapped so a non-instance receiver, e.g. `Math`/`Complex`, still
   raises internally and falls through to the existing Math.*/map/project
   dispatch unchanged — no observable behavior change for those paths).
   Apply this helper identically at all three call sites (mirrors this
   session's established "one root cause, one shared fix" pattern).
2. `parser.py::_type_first_bind`: replace the fixed 4-token
   `IDENT DOT IDENT LPAREN` lookahead with a new `_dotted_call_lookahead`
   helper that accepts *any* depth of `.<ident>` hops before the `(`,
   not just exactly one.

## Explicitly out of scope

- Any change to `typecheck.py` (already general, confirmed by direct
  reading — no fix needed there).
- Any change to the Operator-DSL mini-language parser itself
  (`_op_expression`/`_op_primary`) — unaffected, still reached exactly
  when the new lookahead does not match.
- Any other narrow-AST-shape-dispatch pattern investigated and ruled
  out as a false positive during the same audit (tensor `*|*` bind,
  `converged(state)` predicate argument, Operator-DSL `OpExpr`
  index/register grammar, `WhenExpr`/`SuperposeExpr` inference and
  binding, `_eval_value_with_unit`/`_infer_attr`/`_infer_unit_convert`,
  and the `Var`-arg fast paths in the classical/Operator method-call
  argument-binding loops) — each already has a fully general fallback
  or is a genuine grammar/structural requirement, not a shortcut.
- Any example content changes.

## Acceptance reference

```gherkin
Feature: method calls resolve a nested struct/class-field receiver

  Scenario: StateBind RHS with a nested receiver
    Given `outer.inner` is itself a class instance with method `get()`
    And `Float nested = outer.inner.get()`
    When compiled and run
    Then it does not raise RUNTIME_ERROR

  Scenario: nested receiver embedded in a larger classical expression
    Given the same class hierarchy
    And `Float nested = outer.inner.get() + 0.0`
    When compiled and run
    Then it does not raise RUNTIME_ERROR

  Scenario: Operator-returning nested receiver parses and runs
    Given `outer.inner` has an Operator-returning method `h()`
    And `Operator H = outer.inner.h()`
    When compiled and run
    Then it does not raise PARSE_ERROR or RUNTIME_ERROR

  Scenario: single-level receiver (already-supported case) is unaffected
    Given `Float nested = inner.get()` (bare Var receiver)
    And `Operator H = inner.h()` (bare Var receiver)
    When compiled and run
    Then both behave exactly as before (regression guard)
```

## Verification plan for this design intake (not shipped as a test)

All four scenarios confirmed live before drafting this Issue (the first
three fail pre-fix for the documented reasons; the fourth already
passes, confirmed as a regression guard). Full `pytest tests/ -q`
regression, diffed against the current baseline, to confirm no new
failures and no incidental behavior change to the existing single-level
receiver paths (Math.*/map/project dispatch, existing class-method
tests). `spec_verification` expected unchanged (161/161).

## AI planning record (size S)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-08
- Size: `S` — one shared evaluator helper applied at three call sites,
  plus one parser lookahead generalization; each individually small and
  mirroring an already-correct sibling pattern.
- Route: direct implementation by this session.
- Confidence: high (both gaps live-verified with minimal repros before
  drafting).

## Exit criteria

- [x] Phase 1 Red:
      `tests/test_liss_0358_nested_attr_receiver_dispatch_red.py` added
      (4 cases). Confirmed 3 of 4 failing with both fixes reverted
      (`RUNTIME_ERROR: unsupported method get`,
      `RUNTIME_ERROR: classical method call requires a bound receiver`,
      `PARSE_ERROR: expected identifier, got ')'` — each matching the
      documented finding exactly); the 4th
      (`test_single_level_receiver_still_works`, the already-supported
      bare-Var-receiver path) correctly already passed, confirming it
      is a regression guard, not a Red-confirming case. (Also caught
      and corrected a process deviation: the parser fix was
      accidentally first made directly on `main` before Red was
      written; corrected via `git stash` → branch → `git stash pop`
      before Red confirmation, per this session's established
      discipline.)
- [x] Phase 2 Green: `evaluator.py` gained a shared
      `_resolve_receiver_instance` helper (next to the analogous
      `_attr_host`), applied identically at all three call sites
      (`_bind_call`, `_eval_classical_method_call`,
      `_resolve_operator_method_call`); `parser.py::_type_first_bind`'s
      fixed 4-token LISS-0139 lookahead replaced with a new
      `_dotted_call_lookahead` helper accepting any depth of `.<ident>`
      hops before the call. All 4 tests pass.
- [x] Phase 3 Refactor: no further code change needed; reviewer
      empathy summary below.
- [x] Full regression: `pytest tests/ -q` → 1256 passed, 52 failed
      (identical failure list to the established baseline — confirmed
      by direct comparison, no new failures, no incidental fixes; +4
      this Issue's own new tests); `python3
      tests/spec_verification/run_all.py` → 161/161 (100%, Gate: PASS,
      unchanged); `git diff --check` → clean.

## Reviewer empathy summary

**何を目的として何を変更したか**: LISS-0357に続き、Adjudicatorの依頼で
実施した広範な監査（`typecheck.py`/`evaluator.py`の「AST形状に依存した
狭い分岐」パターンの体系的調査）で見つかった、`recv.method(...)`の
レシーバ解決が3箇所で同一の狭いチェック（裸のVarかつself.objectsに
束縛済みの場合のみ）を持ち、`outer.inner.method()`のようなネストした
フィールドアクセスを拒否していた問題を修正した。加えて、Operator返す
メソッドの経路を検証中に、パーサー側にも同一カテゴリの別バグ
（`Operator H = recv.method(…)`の受理チェックが固定4トークン先読みで
「ドット1段のみ」しか認識しない）を発見し、同じIssueで併せて修正した
（Adjudicator確認済み、当初のスコープ外調査として提示した上で承認を
得た）。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- `evaluator.py`側の3箇所は、`typecheck.py`が既にこの形の式を一般的に
  型付けできていることを確認した上で、評価器側だけが狭いという判断を
  下した。共有ヘルパー`_resolve_receiver_instance`は、既存の
  `_attr_host`と同じ「まずVar+self.objects高速パス、それ以外は一般
  評価器にフォールバック」という設計を踏襲し、非インスタンスの
  レシーバ（`Math`/`Complex`等）で例外を握りつぶして`None`を返す
  ことで、既存のMath.*/map/project経路への副作用がないことを
  ライブテストで確認した。
- パーサー側の`_dotted_call_lookahead`は、既存の4トークン固定チェック
  が果たしていた「レシーバに最低1つの`.`が必要」という前提を保った
  まま、任意の深さのドット連鎖を受理するよう一般化した。
- Green後の回帰テストで、失敗件数だけでなく失敗リスト全体を既存
  ベースラインと1行ずつ比較し、完全一致（新規失敗0件、偶発的な修正
  0件）を確認した。

**人間がコードレビューで重点的に見るべきポイント**:
- `_resolve_receiver_instance`が`self._eval_value`を`try/except
  KernelError`で包んでいる設計が、将来的に本当のエラーを握りつぶして
  しまうリスクがないか（現状は「候補がClassInstance/StructValueで
  なければNone」という厳格なチェックで抑えている）。
- パーサーの`_dotted_call_lookahead`が、Operator-DSL側の予約アトム名
  と衝突するケース（例: `X.method()`のような紛らわしい記法）を
  誤って一般式側に倒していないか。

## Non-goals

- `typecheck.py` changes.
- Operator-DSL mini-language grammar changes.
- Example content changes.
