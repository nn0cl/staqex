# LISS-0355: fix Classical-operand-vs-bare-literal mixing discarding payload and dimension in `typecheck.py`

## Metadata

- Local issue ID: LISS-0355
- Status/phase: **complete** (2026-08-07) — PR
  [#427](https://github.com/nn0cl/staqex/pull/427) merged, commit
  `62d2285`
- Type: Kernel bug fix (`compiler/staqex/typecheck.py`); no example
  content
- Priority: P1 (broader in scope than the four sibling
  hardcoded-payload bugs this session already fixed — affects *any*
  operator, and discards *dimension*, not just payload naming)
- Initial planning size: `S`
- Owner / agent: Claude Code
- Program: standalone Kernel fix, found while investigating LISS-0338's
  last documented gap (`abs()`'s missing classical-scalar
  implementation)
- Parent: none
- Depends on: none
- Blocks: none
- Branch: `feature/liss-0355-classical-literal-mixing-dimension-fix`
- GitHub Issue / PR: [#427](https://github.com/nn0cl/staqex/pull/427)
  (merged, `62d2285`)

## Design decision

Investigating `abs()`'s classical-scalar support led to a live repro
(`Bool ok = x == 3.0`, `x: Float`) that failed
`PRODUCT_TYPE_MISMATCH: cannot assign Classical<Float> to declared
Classical<Bool>` — surprising, since LISS-0352 had already fixed
Classical relational comparisons. Root-caused: LISS-0352's fix only
covers "both operands are named Classical variables." When **one**
operand is a bare numeric literal (`x == 3.0`, not `x == y`), a
**different, earlier** branch in `_infer_binop` intercepts first.

That branch's original purpose (comment: "Allow `pi / 2.0` / `2 * pi`:
numeric literals are State-typed sugar") is to let a Classical scalar
combine with a bare literal (which defaults to `State`-kind by
default) without triggering the "cannot mix classical with quantum
State" rejection a few lines below. But it implemented this by
**unconditionally returning `Ty("Classical", "Float", DIMLESS)` for
every operator**, based on a misreading of which operand's dimension
it was checking: `other` in that branch is the **literal's own** Ty
(always dimensionless Int/Float/Any, trivially), not the actual
Classical operand's. So this branch fires for **any** Classical
operand — including dimensioned ones like `Energy`/`Time` — whenever
paired with a bare literal, and discards that operand's real payload
**and dimension** entirely, for **every** operator, not just the
relational ones LISS-0352 already fixed for the variable-vs-variable
case.

Confirmed live, broader than the originally-suspected relational-only
scope:

| Repro | Before this fix |
|---|---|
| `Bool ok = x == 3.0` (`x: Float`) | `PRODUCT_TYPE_MISMATCH` (RELATIONAL, literal side) |
| `Int y = double_it(x)` where `double_it(x: Int) -> Int { return x * 2 }` | `RETURN_TYPE_MISMATCH: returns Classical<Float>, declared Classical<Int>` (LISS-0349's `*`/`/` fix bypassed for the literal case) |
| `Energy e2 = scale(e)` where `scale(e: Energy) -> Energy { return e * 2.0 }` | `DIMENSION_MISMATCH_ERROR: [Energy] vs [1]` — the `Energy` **dimension itself** is discarded, not merely mistyped |
| `Bool ok = lit_lt(x)` where `lit_lt(x: Float) -> Bool { return 3.0 < x }` (literal on the *left*) | same `RETURN_TYPE_MISMATCH` as the `==` case, confirming both operand orderings are affected |

**Blast-radius check on shipped examples**: exactly one match across
all of `examples/` (`item.effect_on_rescue * 10.0` in
`examples/showcase/S01_quantum_disaster_response/domain/recovery.sqx`),
and it is coincidentally unaffected — `effect_on_rescue` is already
dimensionless `Float`, so the bug's forced `Classical<Float>` happens
to match the correct answer. **No currently-shipped example is
actually broken by this bug.**

**Adopted fix**: instead of hardcoding the result inside the buggy
branch, reinterpret the literal side as genuinely `Classical`-kind
(same payload — `Int`/`Float` per the literal's own type — same
`DIMLESS` dimension) immediately after `left`/`right` are first
inferred, *before* any kind-based dispatch runs. This makes the
already-correct "Classical ⊕ Classical" logic (payload/dimension
preservation from LISS-0343/0349, `RELATIONAL` → `Bool` from LISS-0352,
`&&`/`||` → `Bool` from LISS-0354) handle the literal-mixing case
uniformly, for every operator, instead of special-casing it with a
hardcoded, operator-blind result. The old branch's now-unreachable
hardcoded-return sub-block is removed (confirmed dead: its condition
is a strict subset of the new coercion's, which now fires first).

## Intent

1. `typecheck.py::_infer_binop`: immediately after `left =
   self._infer(expr.lhs)` / `right = self._infer(expr.rhs)`, reinterpret
   a bare-literal side (`isinstance(expr.rhs/.lhs, (LitInt, LitFloat))`,
   dimensionless) as `Classical`-kind when the *other* side is already
   `Classical`-kind, before any subsequent branching.
2. Remove the now-dead hardcoded-return sub-block in the
   `if left.kind == "State" or right.kind == "State":` block (its
   condition can no longer be reached — the new coercion always fires
   first for the same input shape).

## Explicitly out of scope

- `abs()`'s own classical-scalar implementation — the original
  investigation target, deferred to its own follow-up Issue now that
  this larger, unrelated bug is out of the way.
- Any example content (confirmed none are currently broken by this
  bug).
- The LISS-0133 genuine classical-scalar/quantum-State scaling logic
  (`J * (Z[0]*Z[1])`-style Operator coefficient scaling) — untouched,
  still reachable for real (non-literal) State expressions.

## Acceptance reference

```gherkin
Feature: Classical operand mixed with a bare literal preserves payload and dimension

  Scenario: relational comparison against a literal produces Bool
    Given `Bool ok = x == 3.0` where `x: Float`
    When compiled
    Then it does not raise PRODUCT_TYPE_MISMATCH

  Scenario: Int * literal preserves Int payload
    Given `fn double_it(x: Int) -> Int { return x * 2 }`
    When compiled and run
    Then it does not raise RETURN_TYPE_MISMATCH

  Scenario: Energy * literal preserves the Energy dimension
    Given `fn scale(e: Energy) -> Energy { return e * 2.0 }`
    When compiled and run
    Then it does not raise DIMENSION_MISMATCH_ERROR or RETURN_TYPE_MISMATCH

  Scenario: a literal on the left side is handled symmetrically
    Given `fn lit_lt(x: Float) -> Bool { return 3.0 < x }`
    When compiled and run
    Then it does not raise RETURN_TYPE_MISMATCH
```

## Verification plan for this design intake (not shipped as a test)

All four scenarios above confirmed live before drafting this Issue.
Blast-radius grep across `examples/` confirmed exactly one coincidental
match, unaffected. Full `pytest tests/ -q` sweep, diffed line-by-line
(not just count) against the pre-fix baseline, confirmed the exact
same 52 failures, no new ones and no incidental fixes — consistent
with the confirmed-empty blast radius on shipped code.
`spec_verification` unchanged (161/161).

## AI planning record (size S)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-07
- Size: `S` — a small coercion added at the top of one function, plus
  removal of the now-dead branch it supersedes; broader in *scope*
  (affects any operator, any Classical payload/dimension) than the
  four sibling hardcoded-payload fixes this session already shipped,
  but mechanically simple once root-caused. All four repro scenarios
  and the blast-radius audit live-verified before drafting.
- Route: direct implementation by this session.
- Confidence: high.

## Exit criteria

- [x] Phase 1 Red:
      `tests/test_liss_0355_classical_literal_mixing_dimension_fix_red.py`
      added (4 cases). Confirmed all 4 failing with the fix temporarily
      reverted (`PRODUCT_TYPE_MISMATCH` / `RETURN_TYPE_MISMATCH`
      matching the documented repros).
- [x] Phase 2 Green: `typecheck.py` fixed (literal-side reinterpreted
      as Classical before kind-based dispatch; now-dead hardcoded
      branch removed). All 4 tests pass.
- [x] Phase 3 Refactor: no further change needed; reviewer empathy
      summary below.
- [x] Full regression: `pytest tests/ -q` → 1241 passed, 52 failed
      (unchanged failure count vs. the established baseline; confirmed
      via full failure-list diff, not just count — identical before
      and after, no new failures and no incidental fixes, consistent
      with the confirmed-empty blast radius on shipped examples — +4
      is this Issue's own new tests); `python3
      tests/spec_verification/run_all.py` → 161/161 (100%, Gate: PASS,
      unchanged); `git diff --check` → clean.

## Reviewer empathy summary

**何を目的として何を変更したか**: `abs()`の古典スカラー実装調査
から派生して発見した、`typecheck.py::_infer_binop`の「Classical値と
裸のリテラルの混合」処理が、演算子を一切見ずに結果を常に
`Classical<Float>`（無次元）にハードコードしていたバグを修正した。
LISS-0343/0349/0352/0354で修正済みの4件（両側とも変数の場合の
payload崩壊）とは別の、より広範囲な問題——片側が裸のリテラルの
場合に限り発動し、あらゆる演算子（関係比較だけでなく`*`/`/`も）に
影響し、payloadだけでなく**次元そのもの**（Energy等）も破棄する
バグだった。修正は、リテラル側を「State側の糖衣構文」として
扱うのではなく、その場でClassical種別に再解釈し、既に正しい
「Classical ⊕ Classical」統一ロジックに委ねる方式を採用した——
ハードコードされたショートカット分岐自体を削除し、無条件return
ではなく型推論の入力を修正するアプローチ。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- 修正前、旧バグ分岐の`other`変数が実は「Classical側」ではなく
  「リテラル側自身」を指していたことに気づかず、最初のEnergy*
  リテラルの実リプロで想定と異なる`DIMENSION_MISMATCH_ERROR`
  （次元自体が失われる）が出たことで、実際にコードをステップ
  トレースして再確認し、正しい根本原因（`other = right if
  left.kind == "Classical" else left`が実はリテラル側を指して
  いた）にたどり着いた。
- 旧分岐の内部にあった`if isinstance(lit_side, ...) and
  other.payload in {...} and other.dim.is_dimensionless(): return
  ...`部分が、新しい修正により本当に到達不能（dead code）に
  なったことを、`lit_side`/`other`という変数名が以降どこにも
  参照されていないことを直接確認した上で削除した。
- 影響範囲監査として`examples/`全体をgrepし、該当パターンが
  1箇所（`recovery.sqx`の`effect_on_rescue * 10.0`）のみで、
  かつ既に無次元Floatだったため偶然影響を受けていなかったことを
  確認した。回帰テストも件数だけでなく失敗リスト全体をdiffし、
  完全に一致（新規失敗も偶然の修正も0件）であることを確認した。

**人間がコードレビューで重点的に見るべきポイント**:
- 特になし。既存の正しいロジック（LISS-0343/0349/0352/0354で
  確立済み）へ委譲する形の修正であり、新しい特殊ケースを追加して
  いない。

## Non-goals

- `abs()`'s classical-scalar implementation (separate follow-up Issue).
- Example content changes.
