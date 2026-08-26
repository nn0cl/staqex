# LISS-0362: migrate operator-factory/struct-coefficient evolve tests to real Time units (WP-0096 work unit 4)

## Metadata

- Local issue ID: LISS-0362
- Status/phase: **complete** (2026-08-08) — PR
  [#443](https://github.com/nn0cl/staqex/pull/443) merged, commit
  `bead530`
- Type: test-fixture-only migration (10 files under `tests/`); no
  Kernel source change, no example content
- Priority: P3
- Initial planning size: `M`
- Owner / agent: Claude Code
- Program: [WP-0096](../work-plans/WP-0096-tests-real-hbar-duration-migration.md)
  work unit 4
- Parent: [WP-0096](../work-plans/WP-0096-tests-real-hbar-duration-migration.md)
- Depends on: none
- Blocks: none
- Branch: `feature/liss-0362-operator-factory-duration-migration`
- GitHub Issue / PR: [#443](https://github.com/nn0cl/staqex/pull/443)
  (merged, `bead530`)

## Design decision

Migrates the 19 `EVOLVE_UNRESOLVED_UNIT_ERROR` failures (WP-0096's own
investigation undercounted this group as 18; corrected here after Red
confirmed the actual count) in 10 files where the Hamiltonian's
coefficient reaches `Operator H = ...` through a function/method
return, a struct/class field, or a classical multi-bind — not written
directly as a literal in the `Operator` expression itself.

**All 10 files read in full before drafting this Issue.** Every case
follows one of the two conversion patterns established in LISS-0360/
LISS-0361 (`K = 1.0545718e-19` = `ℏ / 1fs`, duration numeral unchanged
with `.fs` appended), applied at the point where the coefficient
numeral is actually written in source — which for this work unit is
usually a struct constructor argument, a classical variable
assignment, or a function parameter, not the `Operator` expression
itself:

1. **Existing-literal-coefficient swap** (same as before): e.g.
   `-1.0 * (Z[0] * Z[1]) - 0.5 * (X[0] + X[1])` →
   `-1.0545718e-19 * (Z[0] * Z[1]) - 5.272859e-20 * (X[0] + X[1])`.
2. **Scale at the value's source**, since the literal doesn't appear
   next to the Pauli term at all: `Float J = 1.0` → `Float J =
   1.0545718e-19`; `D.Coeffs pack = D.Coeffs(0.5)` → `D.Coeffs(pack =
   D.Coeffs(1.0545718e-19)` (struct constructor argument);
   `Phys.Model(1.0, 0.5)` → `Phys.Model(1.0545718e-19, 5.272859e-20)`
   (class constructor argument); `J, h = 1.0, 0.5` →
   `J, h = 1.0545718e-19, 5.272859e-20` (classical multi-bind).

**One consolidation, not a new pattern**:
`test_liss0051_operator_factory_runtime_red.py` is a pure re-export —
it imports its three test functions directly from
`test_liss0107_examples_linker_runtime_red.py` (`from
test_liss0107_examples_linker_runtime_red import
test_linked_hamiltonian_factory_op_space_terminates, ...`). Its 1
failing case and `test_liss0107_...`'s 1 failing case are the *same
test object* — fixing `test_liss0107_examples_linker_runtime_red.py`'s
`hop(0, 1) + hop(1, 0)` Hamiltonian (wrapped as `1.0545718e-19 *
(hop(0, 1) + hop(1, 0))`) and its `for 0.1` → `for 0.1.fs` resolves
both files' failures with one edit.

**One new pattern found, live-verified before finalizing scope**:
`test_classical_float_operator_evolve_binding_red.py::test_evolve_for_
method_returned_float_runs` routes the duration through a method call
(`Float duration = s.t()`, where `s.t()` returns `this.duration`) —
not a literal, `Var`, or direct field `Attr`. Confirmed live this
*does* work correctly end-to-end, but only when the field/parameter/
return chain is declared `Time`-typed throughout (not `Float`) and
constructed from a `.fs`-suffixed literal — unit tracking propagates
correctly through `Time`-typed class fields → method-local `Time`
variables → `return` → the caller's `Time`-typed local binding. This
required changing 4 type annotations (`pub val duration: Float` →
`Time`; `fn init(t: Float)` → `Time`; `pub fn t() -> Float` → `Time`;
`Float out = ...` → `Time out = ...`) in addition to the coefficient
and duration edits, but is otherwise a normal case-2 conversion, not a
new Kernel gap — the general-value-plus-unit machinery LISS-0357
already fixed handles this correctly once the declared types line up.

**Scope decision, confirmed with the Adjudicator before drafting**: 19
cases across 10 files is sizable, and WP-0096's own investigation
flagged this work unit as a candidate for splitting into two Issues if
review size warranted it. Having now read every file and found the
patterns fully uniform (no unresolved surprises, unlike work unit 2),
kept as **one Issue** rather than splitting — splitting would add
branch/PR/review overhead without reducing risk, since every edit is
independent and individually verified.

## Per-file edits

- **`test_liss0107_examples_linker_runtime_red.py`** (also fixes
  `test_liss0051_operator_factory_runtime_red.py`'s re-exported case):
  `hop(0, 1) + hop(1, 0)` → `1.0545718e-19 * (hop(0, 1) + hop(1, 0))`;
  `for 0.1` → `for 0.1.fs`.
- **`test_operator_method_call_return_red.py`**: `_METHOD_LITERAL`:
  `-1.0 * (Z[0] * Z[1]) - 0.5 * (X[0] + X[1])` → coefficient swap;
  `_METHOD_FIELDS`: `Phys.Model(1.0, 0.5)` →
  `Phys.Model(1.0545718e-19, 5.272859e-20)`; both `for 0.7` →
  `for 0.7.fs`.
- **`test_sparse_pauli_operator_return_red.py`**: `_FACTORY_LITERAL`:
  coefficient swap; `_FACTORY_NAMED_FLOAT`: `Float J = 1.0` / `Float h
  = 0.5` → scaled values; both `for 0.7` → `for 0.7.fs`.
- **`test_liss_0297_operator_freefn_struct_coeffs_red.py`**:
  `D.Coeffs(0.5)` → `D.Coeffs(1.0545718e-19)`; `D.Coeffs(0.6, 0.5)` →
  `D.Coeffs(1.0545718e-19 * 0.6, ...)`-style scaled values (exact
  literals computed at edit time); `D.Coeffs(0.4, 0.3)` → scaled
  values; `for 0.1`/`for 0.2`/`for 0.15` → `.fs`-suffixed.
- **`test_liss_0305_classical_multi_bind_red.py`**: `J, h = 1.0, 0.5`
  → `J, h = 1.0545718e-19, 5.272859e-20`; `for 0.7` → `for 0.7.fs`.
- **`test_liss_0306_nested_opattr_and_effects_red.py`**: `Inner(0.5)` →
  `Inner(1.0545718e-19)`; `Drive(0.5)` → `Drive(1.0545718e-19)`; both
  `for 0.1` → `for 0.1.fs`.
- **`test_liss_0309_multi_ket_multi_bind_red.py`**: `J, h = 1.0, 0.5` →
  `J, h = 1.0545718e-19, 5.272859e-20`; `for 0.7` → `for 0.7.fs`.
- **`test_classical_float_operator_evolve_binding_red.py`**:
  `_PARAM_FACTORY`: `tfim(1.0, 0.5)` →
  `tfim(1.0545718e-19, 5.272859e-20)`; `_FIELD_TO_FLOAT`: `D.C(1.0,
  0.5)` → `D.C(1.0545718e-19, 5.272859e-20)`;
  `_EVOLVE_FOR_METHOD_FLOAT`: coefficient swap plus the `Time`-typed
  chain described above, `P.Schedule(0.7)` → `P.Schedule(0.7.fs)`; all
  three `for 0.7` → `for 0.7.fs`.
- **`test_liss_0121_classical_coefficient_vs_linear_red.py`**:
  `_NAMED_IN_BINDER`/`_LITERAL_IN_BINDER`: `Float J = 1.0`/`1.0 * Z[i] *
  Z[next(i)]` → scaled to `1.0545718e-19`; `_NAMED_OUTSIDE_BINDER`/
  `_LITERAL_OUTSIDE_BINDER`: `Float hx = 0.25`/`0.25 * X` → scaled to
  `2.6364295e-20` (`0.25 * K`); `_STRUCT_FIELD_COEFF`:
  `Dom.Couplings(0.25)` → `Dom.Couplings(2.6364295e-20)`; all `for 0.1`
  → `for 0.1.fs`. Live-verified this does not introduce
  `LINEAR_IMPLICIT_DISCARD`/`LINEAR_DUPLICATE_USE` on the scaled
  coefficients (the property 3 currently-passing tests in this file
  check via these same shared fixtures).

No Kernel source change. No example content change.

## Explicitly out of scope

- Any other WP-0096 work unit.
- `test_liss0051_operator_factory_runtime_red.py` itself (no edit
  needed — fixed transitively via its re-export source).
- Any currently-passing test in these 10 files not listed above.

## Acceptance reference

```gherkin
Feature: operator-factory/struct-coefficient evolve tests use real Time units

  Scenario: each migrated test passes with behavior unchanged
    Given the 19 cases across the 10 files listed above, migrated with
      the K-scale/`.fs`-duration conversion (applied at the coefficient's
      actual source: literal, struct/class constructor argument,
      classical multi-bind, or function parameter)
    When run
    Then each produces the same status result as originally intended
      pre-ADR-0195 (no EVOLVE_UNRESOLVED_UNIT_ERROR)

  Scenario: method-returned duration requires a Time-typed chain
    Given test_evolve_for_method_returned_float_runs' Schedule class
      with its duration field, init parameter, and t() method all
      declared Time-typed, constructed from a .fs-suffixed literal
    When run
    Then it does not raise EVOLVE_UNRESOLVED_UNIT_ERROR
```

## Verification plan for this design intake (not shipped as a test)

Every edit pattern (coefficient swap, source-value scaling, the
Time-typed method-return chain) live-verified in isolation before this
Issue was drafted. Full `pytest tests/ -q` regression, diffed against
the current baseline (30 failed, 1278 passed), confirming exactly these
19 cases move from FAIL to PASS and nothing else changes.
`spec_verification` expected unchanged (161/161).

## AI planning record (size M)

- Status: proposed, pre-Phase-1
- Authoring environment: Claude Code (Sonnet 5), this session
- Date: 2026-08-08
- Size: `M` — 10 files (9 needing edits, 1 fixed transitively), ~19
  cases, every edit pattern independently live-verified before
  drafting; kept as one Issue after confirming full uniformity, per
  Adjudicator direction.
- Route: direct implementation by this session.
- Confidence: high.

## Exit criteria

- [x] Phase 1 Red: confirmed exactly 19 cases already fail on `main`
      for the documented `EVOLVE_UNRESOLVED_UNIT_ERROR` reason across
      the 10 files (pre-existing tests, no new test file needed); 17
      other tests in the same files already passed unchanged.
- [x] Phase 2 Green: all edits above applied exactly as planned — no
      surprises this time (every pattern was already live-verified
      during design intake). All 36 tests across the 10 files pass.
- [x] Phase 3 Refactor: no further code change needed; reviewer
      empathy summary below; WP-0096 work unit 4 marked complete.
- [x] Full regression: `pytest tests/ -q` → 1297 passed, 11 failed
      (exactly -19 vs. the established 30-failure baseline, confirmed
      via full failure-list comparison — none of the 10 target files
      remain); `python3 tests/spec_verification/run_all.py` → 161/161
      (100%, Gate: PASS, unchanged); `git diff --check` → clean.

## Reviewer empathy summary

**何を目的として何を変更したか**: WP-0096作業単位4として、Hamiltonian
の係数が関数/メソッド返却値・struct/classフィールド・古典multi-bind
経由で`Operator H = ...`式に到達する10ファイル・19件の
`EVOLVE_UNRESOLVED_UNIT_ERROR`失敗を、確立済みの`K`スケール変換で
実`Time`単位へ移行した。係数リテラルが式の直近にないケースが多い
ため、変換は係数の実際の発生源（struct constructor引数、classical
変数代入、関数パラメータ）で適用した。

**AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
- `test_liss0051_operator_factory_runtime_red.py`が
  `test_liss0107_examples_linker_runtime_red.py`のテスト関数を
  そのままre-exportしているだけであることをソース読解で確認し、
  1箇所の修正で両ファイルの失敗が解消されることを事前に把握した
  （二重修正を避けた）。
- `test_evolve_for_method_returned_float_runs`（durationがメソッド
  呼び出し`s.t()`経由で渡される唯一のケース）について、設計時点で
  ライブ検証を行い、フィールド・パラメータ・戻り値の型注釈を全て
  `Float`から`Time`に変更し、`.fs`付きリテラルで構築する必要がある
  ことを確認してから実装した——LISS-0357が一般化した単位追跡機構
  （`_eval_value_with_unit`）が、宣言型が揃っていれば正しくこの
  チェーンを通すことをライブテストで確認済み。
- 19件全てが設計時点（Plan承認前）で個別にライブ検証済みだった
  ため、Green実施時に想定外の事象は発生しなかった。

**人間がコードレビューで重点的に見るべきポイント**:
- 特になし（設計時点の検証がそのままGreenの結果と一致した、低リスク
  な変更）。

## Non-goals

- Kernel source changes.
- Other WP-0096 work units.
