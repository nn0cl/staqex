# LISS-0357: `evolve ... for <duration>`'s fail-closed unit check recognizes struct-field and inline-literal durations

## Metadata

- Local issue ID: LISS-0357
- Status/phase: **complete** (2026-08-07) — PR
  [#432](https://github.com/nn0cl/staqex/pull/432) merged, commit
  `8f25c61`
- Type: Kernel bug fix (`compiler/staqex/runtime/evaluator.py`); no
  example content
- Priority: P2
- Initial planning size: `XS`
- Owner / agent: Claude Code
- Program: standalone Kernel fix, closes the "Related, not blocking"
  item flagged in
  [LISS-0335](LISS-0335-a10-mission-observatory-real-unit-migration.md)
- Parent: none
- Depends on: none
- Blocks: none
- Branch: `feature/liss-0357-evolve-duration-attr-and-literal-unit-recognition`
- GitHub Issue / PR: [#432](https://github.com/nn0cl/staqex/pull/432)
  (merged, `8f25c61`)

## Design decision

ADR 0195's fail-closed `evolve ... for <duration>` unit check
(`_hamiltonian_evolve_one_step` in
`compiler/staqex/runtime/evaluator.py`) only resolves `duration_unit`
when `expr.duration` is a bare `Var`:

```python
duration_unit = (
    self.scalar_units.get(expr.duration.name)
    if isinstance(expr.duration, Var)
    else None
)
```

Two narrower gaps share this exact root cause, both already found live
and worked around in prior Issues rather than fixed at the source:

1. **Struct-field access** (`evolve site under Hssh for
   config.duration`, `config.duration` declared `Time`-typed and
   tracked via ADR 0174's `field_units`) — found during
   [LISS-0335](LISS-0335-a10-mission-observatory-real-unit-migration.md)
   (2026-08-05), worked around there by binding
   `Time dur = config.duration` immediately before `evolve`.
2. **Inline unit-suffixed literal** (`evolve ... for 0.25.fs` directly
   in the `for` clause, represented as an `Attr` node
   `Attr(obj=LitFloat(0.25), name="fs")`) — found live during
   LISS-0345's own Green phase, worked around there the same way (a
   separate pre-bound `Time` variable).

Both are rejected identically with `EVOLVE_UNRESOLVED_UNIT_ERROR` even
though the underlying value genuinely carries a resolvable `Time` unit.

**Adopted fix**: `evaluator.py` already has a correct, general
value+unit resolver for exactly this shape of expression —
`_eval_value_with_unit` (used elsewhere for `+`/`-` unit-aware
arithmetic) — which already handles `Var`, `Attr` struct-field reads
(via `_attr_field_unit`/`_attr_host`), `Attr` literal-suffix reads
(`isinstance(expr.obj, (LitInt, LitFloat)) and expr.name in
UNIT_TABLE`), and `UnitConvert`. Replacing the narrow
`isinstance(expr.duration, Var)` branch with a single call to
`self._eval_value_with_unit(expr.duration, {})` (reusing its returned
value directly, instead of a second separate `_eval_value` call) fixes
both gaps with the same one-line-shaped change, since they share the
identical root cause. `typecheck.py` requires no change — confirmed it
has no special-casing here (`_infer(expr.duration)` is already
generic); this is purely a runtime evaluator gap.

Confirmed via grep this is the only call site with this narrow check
in the Kernel (no other `evolve`-duration path exists), so the fix has
no other call sites to mirror it into.

## Intent

1. `evaluator.py::_hamiltonian_evolve_one_step`: replace the
   `duration_unit` computation and the subsequent `t_raw =
   float(self._eval_value(expr.duration, {}))` line with a single
   `t_raw_val, duration_unit = self._eval_value_with_unit(expr.duration,
   {})` call, keeping the existing `UNIT_TABLE.get(duration_unit,
   (None, None))[0] != "Time"` fail-closed check and the subsequent
   `to_canonical_magnitude` canonicalization unchanged.

## Explicitly out of scope

- Any change to `_eval_value_with_unit` itself (already correct,
  reused as-is).
- Any change to ADR 0174 field-unit tracking or ADR 0195's fail-closed
  semantics (still rejects genuinely dimensionless durations).
- Removing the now-unnecessary local-variable workarounds from
  `A10_mission_observatory` or any other already-shipped example (they
  remain valid, just no longer required); no example content touched.
- `typecheck.py` (already correct, no change needed).

## Acceptance reference

```gherkin
Feature: evolve's fail-closed duration check recognizes struct-field and inline-literal durations

  Scenario: struct-field-access duration is accepted
    Given a struct with a `Time`-typed field constructed from a dimensioned literal
    And `evolve <state> under <H> for <instance>.<field>` (direct field access, no local rebinding)
    When compiled and run
    Then it does not raise EVOLVE_UNRESOLVED_UNIT_ERROR

  Scenario: inline unit-suffixed literal duration is accepted
    Given `evolve <state> under <H> for 0.25.fs` (literal directly in the for clause)
    When compiled and run
    Then it does not raise EVOLVE_UNRESOLVED_UNIT_ERROR

  Scenario: a genuinely dimensionless duration is still rejected (fail-closed preserved)
    Given `Float t = 1.0; evolve <state> under <H> for t` (no unit suffix anywhere)
    When compiled and run
    Then it raises EVOLVE_UNRESOLVED_UNIT_ERROR (ADR 0195 unchanged)
```

## Verification plan for this design intake (not shipped as a test)

Both gaps confirmed live before drafting this Issue (both fail
identically pre-fix); full `pytest tests/ -q` sweep after the fix,
diffed line-by-line against the current baseline (52 failed, 1249
passed), to confirm no new failures and to check whether any existing
passing test's behavior changes (expected: none, since the
local-variable workarounds remain valid alternate paths, not the only
path). `spec_verification` expected unchanged (161/161).

## AI planning record (size XS)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-07
- Size: `XS` — a single call-site change in one function, reusing an
  already-correct existing helper.
- Route: direct implementation by this session.
- Confidence: high.

## Exit criteria

- [x] Phase 1 Red:
      `tests/test_liss_0357_evolve_duration_attr_and_literal_unit_recognition_red.py`
      added (3 cases). Confirmed 2 of 3 failing with the Kernel change
      not yet applied (`EVOLVE_UNRESOLVED_UNIT_ERROR` on both the
      struct-field and inline-literal cases); the 3rd
      (`test_genuinely_dimensionless_duration_is_still_rejected`)
      correctly already passed, confirming it is a fail-closed
      regression guard, not a Red-confirming case.
- [x] Phase 2 Green: `evaluator.py::_hamiltonian_evolve_one_step`'s
      duration-unit resolution replaced with a single
      `self._eval_value_with_unit(expr.duration, {})` call, reusing its
      returned value directly instead of a second `_eval_value` call.
      All 3 tests pass.
- [x] Phase 3 Refactor: no further code change needed; reviewer
      empathy summary below.
- [x] Full regression: `pytest tests/ -q` → 1252 passed, 52 failed
      (unchanged failure count vs. the established baseline — no new
      failures, no incidental fixes — +3 this Issue's own new tests);
      `python3 tests/spec_verification/run_all.py` → 161/161 (100%,
      Gate: PASS, unchanged); `git diff --check` → clean.

## Reviewer empathy summary

**何を目的として何を変更したか**: `evolve ... for <duration>`の
ADR 0195 fail-closedユニットチェックが、`duration`が裸の`Var`の場合
しか単位を認識しない（`isinstance(expr.duration, Var)`）という狭い
制約を持っていたため、LISS-0335で発見された構造体フィールドアクセス
（`config.duration`）と、LISS-0345で発見されたインライン単位付き
リテラル（`evolve ... for 0.25.fs`）の両方が、実際には解決可能な
`Time`単位を持つにもかかわらず`EVOLVE_UNRESOLVED_UNIT_ERROR`で拒否
されていた。両方とも根本原因は同一（狭すぎるVarのみのチェック）
だったため、既に`Var`/構造体フィールド`Attr`/リテラル接尾辞`Attr`を
正しく処理する既存のヘルパー`_eval_value_with_unit`に置き換える
一箇所の修正で両方を同時に解消した。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- `_eval_value_with_unit`は`assign={}`で呼び出される場合、`Attr`の
  ホスト解決が`self.objects`（グローバル/main()トップレベルの
  オブジェクトストア）にフォールバックすることを、既存コード
  （`_attr_host`）を読み込んで確認した上で採用した。実際に
  `main()`内のローカル`Config config = ...`が`self.objects`経由で
  正しく解決されることをライブテストで確認済み。
- 修正がADR 0195の意図（fail-closed、真に無次元のdurationは依然
  拒否）を壊していないことを、専用の回帰テストケースで明示的に
  確認した。

**人間がコードレビューで重点的に見るべきポイント**:
- `_eval_value_with_unit`の再利用が、`evolve`の他の未検証パス
  （`until`ループ内での再評価など）に意図しない副作用を及ぼさないか。
  Grep調査ではこの狭いチェックの呼び出し箇所はこの一箇所のみで
  あることを確認済み。

## Non-goals

- `typecheck.py` changes.
- Example content changes.
- `_eval_value_with_unit` changes.
