# LISS-0374: matrix-element middle type check silently skips a class-method callee

## Metadata

- Local issue ID: LISS-0374
- Status/phase: **complete** (2026-08-08) — PR
  [#467](https://github.com/nn0cl/staqex/pull/467) merged, commit
  `a7783c0`
- Type: Kernel bug fix (`compiler/staqex/typecheck.py`); no example
  content
- Priority: P3 (spurious silent acceptance of a type error — same
  narrow-AST-shape-dispatch category as LISS-0357/0358, this session's
  first round; distinct from the crash severity of LISS-0373)
- Initial planning size: `S`
- Owner / agent: Claude Code
- Program: standalone Kernel fix, second and final candidate from the
  fourth architectural audit round (LISS-0373 covered the first)
- Parent: none
- Depends on: none
- Blocks: none
- Branch: `feature/liss-0374-matrix-element-middle-attr-dispatch`
- GitHub Issue / PR: [#467](https://github.com/nn0cl/staqex/pull/467)
  (merged, `a7783c0`)

## Design decision

Live-verified: `⟨0|psi|1⟩` (desugared: `inner(|0>, psi(|1>))`) with
`psi` a plain `State`-kind local correctly raises
`OPERATOR_ALGEBRA_TYPE_ERROR` (`compiled.ok = False`). The
equivalent-shaped misuse through a class method returning `State`
(`⟨0|b.getPsi|1⟩`, `getPsi(x: State) -> State { return this.psi }`)
compiles clean (`compiled.ok = True`) — the same type error silently
escapes.

Root cause: `typecheck.py::_check_matrix_element_middle` bails
immediately for any non-`Var` callee shape:

```python
callee = applied.callee
if not isinstance(callee, Var):
    return
```

so a middle position reached through an `Attr` (a class-method or
field reference, e.g. `b.getPsi`) is never checked at all — the same
narrow-AST-shape-dispatch category as LISS-0357/0358 (nested-`Attr`
receiver dispatch), the first round's findings.

**Adopted fix**: widen the callee-shape recognition to a single-level
`Attr` whose object is a plain `Var` (`b.getPsi`), resolving the
method's declared return type through `self.fun_returns` — the same
table `check_unit` already builds for every class method with a return
type (`self.fun_returns[f"{d.name}.{method.name}"] = (method, ty)`,
already used elsewhere for method-call return-type inference) — instead
of inventing new lookup infrastructure. If the receiver's bound type is
`Object`/`Struct`-kind and `f"{receiver_class}.{method_name}"` resolves
in `fun_returns`, the resolved return type is checked exactly the same
way the existing bare-`Var` branch already checks an `env`-resolved
type: only flag `OPERATOR_ALGEBRA_TYPE_ERROR` when the type is known
and not `Operator`-kind; stay silent (fail-open, unchanged) when it
can't be resolved at all — matching the existing branch's own
fail-open stance for an unresolvable plain-`Var` type.

## Explicitly out of scope

- A class **field** of Operator kind used as the middle
  (`b.hamiltonian(|1>)` where `hamiltonian` is a plain field, not a
  method) — `fun_returns` only tracks methods, so this shape stays
  unchecked (fail-open), matching the existing behavior for any
  currently-unresolvable middle type. Not part of the confirmed
  finding, which used a method.
- Nested/multi-level `Attr` chains (`a.b.getPsi`) — the confirmed
  finding and its live repro used a single-level `b.getPsi`; the
  acceptance scenario doesn't require chained-attribute resolution.
- A middle reached through a nested `Call` (e.g. `o.z()(|1>)`, calling
  a zero-arg accessor and then applying its result) — a different AST
  shape (`callee` is itself a `Call`, not `Var`/`Attr`), not part of
  the confirmed finding; live-verified this shape already falls through
  the existing (and this fix's) final `else: return` unchanged, so no
  behavior change either way.
- LISS-0373 (the round's first, and this session's most severe,
  finding — a compiler crash) — fixed and merged separately.

## Acceptance reference

```gherkin
Feature: the matrix-element middle type check covers a class-method callee, not just a plain name

  Scenario: a class method returning State is rejected the same way a plain State-kind name already is
    Given `class Box { fn getPsi(x: State) -> State { return this.psi } }`
      and `⟨0|b.getPsi|1⟩` (b: Box)
    When compiled
    Then it raises OPERATOR_ALGEBRA_TYPE_ERROR (regression guard: the
      equivalent bare-name form `⟨0|psi|1⟩` already raises this)

  Scenario: an unresolvable Attr-shaped middle stays fail-open, unchanged
    Given a middle reached through an Attr whose method cannot be
      resolved in fun_returns
    When compiled
    Then this check does not raise OPERATOR_ALGEBRA_TYPE_ERROR
      (matches the existing fail-open stance for an unresolvable
      plain-Var type)
```

## Verification plan for this design intake (not shipped as a test)

The silent-acceptance finding confirmed live before drafting this
Issue by comparing `compiled.ok`/diagnostic codes between the baseline
bare-`Var` misuse (correctly rejected) and the equivalent class-method
misuse (silently accepted) with correct class syntax
(`fn getPsi(x: State) -> State { return this.psi }`, `Box b = Box(seed)`,
matching the repo's existing class-test idiom). Full `pytest tests/ -q`
sweep after the fix, diffed against the current baseline (0 failed,
1328 passed — `main` is fully green), confirming no regression.
`spec_verification` expected unchanged (161/161).

## AI planning record (size S)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-08
- Size: `S` — one function widened to recognize one additional AST
  shape, resolved through an already-existing lookup table
  (`fun_returns`); no new infrastructure.
- Route: direct implementation by this session.
- Confidence: high — the finding and the fix's target lookup mechanism
  (`fun_returns`, already populated for exactly this purpose) were both
  directly confirmed by reading the surrounding code and
  live-reproducing (with corrected class syntax matched against an
  existing passing test in this repo) before planning.

## Exit criteria

- [x] Phase 1 Red: `tests/test_liss_0374_matrix_element_middle_attr_dispatch_red.py`
      added (2 cases). Confirmed via `git stash` isolation: the
      baseline bare-`Var` case already passed (unchanged, correctly
      rejected before this fix); the class-method case failed with
      `compiled.ok == True` (silently accepted, matching the finding
      exactly).
- [x] Phase 2 Green: `_check_matrix_element_middle` widened to resolve
      a single-level `Attr(Var, name)` callee through `self.fun_returns`
      (the same table `check_unit` already populates for every class
      method with a return type), checked the same way the existing
      `Var` branch already checks an `env`-resolved type. Both tests
      pass.
- [x] Phase 3 Refactor: design decision section already recorded the
      full rationale at Plan time (no new findings surfaced during
      Green); reviewer empathy summary below.
- [x] Full regression: `pytest tests/ -q` → **1330 passed, 0 failed**
      (+2 this Issue's own new tests) — `main` stays fully green;
      `python3 tests/spec_verification/run_all.py` → **161/161** (100%,
      Gate: PASS, unchanged); `git diff --check` → clean.

### 変更の要約 (PR Summary)

**何を目的として何を変更したか**: 第4回アーキテクチャ監査の第2候補、
`_check_matrix_element_middle`(`<0|A|1>`の中央位置がOperator型で
あることを検証するチェック)が`Attr`形状のcallee(クラスメソッド
`b.getPsi`)を一切検証せずスキップしていた問題を修正した。同等の
裸の変数名形式(`<0|psi|1>`、`psi`がState型)は既に正しく
`OPERATOR_ALGEBRA_TYPE_ERROR`を送出するが、クラスメソッド経由の
同じ誤用(`getPsi`がStateを返す)はコンパイルが通ってしまっていた。
修正は、既に`check_unit`が全クラスメソッドの戻り値型のために
構築済みの`self.fun_returns`テーブル(メソッド呼び出しの戻り値型
推論に既に使われている)経由で単一階層の`Attr(Var, name)`形状の
callee を解決するよう認識範囲を拡張しただけで、新しいインフラは
追加していない。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- `fun_returns`はメソッド呼び出し時の引数の個数と無関係に、
  メソッド名から戻り値型への単純なマッピングである。そのため
  理論上、0引数メソッドが誤って1引数で呼ばれるbra-ket糖衣構文
  (`<0|b.hamiltonian|1>`、`hamiltonian()`が0引数でOperatorを
  返す場合)でも本チェックは(引数数の不一致を検証せず)型だけを
  見て通してしまう可能性があるが、これは元々のconfirmed findingの
  範囲外であり、別の場所で引数数の妥当性が検証されるべき問題として
  Non-goalsに明記した。
- クラスの「フィールド」(メソッドではない)がOperator型を持つ
  ケース(`b.hamiltonian`が`val`フィールド)は`fun_returns`に
  現れないため、修正後も未検証のまま(fail-open)——これは元の
  裸の変数名チェックが解決不能な型に対して同様にfail-openである
  ことと一貫しており、意図的なスコープ外とした。

**人間がコードレビューで重点的に見るべきポイント**:
- `fun_returns`のキー形式(`f"{receiver_ty.payload}.{callee.name}"`)
  が、`receiver_ty.payload`(バインド時の型注釈名)と
  `check_unit`が`fun_returns`に登録するキー(`d.name`/
  `d.qualified_name`)の間で一致することを、既存の他の呼び出し箇所
  (例:通常のメソッド呼び出し型推論)と同じ規約に依拠している点。

## Non-goals

- Class-field (non-method) Operator middles.
- Nested/multi-level `Attr` chains.
- A middle reached through a nested `Call`.
