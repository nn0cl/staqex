# LISS-0353: add an execution path for free functions that return a struct type

## Metadata

- Local issue ID: LISS-0353
- Status/phase: **complete** (2026-08-07) — PR
  [#422](https://github.com/nn0cl/staqex/pull/422) merged, commit
  `dbeb100`
- Type: Kernel bug fix (`compiler/staqex/runtime/evaluator.py`); no
  example content
- Priority: P2
- Initial planning size: `S`
- Owner / agent: Claude Code
- Program: standalone Kernel fix, one of the classical-language gaps
  documented under LISS-0338's "Related, not blocking" (found during
  A11's rewrite, deliberately not fixed there — design avoided
  triggering it instead)
- Parent: none
- Depends on: none
- Blocks: none
- Branch: `feature/liss-0353-struct-returning-free-function-execution-path`
- GitHub Issue / PR: [#422](https://github.com/nn0cl/staqex/pull/422)
  (merged, `dbeb100`)

## Design decision

LISS-0338 documented, but did not fix: "no execution path for free
functions that RETURN a struct type (routes through `_bind_user_fun`,
not `_eval_classical_call`, whose `classical_heads` set excludes
structs)."

Confirmed live, then root-caused precisely (the exact mechanism turned
out to be two separate, compounding gaps, not one):

**Gap 1 — top-level dispatch**: `evaluator.py`'s `_run_unit_body`
statement dispatch, on seeing a struct-typed binding
(`Point p = <Call>`), unconditionally routes to `_construct_struct`
assuming the RHS call is literally that struct's own constructor
(`Point(...)`). When the RHS is instead a free function that
internally constructs and returns the struct (`make_point(...)`),
`_construct_struct` fails with `RUNTIME_ERROR: unknown struct
constructor `make_point()`` — it never considers that the callee might
be an ordinary function in `self.funs`.

**Gap 2 — the classical-value gate**: `_eval_classical_call`'s
`classical_heads` set (used by `_eval_value`'s generic `Call` handling,
and needed once Gap 1 is fixed to reach that fallback at all) is a
fixed list of scalar/dimensioned types (`Float`, `Int`, `Energy`, ...)
that excludes struct names entirely — so even routing correctly away
from `_construct_struct` still failed with `RUNTIME_ERROR: call cannot
be classical value in Phase 2.2 value context: 'make_point' is not a
pure classical-returning fn`.

**Gap 3 — found while fixing Gaps 1-2**: once both were fixed, a
*third*, previously-unknown-to-LISS-0338 issue surfaced:
`_construct_struct` (and its helper `_eval_struct_arg`) evaluate
constructor arguments with **no knowledge of an enclosing function's
local parameter frame** — they only ever look up `self.objects`
(globally-registered names). So `make_point`'s own body (`return
Point(a, b)`, where `a`/`b` are `make_point`'s *parameters*, not global
objects) failed with `RUNTIME_ERROR: unbound variable 'a'` even after
Gaps 1-2 were fixed — `_construct_struct` had never been called from
inside a free function's local evaluation context before, so this path
was simply never exercised.

**Adopted fix** (all three, since Gap 3 was undetectable without first
fixing 1-2, and the repro doesn't compile-and-run end to end until all
three are addressed):

1. In the top-level struct-typed-binding dispatch: before assuming
   direct construction, check whether the RHS call's callee resolves
   to a *known free function* (`self.funs`) other than the struct's
   own name — if so, evaluate it as an ordinary classical call
   (`_eval_value_with_unit`) instead of `_construct_struct`.
2. In `_eval_classical_call`'s free-function branch: accept a struct
   return type (`fun.return_type.name in self.structs`) alongside the
   existing `classical_heads` set — a struct is also a pure classical
   value.
3. Thread an optional `assign` (the enclosing free function's local
   parameter frame) through `_construct_struct` → `_eval_struct_arg`,
   defaulting to `None`/`{}` at every pre-existing call site (backward
   compatible — those sites have no enclosing local frame to thread),
   and pass it through at the one call site that does have one
   (`_eval_value`'s generic `Call` handling, which already receives
   `assign` as a parameter but was not forwarding it).

## Intent

1. `evaluator.py`'s `_run_unit_body`: in the struct-typed-binding
   branch, detect a free-function callee (not the struct's own name)
   and route through `_eval_value_with_unit` instead of
   `_construct_struct`.
2. `_eval_classical_call`: relax the free-function return-type gate to
   also accept `self.structs` membership.
3. `_construct_struct(struct_name, expr, assign=None)` and
   `_eval_struct_arg(arg, assign=None)`: accept and thread an optional
   caller-local frame; check it before falling back to
   `self.objects`/`self.scalars`.
4. `_eval_value`'s generic `Call` handling: pass its own `assign`
   parameter through to `_construct_struct` (previously dropped).

## Explicitly out of scope

- The other two LISS-0338-era gaps (`&&` unsupported in expression
  position; `abs()`'s missing classical-scalar implementation) —
  unrelated code paths, not touched here.
- `_construct_instance` (the equivalent path for **classes**, not
  structs) — not audited or touched in this Issue; LISS-0338's own
  finding was specifically about structs. Flagged as an open question
  for a future Issue if a class-returning free function is ever needed
  (not currently exercised by any example).
- `_bind_call` (the **State**-binding dispatch path, `state x =
  SomeCall(...)`) — LISS-0338 already fixed direct struct/class
  construction there; this Issue's `assign`-threading only affects the
  **classical** value path (`_eval_value`/`_eval_classical_call`), not
  `_bind_call`, which has no local-frame concept to thread.
- Any example content.

## Acceptance reference

```gherkin
Feature: a free function may return a struct type

  Scenario: positional-args struct construction inside a free function's own body
    Given `fn make_point(a: Float, b: Float) -> Point { return Point(a, b) }`
    When `Point p = make_point(1.0, 2.0)` is compiled and run
    Then it does not raise RUNTIME_ERROR
    And p.x/p.y hold the constructed values

  Scenario: kwargs-form construction inside a free function's own body
    Given `fn make_point_kw(a: Float, b: Float) -> Point { return Point { x: a, y: b } }`
    When it is compiled and run
    Then it does not raise RUNTIME_ERROR

  Scenario: a struct-returning call nested as an argument to another call
    Given `point_sum(make_point(5.0, 6.0))`
    When it is compiled and run
    Then it does not raise RUNTIME_ERROR
```

## Verification plan for this design intake (not shipped as a test)

Confirmed live, in sequence: the original repro failed
`RUNTIME_ERROR: unknown struct constructor` before Gap 1's fix; after
Gap 1 alone, failed `RUNTIME_ERROR: call cannot be classical value...`
(Gap 2); after Gaps 1-2, failed `RUNTIME_ERROR: unbound variable 'a'`
(Gap 3, found only once 1-2 were fixed); after all three, compiles and
runs successfully. Two additional scenarios (kwargs-form construction,
nested-as-argument usage) also confirmed live. Full `pytest tests/ -q`
sweep confirmed no new failures at the exact established baseline (52
failed, 1230 passed); `spec_verification` unchanged (161/161).

## AI planning record (size S)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-07
- Size: `S` — three small, targeted changes across two functions plus
  one signature-threading change, each individually small, but their
  compounding nature (Gap 3 only visible after fixing 1-2) meant the
  full fix required all three together. All three, and their lack of
  regression, live-verified before this Issue was drafted.
- Route: direct implementation by this session.
- Confidence: high.

## Exit criteria

- [x] Phase 1 Red:
      `tests/test_liss_0353_struct_returning_free_function_execution_path_red.py`
      added (3 cases). Confirmed all 3 failing with the fix temporarily
      reverted: `RUNTIME_ERROR: call cannot be classical value in
      Phase 2.2 value context: 'make_point' is not a pure
      classical-returning fn` (Gap 2 — the first gap each case's
      top-level dispatch reaches, since Gap 1's fix was part of the
      same reverted diff).
- [x] Phase 2 Green: `evaluator.py` fixed (all three gaps). All 3
      tests pass.
- [x] Phase 3 Refactor: no further change needed; reviewer empathy
      summary below.
- [x] Full regression: `pytest tests/ -q` → 1233 passed, 52 failed
      (unchanged failure count vs. the established baseline, no new
      failures — +3 is this Issue's own new tests); `python3
      tests/spec_verification/run_all.py` → 161/161 (100%, Gate: PASS,
      unchanged); `git diff --check` → clean.

## Reviewer empathy summary

**何を目的として何を変更したか**: LISS-0338で発見・文書化されて
いたが未修正のまま残っていた「構造体を返す自由関数に実行パスが
ない」というギャップを修正した。当初は単一のギャップ
（`classical_heads`セットが構造体を除外している）と想定していたが、
実際に修正を進める過程で、複合する3つの独立したギャップ（トップ
レベルディスパッチが常に直接コンストラクタ呼び出しと誤認識、
`classical_heads`ゲート、`_construct_struct`がローカル関数パラメータ
フレームを一切知らない）であることが判明し、3つとも修正した。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- 3つ目のギャップ（`_construct_struct`のローカルフレーム未対応）は、
  最初の2つを修正するまで全く見えなかった——`unbound variable 'a'`
  というエラーは、1つ目・2つ目のギャップが未修正の状態では絶対に
  到達しないコードパスだったため。この「修正するまで次のバグが
  見えない」という連鎖を、都度実際にコードを実行して確認しながら
  1つずつ潰していった。
- `assign`パラメータのデフォルト値を`None`にし、既存の全呼び出し
  箇所（トップレベル/グローバルスコープのみを想定していた箇所）は
  無変更のまま後方互換を保ちつつ、`_eval_value`のCall処理箇所
  （既に`assign`を受け取っていたが下流に伝達していなかった）だけを
  明示的に修正した。

**人間がコードレビューで重点的に見るべきポイント**:
- `_construct_instance`（クラス版の同等パス）は本Issueでは意図的に
  未調査・未修正。クラスを返す自由関数が将来必要になった場合、
  同種の問題が再発する可能性がある（design decisionのExplicitly
  out of scopeに明記済み）。
- `_bind_call`（State側のバインディングパス）は`assign`の概念を
  持たないため今回のスレッディング対象外——LISS-0338で既に直接
  構築ケースは修正済みであることを確認した上で、意図的に触れて
  いない。

## Non-goals

- The remaining LISS-0338-era classical-language gaps.
- `_construct_instance` / class-returning free functions.
- Example content.
