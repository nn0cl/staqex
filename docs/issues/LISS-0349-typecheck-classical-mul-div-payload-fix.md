# LISS-0349: fix Classical `*`/`/` payload-collapse bug in `typecheck.py`

## Metadata

- Local issue ID: LISS-0349
- Status/phase: **complete** (2026-08-06) — PR
  [#414](https://github.com/nn0cl/staqex/pull/414) merged, commit
  `e1b0797`
- Type: Kernel bug fix (`compiler/staqex/typecheck.py`); no example
  content
- Priority: P2
- Initial planning size: `XS`
- Owner / agent: Claude Code
- Program: standalone Kernel fix, flagged as a suspected sibling of
  [LISS-0343](LISS-0343-typecheck-classical-payload-and-quantum-matter-discovery-migration.md)
  during [WP-0095](../work-plans/WP-0095-real-hbar-hamiltonian-dynamics.md)
  work unit 11 and never fixed for lack of a live repro at the time;
  now confirmed live and fixed on its own, after WP-0095's completion,
  per the Adjudicator's explicit direction to investigate this next
- Parent: none (not itself part of WP-0095 — WP-0095 is complete;
  this is a standalone Kernel correctness fix in the same file)
- Depends on: none
- Blocks: none
- Branch: `feature/liss-0349-typecheck-classical-mul-div-payload-fix`
- GitHub Issue / PR: [#414](https://github.com/nn0cl/staqex/pull/414)
  (merged, `e1b0797`)

## Design decision

LISS-0343 fixed `typecheck.py::_infer_binop`'s Classical `+`/`-`
branch, which hardcoded its result payload to `"Float"` regardless of
operand payload (the dimension itself was tracked correctly). That
Issue explicitly flagged the sibling Classical `*`/`/` branch (same
function, ~30 lines below) as *suspected* to have the identical issue,
but left it unfixed since no live repro forced that code path at the
time.

Confirmed live now: the Classical `*`/`/` branch (`typecheck.py`
~lines 3335-3339, immediately below the already-fixed `+`/`-` branch)
still hardcodes its result payload to `"Float"`:

```python
if expr.op == "*":
    return Ty("Classical", "Float", left.dim.mul(right.dim))
if expr.op == "/":
    return Ty("Classical", "Float", left.dim.div(right.dim))
```

Repro: `fn force_from_energy(e: Energy, len: Length) -> Force { return
e / len }` — the *dimension* is computed correctly (`Energy.dim.div(Length.dim)`
does equal `Force`'s dimension, so no `DIMENSION_MISMATCH_ERROR`), but
the result's payload name stays `"Float"`, so a function declared `->
Force` fails `RETURN_TYPE_MISMATCH: returns Classical<Float>, declared
Classical<Force>`.

**Adopted fix**: mirror the already-correct **State**-side `*`/`/`
branch (same file, ~lines 3364-3371), which already derives the
correct payload from the computed *result* dimension via the existing
`_payload_for_dim(dim, fallback)` helper — this is the right tool here
(unlike LISS-0343's `+`/`-` fix, which preserved one *operand's*
payload directly, since `+`/`-` never change the dimension; `*`/`/`
*do* change the dimension, producing a genuinely different physical
quantity, so the payload must be derived from the *new* dimension via
`TYPE_DIMS` lookup, not carried over from either operand):

```python
if expr.op == "*":
    dim = left.dim.mul(right.dim)
    payload = _payload_for_dim(dim, _promote(left.payload, right.payload))
    return Ty("Classical", payload, dim)
if expr.op == "/":
    dim = left.dim.div(right.dim)
    payload = _payload_for_dim(dim, _promote(left.payload, right.payload))
    return Ty("Classical", payload, dim)
```

**No regression found this time** (unlike LISS-0343's `+`/`-` fix,
which broke an existing test relying on the old `Int + Int -> Float`
coercion): `_payload_for_dim`'s dimensionless fallback path already
matches the existing `Int`/`Float` legacy convention (`_promote("Int",
"Int") == "Int"`, and `_payload_for_dim(DIMLESS, "Int")` returns
`"Int"` since `"Int"` is in the fallback-preserving set — this mirrors
what the already-shipped, already-tested State-side `*`/`/` branch
already does for `Int * Int`, so there is no new-vs-old behavior
mismatch to regress). Confirmed via full regression sweep: `pytest
tests/ -q` stays at the exact post-WP-0095 baseline (52 failed, 1223
passed), no new failures.

## Intent

1. `typecheck.py::_infer_binop`'s Classical `*` and `/` branches:
   replace the hardcoded `"Float"` payload with `_payload_for_dim(dim,
   _promote(left.payload, right.payload))`, computed from the actual
   result dimension — mirroring the already-correct State-side `*`/`/`
   implementation in the same function.

## Explicitly out of scope

- Any example content migration.
- The Float relational-comparison mistyping (`>`/`<`/`>=`/`<=`
  returning `Classical<Float>` instead of `Classical<Bool>`,
  documented under LISS-0338's "Related, not blocking") — a different
  operator-kind branch in the same function, not touched here.
- The three other LISS-0338-era classical-language gaps (struct-
  returning free functions, `&&` in expression position, `abs()` with
  no classical-scalar form) — unrelated.
- `op_n_qubits`'s Jordan-Wigner qubit-undercount bug (LISS-0336,
  unrelated code path).

## Acceptance reference

```gherkin
Feature: Classical Energy / Length preserves its derived-dimension payload type

  Scenario: a function returning Force computed via / type-checks and runs
    Given a function `force_from_energy(e: Energy, len: Length) -> Force { return e / len }`
    When it is compiled
    Then it does not raise RETURN_TYPE_MISMATCH

  Scenario: the legacy Int * Int convention is unaffected
    Given a class method returning State<Int> via dirac(this.x * this.x) where x: Int
    When it is compiled
    Then it does not raise RETURN_TYPE_MISMATCH
```

## Verification plan for this design intake (not shipped as a test)

Confirmed live: `Energy / Length -> Force` fails before the fix
(`RETURN_TYPE_MISMATCH`), compiles and runs after. `Int * Int` inside
`dirac()` (State-side, exercising the already-correct sibling
implementation this fix mirrors) confirmed unaffected. Full `pytest
tests/ -q` sweep confirmed no new failures at the exact post-WP-0095
baseline (52 failed, 1223 passed).

## AI planning record (size XS)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-06
- Size: `XS` — a two-branch fix in one function, mirroring
  already-correct sibling code 30 lines away; both the fix and its
  lack of regression were live-verified before this Issue was drafted.
- Route: direct implementation by this session.
- Confidence: high.

## Exit criteria

- [x] Phase 1 Red:
      `tests/test_liss_0349_typecheck_classical_mul_div_payload_fix_red.py`
      added (2 cases). Confirmed both failing with the fix temporarily
      reverted: `test_energy_div_length_preserves_force_payload` →
      `RETURN_TYPE_MISMATCH` (`force_from_energy` returns
      `Classical<Float>`, declared `Classical<Force>`);
      `test_int_times_int_still_type_checks_in_state_context` →
      `RETURN_TYPE_MISMATCH` (`squared` returns `State<Float>`,
      declared `State<Int>`) — a **second, independent confirmation
      angle**: `this.x * this.x` (a Classical field read) hits the same
      hardcoded branch before `dirac(...)` wraps it into a `State`, so
      this test exercises the bug via State-wrapping rather than a
      direct Classical return.
- [x] Phase 2 Green: `typecheck.py`'s Classical `*`/`/` branches fixed
      (mirrors the already-correct State-side implementation via
      `_payload_for_dim`). Both tests pass.
- [x] Phase 3 Refactor: no further change needed; reviewer empathy
      summary below.
- [x] Full regression: `pytest tests/ -q` → 1225 passed, 52 failed
      (unchanged failure count vs. the post-WP-0095 baseline, no new
      failures — +2 is this Issue's own new tests); `python3
      tests/spec_verification/run_all.py` → 161/161 (100%, Gate: PASS,
      unchanged); `git diff --check` → clean.

## Reviewer empathy summary

**何を目的として何を変更したか**: `typecheck.py`の`_infer_binop`で
Classical同士の`*`/`/`が結果のpayload型を常に文字列`"Float"`に
ハードコードしていたバグを修正した。LISS-0343で修正済みの`+`/`-`
ブランチの姉妹バグとして疑われていたものを、実リプロ
（`Energy / Length -> Force`）で確認してから修正した。修正内容は
`+`/`-`ブランチと同じ「専用ロジックを書く」方式ではなく、同じ関数内
30行下にある**既に正しいState側の`*`/`/`実装**（`_payload_for_dim`
ヘルパーを使い、演算結果の新しい次元からpayload名を導出する）を
そのままミラーした——`*`/`/`は演算子の次元自体が変化する
（例：Energy÷Length=Force という別の物理量になる）ため、`+`/`-`の
ときのような「オペランドのpayloadをそのまま引き継ぐ」方式は適用
できず、次元ベースの逆引きが必要だったため。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- LISS-0343の`+`/`-`修正時に見つかった「`_promote`をそのまま使うと
  `Int + Int`の既存の昇格規約を壊す」という問題が、今回の`*`/`/`
  修正でも再発するかを事前に検討した。`_payload_for_dim`の無次元
  フォールバック経路はすでに`Int`/`Float`をfallbackとしてそのまま
  通す実装になっており（`"Int"`が`{"Int","Float","Any"}`に含まれる
  ため）、これは既存の（テスト済みの）State側`*`/`/`実装が既に
  依拠している規約と完全に一致することを確認した。実際、フル回帰
  テストで新規失敗が0件だったことでこれを裏付けた。
- 2つ目のテスト（`this.x * this.x`を`dirac()`で包む）を書く過程で、
  「Classical側の`*`ブランチを直接テストしているつもりが、実は
  `dirac()`でState側にラップされた結果を見ている」という構造に
  気づき、これが独立した確認角度として機能することを確認した。

**人間がコードレビューで重点的に見るべきポイント**:
- 特になし。既に検証済みのState側実装をそのままミラーしただけの、
  低リスクな修正。

## Non-goals

- Example content migrations.
- The Float relational-comparison mistyping and other LISS-0338-era
  gaps.
- `op_n_qubits` (unrelated).
