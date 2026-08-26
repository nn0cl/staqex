# LISS-0354: implement `&&`/`||` as total-pushforward Boolean operators (ADR 0196)

## Metadata

- Local issue ID: LISS-0354
- Status/phase: **complete** (2026-08-07) — PR
  [#425](https://github.com/nn0cl/staqex/pull/425) merged, commit
  `fcda1c6`
- Type: Kernel feature (`compiler/staqex/parser.py`,
  `compiler/staqex/typecheck.py`,
  `compiler/staqex/runtime/evaluator.py`); no example content
- Priority: P2
- Initial planning size: `S`
- Owner / agent: Claude Code
- Program: implements [ADR 0196](../architecture/adr/0196-boolean-total-pushforward-logical-operators.md)
  (Accepted 2026-08-07), the design work required before this
  implementation per that ADR's own acceptance boundary
- Parent: [ADR 0196](../architecture/adr/0196-boolean-total-pushforward-logical-operators.md)
- Depends on: ADR 0196 (Accepted)
- Blocks: none
- Branch: `feature/liss-0354-boolean-total-pushforward-logical-operators`
- GitHub Issue / PR: [#425](https://github.com/nn0cl/staqex/pull/425)
  (merged, `fcda1c6`)

## Design decision

Implements ADR 0196's accepted decision directly:
`_logical_or`/`_logical_and` grammar levels inserted between `_pipe`
and `_comparison`; `typecheck.py` cases for both `Classical<Bool>` and
`State<Bool>` (Bool-only, no implicit truthiness coercion); `_apply_op`
truth-table cases (mechanically non-short-circuit, since both operands
are already fully evaluated by the caller before `_apply_op` runs, for
every existing `BinOp` — confirmed in ADR 0196's own robustness audit).

**Live-verified before drafting this Issue** (all three layers):

1. **Classical**: `fn both(a: Bool, b: Bool) -> Bool { return a && b }`
   compiles and runs correctly for all combinations.
2. **State, single-world**: `state a = dirac(true); state b =
   dirac(false); state c = a && b; measure c tracing_out a, b` →
   `false`, as expected.
3. **State, genuinely multi-world** (the concrete "total pushforward,
   not short-circuit" confirmation): two independent `coin()`s, each
   mapped to an explicit `State<Bool>` via `mix`, combined with `&&`,
   measured with a fixed seed → `P(true) = 0.25`, `P(false) = 0.75`,
   exactly matching two independent fair coins both landing "true" —
   the correct per-world truth-table result. If evaluation incorrectly
   short-circuited (skipped the right operand for any world where the
   left was already `false`), this distribution would not match.

**Found and fixed a genuine regression in two pre-existing tests**
(not a new bug — the old tests encoded exactly the pre-ADR-0196
behavior this ADR was accepted to supersede):
`test_binder_compound_where_red.py::test_classical_ampersand_outside_where_still_errors`
and
`test_binder_where_or_red.py::test_statement_or_still_errors`
both asserted `Float && Float` / `Float || Float` must produce a
parse-level rejection (`LEX_ERROR`/`PARSE_ERROR`/`FORBIDDEN_KEYWORD`).
Under ADR 0196, `&&`/`||` are now valid general-expression grammar, so
this exact repro correctly *parses* and is instead rejected at
typecheck (`TYPE_MISMATCH`: `Float` is not `Bool`) — a more precise
error than the old blanket parse-level rejection. Renamed and updated
both tests to assert the new, ADR-0196-accepted contract (parses
cleanly, `TYPE_MISMATCH` at typecheck), confirmed with the Adjudicator
before touching either pre-existing file.

**Correction (2026-08-07)**: this Issue originally flagged a suspected
`mix` type-inference quirk here — constructing a multi-world
`State<Bool>` via `mix (coin_result) { 0 -> dirac(false), else ->
dirac(true) }` **without** an explicit `State<Bool>` type annotation
was reported to infer payload `"Coin"` (from the scrutinee) instead of
`"Bool"` (from the arm bodies). Re-investigated directly: this does
**not** reproduce, not even at this Issue's own merged commit
(`fcda1c6`) — `typecheck.py`'s `WhenExpr` inference already correctly
derives payload from the arm bodies (`_infer(arm.body)` per arm,
`_promote`d together), never from the scrutinee. The original repro
was almost certainly run against an intermediate, not-yet-finished
state of this Issue's own `typecheck.py` work rather than a genuine,
persistent Kernel bug — a documentation error on this Issue's part,
not a code defect. No fix needed; no follow-up Issue required. See
`docs/architecture/open-work-register.md`'s dated entry for the same
correction.

## Intent

1. `parser.py`: insert `_logical_or`/`_logical_and` between `_pipe` and
   `_comparison` in `_expression`'s chain, matching `TokenKind.OR`/
   `TokenKind.AND`. `_op_expression`'s own `_op_guard`/`_op_guard_and`
   (Operator-DSL binder guard) unchanged.
2. `typecheck.py::_infer_binop`: add `if expr.op in {"&&", "||"}` cases
   to both the Classical-kind and State-kind branches — both operands
   must already be `Bool` payload (else `TYPE_MISMATCH`); result is
   `Classical<Bool>` / `State<Bool>` respectively.
3. `evaluator.py::_apply_op`: add `"&&"`/`"||"` cases (`bool(l) and
   bool(r)` / `bool(l) or bool(r)` on the already-evaluated operands).
4. Update the two pre-existing tests named above to the new,
   ADR-0196-accepted contract.

## Explicitly out of scope

- `!` (logical NOT) — ADR 0196 explicitly excludes it, left for a
  future ADR.
- The Operator-DSL's own `&&`/`||` (binder guard) — unchanged, separate
  grammar production.
- The `mix`-scrutinee-type-inference quirk found above — unrelated
  pre-existing behavior, flagged for a future Issue.
- `_construct_instance`/class-returning paths, `abs()`'s missing
  classical-scalar form — unrelated backlog items.

## Acceptance reference

```gherkin
Feature: && / || are total-pushforward Boolean operators

  Scenario: Classical Bool && / || type-check and run correctly
    Given `fn both(a: Bool, b: Bool) -> Bool { return a && b }`
    When compiled and run for all four truth-table combinations
    Then each produces the correct Boolean result

  Scenario: non-Bool operands are rejected at typecheck, not at parse
    Given `Float x = 1.0; Float y = 2.0; Float z = x && y`
    When compiled
    Then it does not raise LEX_ERROR or PARSE_ERROR
    And it raises TYPE_MISMATCH

  Scenario: State<Bool> && is a genuine per-world pushforward, not short-circuit
    Given two independent coin()s each mapped to State<Bool>, combined with &&
    When measured with a fixed seed across many trials
    Then P(true) matches the product of each coin's independent P(true) (0.25 for two fair coins)

  Scenario: the Operator-DSL's own binder-guard && is unaffected
    Given `sum(...) where i < j && j < 2 { ... }`
    When compiled
    Then it behaves exactly as before (unchanged code path)
```

## Verification plan for this design intake (not shipped as a test)

All four scenarios above confirmed live before drafting this Issue,
including the concrete probability-distribution check for the
multi-world pushforward case. Full `pytest tests/ -q` sweep, after
updating the two pre-existing tests, returns to the exact established
baseline (52 failed, 1233 passed, no net regression);
`spec_verification` unchanged (161/161).

## AI planning record (size S)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-07
- Size: `S` — three small, targeted changes across three files
  (grammar, typecheck, runtime), each individually simple and mirroring
  already-established patterns in the same functions; the two
  pre-existing test updates add a small amount of additional surface.
  Every piece live-verified, including the concrete multi-world
  probability check, before this Issue was drafted.
- Route: direct implementation by this session.
- Confidence: high.

## Exit criteria

- [x] Phase 1 Red:
      `tests/test_liss_0354_boolean_total_pushforward_logical_operators_red.py`
      added (4 cases). Confirmed 3 of 4 failing with the Kernel change
      temporarily reverted (`PARSE_ERROR: unexpected token in
      expression: '&&'`); the 4th
      (`test_operator_dsl_binder_guard_and_or_unaffected`) correctly
      already passed even reverted, confirming it is a regression
      guard for the unchanged Operator-DSL path, not a Red-confirming
      case.
- [x] Phase 2 Green: `parser.py`/`typecheck.py`/`evaluator.py` fix
      applied; `test_binder_compound_where_red.py` and
      `test_binder_where_or_red.py` updated to the new,
      ADR-0196-accepted contract (renamed test functions, now assert
      `TYPE_MISMATCH` instead of a parse-level rejection). All 4 new
      tests pass.
- [x] Phase 3 Refactor: no further code change needed; reviewer
      empathy summary below; `dec-0002-state-first-semantics-and-measurement.md`
      updated per ADR 0188's DEC-page-update rule.
- [x] Full regression: `pytest tests/ -q` → 1237 passed, 52 failed
      (unchanged failure count vs. the established baseline, no new
      failures — +4 this Issue's own new tests); `python3
      tests/spec_verification/run_all.py` → 161/161 (100%, Gate: PASS,
      unchanged); `git diff --check` → clean.

## Reviewer empathy summary

**何を目的として何を変更したか**: ADR 0196で受理された設計
（`&&`/`||`を一般式で使える「total pushforward」Boolean演算子として
導入）を実装した。パーサーに`_logical_or`/`_logical_and`という新しい
優先順位段を`_pipe`と`_comparison`の間に挿入し、typecheck.pyの
Classical/State両ブランチに`&&`/`||`ケースを追加、evaluator.pyの
`_apply_op`に真理値表ケースを追加した。Operator DSL独自の
`&&`/`||`（binder guard）は完全に無変更。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- 実装後の回帰テストで、既存の2つのテスト
  （`test_classical_ampersand_outside_where_still_errors`、
  `test_statement_or_still_errors`）が、`&&`/`||`が一般式ではパース
  エラーになることを旧仕様としてアサートしていたため失敗した。
  これはバグではなく、ADR 0196が正式に上書きした旧仕様そのもの
  だったため、ユーザーに確認の上で新仕様（`TYPE_MISMATCH`を期待）
  に更新した。
- 「short-circuitでないこと」を実際に検証するテストとして、2つの
  独立したフェアコインをそれぞれ`State<Bool>`にマッピングし`&&`で
  結合、400試行のシード掃引でP(true)が理論値0.25に統計的に一致する
  ことを確認する方式を採用した——単純な真理値表の正しさだけでは
  short-circuit実装と非short-circuit実装を区別できないため。
- 実装当初、`mix (coin_result) { 0 -> dirac(false), else ->
  dirac(true) }`が明示的な`State<Bool>`型注釈なしでは`Coin`
  payloadを継承してしまうという別問題を発見したと記録したが、
  後日（2026-08-07）再調査したところ再現せず、本Issue自身の
  マージ済みコミット時点でも既に正しく動作していたことを確認した。
  実装途中の中間状態を誤ってテストしたことによる、コード上のバグ
  ではなく記録上の誤りだったと結論し、Issue本文・open-work-register
  ともに訂正済み。

**人間がコードレビューで重点的に見るべきポイント**:
- `dec-0002`への追記内容が、ADR 0196の意図（total pushforward、
  short-circuitなし）を簡潔かつ正確に反映しているか。

## Non-goals

- `!` (logical NOT).
- Operator-DSL binder-guard `&&`/`||` (unchanged).
