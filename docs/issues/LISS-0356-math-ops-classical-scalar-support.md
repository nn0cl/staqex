# LISS-0356: add classical-scalar execution support for `MATH_OPS` (`abs`/`sin`/`cos`/`exp`/`sqrt`/`log`/`tan`)

## Metadata

- Local issue ID: LISS-0356
- Status/phase: **complete** (2026-08-07) — PR
  [#429](https://github.com/nn0cl/staqex/pull/429) merged, commit
  `32b0852`
- Type: Kernel bug fix (`compiler/staqex/runtime/evaluator.py`); no
  example content
- Priority: P2
- Initial planning size: `XS`
- Owner / agent: Claude Code
- Program: standalone Kernel fix, closes the last item in LISS-0338's
  documented "Related, not blocking" backlog (`abs()`'s missing
  classical-scalar implementation) — investigation found the identical
  gap in all six siblings, not just `abs()`
- Parent: none
- Depends on: none
- Blocks: none
- Branch: `feature/liss-0356-math-ops-classical-scalar-support`
- GitHub Issue / PR: [#429](https://github.com/nn0cl/staqex/pull/429)
  (merged, `32b0852`)

## Design decision

LISS-0338 documented, but did not fix: "`abs()` has no classical-scalar
implementation (only a quantum `map_coord` one)." Investigating this
found `stdlib/math_ops.py::MATH_OPS` (`sin`, `cos`, `exp`, `sqrt`,
`abs`, `log`, `tan`) is consumed **only** via `joint.map_coord` — a
State-pushforward path reachable when the call appears as a quantum
coordinate transform (`state y = abs(x)` on a quantum coordinate `x`).
A classical-scalar call (`Float y = abs(x)` inside an ordinary
classical free function) has no evaluator support at all.

Confirmed live: `fn abs_val(x: Float) -> Float { return abs(x) }`
*compiles* successfully (typecheck.py has no `MATH_OPS` awareness
either; unrecognized function calls fall through to a permissive
`Ty("State", "Any", DIMLESS)` default that happens to satisfy the
declared `Float` return type), but *fails at runtime*:
`RUNTIME_ERROR: call cannot be classical value in Phase 2.2 value
context` — the same `_eval_classical_call` gate LISS-0353 already
touched for struct-returning functions, since `abs` is a builtin, not
a `self.funs` entry, and the function had no fallback for builtin math
ops.

**Confirmed the same gap for all seven `MATH_OPS` entries**, not just
`abs()` — each fails identically in classical-scalar context. Given
this is the exact same mechanism (missing recognition of
`math_ops.known_math_op`, not seven independent bugs), and this
session's established precedent (LISS-0349/0350 fixing a sibling
alongside the originally-reported operator rather than leaving an
identical gap unaddressed), this Issue fixes the whole family
together, confirmed with the Adjudicator before widening scope beyond
LISS-0338's literal wording.

**Adopted fix**: in `evaluator.py::_eval_classical_call`, before
falling through to the `self.funs` lookup, check
`math_ops.known_math_op(expr.callee.name)` — if true, evaluate the
single argument as an ordinary classical value and apply
`math_ops.apply_math`. `_eval_value`'s generic `Call` handling already
delegates to `_eval_classical_call` for anything not struct/class
construction, so no separate change is needed there. `typecheck.py` is
left untouched — its existing permissive `State<Any>` fallback for
unrecognized function names already lets `Float y = abs(x)` compile
against any declared classical type; tightening it to give `abs`/etc.
a more precise inferred type is a separate, optional follow-up, not
required to fix the actual runtime gap this Issue addresses.

## Intent

1. `evaluator.py::_eval_classical_call`: add a
   `math_ops.known_math_op(expr.callee.name)` check before the
   `self.funs` lookup — evaluate the single argument classically, apply
   `math_ops.apply_math`, return the result.

## Explicitly out of scope

- `typecheck.py` — no change; the existing permissive fallback already
  allows this pattern to compile against any declared classical type.
  Tightening it to a more precise inferred type is optional future
  work, not required here.
- The quantum `map_coord` pushforward path for `MATH_OPS` (unchanged,
  already correct).
- Any example content.

## Acceptance reference

```gherkin
Feature: MATH_OPS are usable as classical scalars

  Scenario: abs() works inside an ordinary classical function
    Given `fn abs_val(x: Float) -> Float { return abs(x) }`
    When compiled and run with x = -3.0
    Then it does not raise RUNTIME_ERROR
    And the result equals 3.0

  Scenario: the same holds for every other MATH_OPS entry
    Given sin/cos/exp/sqrt/log/tan used the same way
    When compiled and run
    Then none raises RUNTIME_ERROR
```

## Verification plan for this design intake (not shipped as a test)

Confirmed live: all seven `MATH_OPS` entries fail identically before
the fix (`RUNTIME_ERROR: call cannot be classical value...`), succeed
after; `abs(-3.0) == 3.0` confirmed to compute the correct value, not
merely "does not error." Full `pytest tests/ -q` sweep, diffed line-by-
line against the pre-fix baseline, confirmed the exact same 52
failures, no new ones and no incidental fixes. `spec_verification`
unchanged (161/161).

## AI planning record (size XS)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-07
- Size: `XS` — a single new case in one function, mirroring the
  existing `self.funs`-lookup structure right next to it.
- Route: direct implementation by this session.
- Confidence: high.

## Exit criteria

- [x] Phase 1 Red:
      `tests/test_liss_0356_math_ops_classical_scalar_support_red.py`
      added (8 cases: one parameterized case per `MATH_OPS` entry, plus
      one value-correctness case). Confirmed all 8 failing with the fix
      temporarily reverted (`RUNTIME_ERROR: call cannot be classical
      value in Phase 2.2 value context`).
- [x] Phase 2 Green: `evaluator.py::_eval_classical_call` fixed. All 8
      tests pass.
- [x] Phase 3 Refactor: no further change needed; reviewer empathy
      summary below.
- [x] Full regression: `pytest tests/ -q` → 1249 passed, 52 failed
      (unchanged failure count vs. the established baseline, no new
      failures — +8 this Issue's own new tests); `python3
      tests/spec_verification/run_all.py` → 161/161 (100%, Gate: PASS,
      unchanged); `git diff --check` → clean.

## Reviewer empathy summary

**何を目的として何を変更したか**: LISS-0338の最後の未解決項目
（`abs()`に古典スカラー実行パスがない、量子`map_coord`経路のみ）を
修正した。調査の結果、`abs()`だけでなく`MATH_OPS`全体
（`sin`/`cos`/`exp`/`sqrt`/`log`/`tan`）が同一の欠落を持つことを
確認し、Adjudicatorの承認を得た上で7つ全てを同一修正で一括対応
した。`evaluator.py::_eval_classical_call`に、`self.funs`ルック
アップの前段で`math_ops.known_math_op`をチェックする分岐を追加し、
既存の`math_ops.apply_math`実装（量子`map_coord`経路が既に使用して
いるもの）を古典スカラー引数にもそのまま再利用した。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- `Float y = abs(x)`が**コンパイル**は既に成功していた（typecheck.py
  が未知の関数呼び出しに対して寛容な`State<Any>`フォールバックを
  返し、宣言された`Float`型と偶然マッチしていたため）ことを確認
  した上で、真のギャップは**実行時のみ**にあることを特定した。
  typecheck.py自体には変更を加えていない（この寛容なフォールバック
  で十分に動作するため、スコープを広げない判断）。
- 修正がPre-existing testに影響しないことを、件数だけでなく失敗
  リスト全体のdiffで確認した（完全一致、新規失敗も偶然の修正も
  0件）。

**人間がコードレビューで重点的に見るべきポイント**:
- typecheck.py側の寛容なフォールバックに依存している設計が、将来
  より厳密な型推論が必要になった際に問題にならないか（本Issueの
  Non-goalsとして明記済み、意図的に据え置き）。

## Non-goals

- `typecheck.py` tightening for `MATH_OPS` return types.
- Example content changes.
