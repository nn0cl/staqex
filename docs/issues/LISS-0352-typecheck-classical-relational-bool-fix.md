# LISS-0352: fix Classical relational comparisons mistyped as `Classical<Float>` in `typecheck.py`

## Metadata

- Local issue ID: LISS-0352
- Status/phase: **complete** (2026-08-07) — PR
  [#420](https://github.com/nn0cl/staqex/pull/420) merged, commit
  `eeafbb8`
- Type: Kernel bug fix (`compiler/staqex/typecheck.py`); no example
  content
- Priority: P2
- Initial planning size: `XS`
- Owner / agent: Claude Code
- Program: standalone Kernel fix, one of the classical-language gaps
  documented under LISS-0338's "Related, not blocking" (found during
  A11's rewrite, deliberately not fixed there — design avoided
  triggering it instead)
- Parent: none
- Depends on: none
- Blocks: none
- Branch: `feature/liss-0352-typecheck-classical-relational-bool-fix`
- GitHub Issue / PR: [#420](https://github.com/nn0cl/staqex/pull/420)
  (merged, `eeafbb8`)

## Design decision

LISS-0338 documented, but did not fix: "Float relational comparisons
(`>`,`<`,`>=`,`<=`) between two classical operands mistyped as
`Classical<Float>` instead of `Classical<Bool>`
(`typecheck.py::_infer_binop`'s classical-arithmetic branch has no
relational-operator case)."

Confirmed live: `fn is_greater(a: Float, b: Float) -> Bool { return a
> b }` fails `RETURN_TYPE_MISMATCH: is_greater returns Classical<Float>,
declared Classical<Bool>`.

Root cause: `_infer_binop`'s Classical-kind branch (the same function
LISS-0343/0349 already fixed two payload-collapse bugs in) handles
`+`/`-` and `*`/`/` explicitly, then falls through to a catch-all
`return Ty("Classical", "Float", DIMLESS)` for **any other operator**
— including relational comparisons (`>`, `<`, `>=`, `<=`, and
presumably `==`/`!=` depending on `RELATIONAL`'s membership). This
catch-all was written before `RELATIONAL` operators needed to route
through the Classical branch at all (the equivalent **State**-kind
branch, 8 lines below in the same function, already has its own
explicit `if expr.op in RELATIONAL: ... return Ty("State", "Bool",
DIMLESS)` case — the Classical side never got the mirror of it).

**Adopted fix**: add the mirrored `if expr.op in RELATIONAL:` case to
the Classical branch, identical in structure to the already-correct
State-side one (dimension-match check, mixed-units check), returning
`Ty("Classical", "Bool", DIMLESS)` instead of `Ty("State", "Bool",
DIMLESS)`.

## Intent

1. `typecheck.py::_infer_binop`'s Classical-kind branch: add an `if
   expr.op in RELATIONAL:` case (before the final catch-all `return
   Ty("Classical", "Float", DIMLESS)`), mirroring the State-side
   RELATIONAL case's dimension/mixed-units checks, returning
   `Ty("Classical", "Bool", DIMLESS)`.

## Explicitly out of scope

- The other two LISS-0338-era gaps (no execution path for
  struct-returning free functions; `&&` unsupported in expression
  position) — unrelated code paths, not touched here.
- `abs()`'s missing classical-scalar implementation — unrelated,
  not touched here.
- Any example content.

## Acceptance reference

```gherkin
Feature: Classical relational comparisons type-check as Bool

  Scenario: a function returning Bool via a classical > comparison type-checks and runs
    Given a function `is_greater(a: Float, b: Float) -> Bool { return a > b }`
    When it is compiled and run
    Then it does not raise RETURN_TYPE_MISMATCH
    And it runs to completion
```

## Verification plan for this design intake (not shipped as a test)

Confirmed live: the repro fails `RETURN_TYPE_MISMATCH` before the fix,
compiles and runs successfully after. Full `pytest tests/ -q` sweep
confirmed no new failures at the exact established baseline (52
failed, 1229 passed); `spec_verification` unchanged (161/161).

## AI planning record (size XS)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-07
- Size: `XS` — a single new case mirroring already-correct sibling
  code 8 lines away; fix and lack of regression both live-verified
  before this Issue was drafted.
- Route: direct implementation by this session.
- Confidence: high.

## Exit criteria

- [x] Phase 1 Red:
      `tests/test_liss_0352_typecheck_classical_relational_bool_fix_red.py`
      added. Confirmed failing with the fix temporarily reverted:
      `RETURN_TYPE_MISMATCH` (`is_greater` returns `Classical<Float>`,
      declared `Classical<Bool>`).
- [x] Phase 2 Green: `typecheck.py`'s Classical branch fixed (mirrors
      the already-correct State-side `RELATIONAL` case). Test passes.
- [x] Phase 3 Refactor: no further change needed; reviewer empathy
      summary below.
- [x] Full regression: `pytest tests/ -q` → 1230 passed, 52 failed
      (unchanged failure count vs. the established baseline, no new
      failures — +1 is this Issue's own new test); `python3
      tests/spec_verification/run_all.py` → 161/161 (100%, Gate: PASS,
      unchanged); `git diff --check` → clean.

## Reviewer empathy summary

**何を目的として何を変更したか**: `typecheck.py`の`_infer_binop`で
Classical同士の関係比較演算子（`>`/`<`/`>=`/`<=`）が、明示的な処理
ケースを持たず、`+`/`-`/`*`/`/`のいずれにも該当しないためcatch-all
フォールバック（`Classical<Float>`）に落ちてしまっていたバグを
修正した。同じ関数内、8行下にある既に正しいState側の`RELATIONAL`
処理ケースをそのままミラーした。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- 特になし。State側の既存実装をそのままミラーしただけの、低リスクな
  修正。LISS-0338で発見・文書化されていた既知のギャップを、今回
  初めて実際に修正した。

**人間がコードレビューで重点的に見るべきポイント**:
- 特になし（既存の正しいState側実装の単純な複製）。

## Non-goals

- The remaining LISS-0338-era classical-language gaps.
- Example content.
